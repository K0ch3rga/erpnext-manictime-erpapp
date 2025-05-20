import requests
from manictime_integration.config.manictime import manic_server, username, password


def create_activity_in_manictime(timeline_id: str, create_activity_dto):
    token = authenticate_in_manictime()
    return post_activity_in_manictime(token, timeline_id, create_activity_dto)


def update_activity_in_manictime(timeline_id: str, create_activity_dto):
    token = authenticate_in_manictime()
    return put_activity_in_manictime(token, timeline_id, create_activity_dto)


def post_activity_in_manictime(token: str, timeline_id: str, new_activity_dto):
    post_activties_url = f"{manic_server}/api/timelines/{timeline_id}/activities"
    post_activities_headers = {
        "Content-Type": "application/vnd.manictime.v3+json; charset=utf-8 ",
        "Accept": "application/vnd.manictime.v3+json",
        "Authorization": f"Bearer {token}",
    }
    activities_response = requests.post(
        post_activties_url, headers=post_activities_headers, data=new_activity_dto, verify=False
    )
    if activities_response != 200:
        raise Exception(f"Request failed with status {activities_response.status_code}")
    return activities_response  # process response


def put_activity_in_manictime(token: str, timeline_id: str, new_activity_dto):
    put_activties_url = f"{manic_server}/api/timelines/{timeline_id}/activities"
    put_activities_headers = {
        "Content-Type": "application/vnd.manictime.v3+json; charset=utf-8 ",
        "Accept": "application/vnd.manictime.v3+json",
        "Authorization": f"Bearer {token}",
    }
    activities_response = requests.put(
        put_activties_url, headers=put_activities_headers, data=new_activity_dto, verify=False
    )
    if activities_response.status_code != 200:
        raise Exception(f"Request failed with status {activities_response.status_code}")
    return activities_response  # process response


def authenticate_in_manictime() -> str:
    auth_data = {"grant_type": "password", "username": username, "password": password}
    token_endpoint = f"{manic_server}/api/token"
    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/vnd.manictime.v3+json",
    }

    token_response = requests.post(token_endpoint, data=auth_data, headers=auth_headers, verify=False)
    if token_response.status_code != 200:
        raise Exception(f"Request failed with status {token_response.status_code}")
    return token_response.get("token")
