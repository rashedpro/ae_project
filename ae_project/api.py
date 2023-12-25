import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def update_project_monitoring_details(self,method):
    if not self.custom_project_monitoring_details_ae:
        return

    pmd = []
    for row_check in self.custom_project_monitoring_details_ae:
        reference = (row_check.item_code)
        if reference in pmd:
            frappe.throw(
                _("{0} item is added twice in project monitoring details").format(
                    row_check.item_code
                )
            )
        pmd.append(reference)

    for row_p in self.custom_project_monitoring_details_ae:
        if flt(row_p.planned_qty)>0 and flt(row_p.initial_planned_qty)==0:
            row_p.initial_planned_qty=row_p.planned_qty

    for row_mon in self.custom_project_monitoring_details_ae:
        print(row_mon)
        row_mon.requested_qty=get_requested_qty(self.name,row_mon.item_code)[0].mri_qty if len(get_requested_qty(self.name,row_mon.item_code))>0  else 0
        row_mon.ordered_qty=get_ordered_qty(self.name,row_mon.item_code)[0].poi_qty if len(get_ordered_qty(self.name,row_mon.item_code))>0  else 0
        row_mon.received_qty=get_received_qty(self.name,row_mon.item_code)[0].pri_qty if len(get_received_qty(self.name,row_mon.item_code))>0  else 0
        row_mon.issued_qty=get_issued_qty(self.name,row_mon.item_code)
        row_mon.available_qty=get_available_qty(row_mon.item_code)[0].actual_qty if len(get_available_qty(row_mon.item_code))>0  else 0
        row_mon.variance=(row_mon.initial_planned_qty if row_mon.initial_planned_qty else 0) - (row_mon.planned_qty if row_mon.planned_qty else 0)


def get_requested_qty(project_name,item_code):
    values = {'project_name': project_name,'item_code':item_code}
    data = frappe.db.sql("""
SELECT
	sum(mri.qty) as mri_qty
FROM
	`tabMaterial Request Item` as mri
where
	mri.project =  %(project_name)s
    and mri.item_code=%(item_code)s
	and mri.docstatus = 1
group by
	mri.item_code
    """, values=values, as_dict=1,debug=0)
    print('data',data)
    return data    

def get_ordered_qty(project_name,item_code):
    values = {'project_name': project_name,'item_code':item_code}
    data = frappe.db.sql("""
SELECT
	sum(poi.qty) as poi_qty
FROM
	`tabPurchase Order Item` as poi
where
	poi.project =  %(project_name)s
    and poi.item_code=%(item_code)s
	and poi.docstatus = 1
group by
	poi.item_code
    """, values=values, as_dict=1)
    print('data',data)
    return data

def get_received_qty(project_name,item_code):
    values = {'project_name': project_name,'item_code':item_code}
    data = frappe.db.sql("""
SELECT
	sum(pri.qty) as pri_qty
FROM
	`tabPurchase Receipt Item` as pri
where
	pri.project =  %(project_name)s
    and pri.item_code=%(item_code)s
	and pri.docstatus = 1
group by
	pri.item_code
    """, values=values, as_dict=1)
    print('data',data)
    return data

def get_issued_qty(project_name,item_code):
    values = {'project_name': project_name,'item_code':item_code}
    dni_data = frappe.db.sql("""
SELECT
	sum(dni.qty) as dni_qty
FROM
	`tabDelivery Note Item` as dni
where
	dni.project =  %(project_name)s
    and dni.item_code=%(item_code)s
	and dni.docstatus = 1
group by
	dni.item_code
    """, values=values, as_dict=1)
    print('dni_data',dni_data)

    sei_data = frappe.db.sql("""
SELECT
	sum(sei.qty) as sei_qty
FROM
	`tabStock Entry Detail` as sei
inner join `tabStock Entry` se on
	se.name = sei.parent                             
where
	sei.project =  %(project_name)s
    and sei.item_code=%(item_code)s
	and sei.docstatus = 1
    and se.stock_entry_type='Material Issue'
group by
	sei.item_code
    """, values=values, as_dict=1)
    print('sei_data',sei_data)

    data=(dni_data[0].dni_qty if len(dni_data)>0  else 0)+(sei_data[0].sei_qty if len(sei_data)>0  else 0)

    return data

def get_available_qty(item_code):
    default_warehouse = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
    values = {'default_warehouse': default_warehouse,'item_code':item_code}
    data = frappe.db.sql("""
SELECT
	sum(actual_qty) as actual_qty
FROM
	`tabBin` bin
where
	bin.warehouse =  %(default_warehouse)s
    and bin.item_code=%(item_code)s
group by
	bin.item_code
    """, values=values, as_dict=1)
    print('data',data)
    return data    




#  called from JS
@frappe.whitelist(allow_guest=True)
def fetch_items_from_sales_order(project_name):
    values = {'project_name': project_name}
    data = frappe.db.sql("""
SELECT
	so_item.item_code,
    so_item.item_name                  
FROM
	`tabSales Order` so
inner join `tabSales Order Item` so_item on
	so.name = so_item.parent
inner join `tabItem` item on
	item.name = so_item.item_code
where
	so.docstatus = 1
	and so.project = %(project_name)s
	and item.is_stock_item = 1
    group by so_item.item_code
    """, values=values, as_dict=1)
    if len(data)>0:
        frappe.msgprint(msg=_("Connected {0} stock items found from Sales Order".format(frappe.bold(len(data)))),indicator="green",alert=1)            
    else:
        frappe.msgprint(msg=_("No Connected stock items found from Sales Order"),indicator="orange",alert=1) 
    return data

# @frappe.whitelist(allow_guest=True)
# def fetch_items_from_sales_order(project_name):
#     values = {'project_name': project_name}
#     data = frappe.db.sql("""
# SELECT
# 	so_item.item_code
# FROM
# 	`tabSales Order` so
# inner join `tabSales Order Item` so_item on
# 	so.name = so_item.parent
# inner join `tabItem` item on
# 	item.name = so_item.item_code
# where
# 	so.docstatus = 0
# 	and so.project = %(project_name)s
# 	and item.is_stock_item = 1
# 	and so_item.item_code not in (
# 	select
# 		proj_monit_detail.item_code
# 	from
# 		`tabProject Monitoring Detail AE` proj_monit_detail
# 	where
# 		proj_monit_detail.parent = %(project_name)s )
#     """, values=values, as_dict=1)
#     if len(data)>0:
#         frappe.msgprint(msg=_("Connected {0} stock items found from Sales Order".format(frappe.bold(len(data)))),indicator="green",alert=1)            
#     else:
#         frappe.msgprint(msg=_("No Connected stock items found from Sales Order"),indicator="orange",alert=1) 
#     return data