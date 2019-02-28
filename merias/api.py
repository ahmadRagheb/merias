from __future__ import unicode_literals

import frappe
import frappe.handler
import frappe.client
from frappe.utils import cstr, flt, getdate, cint, nowdate, add_days, get_link_to_form


def workflow(doc, method):
	checker = doc.difference_exist
	value = flt(doc.total_outgoing_value)
	if(checker):
		if(value<100):
			doc.workflow_state = "New(2t)"
		elif(100<value and value<1000):
			doc.workflow_state = "New(3t)"
		else:
			doc.workflow_state = "New(3t)"
	else:
		doc.workflow_state = "New"

def stock_entry(doc, method):
	""" by defult system check if item qty in warehouse >= transfered qty from that warehouse
		if okay then we add transfer with actuall qty then this will give us the totall
		the we subtracted blocked item from total  
	"""
	if doc.purpose == "Material Transfer":
		for d in doc.get('items'):
			
			bloked_qty = frappe.db.sql('''SELECT sum(smi.qty) FROM `tabSales Order` so 
			LEFT JOIN `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
			smi.warehouse = %s and smi.is_blocked = 1 and so.status not in ('Cancelled','Completed') ''',
			(d.item_code, d.s_warehouse)
			)

			blocked_qty = flt(bloked_qty[0][0]) or 0
			
			actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
				where item_code = %s and warehouse = %s", (str(d.item_code), str(d.s_warehouse)))
			actual_qty = flt(actual_qty[0][0]) or 0

			allowed_qty = (d.transfer_qty + actual_qty) - blocked_qty

			if actual_qty < blocked_qty:
				frappe.throw("You can't Transfer item {} because transfer quantity {} is \
				more than stock available quantity {} for warehouse {}".format(
					d.item_code, d.transfer_qty, allowed_qty, d.s_warehouse))


def check_availability_for_items_based_on_booked(doc, method):
	""" when create Sales Order for item Pepsi and it has 
		stock_qty= 5 in store and 
		booked_items=3 then  
		available_qty = stock_qty - boo	ked_items
		and then verify qty in sales order < or = avaliable """
	for d in doc.get('items'):

		bloked_qty = frappe.db.sql('''SELECT sum(smi.qty) FROM `tabSales Order` so 
		LEFT JOIN `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
		smi.warehouse = %s and smi.is_blocked = 1 and so.status not in ('Cancelled','Completed') ''',
		(d.item_code, d.warehouse)
		)

		# bloked_qty = frappe.db.sql("select sum(qty) from `tabSales Order Item` \
		# 	where item_code = %s and warehouse = %s and is_blocked = 1 \
		# 	and parent != %s", (d.item_code, d.warehouse,d.parent))
		bloked_qty = flt(bloked_qty[0][0]) or 0

		actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
			where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
		actual_qty = flt(actual_qty[0][0]) or 0
		projected_qty = frappe.db.sql("select sum(projected_qty) from `tabBin` \
			where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
		projected_qty = flt(projected_qty[0][0]) or 0
		allowed_qty = actual_qty - bloked_qty
		allowed_and_qty = allowed_qty+d.qty
		if  allowed_and_qty < d.stock_qty:
			frappe.throw("You can't order item {} because ordered quantity {} is more than stock available quantity {}".format(
				d.item_code, d.stock_qty, allowed_and_qty))

def si_for_items_based_on_booked(doc, method):
	""" when create Sales Order for item Pepsi and it has 
		stock_qty= 5 in store and 
		booked_items=3 then  
		available_qty = stock_qty - booked_items 
		and then verify qty in sales order < or = avaliable """
	for d in doc.get('items'):
		if d.warehouse:
			bloked_qty = frappe.db.sql('''SELECT sum(smi.qty) FROM `tabSales Order` so 
			LEFT JOIN `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
			smi.warehouse = %s and smi.is_blocked = 1 and so.status not in ('Cancelled','Completed') ''',
			(d.item_code, d.warehouse)
			)
			actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
				where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
			projected_qty = frappe.db.sql("select sum(projected_qty) from `tabBin` \
				where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))	
		else:
			bloked_qty = frappe.db.sql('''SELECT sum(smi.qty) FROM `tabSales Order` so 
			LEFT JOIN `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
			smi.is_blocked = 1 and so.status not in ('Cancelled','Completed') ''',
			(d.item_code)
			)
			actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
			where item_code = %s", (d.item_code))
			projected_qty = frappe.db.sql("select sum(projected_qty) from `tabBin` \
			where item_code = %s", (d.item_code))

		bloked_qty = flt(bloked_qty[0][0]) or 0
		actual_qty = flt(actual_qty[0][0]) or 0
		projected_qty = flt(projected_qty[0][0]) or 0

		real_blocked_qty = actual_qty - bloked_qty 

		if d.stock_qty > real_blocked_qty :
			frappe.throw("You can't order item {} because ordered quantity {} is more than stock available quantity {}".format(
				d.item_code, d.stock_qty, real_blocked_qty))
