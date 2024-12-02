import frappe

def after_insert(doc, method):
    frappe.msgprint("User with ID {} has been created.".format(doc.name))
