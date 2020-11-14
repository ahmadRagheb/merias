from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Other Reports"),
            "icon": "fa fa-list",
            "items": [
                {
                    "type": "doctype",
                    "name": "Release Blocked Item",
                    "description": _("Release Blocked Item."),
                    "onboard": 1,
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Blocked Items",
                    "doctype": "Item"
                }
            ]
        },
    ]
