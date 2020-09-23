// frappe.ui.form.on('Delivery Note Item', {
//     items_add: function(frm, cdt, cdn) {
//         var row = locals[cdt][cdn];
//         frappe.call({
//             method: "merias.api.cost_center_check_api",
//             callback: function(r) {
//                 if(!r.exc) {
//                     frappe.model.set_value(row.doctype, row.name, 'cost_center', r.message);  
//                 }
//             }
//         });

//     },
//     cost_center: function(frm, cdt, cdn) {
//         var row = locals[cdt][cdn];
//         frappe.call({
//             method: "merias.api.cost_center_check_api",
//             callback: function(r) {
//                 if(!r.exc) {
//                     console.log("log",r.message);
//                     frappe.model.set_value(row.doctype, row.name, 'cost_center', r.message);  
//                 }
//             }
//         });
//     }
// });

