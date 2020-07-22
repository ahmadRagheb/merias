# -*- coding: utf-8 -*-
# Copyright (c) 2019, ahmadragheb and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from merias.api import has_product_bundle

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
						if has_product_bundle(d.item_code):
							for p in so.get("packed_items"):
								if p.parent_item == d.item_code:
									pb = frappe.get_doc('Product Bundle', p.parent_item)
									for row_pb in pb.get('items'):
										if row_pb.item_code == p.item_code:
											rate = 1/row_pb.qty
											p.blocked_qty = d.blocked_qty/rate
				so.save()
				frappe.db.commit()

