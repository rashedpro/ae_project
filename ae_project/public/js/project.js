frappe.ui.form.on("Project", {
    refresh:function(frm) {
		if (!frm.is_new() && frm.doc.custom_project_monitoring_details_ae && frm.doc.custom_project_monitoring_details_ae.length>0) {
			frm.add_custom_button(__("Material Request"), function() {
                choose_items_and_create_material_request(frm)
			}, __("<b>Create</b>"));
		}        
    },    
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
    before_custom_project_monitoring_details_ae_remove(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        if (row.requested_qty>0 || row.ordered_qty>0 || row.received_qty>0 || row.issued_qty>0 || row.available_qty>0) {
            frappe.throw(__('Cannot delete row, as monitoring qty already generated.'))
        }
    }
})

function choose_items_and_create_material_request(frm) {
    let dialog_child_table_data = frm.doc.custom_project_monitoring_details_ae.filter(
        (item) => item.name
    ).map((item) => {
        return {
            "item_code": item.item_code,
            "item_name": item.item_name,
        }
    });
    const table_fields = [
        {
            fieldtype:"Link",
            fieldname:"item_code",
            options: "Item",
            label: __("Item Code"),
            read_only: 1,
            in_list_view: 1,
            columns: 2
        },
        {
            fieldtype:"Data",
            fieldname:"item_name",
            label: __("Name"),
            read_only: 1,
            in_list_view: 1,
        }                    
    ];                

    const dialog = new frappe.ui.Dialog({
        title: __("Select Items for Material Request"),
        fields: [
            {
                fieldname: "material_requet_items",
                fieldtype: "Table",
                cannot_add_rows: true,
                cannot_delete_rows: true,
                in_place_edit: false,
                reqd: 1,
                data: dialog_child_table_data,
                get_data: () => {
                    return data;
                },
                fields: table_fields
            },
        ],
        primary_action: function() {
            frappe.db.get_single_value('Stock Settings', 'default_warehouse')
            .then(default_warehouse => {
                let selected_items=dialog.fields_dict.material_requet_items.grid.get_selected_children()
                let doc = frappe.model.get_new_doc("Material Request");
                doc.naming_series='MAT-MR-.YYYY.-'
                doc.material_request_type='Purchase'
                doc.set_warehouse=default_warehouse
                doc.transaction_date=frappe.datetime.get_today()
                for (let index = 0; index < selected_items.length; index++) {
                    const user_item = selected_items[index];
                    var row = frappe.model.add_child(doc, "Material Request Item", "items");
                    row.item_code=user_item.item_code
                    row.qty=1
                }
                // if in new tab below 2 lines, but it doesn't fill up child table
                // frappe.open_in_new_tab = true;
                // frappe.route_options=doc
                frappe.set_route("Form", "Material Request", doc.name);                            
            })                        
            dialog.hide();
        },
        primary_action_label: __('Create Material Request')
    });   
    dialog.show();  
}