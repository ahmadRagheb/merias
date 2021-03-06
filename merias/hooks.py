# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "merias"
app_title = "Merias"
app_publisher = "ahmadragheb"
app_description = "simple custoization to merias co"
app_icon = "octicon octicon-file-directory"
app_color = "pink"
app_email = "ahmedragheb75@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/merias/css/merias.css"
# app_include_js = "/assets/merias/js/merias.js"
app_include_js = "/assets/merias/js/merias.js"

# include js, css files in header of web template
# web_include_css = "/assets/merias/css/merias.css"
# web_include_js = "/assets/merias/js/merias.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_js = {"Delivery Note" : "public/js/deliver_note.js"}
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
# get_website_user_home_page = "merias.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "merias.install.before_install"
# after_install = "merias.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "merias.notifications.get_notification_config"

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
	"Sales Order": {
		"validate": "merias.api.map_qty_to_blocked_field",
		"on_update":"merias.api.check_availability_for_items_based_on_booked",
		"before_insert": "merias.api.so_team",
	},"Sales Invoice": {
		"on_submit": "merias.api.si_for_items_based_on_booked",
	},"Delivery Note": {
		"on_submit": "merias.api.delivery_note_affect_so_blocked",
		"on_cancel": "merias.api.delivery_note_cancel",
	},"Stock Entry": {
		"on_submit": "merias.api.stock_entry",
		"validate": "merias.api.workflow",
	},
	"Customer": {
		"before_insert":  "merias.api.generate_unique_customer_number",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"merias.tasks.all"
# 	],
# 	"daily": [
# 		"merias.tasks.daily"
# 	],
# 	"hourly": [
# 		"merias.tasks.hourly"
# 	],
# 	"weekly": [
# 		"merias.tasks.weekly"
# 	]
# 	"monthly": [
# 		"merias.tasks.monthly"
# 	]
# }
scheduler_events = {
	# "all": [
	# 	"merias.tasks.all"
	# ],
	# "daily": [
	# 	"merias.tasks.daily"
	# ],
	"hourly": [
		"merias.tasks.hourly"
	],
	# "weekly": [
	# 	"merias.tasks.weekly"
	# ]
	# "monthly": [
	# 	"merias.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "merias.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "merias.event.get_events"
# ]

#TODO add filter to custom feilds and property setter the files we only need
#TODO add workflow state by filter only one is active , also add workflow states

fixtures = ["Custom Field", "Property Setter"]
#fixtures = ["Custom Script","Custom Field", "Workflow State", "Workflow", "Role","DocPerm", "User Permission", "User Permission for Page and Report", "User", "Employee" ]
