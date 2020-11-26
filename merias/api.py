from __future__ import unicode_literals

import frappe
import frappe.handler
import frappe.client
from frappe.utils import flt
from frappe.model.naming import make_autoname


# Sales Order hook validate
def map_qty_to_blocked_field(doc, method):
    """
    Assign blocked qty to be equal to stock qty ,
    so we evaluate this based on the item basic stock uom
    and avoid any complex logic in checking item availability
    """

    items = doc.get("items")
    for row in items:
        row.blocked_qty = row.stock_qty


# Sales Order hook before_insert
def so_team(doc, method):
    user = str(frappe.session.data.user)
    roles = frappe.permissions.get_roles(user)
    valid = False
    if "Sales Person" in roles:
        valid = True
    if valid:
        emp = frappe.get_value('Employee', {'user_id': user}, 'name')
        if emp:
            sales_person = frappe.get_value(
                'Sales Person', {'employee': emp, "enabled": 1}, 'name')
            if sales_person:
                row = doc.append("sales_team", {})
                row.sales_person = sales_person
                row.allocated_percentage = 100


# Sales Order hook on_update
def check_availability_for_items_based_on_booked(doc, method):
    """ when create Sales Order for item Pepsi and it has
        stock_qty= 5 in store and
        booked_items=3 then
        available_qty = stock_qty - booked_items
        and then verify qty in sales order < or = avaliable """
    for d in doc.get('items'):
        if has_product_bundle(d.item_code):
            for p in doc.get("packed_items"):
                if p.parent_item == d.item_code:
                    p.blocked_qty = p.qty
                    p.is_blocked = 1
                    sql_stat = '''select sum(pi.blocked_qty) as qty, so.name, pi.item_code from
                                `tabPacked Item` as pi inner join `tabSales Order` as so on
                                so.name = pi.parent and pi.item_code = '{}'  and pi.warehouse = '{}' and pi.is_blocked = 1
                                and so.status not in ('Cancelled','Completed','Closed') '''.format(p.item_code, p.warehouse)

                    blocked = frappe.db.sql(sql_stat)
                    bloked_qty = flt(blocked[0][0]) or 0
                    actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
                        where item_code = %s and warehouse = %s", (p.item_code, p.warehouse))
                    actual_qty = flt(actual_qty[0][0]) or 0

                    if  actual_qty < bloked_qty:
                        frappe.throw("You can't order item {} in packed item list from warehouse {}, because ordered quantity {} is more than stock available quantity {}".format(
                            d.item_code, p.warehouse, p.qty, actual_qty))

        else:
            sql_stat ='''select sum(soi.blocked_qty) as qty, so.name, soi.item_code from
            `tabSales Order Item` as soi inner join `tabSales Order` as so on
            so.name = soi.parent and soi.item_code = '{}'  and soi.warehouse = '{}' and soi.is_blocked = 1
            and so.status not in ('Cancelled','Completed','Closed') 
                '''.format(d.item_code, d.warehouse)
            blocked = frappe.db.sql(sql_stat)
            bloked_qty = flt(blocked[0][0]) or 0

            actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
                where item_code = %s and warehouse = %s", (d.item_code, d.warehouse))
            actual_qty = flt(actual_qty[0][0]) or 0

            if actual_qty < bloked_qty:
                frappe.throw("You can't order item {} from warehouse {}, because ordered quantity {} is more than stock available quantity {}".format(
                    d.item_code, d.warehouse,  d.stock_qty, actual_qty))


# Stock Entry validate
def workflow(doc, method):
    checker = doc.difference_exist
    value = flt(doc.difference_value)
    if(checker):
        if(value < 100):
            doc.workflow_state = "New(2t)"
        elif(100<=value and doc.workflow_state not in ["New(3t)", "Approved By Accounts Manager",
         "Approved By Branch Manager", "Approved By CEO",
        "Rejected By Accounts Manager","Rejected By Branch Manager", "Rejected By CEO"]):
            doc.workflow_state = "New(3t)"
    else:
        doc.workflow_state = "New"


# Stock Entry on_submit
def stock_entry(doc, method):
    """ by defult system check if item qty in warehouse >= transfered qty from that warehouse
        if okay then we add transfer with actuall qty then this will give us the totall
        the we subtracted blocked item from total
    """
    if doc.purpose == "Material Transfer":
        for d in doc.get('items'):

            soi_bloked_qty = frappe.db.sql('''SELECT sum(smi.blocked_qty) as qty FROM `tabSales Order` so
            inner join `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
            smi.warehouse = %s and smi.is_blocked = 1 and so.status not in ('Cancelled','Completed','Closed') ''',
            (d.item_code, d.s_warehouse))
            soi_bloked_qty = flt(soi_bloked_qty[0][0]) or 0

            sopi = frappe.db.sql('''SELECT sum(pi.blocked_qty) as qty FROM `tabSales Order` so
            inner join `tabPacked Item` pi ON pi.item_code = %s and so.name = pi.parent and
            pi.warehouse = %s and pi.is_blocked = 1 and so.status not in ('Cancelled','Completed','Closed') ''',
            (d.item_code, d.s_warehouse))
            sopi = flt(sopi[0][0]) or 0

            blocked_qty = soi_bloked_qty + sopi

            actual_qty = frappe.db.sql("select sum(actual_qty) from `tabBin` \
                where item_code = '{}' and warehouse = '{}' ".format(d.item_code, d.s_warehouse))
            actual_qty = flt(actual_qty[0][0]) or 0

            allowed_qty = (d.transfer_qty + actual_qty) - blocked_qty

            if actual_qty < blocked_qty:
                frappe.throw("You can't Transfer item {} because transfer quantity {} is \
                more than stock available quantity {} for warehouse {} {} ".format(
                    d.item_code, d.transfer_qty, allowed_qty, d.s_warehouse, 
                    "<br><br> Note: Blocked qty for this item: {}".format(blocked_qty)))


# Sales Invoice on_submit
def si_for_items_based_on_booked(doc, method):
    if doc.update_stock == 1:
        si_update_stock(doc, method)


def si_update_stock(doc, method):
    """ when create Sales Order for item Pepsi and it has stock_qty= 5 in store and booked_items=3 then
        available_qty = stock_qty - booked_items and then verify qty in sales order < or = avaliable """
        
    for d in doc.get('items'):
        if d.warehouse:
            if has_product_bundle(d.item_code):
                for p in doc.get("packed_items"):
                    if p.parent_item == d.item_code:
                        bloked_qty = frappe.db.sql('''SELECT sum(pi.blocked_qty) FROM `tabSales Order` so
                        LEFT JOIN `tabPacked Item` pi ON pi.item_code = %s and so.name = pi.parent and
                        pi.warehouse = %s and pi.is_blocked = 1 and so.status not in ('Cancelled','Completed','Closed') ''',
                        (p.item_code, p.warehouse))

                        # stock_uom  d.stock_qty 
                        sql_stat = "select sum(actual_qty) as qty from `tabBin` where item_code = '{}' and warehouse = '{}'".format(
                            p.item_code, p.warehouse)
                        actual_qty = frappe.db.sql(sql_stat)
                        bloked_qty = flt(bloked_qty[0][0]) or 0
                        actual_qty = flt(actual_qty[0][0]) or 0
                        if bloked_qty != 0 :
                            real_blocked_qty = actual_qty - bloked_qty
                            rr = real_blocked_qty + p.qty
                            if p.qty > real_blocked_qty :
                                frappe.throw("You can't order item {} in packed Item from warehouse {}, because ordered quantity {} is more than stock available quantity {}".format(
                                    p.item_code, p.warehouse, p.qty, rr))

            else:
                bloked_qty = frappe.db.sql('''SELECT sum(smi.blocked_qty) FROM `tabSales Order` so
                LEFT JOIN `tabSales Order Item` smi ON smi.item_code = %s and so.name = smi.parent and
                smi.warehouse = %s and smi.is_blocked = 1 and so.status not in ('Cancelled','Completed','Closed') ''',
                (d.item_code, d.warehouse))

                # stock_uom  d.stock_qty 
                sql_stat = "select sum(actual_qty) as qty from `tabBin` where item_code = '{}' and warehouse = '{}'".format(d.item_code, d.warehouse)
                actual_qty = frappe.db.sql(sql_stat)

                bloked_qty = flt(bloked_qty[0][0]) or 0
                actual_qty = flt(actual_qty[0][0]) or 0
                if bloked_qty != 0 :
                    real_blocked_qty = actual_qty - bloked_qty
                    rr = real_blocked_qty + d.qty
                    if d.qty > real_blocked_qty:
                        frappe.throw("You can't order item {} because ordered quantity {} is more than stock available quantity {}".format(
                            d.item_code, d.qty, rr))
        else:
            frappe.throw("Please select warehouse for item {}".format(d.item_code))


# Delivery Note on_submit
def delivery_note_affect_so_blocked(doc, method):
    if doc.is_return == 0:
        for d in doc.get('items'):
            if d.against_sales_order:
                so = frappe.get_doc("Sales Order",d.against_sales_order)
                soi = so.get("items")
                for row in soi:
                    if row.warehouse == d.warehouse and row.item_code == d.item_code:
                        row.blocked_qty = row.blocked_qty - d.stock_qty
                        if row.blocked_qty < 0:
                            frappe.throw("Blocked qty in Sales order not equal to Deliverd qty in row {}".format(row.idx))
                so.save()
                frappe.db.commit()
                if has_product_bundle(d.item_code):
                    bundle_dn_item(doc, d, True)


# Delivery Note on_cancel
def delivery_note_cancel(doc, method):
    if doc.is_return == 0:
        for d in doc.get('items'):
            if d.against_sales_order:
                so = frappe.get_doc("Sales Order", d.against_sales_order)
                soi = so.get("items")
                for row in soi:
                    if row.warehouse == d.warehouse and row.item_code == d.item_code:
                        row.blocked_qty = row.blocked_qty + d.stock_qty
                        if row.blocked_qty < 0:
                            frappe.throw("Blocked qty in Sales order not equal to Deliverd qty in row {}".format(row.idx))
                so.save()
                frappe.db.commit()
                if has_product_bundle(d.item_code):
                    bundle_dn_item(doc, d, False)


# Customer before_insert
def generate_unique_customer_number(doc, method):
    doc.customer_number = make_autoname('.#####')


def has_product_bundle(item_code):
    return frappe.db.sql("""select name from `tabProduct Bundle`
        where new_item_code=%s and docstatus != 2""", item_code)


def bundle_dn_item(doc, d, remove_qty):
    # if this item is bundel we search on packed items components
    for p in doc.get("packed_items"):
        if p.parent_item == d.item_code:
            so = frappe.get_doc("Sales Order", d.against_sales_order)
            sopi = so.get("packed_items")
            for pi_row in sopi:
                if pi_row.warehouse == p.warehouse and pi_row.item_code == p.item_code:
                    if remove_qty:
                        pi_row.blocked_qty = pi_row.blocked_qty - p.qty
                    else:
                        pi_row.blocked_qty = pi_row.blocked_qty + p.qty
                    if pi_row.blocked_qty < 0:
                        frappe.throw("Blocked qty in Sales order not equal to Deliverd qty Packed Items in row {}".format(pi_row.idx))
            so.save()
    frappe.db.commit()
