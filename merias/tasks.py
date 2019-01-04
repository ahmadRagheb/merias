from __future__ import unicode_literals

import frappe
import frappe.handler
import frappe.client
from frappe.utils import cstr, flt, getdate, cint, nowdate, add_days, get_link_to_form


def hourly():
	blocked_so = frappe.db.sql('''SELECT so.name FROM `tabSales Order` so
		LEFT JOIN `tabSales Order Item` smi ON so.name = smi.parent and
		smi.is_blocked = 1 and so.status not in ('Cancelled','Completed') ''',as_dict=True)

	so = tuple([x.name for x in blocked_so ])
	message = "Hi, There is not collected Sales Order {}".format(so)
	user_list = frappe.get_all('User',filters={'enabled':1})
	for user in user_list:
		roles = [ur.role for ur in user.roles]
		if ("Sales User" in roles) or ("Sales Manager" in roles):
			frappe.publish_realtime(event='eval_js', message='alert("{0}")'.format(message),
				user=user['name'])

