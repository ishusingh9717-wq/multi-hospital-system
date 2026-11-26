
from flask import Blueprint, request, redirect, session
from datetime import datetime
from database import get_db
from helpers import render_page, need_login

prescriptions_bp = Blueprint('prescriptions', __name__)

@prescriptions_bp.route('/prescriptions', methods=['GET','POST'])
def prescriptions():
    if need_login():
        return redirect('/login')

    db = get_db()

    if request.method == 'POST' and session['role'] == 'doctor':
        doc = db.execute(
            "SELECT id FROM doctors WHERE user_id=?",
            (session['user_id'],)
        ).fetchone()

        if not doc:
            return redirect('/dashboard')

        db.execute("""
            INSERT INTO prescriptions
            (appointment_id,patient_id,doctor_id,medicine,notes,date)
            VALUES (?,?,?,?,?,?)
        """, (
            request.form['appointment_id'],
            request.form['patient_id'],
            doc['id'],
            request.form['medicine'],
            request.form['notes'],
            datetime.now().strftime("%Y-%m-%d")
        ))

        db.commit()
        return redirect('/prescriptions')

    rows = db.execute("""
        SELECT pr.*, p.name as pname, d.name as dname
        FROM prescriptions pr
        LEFT JOIN patients p ON pr.patient_id=p.id
        LEFT JOIN doctors d ON pr.doctor_id=d.id
        ORDER BY pr.id DESC
    """).fetchall()

    tr = "".join([
        f"<tr><td>{r['pname']}</td><td>{r['dname']}</td><td>{r['medicine']}</td><td>{r['notes']}</td><td>{r['date']}</td></tr>"
        for r in rows
    ])

    form = ''

    if session['role'] == 'doctor':
        doc = db.execute(
            "SELECT id FROM doctors WHERE user_id=?",
            (session['user_id'],)
        ).fetchone()

        if doc:
            appts = db.execute("""
                SELECT a.id, p.name
                FROM appointments a
                JOIN patients p ON a.patient_id=p.id
                WHERE a.doctor_id=? AND a.status='Accepted'
            """, (doc['id'],)).fetchall()

            a_opt = "".join([
                f"<option value='{a['id']}'>{a['name']} - Appt {a['id']}</option>"
                for a in appts
            ])

            pats = db.execute(
                "SELECT id, name FROM patients"
            ).fetchall()

            p_opt = "".join([
                f"<option value='{p['id']}'>{p['name']}</option>"
                for p in pats
            ])

            form = f'''
            <div class="form-card">
            <h5>Provide Prescription</h5>
            <form method="POST">
            <select name="appointment_id" class="form-control mb-2">
            {a_opt}</select>
            <select name="patient_id" class="form-control mb-2">
            {p_opt}</select>
            <input name="medicine" placeholder="Medicine" required>
            <input name="notes" placeholder="Notes" required>
            <button class="green-btn">Give Prescription</button>
            </form></div>
            '''

    c = f'''
    <h3>Prescriptions</h3>
    <div class="d-flex gap-4">
    {form}
    <div class="table-box">
    <table class="table">
    <tr><th>Patient</th><th>Doctor</th><th>Medicine</th><th>Notes</th><th>Date</th></tr>
    {tr}
    </table></div></div>
    '''

    return render_page(c, 'prescriptions')
