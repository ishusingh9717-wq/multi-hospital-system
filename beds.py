
from flask import Blueprint, request, redirect, session
from database import get_db
from helpers import render_page, need_login

beds_bp = Blueprint('beds', __name__)

@beds_bp.route('/beds', methods=['GET', 'POST'])
def beds():
    if need_login():
        return redirect('/login')

    db = get_db()

    if request.method == 'POST' and session['role'] == 'admin':
        hid = request.form['hospital_id']

        existing = db.execute(
            "SELECT id FROM beds WHERE hospital_id=?",
            (hid,)
        ).fetchone()

        if existing:
            db.execute("""
                UPDATE beds
                SET occupied_icu=?, occupied_general=?, occupied_emergency=?
                WHERE hospital_id=?
            """, (
                request.form['icu'],
                request.form['general'],
                request.form['emergency'],
                hid
            ))
        else:
            hospital = db.execute(
                "SELECT id FROM hospitals WHERE id=?",
                (hid,)
            ).fetchone()

            if hospital:
                db.execute("""
                    INSERT INTO beds
                    (hospital_id, total_icu, occupied_icu,
                     total_general, occupied_general,
                     total_emergency, occupied_emergency)
                    VALUES (?, 10, ?, 50, ?, 10, ?)
                """, (
                    hid,
                    request.form['icu'],
                    request.form['general'],
                    request.form['emergency']
                ))

        db.commit()

    rows = db.execute("""
        SELECT b.*, h.name as hname
        FROM beds b
        JOIN hospitals h ON b.hospital_id=h.id
    """).fetchall()

    tr = "".join([
        f"<tr><td>{r['hname']}</td>"
        f"<td>{r['total_icu']-r['occupied_icu']} / {r['total_icu']} free</td>"
        f"<td>{r['total_general']-r['occupied_general']} / {r['total_general']} free</td>"
        f"<td>{r['total_emergency']-r['occupied_emergency']} / {r['total_emergency']} free</td></tr>"
        for r in rows
    ])

    form = ''

    if session['role'] == 'admin':
        hosps = db.execute(
            "SELECT id, name FROM hospitals"
        ).fetchall()

        h_opt = "".join([
            f"<option value='{h['id']}'>{h['name']}</option>"
            for h in hosps
        ])

        form = f'''
        <div class="form-card">
        <h5>Update Occupied Beds (Admin)</h5>
        <form method="POST">
        <select name="hospital_id" class="form-control mb-2">
        {h_opt}
        </select>
        <input name="icu" placeholder="Occupied ICU" required>
        <input name="general" placeholder="Occupied General" required>
        <input name="emergency" placeholder="Occupied Emergency" required>
        <button class="blue-btn">Update Beds</button>
        </form></div>
        '''

    c = f'''
    <h3>Beds — Admin manages, Patient views availability</h3>
    <div class="d-flex gap-4">
    {form}
    <div class="table-box">
    <table class="table">
    <tr><th>Hospital</th><th>ICU Free</th>
    <th>General Free</th><th>Emergency Free</th></tr>
    {tr}
    </table></div></div>
    '''

    return render_page(c, 'beds')
