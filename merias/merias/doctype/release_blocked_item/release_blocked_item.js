// Copyright (c) 2019, ahmadragheb and contributors
// For license information, please see license.txt

frappe.ui.form.on('Release Blocked Item', {
    sales_order: function(frm) {
		if (frm.doc.sales_order){
			frm.items = []
			frm.refresh_field("items");
			frappe.model.with_doc("Sales Order", frm.doc.sales_order, function() {
				var tabletransfer= frappe.model.get_doc("Sales Order", frm.doc.sales_order)
				$.each(tabletransfer.items, function(index, row){
					if(row.is_blocked == 1 ){
						var d = frm.add_child("items");
						d.item_code = row.item_code;
						d.item_name = row.item_name;
						d.customer_item_code = row.customer_item_code;
						d.qty = row.qty;
						d.is_blocked = row.is_blocked;
						d.blocked_qty = row.blocked_qty;
						d.warehouse = row.warehouse;
						frm.refresh_field("items");
				}
				});
			});
		}
	}
});

