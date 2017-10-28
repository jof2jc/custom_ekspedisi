# -*- coding: utf-8 -*-
# Copyright (c) 2015, jonathan and Contributors
# See license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cstr
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate
from collections import defaultdict

# test_records = frappe.get_test_records('testdoctype')

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
	if self.bkk_invoice:
		pi = frappe.get_doc("Purchase Invoice", self.bkk_invoice)

		if self.docstatus == 1:
			pi.delivery_status = "Delivered"
		elif self.docstatus == 2:
			pi.delivery_status = "Not Set"

		#frappe.throw(_("Status: {0}").format(pi.delivery_status))

		pi.save()

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