frappe.ui.form.on('Library Membership', {
    refresh: function(frm) {
        // Add a custom button to make a Library Membership Payment
        frm.add_custom_button(__('Make Membership Payment'), () => {
            const dialog = new frappe.ui.Dialog({
                title: __('Make Membership Payment'),
                fields: [
                    {
                        fieldname: 'membership_amount',
                        label: __('Updated Membership Amount'),
                        fieldtype: 'Float',
                        default: frm.doc.membership_amount,
                        reqd: 1
                    }
                ],
                primary_action_label: __('Proceed'),
                primary_action(values) {
                    const membershipAmount = values.membership_amount;

                    if (!membershipAmount || membershipAmount <= 0) {
                        frappe.msgprint({
                            title: __('Invalid Amount'),
                            message: __('Please enter a valid Membership Amount.'),
                            indicator: 'red'
                        });
                        return;
                    }

                    dialog.hide();

                    // Create and save a new Fine Receipt document
                    frappe.call({
                        method: "frappe.client.insert",
                        args: {
                            doc: {
                                doctype: 'Fine Receipt',
                                library_membership: frm.doc.name,
                                fine_amount: membershipAmount,  // Set the fine_amount field here
                                fine_type: 'Membership',  // Set the fine type
                                status: 'Unpaid',  // Adjust the default status
                                receipt_date: frappe.datetime.now_date()  // Set today's date
                            }
                        },
                        callback: function(response) {
                            if (response.message) {
                                frappe.msgprint({
                                    title: __('Success'),
                                    message: __('Fine Receipt created successfully.'),
                                    indicator: 'green'
                                });
                                // Optionally, reload the form or navigate to the new Fine Receipt
                                frappe.set_route("Form", "Fine Receipt", response.message.name);
                            }
                        },
                        error: function(err) {
                            frappe.msgprint({
                                title: __('Error'),
                                message: __('An error occurred while creating the Fine Receipt.'),
                                indicator: 'red'
                            });
                        }
                    });
                }
            });

            dialog.show();
        });

        // Add a button to navigate to Fine Receipt if already linked
        if (frm.doc.docstatus === 1 && frm.doc.membership_amount > 0) {
            frm.add_custom_button(__('Go to Fine Receipt'), function() {
                frappe.call({
                    method: "library_management.library_management.doctype.library_membership.library_membership.get_fine_receipt",
                    args: {
                        membership_id: frm.doc.name
                    },
                    callback: function(response) {
                        if (response.message) {
                            frappe.set_route("Form", "Fine Receipt", response.message);
                        } else {
                            frappe.msgprint({
                                title: __('No Fine Receipt Found'),
                                message: __('There is no Fine Receipt linked to this membership.'),
                                indicator: 'red'
                            });
                        }
                    }
                });
            }, __('Actions'));
        }
    },

    from_date: function(frm) {
        validate_dates(frm);
    },
    to_date: function(frm) {
        validate_dates(frm);
    }
});

function validate_dates(frm) {
    const { from_date, to_date } = frm.doc;

    if (from_date && to_date) {
        const fromDateObj = new Date(from_date);
        const toDateObj = new Date(to_date);

        if (fromDateObj > toDateObj) {
            frappe.throw(__(' "From Date" cannot be greater than the "To Date".'));
            frm.set_value('to_date', '');
        }
    }
}
