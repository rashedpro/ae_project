import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    print("Creating project monitoring related fields...")
    custom_fields = {
        "Project": [
            dict(
                fieldname="custom_project_monitoring_details_section",
                label="Project Monitoring Details",
                fieldtype="Section Break",
                insert_after="department",
                is_custom_field=1,
                is_system_generated=0,
            ),
            dict(
                fieldname="custom_fetch_items_from_sales_order",
                label="Fetch Items From Sales Order",
                fieldtype="Button",
                insert_after="custom_project_monitoring_details",
                is_custom_field=1,
                is_system_generated=0,
            ),
            dict(
                fieldname="custom_project_monitoring_details_ae",
                fieldtype="Table",
                options="Project Monitoring Detail AE",
                insert_after="custom_fetch_items_from_sales_order",
                is_custom_field=1,
                is_system_generated=0,
            )             
        ]
    }

    create_custom_fields(custom_fields, update=True)