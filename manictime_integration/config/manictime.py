from frappe import get_doc

config = get_doc("Manictime settings")

manic_server = config.url
username = config.username
password = config.get_password("password")
