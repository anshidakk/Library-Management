
frappe.ui.form.on('Library Member', {
    refresh: function(frm) {
        // Add a custom button to create a Library Membership
        frm.add_custom_button('Create Membership', () => {
            frappe.new_doc('Library Membership', {
                library_member: frm.doc.name
            });
        });

        // Add a custom button to create a Library Transaction
        frm.add_custom_button('Create Transaction', () => {
            frappe.new_doc('Library Transaction', {
                library_member: frm.doc.name
            });
        });
    }
});
