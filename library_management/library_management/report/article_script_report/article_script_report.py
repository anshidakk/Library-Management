# Copyright (c) 2024, anshida and contributors
# For license information, please see license.txt

# article_report.py
import frappe
from frappe import _

def execute(filters=None):
    """
    Executes the script report and returns columns, data, and other information.
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary

def get_columns():
    """
    Define the columns of the report.
    """
    return [
        {"label": _("Article Name"), "fieldname": "article_name", "fieldtype": "Data", "width": 200},
        {"label": _("Author"), "fieldname": "author", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("ISBN"), "fieldname": "isbn", "fieldtype": "Data", "width": 100},
        {"label": _("Publisher"), "fieldname": "publisher", "fieldtype": "Data", "width": 150},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Text Editor", "width": 350},
        {"label": _("Route"), "fieldname": "route", "fieldtype": "Data", "width": 200},
    ]

def get_data(filters):
    """
    Fetch data for the report based on the provided filters.
    """
    conditions = []

    if filters.get("article_name"):
        conditions.append(f"""name LIKE '%{filters["article_name"]}%'""")

    if filters.get("author"):
        conditions.append(f"""author LIKE '%{filters["author"]}%'""")

    if filters.get("status"):
        conditions.append(f"""status = '{filters["status"]}'""")

    if filters.get("isbn"):
        conditions.append(f"""isbn LIKE '%{filters["isbn"]}%'""")

    if filters.get("publisher"):
        conditions.append(f"""publisher LIKE '%{filters["publisher"]}%'""")

    if filters.get("route"):
        conditions.append(f"""route LIKE '%{filters["route"]}%'""")

    condition_string = " AND ".join(conditions)
    if condition_string:
        condition_string = f"WHERE {condition_string}"

    query = f"""
        SELECT
            name as article_name,
            author,
            status,
            isbn,
            publisher,
            description,
            route
        FROM
            `tabArticle`
        {condition_string}
    """

    return frappe.db.sql(query, as_dict=True)

def get_chart_data(data):
    """
    Generate chart data for the report.
    """
    issued_count = sum(1 for d in data if d.get("status") == "Issued")
    available_count = sum(1 for d in data if d.get("status") == "Available")

    return {
        "labels": ["Issued", "Available"],
        "dataset_name": _("Article Status"),
        "values": [issued_count, available_count],
        "type": "bar",
        "colors": ["#e74c3c", "#2ecc71"],
    }

def get_summary(data):
    """
    Generate a summary for the report.
    """
    total_articles = len(data)
    issued_count = sum(1 for d in data if d.get("status") == "Issued")
    available_count = sum(1 for d in data if d.get("status") == "Available")

    return [
        {"value": total_articles, "label": _("Total Articles"), "datatype": "Int"},
        {"value": issued_count, "label": _("Issued Articles"), "datatype": "Int"},
        {"value": available_count, "label": _("Available Articles"), "datatype": "Int"},
    ]
