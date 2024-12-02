
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days

class LibraryMembership(Document):
    def before_submit(self):
        # Check for active membership
        self.check_active_membership()

        # Validate dates and set to_date based on loan period
        self.validate_membership_dates()

        loan_period = frappe.db.get_single_value("Library Settings", "loan_period") or 30
        self.to_date = add_days(self.from_date, loan_period)

        # Ensure membership amount is paid
        self.validate_membership_payment()

        # Generate a Fine Receipt if membership amount is specified
        fine_receipt = self.create_fine_receipt()

        # Automatically submit if payment is made
        if fine_receipt and fine_receipt.status == "Paid":
            frappe.msgprint(_("Membership payment confirmed. Membership submitted automatically."))

    def check_active_membership(self):
        exists = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": 1,
                "to_date": (">", self.from_date),
            },
        )
        if exists:
            frappe.throw(_("There is an active membership for this member."))

    def validate_membership_dates(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw(_("From date cannot be greater than To date."))

    def validate_membership_payment(self):
        if not self.membership_amount or self.membership_amount <= 0:
            frappe.throw(_("Membership amount must be greater than zero."))

    def create_fine_receipt(self):
        existing_receipt = frappe.get_all(
            "Fine Receipt",
            filters={
                "library_membership": self.name,
                "status": ["in", ["Unpaid", "Paid"]],
            },
            fields=["name", "status"]
        )

        if existing_receipt:
            receipt = existing_receipt[0]
            frappe.msgprint(_("A Fine Receipt already exists with status: {0}.").format(receipt.status))
            return frappe.get_doc("Fine Receipt", receipt.name)

        # Create a new Fine Receipt
        fine_receipt = frappe.get_doc({
            "doctype": "Fine Receipt",
            "library_membership": self.name,
            "fine_type": "Membership",
            "fine_amount": self.membership_amount,
            "status": "Unpaid",  # Default to Unpaid
        })

        fine_receipt.insert(ignore_permissions=True)
        #frappe.msgprint(_("Fine Receipt created for membership amount: {0}.").format(self.membership_amount))

        return fine_receipt
