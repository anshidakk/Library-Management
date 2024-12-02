# Copyright (c) 2024, anshida and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _

def execute(filters=None):
    """
    Executes the script report and returns columns and data.
    """
    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    """
    Define the columns of the report.
    """
    return [
        {"label": _("ID"), "fieldname": "id", "fieldtype": "Data", "width": 100},
        {"label": _("Article Name"), "fieldname": "article_name", "fieldtype": "Data", "width": 200},
        {"label": _("Author"), "fieldname": "author", "fieldtype": "Data", "width": 150},
        {"label": _("Library Member"), "fieldname": "full_name", "fieldtype": "Data", "width": 200},
        {"label": _("Phone"), "fieldname": "phone", "fieldtype": "Data", "width": 150},
        {"label": _("Type"), "fieldname": "type", "fieldtype": "Select", "options": "Issue\nReturn", "width": 100},
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 150},
    ]

def get_data(filters):
    """
    Fetch data for the report based on the provided filters.
    """
    conditions = []

    if filters.get("article"):
        conditions.append(f"""article = '{filters["article"]}'""")

    if filters.get("library_member"):
        conditions.append(f"""library_member = '{filters["library_member"]}'""")

    if filters.get("type"):
        conditions.append(f"""type = '{filters["type"]}'""")

    if filters.get("date"):
        conditions.append(f"""date = '{filters["date"]}'""")

    condition_string = " AND ".join(conditions)
    if condition_string:
        condition_string = f"WHERE {condition_string}"

    query = f"""
        SELECT
            lt.name as id,
            a.article_name,
            a.author,
            lm.full_name,
            lm.phone,
            lt.type,
            lt.date
        FROM
            `tabLibrary Transaction` lt
        LEFT JOIN
            `tabArticle` a ON lt.article = a.name
        LEFT JOIN
            `tabLibrary Member` lm ON lt.library_member = lm.name
        {condition_string}
    """

    return frappe.db.sql(query, as_dict=True)
