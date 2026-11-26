
from flask import Blueprint, request, redirect, session
from database import get_db, notify
from helpers import render_page, need_login

appointments_bp = Blueprint('appointments', __name__)


# ADMIN: View all appointments
@appointments_bp.route('/appointments')
def appointments():
    if need_login() or session['role'] != 'admin':
        return redirect('/dashboard')

    db = get_db()

    rows = db.execute("""
        SELECT a.id, p.name AS pname, d.name AS dname,
        h.name AS hname, a.date, a.status
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id=p.id
        LEFT JOIN doctors d ON a.doctor_id=d.id
        LEFT JOIN hospitals h ON a.hospital_id=h.id
        ORDER BY a.id DESC
    """).fetchall()

    tr = "".join([
        f"<tr><td>{r['id']}</td><td>{r['pname']}</td>"
        f"<td>{r['dname']}</td><td>{r['hname']}</td>"
        f"<td>{r['date']}</td><td>{r['status']}</td></tr>"
        for r in rows
    ])

    content = f'''
    <h3>All Appointments (Admin)</h3>
    <div class="table-box">
    <table class="table">
    <tr>
    <th>ID</th><th>Patient</th><th>Doctor</th>
    <th>Hospital</th><th>Date</th><th>Status</th>
    </tr>
    {tr}
    </table></div>
    '''

    return render_page(content, 'appointments')


# PATIENT: Book appointment
@appointments_bp.route('/book', methods=['GET', 'POST'])
def book():
    if need_login() or session['role'] != 'patient':
        return redirect('/dashboard')

    db = get_db()

    pat = db.execute(
        "SELECT * FROM patients WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()

    if not pat:
        return redirect('/my_profile')

    hospitals = db.execute(
        "SELECT * FROM hospitals"
    ).fetchall()

    selected = request.args.get('hospital_id')

    if not selected and hospitals:
        selected = hospitals[0]['id']

    # Demo version: show all added doctors
    doctors = db.execute(
        "SELECT * FROM doctors ORDER BY id DESC"
    ).fetchall()

    if request.method == 'POST':
        doctor_id = request.form['doctor']
        hospital_id = request.form['hospital_id']
        appointment_date = request.form['date']

        db.execute("""
            INSERT INTO appointments
            (patient_id, doctor_id, hospital_id, date, status)
            VALUES (?, ?, ?, ?, 'Pending')
        """, (
            pat['id'],
            doctor_id,
            hospital_id,
            appointment_date
        ))

        db.commit()

        doc = db.execute(
            "SELECT user_id, name FROM doctors WHERE id=?",
            (doctor_id,)
        ).fetchone()

        if doc and doc['user_id']:
            notify(
                doc['user_id'],
                f"New appointment request from {pat['name']} on {appointment_date}"
            )

        return redirect('/my_appointments')

    hospital_options = "".join([
        f"<option value='{h['id']}' "
        f"{'selected' if str(h['id']) == str(selected) else ''}>"
        f"{h['name']}</option>"
        for h in hospitals
    ])

    doctor_options = "".join([
        f"<option value='{d['id']}'>{d['name']} - "
        f"{d['category']} - Rs.{d['fee']}</option>"
        for d in doctors
    ])

    content = f'''
    <h3>Book Appointment</h3>
    <p>1. Select Hospital → 2. Select Doctor → 3. Choose Date</p>

    <form method="GET">
    <label>Select Hospital</label>
    <select name="hospital_id" class="form-control mb-2"
    onchange="this.form.submit()">
    {hospital_options}
    </select>
    </form>

    <div class="form-card">
    <form method="POST">
    <input type="hidden" name="hospital_id" value="{selected}">

    <select name="doctor" class="form-control mb-2" required>
    {doctor_options}
    </select>

    <input type="date" name="date"
    class="form-control mb-2" required>

    <button class="blue-btn">Fix Appointment</button>
    </form>
    </div>
    '''

    return render_page(content, 'book')


# PATIENT AND DOCTOR: View appointments
@appointments_bp.route('/my_appointments')
def my_appointments():
    if need_login():
        return redirect('/login')

    db = get_db()

    if session['role'] == 'doctor':

        doc = db.execute(
            "SELECT id FROM doctors WHERE user_id=?",
            (session['user_id'],)
        ).fetchone()

        if not doc:
            return redirect('/dashboard')

        rows = db.execute("""
            SELECT a.id, p.name AS pname, h.name AS hname,
            a.date, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id=p.id
            JOIN hospitals h ON a.hospital_id=h.id
            WHERE a.doctor_id=?
            ORDER BY a.id DESC
        """, (doc['id'],)).fetchall()

        tr = ""

        for r in rows:
            buttons = ""

            if r['status'] == 'Pending':
                buttons = f"""
                <a href='/appt_action/{r['id']}/Accepted'
                class='btn btn-sm btn-success'>Accept</a>

                <a href='/appt_action/{r['id']}/Rejected'
                class='btn btn-sm btn-danger'>Reject</a>
                """

            tr += f"""
            <tr>
            <td>{r['pname']}</td>
            <td>{r['hname']}</td>
            <td>{r['date']}</td>
            <td>{r['status']}</td>
            <td>{buttons}</td>
            </tr>
            """

        content = f'''
        <h3>My Appointments — Doctor</h3>
        <div class="table-box">
        <table class="table">
        <tr>
        <th>Patient</th><th>Hospital</th>
        <th>Date</th><th>Status</th><th>Action</th>
        </tr>
        {tr}
        </table></div>
        '''

        return render_page(content, 'my_appointments')

    elif session['role'] == 'patient':

        pat = db.execute(
            "SELECT id FROM patients WHERE user_id=?",
            (session['user_id'],)
        ).fetchone()

        if not pat:
            return redirect('/my_profile')

        rows = db.execute("""
            SELECT a.id, d.name AS dname, h.name AS hname,
            a.date, a.status
            FROM appointments a
            JOIN doctors d ON a.doctor_id=d.id
            JOIN hospitals h ON a.hospital_id=h.id
            WHERE a.patient_id=?
            ORDER BY a.id DESC
        """, (pat['id'],)).fetchall()

        tr = "".join([
            f"<tr><td>{r['dname']}</td><td>{r['hname']}</td>"
            f"<td>{r['date']}</td><td>{r['status']}</td></tr>"
            for r in rows
        ])

        content = f'''
        <h3>My Appointments — Patient</h3>
        <div class="table-box">
        <table class="table">
        <tr>
        <th>Doctor</th><th>Hospital</th>
        <th>Date</th><th>Status</th>
        </tr>
        {tr}
        </table></div>
        '''

        return render_page(content, 'my_appointments')

    return redirect('/dashboard')


# DOCTOR: Accept or reject appointment
@appointments_bp.route('/appt_action/<int:aid>/<status>')
def appt_action(aid, status):
    if need_login() or session['role'] != 'doctor':
        return redirect('/login')

    if status not in ('Accepted', 'Rejected'):
        return redirect('/my_appointments')

    db = get_db()

    doc = db.execute(
        "SELECT id FROM doctors WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()

    if not doc:
        return redirect('/dashboard')

    appointment = db.execute("""
        SELECT patient_id FROM appointments
        WHERE id=? AND doctor_id=?
    """, (aid, doc['id'])).fetchone()

    if not appointment:
        return redirect('/my_appointments')

    db.execute(
        "UPDATE appointments SET status=? WHERE id=?",
        (status, aid)
    )

    pat = db.execute(
        "SELECT user_id FROM patients WHERE id=?",
        (appointment['patient_id'],)
    ).fetchone()

    if pat and pat['user_id']:
        notify(
            pat['user_id'],
            f"Dr. {session.get('name', '')} {status} your appointment."
        )

    db.commit()

    return redirect('/my_appointments')
