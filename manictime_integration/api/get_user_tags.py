from frappe import session, get_all, db
from frappe.utils import add_to_date, today, date_diff
from typing import Dict


def get_user_tags():
    """
    Session {
    data: Data;
    user: string;
    sid:  string;
    }

    Data {
    user:           string;
    session_ip:     string;
    last_updated:   Date;
    session_expiry: string;
    full_name:      string;
    user_type:      string;
    lang:           string;
    }   
    """
    
    email = session.user
    completed_threshold = add_to_date(today(), days=-10)
    tasks = get_all("Task", fields=["subject", "project", "description", "completed_on", 'status'], filters={"_assign": ["like", f"%{email}%"], 'status': ['not in', ['Canceled']]})
    
    for task in tasks:
        if task.status == 'Completed' and date_diff(task.completed_on, completed_threshold) < 0:
            tasks.remove(task)
            
    
    projects: Dict[str] = {}
    for task in tasks:
        if task.project not in projects:
            projects[task.project] = db.get_value("Project", task.project, "project_name")
    
    return list(map(lambda t: {**t, 'project': projects[t.project], 'billable': True}, tasks))
