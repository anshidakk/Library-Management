
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, nowdate

class LibraryTransaction(Document):
    def before_submit(self):
        # Ensure date is set to today if not provided
        if not self.date:
            self.date = nowdate()

        article = frappe.get_doc("Article", self.article)

        if self.type == "Issue":
            self.validate_issue(article)
            self.validate_maximum_limit()
            if not self.issue_date:  # Only set if not already set
                self.issue_date = nowdate()  # Set issue date
            article.status = "Issued"
            article.save()
            self.add_article_to_member()

        elif self.type == "Return":
            self.validate_return(article)
            if not self.return_date:  # Only set if not already set
                self.return_date = nowdate()  # Set return date
            self.calculate_fine()  # Calculate fine based on fine_type

            if self.fine_amount > 0:
                self.validate_fine_status()
                self.create_fine_receipt()
            else:
                frappe.msgprint(_("No fine applicable for this transaction."))

            # Update the article status and remove it from the member's record
            article.status = "Available"
            article.save()
            self.remove_article_from_member()

        # Update the status of the transaction
        self.status = "Completed"

    def validate_issue(self, article):
        """Validate if the membership is valid and if the article can be issued."""
        self.validate_membership()
        if article.status == "Issued":
            frappe.throw(_("Article is already issued by another member"))

    def validate_return(self, article):
        """Validate if the article can be returned."""
        if article.status == "Available":
            frappe.throw(_("Article cannot be returned without being issued first"))

    def validate_maximum_limit(self):
        """Check if the member has reached the maximum limit of issued articles."""
        max_articles = frappe.db.get_single_value("Library Settings", "max_articles")
        count = frappe.db.count(
            "Library Transaction",
            {
                "library_member": self.library_member,
                "type": "Issue",
                "docstatus": 1,
            },
        )
        if count >= max_articles:
            frappe.throw(_("Maximum limit reached for issuing articles"))

    def validate_membership(self):
        """Check if the library member has a valid membership."""
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": 1,
                "from_date": ("<", self.date),
                "to_date": (">", self.date),
            },
        )
        if not valid_membership:
            frappe.throw(_("The member does not have a valid membership"))

    def add_article_to_member(self):
        """Add issued article to the library member's record."""
        library_member = frappe.get_doc("Library Member", self.library_member)
        library_member.append("books", {
            "article": self.article,
        })
        library_member.save()

    def remove_article_from_member(self):
        """Remove returned article from the library member's record."""
        library_member = frappe.get_doc("Library Member", self.library_member)

        # Find and remove the book from the member's list using list comprehension
        library_member.books = [book for book in library_member.books if book.article != self.article]

        library_member.save()

    def calculate_fine(self):
        """Calculate and set fine for overdue returns, damage, or lost articles."""

        # Check that fine_type is defined
        if not hasattr(self, 'fine_type'):
            frappe.throw(_("Fine type must be specified."))

        fine_type = self.fine_type

        if fine_type == "Overdue":
            # Overdue fine calculation
            if not self.issue_date or not self.return_date:
                frappe.throw(_("Issue date or return date is missing for overdue fine calculation"))

            loan_period = frappe.db.get_single_value("Library Settings", "loan_period")
            overdue_fine_per_day = frappe.db.get_single_value("Library Settings", "overdue_fine_per_day")

            days_issued = date_diff(self.return_date, self.issue_date)
            overdue_days = days_issued - loan_period

            # Calculate fine amount
            self.fine_amount = max(0, overdue_days * overdue_fine_per_day)

        elif fine_type == "Damage":
            # Fixed fine for damage
            damage_fine_amount = frappe.db.get_single_value("Library Settings", "damage_fine_amount")
            self.fine_amount = damage_fine_amount

        elif fine_type == "Lost":
            # Fine based on article price
            if not hasattr(self, 'article_price') or not self.article_price:
                frappe.throw(_("Article price is required to calculate lost fine"))

            lost_fine_rate = frappe.db.get_single_value("Library Settings", "lost_fine_rate")
            self.fine_amount = (self.article_price * lost_fine_rate) / 100

        else:
            self.fine_amount = 0

        frappe.msgprint(_("Fine calculated: {0}").format(self.fine_amount))

    def create_fine_receipt(self):
        """Create a fine receipt for the overdue article."""

        # Check for existing unpaid receipts before creating a new one
        existing_receipts = frappe.get_all(
            "Fine Receipt",
            filters={
                "library_transaction": self.name,
                "status": "Unpaid",
            },
            fields=["name"]
        )

        if existing_receipts:
            frappe.throw(_("A fine receipt already exists for this transaction."))

        fine_receipt = frappe.get_doc({
            "doctype": "Fine Receipt",
            "library_transaction": self.name,
            "library_member": self.library_member,
            "fine_amount": self.fine_amount,
            "receipt_date": nowdate(),
            "status": "Unpaid",  # Initial status can be Unpaid
        })

        fine_receipt.insert()

        frappe.msgprint(_("Fine receipt created for the member: {0}").format(self.library_member))

    def validate_fine_status(self):
        """Ensure that any outstanding fine is cleared before processing the transaction."""

        # Check for unpaid fine receipts associated with this transaction
        unpaid_fines = frappe.get_all(
            "Fine Receipt",
            filters={
                "library_transaction": self.name,
                "status": "Unpaid",
            },
            fields=["name"]
        )

        if unpaid_fines:
            frappe.throw(_("Outstanding fines must be paid before completing the transaction."))
