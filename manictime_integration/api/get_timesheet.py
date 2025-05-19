from typing import List
from frappe import (
    utils,
    get_doc,
    get_last_doc,
    log,
    db,
)
from frappe.integrations.utils import make_get_request, make_post_request
from datetime import datetime
from itertools import groupby
from manictime_integration.config.manictime import (manic_server, username, password)


def get_timesheets_from_manictime():
    token = authenticate_in_manictime()
    timeline_groups = request_timelines_groupedby_employee(token)
    now = utils.now()[:10]
    if not (sync := get_doc("Last synchronization").last_synchronization_datetime[:10]):
        sync = "1970-1-1"

    for timeline_group in timeline_groups:
        try:
            employee = db.get_list('Employee', filters={'user_id': timeline_group[0]}) # user id is same as email
        except Exception as e:
            log(e)
            continue

        for timeline in timeline_group[1]:
            activities_endpoint = [
                link["href"]
                for link in timeline["links"]
                if link["rel"] == "manictime/activities"
            ][0] + f"?fromTime={sync}&toTime={now}"
            activities = request_timeline_activities(token, activities_endpoint)
            for activity in activities:
                try:
                    task_name = activity["task"]
                    task = get_last_doc("Task", filters={"subject": task_name})
                    project_name = activity["project"]
                    project = get_last_doc(
                        "Project", filters={"project_name": project_name}
                    )
                    billable = False  # activity["billable"]
                except Exception as e:
                    log(e)

                activity_start = activity["activity_start"]
                activity_end = activity["activity_end"]
           
                doc = get_doc(
                    {
                        "doctype": "Timesheet",
                        "company": "Admin",
                        "employee": employee[0].name,
                        "parent_project": project.name,
                        "time_logs": [
                            {
                                "activity_type": "Execution",
                                "from_time": str(activity_start)[:19],
                                "to_time": str(activity_end)[:19],
                                "company": "Admin",
                                "project": project.name,
                                "task": task.name,
                                "billable": billable,
                            }
                        ],
                    }
                ).insert()
    db.commit()


def authenticate_in_manictime() -> str:
    auth_data = {"grant_type": "password", "username": username, "password": password}
    token_endpoint = f"{manic_server}/api/token"
    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/vnd.manictime.v3+json",
    }

    token_response = make_post_request(
        token_endpoint, data=auth_data, headers=auth_headers
    )
    return token_response["token"]


def request_timelines_groupedby_employee(
    auth_token: str,
) -> List[tuple[str, List[object]]]:
    timeline_endpoint = f"{manic_server}/api/timelines"
    timeline_headers = {
        "Content-Type": "application/vnd.manictime.v3+json; charset=utf-8 ",
        "Accept": "application/vnd.manictime.v3+json",
        "Authorization": f"Bearer {auth_token}",
    }
    timeline_response = make_get_request(timeline_endpoint, headers=timeline_headers)

    timeline_groups = [
        (i, list(d))
        for i, d in groupby(
            timeline_response["timelines"], lambda t: t["owner"]["username"]
        )
    ]

    return timeline_groups


def request_timeline_activities(auth_token: str, url: str) -> List[dict]:
    activities_header = {
        "Content-Type": "application/vnd.manictime.v3+json; charset=utf-8 ",
        "Accept": "application/vnd.manictime.v3+json",
        "Authorization": f"Bearer {auth_token}",
    }

    not_valid_activities = frozenset(["Active", "Session lock", "Away", ""])
    activities = make_get_request(url, headers=activities_header)
    activities_list: List[dict] = []
    for activity in activities["entities"]:
        if (activity["entityType"] == "activity") & ((name := activity["values"]["name"]) not in not_valid_activities) & (':erpnextimporter' in name):
            tags = name.split(", ")
            tags.remove(':erpnextimporter')
            billable = ":billable" in tags
            if billable:
                tags.remove(":billable")

            activity_start = datetime.fromisoformat(
                activity["values"]["timeInterval"]["start"]
            )
            activity_end = utils.add_to_date(
                activity_start,
                seconds=activity["values"]["timeInterval"]["duration"],
            )
            if len(tags) == 1:
                tags[1] = tags[0]
            activities_list.append(
                {
                    "project": tags[0],
                    "task": tags[1],
                    "activity_start": activity_start,
                    "activity_end": activity_end,
                    "billable": billable,
                }
            )

    return activities_list
