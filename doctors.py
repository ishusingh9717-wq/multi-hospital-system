
from flask import Blueprint, request, redirect, session
from database import get_db
from helpers import render_page, need_login

doctors_bp = Blueprint('doctors', __name__)


# ADMIN: Add and View Doctors
@doctors_bp.route('/doctors', methods=['GET', 'POST'])
def doctors():

    if need_login() or session['role'] != 'admin':
        return redirect('/dashboard')

    db = get_db()

    if request.method == 'POST':

        db.execute("""
            INSERT INTO doctors
            (user_id, name, age, category, fee, phone)
            VALUES (NULL, ?, ?, ?, ?, ?)
        """, (
            request.form['name'],
            request.form['age'],
            request.form['category'],
            request.form['fee'],
            request.form['phone']
        ))

        db.commit()
        return redirect('/doctors')

    rows = db.execute(
        "SELECT * FROM doctors ORDER BY id DESC"
    ).fetchall()

    tr = ""

    for r in rows:
        tr += f"""
        <tr>
        <td>{r['id']}</td>
        <td>{r['name']}</td>
        <td>{r['category']}</td>
        <td>Rs.{r['fee']}</td>
        <td>{r['phone']}</td>
        </tr>
        """

    content = f'''
    <h3>Doctors Management (Admin)</h3>

    <div class="d-flex gap-4 flex-wrap">

    <div class="form-card">
    <h5>Add New Doctor</h5>

    <form method="POST">
    <input name="name" placeholder="Doctor Name" required>
    <input name="age" type="number" placeholder="Age" required>
    <input name="category" placeholder="Specialization" required>
    <input name="fee" type="number" placeholder="Consultation Fee" required>
    <input name="phone" placeholder="Phone Number" required>

    <button class="blue-btn">Add Doctor</button>
    </form>
    </div>

    <div class="table-box">
    <h5>Doctor List</h5>

    <table class="table">
    <tr>
    <th>ID</th>
    <th>Name</th>
    <th>Category</th>
    <th>Fee</th>
    <th>Phone</th>
    </tr>

    {tr}

    </table>
    </div>
    </div>
    '''

    return render_page(content, 'doctors')


# DOCTOR: View My Patients
@doctors_bp.route('/my_patients')
def my_patients():

    if need_login() or session['role'] != 'doctor':
        return redirect('/dashboard')

    db = get_db()

    doc = db.execute(
        "SELECT id FROM doctors WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()

    if not doc:
        return redirect('/my_profile')

    rows = db.execute("""
        SELECT DISTINCT p.*
        FROM patients p
        JOIN appointments a ON p.id = a.patient_id
        WHERE a.doctor_id = ?
        ORDER BY p.id DESC
    """, (doc['id'],)).fetchall()

    tr = ""

    for r in rows:
        tr += f"""
        <tr>
        <td>{r['name']}</td>
        <td>{r['age']}</td>
        <td>{r['gender']}</td>
        <td>{r['phone']}</td>
        </tr>
        """

    content = f'''
    <h3>My Patients</h3>

    <div class="table-box">
    <table class="table">

    <tr>
    <th>Name</th>
    <th>Age</th>
    <th>Gender</th>
    <th>Phone</th>
    </tr>

    {tr}

    </table>
    </div>
    '''

    return render_page(content, 'my_patients')
