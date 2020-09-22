# Copyright (c) 2013, ahmadragheb and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		_("Sales Order") + ":Link/Sales Order:120",
		_("Item") + ":Link/Item:120",
		_("qty") + "::60"
	]

def get_data(filters):
	conditions = get_conditions(filters)


	# dn = frappe.db.sql("""select dni.against_sales_order , dni.item_code, sum(dni.qty) as qty 
	# from `tabDelivery Note Item` dni Inner JOIN `tabDelivery Note` dn on dni.parent = dn.name
	# 	and dn.docstatus =1 and dni.against_sales_order IS NOT NULL and dn.is_return = 0 
	# 	group by dni.against_sales_order """, as_dict=1)
	# dn = frappe.db.sql("""select against_sales_order , item_code, sum(qty) as qty
	# from `tabDelivery Note Item` where docstatus =1 and against_sales_order IS NOT NULL
	# group by against_sales_order""", as_dict=1)

	# dn_dict = {}
	# for item in dn:
	# 	against_sales_order = item.pop('against_sales_order')
	# 	dn_dict[against_sales_order] = item

	so = frappe.db.sql("""
		SELECT so.name, smi.item_code, smi.blocked_qty as qty
		FROM `tabSales Order` so
		LEFT JOIN `tabSales Order Item` smi ON  so.name = smi.parent
		WHERE smi.is_blocked=1 and so.status not in ('Cancelled','Completed', 'Draft', 'Closed') and
			  smi.blocked_qty IS NOT NULL and smi.blocked_qty != 0
	""", as_dict=1)
	# so_dict = {}
	# for item in so:
	# 	# name = item.pop('name')
	# 	name = item['name']
	# 	so_dict[name] = item

	# for so in so_dict :
	# 	if so in dn_dict:
	# 		qty = dn_dict[so].qty
	# 		so_dict[so].blocked_qty = flt(so_dict[so].blocked_qty) - flt(qty)

	result = [[x.name, x.item_code, x.qty] for x in so]

	return result


def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"].index(filters["month"]) + 1
		conditions += " and month(date_of_birth) = '%s'" % month

	if filters.get("company"): conditions += " and company = '%s'" % \
		filters["company"].replace("'", "\\'")

	return conditions
