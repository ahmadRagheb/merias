## Merias

Simple custoization to blocked items in Sales Order. to read more please refer to [Documentation](docs/Selling/sales_order.md)


This feature applied to:
- Product Bundle which contains many items (showed in packed item) 
- Normal Item

#### Doctypes : 
Recipient : Recipient Name and contact, used to definde the recipient informations, Linked doctype in Sales order.
Release Blocked Item : for releasing blocked item in Sales order

#### Reports:
blocked items : Report to show blocked items

#### Tasks:
hourly task To msgprint how much sales order is blocked in Sales order with a redirect button to see it all and take action. 

#### hooks:

###### Sales Order : 
 - validate : "merias.api.map_qty_to_blocked_field" , 
  This is the start for all the logic we are building, in each items row there is a blcoked_qty field equal to stock_qty.
  we used stock qty to cover using different UOM .  
  
 - on_update : "merias.api.check_availability_for_items_based_on_booked", 
   check that actual qty is more than blocked qty in the warehouse . will check for both packed_items(product bundle items) and normal item.
 
 - before_insert : "merias.api.so_team"
  check if the creator of Sales order is a sales person , if so added sales team with allocated precentage 100
	
  
###### Sales Invoice
  -	on_submit : merias.api.si_for_items_based_on_booked"
   check that actual qty is more than blocked qty in the warehouse and and there is enough qty in warehouse to sell the qty in sales invoice .
   will check for both packed_items(product bundle items) and normal item.

###### Delivery Note
 - on_submit : "merias.api.delivery_note_affect_so_blocked" 
  free qty from blocked_qty in SO because we deliver .
  
 NEED DOCS
 
 - on_cancel : "merias.api.delivery_note_cancel"
   add qty to blocked_qty in SO because we cancel delivery  .

###### Stock Entry 
 - on_submit : "merias.api.stock_entry"
   For "Material Transfer" type : we calculate the real available qty after subtract blocked qty , and check if transfered qty is really exist in warehouse
 - validate : "merias.api.workflow",
  Conditional work flow we might can remove this if we used conditional workflow in v12 

###### Customer
 - before_insert : "merias.api.generate_unique_customer_number"
   naming customer with a naming series 


#### License

MIT
