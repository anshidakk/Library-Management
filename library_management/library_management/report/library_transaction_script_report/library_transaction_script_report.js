// Copyright (c) 2024, anshida and contributors
// For license information, please see license.txt

frappe.query_reports["Library Transaction Script Report"] = {
    filters: [
        {
            fieldname: "article",
            label: __("Article"),
            fieldtype: "Link",
            options: "Article",
            reqd: 0
        },
        {
            fieldname: "library_member",
            label: __("Library Member"),
            fieldtype: "Link",
            options: "Library Member",
            reqd: 0
        },
        {
            fieldname: "type",
            label: __("Type"),
            fieldtype: "Select",
            options: ["", "Issue", "Return"],
            reqd: 0
        },
        {
            fieldname: "date",
            label: __("Date"),
            fieldtype: "Date",
            reqd: 0
        }
    ]
};
