# -*- coding: utf-8 -*-
# Copyright (c) 2015, jonathan and Contributors
# See license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate
from collections import defaultdict
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, now_datetime, flt, cstr, formatdate, get_datetime, add_days, getdate

# test_records = frappe.get_test_records('testdoctype')

@frappe.whitelist()
def set_autoname(doc, method):
	if "set_autoname_based_on_posting_date" in frappe.db.get_table_columns("Company") and not doc.amended_from:
		if frappe.db.get_value("Company",doc.company,"set_autoname_based_on_posting_date"):
			_month = getdate(doc.posting_date).strftime('%m')
			_year = getdate(doc.posting_date).strftime('%y')
			
			if doc.doctype == "Journal Entry":
				_series = cstr(doc.naming_series).replace("MM",_month).replace("YY",_year)
			elif doc.doctype == "Delivery Note" and not doc.no_do:
				_series = cstr(doc.naming_series).replace("MM",_month).replace("YY",_year)
			else:
				_series = cstr(doc.naming_series).replace("MM",_month).replace("YY",_year).replace("no_do.",doc.no_do)
			
			#if not doc.is_return:
			#	doc.name = make_autoname("INV/." + _year + "./." + _month + "./.###")
			#else:
			doc.name = make_autoname(_series)

def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters, as_dict):
	return frappe.db.sql("""
		select `tabDelivery Note`.name, `tabDelivery Note`.customer, `tabDelivery Note`.posting_date
		from `tabDelivery Note`
		where `tabDelivery Note`.`%(key)s` like %(txt)s and
			`tabDelivery Note`.docstatus = 1
			and status not in ("Stopped", "Closed") %(fcond)s
			and (
				(`tabDelivery Note`.is_return = 0 and `tabDelivery Note`.per_billed < 100)
				or (
					`tabDelivery Note`.is_return = 1
					and return_against in (select name from `tabDelivery Note` where per_billed < 100)
				)
			)
			%(mcond)s order by `tabDelivery Note`.`%(key)s` asc
	""" % {
		"key": searchfield,
		"fcond": get_filters_cond(doctype, filters, []),
		"mcond": get_match_cond(doctype),
		"txt": "%(txt)s"
	}, {"txt": ("%%%s%%" % txt)}, as_dict=as_dict)

def set_delivery_status_bkk_invoice(self, method):
	if self.voucher_bkk:
		jv = frappe.get_doc("Journal Entry", self.voucher_bkk)

		if self.docstatus == 1:
			jv.delivery_note = self.name
		elif self.docstatus == 2:
			jv.delivery_note = ""

		#frappe.throw(_("Status: {0}").format(pi.delivery_status))

		jv.save()

def set_delivery_status_per_billed(self, method):
	if self.docstatus == 1 or self.docstatus == 2:
		for d in self.items:
			if d.delivery_note:
				ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabDelivery Note Item`
				where parent=%s""", (d.delivery_note))[0][0])
				print 'ref_doc_qty=' + cstr(ref_doc_qty)
	
				billed_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabSales Invoice Item` 
					where delivery_note=%s and docstatus=1""", (d.delivery_note))[0][0])
				print 'billed_qty=' + cstr(billed_qty)

				per_billed = ((ref_doc_qty if billed_qty > ref_doc_qty else billed_qty)\
					/ ref_doc_qty)*100
				print 'per_billed=' + cstr(per_billed)

				doc = frappe.get_doc("Delivery Note", d.delivery_note)

				if self.docstatus == 1 and doc.per_billed < 100:
					doc.db_set("per_billed", per_billed)
				else:
					doc.db_set("per_billed", "0")

				doc.set_status(update=True)

def patch_delivery_status_per_billed():
	_list = frappe.db.sql ("""SELECT it.delivery_note, ifnull(sum(qty), 0) as billed_qty FROM `tabSales Invoice` si INNER JOIN `tabSales Invoice Item` it 
			ON si.name=it.parent where si.docstatus=1 group by it.delivery_note""", as_dict=1)

	for d in _list:
		print 'd.delivery_note=' + d.delivery_note
		ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabDelivery Note Item`
				where parent=%s""", (d.delivery_note))[0][0])
		print 'ref_doc_qty=' + cstr(ref_doc_qty)

		#billed_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabSales Invoice Item` 
				#where delivery_note=%s and docstatus=1""", (d.delivery_note))[0][0])
		print 'd.billed_qty=' + cstr(d.billed_qty)

		per_billed = ((ref_doc_qty if d.billed_qty > ref_doc_qty else d.billed_qty)\
				/ ref_doc_qty)*100
		print 'per_billed=' + cstr(per_billed)

		doc = frappe.get_doc("Delivery Note", d.delivery_note)
		doc.db_set("per_billed", per_billed)
		doc.set_status(update=True)

def set_vehicle_status(self, method):
	#batch_doc = frappe.get_doc("Batch", batch_id)
	#pi_doc = frappe.get_doc("Purchase Invoice", pi_name)

	#frappe.throw(_("hai {0}").format(self.name))

	if self.vehicles is not None:
		for d in self.vehicles:
			#has_batch_no = frappe.db.get_value('Item', d.item_code, 'has_batch_no')
			if d.vehicle_no:
				#frappe.throw(_("hai {0}").format(d.vehicle_no))
				vehicle_doc = frappe.get_doc("Asset", d.vehicle_no)

				if self.docstatus == 1:
					vehicle_doc.vehicle_status = "In Use"
					vehicle_doc.reference_doc_name = self.name
	
					if d.is_finish:
						#frappe.msgprint(_("hai finish"))
						vehicle_doc.vehicle_status = "Available"
						vehicle_doc.reference_doc_name = ""
				else:
					#frappe.msgprint(_("hai cancel"))
					vehicle_doc.vehicle_status = "Available"
					vehicle_doc.reference_doc_name = ""
			
				vehicle_doc.save()