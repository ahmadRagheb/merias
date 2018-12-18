from __future__ import unicode_literals

import json
import frappe
import frappe.handler
import frappe.client
from frappe.utils.response import build_response
from frappe.utils import cstr, flt, getdate, cint, nowdate, add_days, get_link_to_form

from frappe import _
from six.moves.urllib.parse import urlparse, urlencode
import base64
		

def check_availability_for_items_based_on_booked(doc, method):
	""" when create Sales Order for item Pepsi and it has 
		stock_qty= 5 in store and 
		booked_items=3 then  
		available_qty = stock_qty - booked_items 
		and then verify qty in sales order < or = avaliable """
	for d in doc.get('items'):
		bloked_qty = frappe.db.sql("select sum(qty) from `tabSales Order Item` \
			where item_code = %s and warehouse = %s and is_blocked = 1 \
			and parent != %s", (d.item_code, d.warehouse,d.parent))
		bloked_qty = flt(bloked_qty[0][0]) or 0

		actual_qty = frappe.db.sql("select actual_qty from `tabBin` \
			where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
		actual_qty = flt(actual_qty[0][0]) or 0
		projected_qty = frappe.db.sql("select projected_qty from `tabBin` \
			where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
		projected_qty = flt(projected_qty[0][0]) or 0

		allowed_qty = actual_qty - bloked_qty
		
		if allowed_qty < d.qty:
			frappe.throw("You can't order item {} because ordered quantity {} is more than stock available quantity {}".format(
				d.item_code, d.qty, allowed_qty))

def si_for_items_based_on_booked(doc, method):
	""" when create Sales Order for item Pepsi and it has 
		stock_qty= 5 in store and 
		booked_items=3 then  
		available_qty = stock_qty - booked_items 
		and then verify qty in sales order < or = avaliable """
	for d in doc.get('items'):
		if d.warehouse:
			bloked_qty = frappe.db.sql("select sum(qty) from `tabSales Order Item` \
				where item_code = %s and warehouse = %s and is_blocked = 1"
				,(d.item_code, d.warehouse))
			actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
				where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
			projected_qty = frappe.db.sql("select sum(projected_qty) from `tabBin` \
				where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
					
		else:
			bloked_qty = frappe.db.sql("select sum(qty) from `tabSales Order Item` \
				where item_code = %s  and is_blocked = 1", (d.item_code))
			actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
			where item_code = %s", (d.item_code))
			projected_qty = frappe.db.sql("select sum(projected_qty) from `tabBin` \
			where item_code = %s", (d.item_code))
		
		bloked_qty = flt(bloked_qty[0][0]) or 0
		actual_qty = flt(actual_qty[0][0]) or 0
		projected_qty = flt(projected_qty[0][0]) or 0
		allowed_qty = actual_qty - bloked_qty
		if allowed_qty < d.qty:
			frappe.throw("You can't order item {} because ordered quantity {} is more than stock available quantity {}".format(
				d.item_code, d.qty, allowed_qty))
