from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
    config = [
        {
            "label": _("Other Reports "),
            "items": [
                {
                    "type": "report",
                    "name": "Blocked Items",
                    "doctype": "Sales Order",
                    "is_query_report": True,
                },
            ]
        },
    ]
    return config