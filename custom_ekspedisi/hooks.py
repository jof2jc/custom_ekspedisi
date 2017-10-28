# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "custom_ekspedisi"
app_title = "Custom Ekspedisi"
app_publisher = "jonathan"
app_description = "custom ekspedisi"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "jof2jc@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_ekspedisi/css/custom_ekspedisi.css"
# app_include_js = "/assets/custom_ekspedisi/js/custom_ekspedisi.js"

# include js, css files in header of web template
# web_include_css = "/assets/custom_ekspedisi/css/custom_ekspedisi.css"
# web_include_js = "/assets/custom_ekspedisi/js/custom_ekspedisi.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "custom_ekspedisi.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_ekspedisi.install.before_install"
# after_install = "custom_ekspedisi.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_ekspedisi.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
    "Delivery Note": {
        "on_update_after_submit": "custom_ekspedisi.custom_ekspedisi.custom_ekspedisi.set_delivery_status_bkk_invoice",
	"on_submit": "custom_ekspedisi.custom_ekspedisi.custom_ekspedisi.set_delivery_status_bkk_invoice",
	"on_cancel": "custom_ekspedisi.custom_ekspedisi.custom_ekspedisi.set_delivery_status_bkk_invoice"
    },
    "Sales Invoice": {
	"on_submit": "custom_ekspedisi.custom_ekspedisi.custom_ekspedisi.set_delivery_status_per_billed",
	"on_cancel": "custom_ekspedisi.custom_ekspedisi.custom_ekspedisi.set_delivery_status_per_billed"
    }
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_ekspedisi.tasks.all"
# 	],
# 	"daily": [
# 		"custom_ekspedisi.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_ekspedisi.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_ekspedisi.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_ekspedisi.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "custom_ekspedisi.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "custom_ekspedisi.event.get_events"
# }

