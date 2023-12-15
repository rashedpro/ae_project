frappe.ui.form.on("Project", {
    custom_fetch_items_from_sales_order(frm) {
        frappe.call('ae_project.api.fetch_items_from_sales_order', {
            project_name: frm.doc.name
        }).then(r => {
            console.log(r.message)
            if (r.message) {
                let item_list = r.message
                for (let index = 0; index < item_list.length; index++) {
                    let item_code = item_list[index].item_code
                    let item_name = item_list[index].item_name
                    var d = frm.add_child('custom_project_monitoring_details_ae');
                    console.log(item_code)
                    frappe.model.set_value(d.doctype, d.name, "item_code", item_code)
                    frappe.model.set_value(d.doctype, d.name, "item_name", item_name)
                    frm.refresh_field('custom_project_monitoring_details_ae')
                }
            }
        })
    }
})

frappe.ui.form.on('Project Monitoring Detail AE', {
    // cdt is Child DocType name i.e Quotation Item
    // cdn is the row name for e.g bbfcb8da6a
    // item_code(frm, cdt, cdn) {
    //     let row = locals[cdt][cdn]
    //     console.log(row.item_code,'9')
    //     row.item_name=
    // },
    before_custom_project_monitoring_details_ae_remove(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        if (row.requested_qty>0 || row.ordered_qty>0 || row.received_qty>0 || row.issued_qty>0 || row.available_qty>0) {
            frappe.throw(__('Cannot delete row, as monitoring qty already generated.'))
        }
    }
})