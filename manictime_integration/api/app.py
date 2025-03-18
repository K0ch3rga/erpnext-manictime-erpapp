import frappe
from datetime import date, timedelta

from manictime_integration.api.get_timesheet import (
    get_timesheets_from_manictime,
)
from manictime_integration.api.get_user_tags import get_user_tags
from manictime_integration.api.get_from_manictime import (get_activities_from_manictime,get_activities_and_usage_from_manictime)
from manictime_integration.api.send_to_manictime import (create_activity_in_manictime)


@frappe.whitelist()
def update_timesheet():
    return get_timesheets_from_manictime()

@frappe.whitelist()
def get_tags():
    return get_user_tags()

@frappe.whitelist()
def get_user_activities(from_time: str, to_time: str=None):
    return get_activities_from_manictime(
               date.fromisoformat(from_time), 
               date.fromisoformat(to_time) + timedelta(days=1) if to_time is not None else date.today()
               )
    
@frappe.whitelist()
def get_user_usage_and_activities(from_time: str, to_time: str=None):
    return get_activities_and_usage_from_manictime(
               date.fromisoformat(from_time),
               date.fromisoformat(to_time) + timedelta(days=1) if to_time is not None else date.today()
               )
               
@frappe.whitelist()
def create_activity(timelineId: str, activity):
    return create_activity_in_manictime(timelineId, activity)

@frappe.whitelist()
def update_activity(timelineId: str, activity):
    return update_activity_in_manictime(timelineId, activity)
