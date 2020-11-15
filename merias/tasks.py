# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
from frappe import _
import frappe.handler
import frappe.client
from frappe.utils import cstr, flt, getdate, cint, nowdate, add_days, get_link_to_form

def hourly():
	""" Schedual task Triggered hourly will send notification to
	Sales User and Sales Manager , with all Sales order contains
	Blocked Items 	
	"""
	
	blocked_so = frappe.db.sql('''SELECT so.name FROM `tabSales Order` so
		JOIN `tabSales Order Item` smi ON so.name = smi.parent and
		smi.is_blocked = 1 and so.status not in ('Cancelled','Completed', 'Draft', 'Closed') ''',as_dict=True)
	count = len(blocked_so)
	action_button = """<button onclick="action_so()">اضغط هنا</button>"""
	message = _(u"""يوجد طلبات بيع ببضاعة محجوزة لم يتم مراجعتها عددها {} للمزيد من المعلومات""".format(count))

	user_list = frappe.get_all('User',filters={'enabled':1})
	for user in user_list:
		user_obj = frappe.get_doc('User',user.name)
		roles = [ur.role for ur in user_obj.roles]
		if ("Sales User" in roles) or ("Sales Manager" in roles):
			frappe.publish_realtime(event='eval_js', message="""frappe.msgprint('{}'+ '{}')""".format(message,action_button),
				user=user['name'])

