
from flask import Blueprint, request, redirect, session
from datetime import datetime
from database import get_db
from helpers import render_page, need_login

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/billing', methods=['GET','POST'])
def billing():
    if need_login() or session['role'] not in ('admin', 'patient'):
        return redirect('/dashboard')

    db = get_db()

    if request.method == 'POST' and session['role'] == 'admin':
        db.execute("""
            INSERT INTO billing
            (patient_id,hospital_id,amount,desc,date)
            VALUES (?,?,?,?,?)
        """, (
            request.form['patient'],
            request.form['hospital_id'],
            request.form['amount'],
            request.form['desc'],
            datetime.now().strftime("%Y-%m-%d")
        ))
        db.commit()
        return redirect('/billing')

    rows = db.execute("""
        SELECT b.*, p.name as pname, h.name as hname
        FROM billing b
        LEFT JOIN patients p ON b.patient_id=p.id
        LEFT JOIN hospitals h ON b.hospital_id=h.id
        ORDER BY b.id DESC
    """).fetchall()

    tr = "".join([
        f"<tr><td>{r['pname']}</td><td>{r['hname']}</td><td>Rs.{r['amount']}</td><td>{r['desc']}</td><td>{r['date']}</td></tr>"
        for r in rows
    ])

    form = ''

    if session['role'] == 'admin':
        pats = db.execute("SELECT id, name FROM patients").fetchall()
        hosps = db.execute("SELECT id, name FROM hospitals").fetchall()

        p_opt = "".join([
            f"<option value='{p['id']}'>{p['name']}</option>"
            for p in pats
        ])

        h_opt = "".join([
            f"<option value='{h['id']}'>{h['name']}</option>"
            for h in hosps
        ])

        form = f'''
        <div class="form-card">
        <h5>Generate Bill</h5>
        <form method="POST">
        <select name="patient" class="form-control mb-2">{p_opt}</select>
        <select name="hospital_id" class="form-control mb-2">{h_opt}</select>
        <input name="amount" placeholder="Amount" required>
        <input name="desc" placeholder="Description" required>
        <button class="green-btn">Generate Bill</button>
        </form></div>
        '''

    c = f'''
    <h3>Billing — Admin + Patient can view</h3>
    <div class="d-flex gap-4">
    {form}
    <div class="table-box">
    <table class="table">
    <tr><th>Patient</th><th>Hospital</th><th>Amount</th><th>Description</th><th>Date</th></tr>
    {tr}
    </table></div></div>
    '''

    return render_page(c, 'billing')


@billing_bp.route('/my_billing')
def my_billing():
    if need_login() or session['role'] != 'patient':
        return redirect('/dashboard')

    db = get_db()

    pat = db.execute(
        "SELECT id FROM patients WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()

    if not pat:
        return redirect('/my_profile')

    rows = db.execute(
        "SELECT * FROM billing WHERE patient_id=? ORDER BY id DESC",
        (pat['id'],)
    ).fetchall()

    tr = "".join([
        f"<tr><td>Rs.{r['amount']}</td><td>{r['desc']}</td><td>{r['date']}</td></tr>"
        for r in rows
    ])

    c = f'''
    <h3>My Billing</h3>
    <div class="table-box">
    <table class="table">
    <tr><th>Amount</th><th>Description</th><th>Date</th></tr>
    {tr}
    </table></div>
    '''

    return render_page(c, 'my_billing')
