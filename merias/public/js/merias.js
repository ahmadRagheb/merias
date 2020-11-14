function action_so(){
    frappe.route_options = {"Sales Order Item.is_blocked": 1, "status": ["not in", "Cancelled, Completed, Draft, Closed"]}
    frappe.set_route("List", "Sales Order")
}