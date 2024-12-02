// Copyright (c) 2024, anshida and contributors
// For license information, please see license.txt


// File: library_management/library_management/report/article_status/article_status_report.js

// article_report.js
frappe.query_reports["Article Script Report"] = {
    filters: [
        {
            fieldname: "article_name",
            label: __("Article Name"),
            fieldtype: "Data",
            default: "",
            reqd: 0
        },
        {
            fieldname: "author",
            label: __("Author"),
            fieldtype: "Data",
            default: "",
            reqd: 0
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: ["", "Available", "Issued"],
            default: "",
            reqd: 0
        },
        {
            fieldname: "isbn",
            label: __("ISBN"),
            fieldtype: "Data",
            default: "",
            reqd: 0
        },
        {
            fieldname: "publisher",
            label: __("Publisher"),
            fieldtype: "Data",
            default: "",
            reqd: 0
        },
        {
            fieldname: "route",
            label: __("Route"),
            fieldtype: "Data",
            default: "",
            reqd: 0
        }
    ],

    onload: function (report) {
        // Fetch chart data
        frappe.call({
            method: "library_management.library_management.report.article_script_report.article_script_report.get_chart_data",
            callback: function (r) {
                if (r.message) {
                    report.set_chart(get_chart(r.message));
                }
            }
        });

        // Fetch summary data
        frappe.call({
            method: "library_management.library_management.report.article_script_report.article_script_report.get_summary",
            callback: function (r) {
                if (r.message) {
                    report.set_summary(r.message);
                }
            }
        });
    }
};

function get_chart(chart_data) {
    return {
        data: {
            labels: chart_data.labels,
            datasets: [
                {
                    name: chart_data.dataset_name,
                    values: chart_data.values
                }
            ]
        },
        type: chart_data.type || "bar",
        colors: chart_data.colors || ["#f39c12", "#2ecc71"],
    };
}
