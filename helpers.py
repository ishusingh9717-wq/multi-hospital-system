
from flask import render_template_string, session

BASE = """
<!doctype html><html><head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{margin:0;background:#f0f2f5}
.sidebar{background:#0a1e35;min-height:100vh;width:230px;position:fixed;color:#aaa}
.sidebar .top{padding:20px;color:white;font-size:20px;font-weight:600}
.sidebar a{display:flex;padding:12px 20px;color:#8a9bb5;text-decoration:none;font-size:15px}
.sidebar a.active,.sidebar a:hover{background:#12325a;color:white;border-left:3px solid #2196f3}
.main{margin-left:230px;padding:30px}
.form-card{background:white;border-radius:8px;padding:15px;width:300px;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.form-card input,.form-card select{width:100%;padding:10px;margin-bottom:10px;border:none;background:#f9f9f9;border-radius:4px}
.blue-btn{background:#2196f3;color:white;width:100%;padding:10px;border:none;border-radius:4px}
.green-btn{background:#2e9c5a;color:white;width:100%;padding:10px;border:none;border-radius:4px}
.table-box{background:white;border-radius:8px;flex:1;padding:10px}
.dash-card{background:white;border-radius:8px;padding:20px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.1);min-width:140px}
</style></head><body>
<div class="sidebar"><div class="top"> Multi-Hospital<br><small style="font-size:12px;color:#8a9bb5">{{name}} ({{role}})</small></div>
{{links|safe}}
<div style="margin-top:60px"><a href="/logout" style="color:#e57373">Logout</a></div></div>
<div class="main">{{content|safe}}</div></body></html>
"""

AUTH = """<!doctype html><html><head><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="bg-light"><div class="container mt-5"><div class="row justify-content-center"><div class="col-md-5"><div class="card p-4 shadow">
<h4 class="text-center"> {{title}}</h4>{{content|safe}}</div></div></div></div></body></html>"""

def sidebar(role, active):
    common = f'<a href="/dashboard" class="{"active" if active=="dashboard" else ""}"> Dashboard</a>'
    common += f'<a href="/hospitals" class="{"active" if active=="hospitals" else ""}"> Hospitals</a>'
    common += f'<a href="/notifications" class="{"active" if active=="notifications" else ""}"> Notifications</a>'

    if role == 'admin':
        common += '<a href="/patients">Patients</a><a href="/doctors">Doctors</a><a href="/appointments">Appointments</a><a href="/billing">Billing</a><a href="/beds">Beds</a><a href="/prescriptions">Prescriptions</a>'
    elif role == 'doctor':
        common += '<a href="/my_patients">My Patients</a><a href="/my_appointments">My Appointments</a><a href="/my_profile">My Profile / Join Hospital</a><a href="/prescriptions">Prescriptions</a>'
    elif role == 'patient':
        common += '<a href="/book">Book Appointment</a><a href="/my_appointments">My Appointments</a><a href="/my_billing">My Billing</a><a href="/beds">View Beds</a><a href="/my_profile">My Profile / Delete ID</a>'

    return common

def render_page(content, active):
    return render_template_string(
        BASE,
        content=content,
        links=sidebar(session.get('role'), active),
        name=session.get('name', ''),
        role=session.get('role', '')
    )

def need_login():
    return 'user_id' not in session
