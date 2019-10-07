from __future__ import unicode_literals

import frappe
import frappe.handler
import frappe.client
from frappe.utils import cstr, flt, getdate, cint, nowdate, add_days, get_link_to_form
from frappe.core.doctype.user.user import get_roles
from frappe.model.naming import make_autoname


def map_qty_to_blocked_field(doc, method):
	items = doc.get("items")
	for row in items:
		row.blocked_qty=row.qty

def so_team(doc,method):
	user = str(frappe.session.data.user)
	roles = frappe.permissions.get_roles(user)

	valid = False
	if "Sales Person" in roles:
		valid = True

	if valid:
		emp = frappe.get_value('Employee', { 'user_id': user }, 'name')
		if emp:
			sales_person = frappe.get_value('Sales Person', { 'employee': emp, "enabled": 1 }, 'name')
			if sales_person:
				row = doc.append("sales_team",{})
				row.sales_person = sales_person
				row.allocated_percentage = 100

def check_availability_for_items_based_on_booked(doc, method):
	
	""" when create Sales Order for item Pepsi and it has
		stock_qty= 5 in store and
		booked_items=3 then
		available_qty = stock_qty - booked_items
		and then verify qty in sales order < or = avaliable """
	for d in doc.get('items'):
		sql_stat ='''select sum(soi.blocked_qty) as qty, so.name, soi.item_code from
		 `tabSales Order Item` as soi inner join `tabSales Order` as so on
		  so.name = soi.parent and soi.item_code = '{}'  and soi.warehouse = '{}' and soi.is_blocked = 1
		  and so.status not in ('Cancelled','Completed','Closed') 
			'''.format(d.item_code , d.warehouse)
		blocked = frappe.db.sql(sql_stat)
		bloked_qty = flt(blocked[0][0]) or 0

		actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
			where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
		actual_qty = flt(actual_qty[0][0]) or 0
		if  actual_qty < bloked_qty:
			frappe.throw("You can't order item {} because ordered quantity {} is more than stock available quantity {}".format(
				d.item_code, d.stock_qty, actual_qty))

def workflow(doc, method):
	checker = doc.difference_exist
	value = flt(doc.difference_value)
	if(checker):
		if(value<100):
			doc.workflow_state = "New(2t)"
		elif(100<=value and doc.workflow_state not in ["New(3t)", "Approved By Accounts Manager",
		 "Approved By Branch Manager", "Approved By CEO",
		"Rejected By Accounts Manager","Rejected By Branch Manager", "Rejected By CEO"]) :
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

			bloked_qty = frappe.db.sql('''SELECT sum(smi.blocked_qty) as qty FROM `tabSales Order` so
			inner join `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
			smi.warehouse = %s and smi.is_blocked = 1 and so.status not in ('Cancelled','Completed','Closed') ''',
			(d.item_code, d.s_warehouse)
			)

			blocked_qty = flt(bloked_qty[0][0]) or 0

			actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
				where item_code = '{}' and warehouse = '{}' ".format(d.item_code, d.s_warehouse))

			actual_qty = flt(actual_qty[0][0]) or 0

			allowed_qty = (d.transfer_qty + actual_qty) - blocked_qty

			if actual_qty < blocked_qty:
				frappe.throw("You can't Transfer item {} because transfer quantity {} is \
				more than stock available quantity {} for warehouse {}".format(
					d.item_code, d.transfer_qty, allowed_qty, d.s_warehouse))


def si_for_items_based_on_booked(doc,method):
	if doc.update_stock == 1:
		si_update_stock(doc, method)
	else:
		si_no_update_stock(doc, method)

def si_no_update_stock(doc, method):
	pass

def si_update_stock(doc, method):
	""" when create Sales Order for item Pepsi and it has
		stock_qty= 5 in store and
		booked_items=3 then
		available_qty = stock_qty - booked_items
		and then verify qty in sales order < or = avaliable """
	for d in doc.get('items'):
		if d.warehouse:
			bloked_qty = frappe.db.sql('''SELECT sum(smi.blocked_qty) FROM `tabSales Order` so
			LEFT JOIN `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
			smi.warehouse = %s and smi.is_blocked = 1 and so.status not in ('Cancelled','Completed','Closed') ''',
			(d.item_code, d.warehouse)
			)

			# stock_uom  d.stock_qty 
			sql_stat = "select sum(actual_qty) as qty from `tabBin` where item_code = '{}' and warehouse = '{}'".format(d.item_code, d.warehouse)
			actual_qty = frappe.db.sql(sql_stat)

			bloked_qty = flt(bloked_qty[0][0]) or 0
			actual_qty = flt(actual_qty[0][0]) or 0
			if bloked_qty != 0 :
				real_blocked_qty = actual_qty - bloked_qty
				rr = real_blocked_qty + d.qty
				if d.qty > real_blocked_qty :
					frappe.throw("You can't order item {} because ordered quantity {} is more than stock available quantity {}".format(
						d.item_code, d.qty, rr))
		else:
			frappe.throw("Please select warehouse for item {}".format(d.item_code) )


def generate_unique_customer_number(doc, method):
	doc.customer_number = make_autoname('.#####')

def delivery_note_affect_so_blocked(doc, method):
	if doc.is_return == 0:
		for d in doc.get('items'):
			if d.against_sales_order:
				so = frappe.get_doc("Sales Order",d.against_sales_order)
				soi = so.get("items")
				for row in soi:
					if row.warehouse == d.warehouse and row.item_code == d.item_code:
						row.blocked_qty = row.blocked_qty - d.qty  
						if row.blocked_qty <0 :
							frappe.throw("Blocked qty is bigger than qty in sales order")
				so.save()
				frappe.db.commit()

def delivery_note_cancel(doc, method):
	if doc.is_return == 0:
		for d in doc.get('items'):
			if d.against_sales_order:
				so = frappe.get_doc("Sales Order",d.against_sales_order)
				soi = so.get("items")
				for row in soi:
					if row.warehouse == d.warehouse and row.item_code == d.item_code:
						row.blocked_qty = row.blocked_qty + d.qty  
						if row.blocked_qty <0 :
							frappe.throw("Blocked qty is bigger than qty in sales order")
				so.save()
				frappe.db.commit()