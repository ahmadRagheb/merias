# -*- coding: utf-8 -*-
# Copyright (c) 2019, ahmadragheb and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ReleaseBlockedItem(Document):
	def on_update(self):
		if self.sales_order:
			so = frappe.get_doc("Sales Order",self.sales_order)
			for d in self.get('items'):
				soi = so.get("items")
				for row in soi:
					if row.warehouse == d.warehouse and row.item_code == d.item_code:
						row.blocked_qty = d.blocked_qty  
						if row.blocked_qty <0 :
							frappe.throw("Blocked qty is bigger than qty in sales order")
				so.save()
				frappe.db.commit()

