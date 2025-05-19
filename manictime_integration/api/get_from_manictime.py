from frappe.integrations.utils import make_get_request, make_post_request
from frappe import session, db
from datetime import date
from typing import List, Dict
from manictime_integration.config.manictime import (manic_server, username, password)

def get_activities_from_manictime(from_time: date, to_time: date) -> List[dict]:
        user = db.get_list("User", filters={'name': session.user}, fields=['*'])[0]
        email = user.email
        token = authenticate_in_manictime()
        
        user_timelines = get_timelines(token, email)
        activities = []
        for timeline in user_timelines:
            activities += get_activities_by_timeline(token, timeline['timelineKey'], from_time.isoformat(), to_time.isoformat())
        
        return activities
        
def get_activities_and_usage_from_manictime(from_time: date, to_time: date) -> Dict: 
        user = db.get_list("User", filters={'name': session.user}, fields=['*'])[0]
        email = user.email
        token = authenticate_in_manictime()
        
        user_tags_timelines = get_timelines(token, email, 'ManicTime/Tags')
        activities = []
        for timeline in user_tags_timelines:
            activities += get_activities_by_timeline(token, timeline['timelineKey'], from_time.isoformat(), to_time.isoformat())
        
        user_usage_timelines = get_timelines(token, email, 'ManicTime/ComputerUsage')
        timeline_id = user_usage_timelines[0]['timelineKey']
        sync_id = user_usage_timelines[0]['lastChangeId']
        usages = []
        for timeline in user_usage_timelines:
            recieved_usages = get_activities_by_timeline(token, timeline['timelineKey'], from_time.isoformat(), to_time.isoformat())
            for usage in recieved_usages: 
                if usage['values']['isActive'] == True:
                    usage['values']['name'] = 'active'
                else:
                    usage['values']['name'] = 'away'
            usages += recieved_usages
        return { 'activities': activities, 'usages': usages, 'timelineId': timeline_id,'syncId': sync_id}
        
        
def get_activities_by_timeline(token: str, timeline_id:str, from_time:str, to_time:str):
    get_activties_url = f"{manic_server}/api/timelines/{timeline_id}/activities?fromTime={from_time}&toTime={to_time}"
    get_activities_headers = {
        "Content-Type": "application/vnd.manictime.v3+json; charset=utf-8 ",
        "Accept": "application/vnd.manictime.v3+json",
        "Authorization": f"Bearer {token}",
    }
    activities_response = make_get_request(get_activties_url, headers=get_activities_headers)
    return [a for a in activities_response['entities'] if a['entityType'] == 'activity'] 
       
       
       
def get_timelines(token: str, username: str, timelines_filter: str = 'ManicTime/Tags'): 
    get_timelines_url = f"{manic_server}/api/timelines"
    timeline_headers = {
        "Content-Type": "application/vnd.manictime.v3+json; charset=utf-8 ",
        "Accept": "application/vnd.manictime.v3+json",
        "Authorization": f"Bearer {token}",
    }
    timelines_response = make_get_request(get_timelines_url, headers=timeline_headers)
    return [t for t in timelines_response['timelines'] if t['owner']['username'] == username and t['schema']['name'] == timelines_filter]
    
       
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
