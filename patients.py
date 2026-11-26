
from flask import Blueprint, request, redirect, session
from database import get_db
from helpers import render_page, need_login

patients_bp = Blueprint('patients', __name__)


# ADMIN: View and Add Patients
@patients_bp.route('/patients', methods=['GET', 'POST'])
def patients():

    if need_login() or session['role'] != 'admin':
        return redirect('/dashboard')

    db = get_db()

    if request.method == 'POST':
        db.execute("""
            INSERT INTO patients
            (user_id, name, age, gender, phone, address)
            VALUES (NULL, ?, ?, ?, ?, ?)
        """, (
            request.form['name'],
            request.form['age'],
            request.form['gender'],
            request.form['phone'],
            request.form['address']
        ))

        db.commit()
        return redirect('/patients')

    rows = db.execute(
        "SELECT * FROM patients ORDER BY id DESC"
    ).fetchall()

    tr = ""

    for r in rows:
        tr += f"""
        <tr>
        <td>{r['id']}</td>
        <td>{r['name']}</td>
        <td>{r['age']}</td>
        <td>{r['gender']}</td>
        <td>{r['phone']}</td>
        </tr>
        """

    content = f'''
    <h3>Patients Management</h3>

    <div class="d-flex gap-4 flex-wrap">

    <div class="form-card">
    <form method="POST">
    <input name="name" placeholder="Name" required>
    <input name="age" type="number" placeholder="Age" required>
    <input name="gender" placeholder="Gender" required>
    <input name="phone" placeholder="Phone" required>
    <input name="address" placeholder="Address" required>
    <button class="blue-btn">Add Patient</button>
    </form>
    </div>

    <div class="table-box">
    <table class="table">
    <tr>
    <th>ID</th><th>Name</th><th>Age</th>
    <th>Gender</th><th>Phone</th>
    </tr>
    {tr}
    </table>
    </div>

    </div>
    '''

    return render_page(content, 'patients')


# DOCTOR AND PATIENT: My Profile
@patients_bp.route('/my_profile', methods=['GET', 'POST'])
def my_profile():

    if need_login():
        return redirect('/login')

    db = get_db()
    role = session['role']

    # DOCTOR PROFILE
    if role == 'doctor':

        doc = db.execute(
            "SELECT * FROM doctors WHERE user_id=?",
            (session['user_id'],)
        ).fetchone()

        # Connect login account with existing doctor record
        if not doc:
            doc = db.execute("""
                SELECT * FROM doctors
                WHERE name=? AND user_id IS NULL
                ORDER BY id DESC LIMIT 1
            """, (session['name'],)).fetchone()

            if doc:
                db.execute(
                    "UPDATE doctors SET user_id=? WHERE id=?",
                    (session['user_id'], doc['id'])
                )
                db.commit()

                doc = db.execute(
                    "SELECT * FROM doctors WHERE user_id=?",
                    (session['user_id'],)
                ).fetchone()

        if not doc:
            return "Doctor profile not found. Contact Admin."

        if request.method == 'POST':

            if 'join_hospital' in request.form:

                db.execute("""
                    INSERT OR IGNORE INTO doctor_hospitals
                    (doctor_id, hospital_id)
                    VALUES (?, ?)
                """, (doc['id'], request.form['join_hospital']))

            else:

                db.execute("""
                    UPDATE doctors
                    SET name=?, age=?, category=?, fee=?, phone=?
                    WHERE id=?
                """, (
                    request.form['name'],
                    request.form['age'],
                    request.form['category'],
                    request.form['fee'],
                    request.form['phone'],
                    doc['id']
                ))

            db.commit()
            return redirect('/my_profile')

        hospitals = db.execute(
            "SELECT * FROM hospitals"
        ).fetchall()

        joined = db.execute("""
            SELECT h.name
            FROM hospitals h
            JOIN doctor_hospitals dh
            ON h.id=dh.hospital_id
            WHERE dh.doctor_id=?
        """, (doc['id'],)).fetchall()

        hospital_options = "".join([
            f"<option value='{h['id']}'>{h['name']}</option>"
            for h in hospitals
        ])

        joined_names = ", ".join([
            h['name'] for h in joined
        ]) or "None yet"

        content = f'''
        <h3>Doctor Profile</h3>
        <p>Joined Hospitals: <b>{joined_names}</b></p>

        <div class="d-flex gap-4 flex-wrap">

        <div class="form-card">
        <h5>Edit Details</h5>

        <form method="POST">
        <input name="name" value="{doc['name']}" required>
        <input name="age" value="{doc['age']}" required>
        <input name="category" value="{doc['category']}" required>
        <input name="fee" value="{doc['fee']}" required>
        <input name="phone" value="{doc['phone']}" required>
        <button class="blue-btn">Update</button>
        </form>
        </div>

        <div class="form-card">
        <h5>Join Hospital</h5>

        <form method="POST">
        <select name="join_hospital" required>
        {hospital_options}
        </select>
        <button class="green-btn">Join Hospital</button>
        </form>
        </div>

        </div>
        '''

        return render_page(content, 'my_profile')


    # PATIENT PROFILE
    if role == 'patient':

        pat = db.execute(
            "SELECT * FROM patients WHERE user_id=?",
            (session['user_id'],)
        ).fetchone()

        if not pat:
            return "Patient profile not found."

        if request.method == 'POST':

            if 'delete_my_id' in request.form:

                db.execute(
                    "DELETE FROM patients WHERE id=?",
                    (pat['id'],)
                )

                db.execute(
                    "DELETE FROM users WHERE id=?",
                    (session['user_id'],)
                )

                db.commit()
                session.clear()

                return redirect('/register')

            db.execute("""
                UPDATE patients
                SET name=?, age=?, gender=?, phone=?, address=?
                WHERE id=?
            """, (
                request.form['name'],
                request.form['age'],
                request.form['gender'],
                request.form['phone'],
                request.form['address'],
                pat['id']
            ))

            db.commit()
            return redirect('/my_profile')

        content = f'''
        <h3>My Profile — Patient</h3>

        <div class="form-card">
        <form method="POST">
        <input name="name" value="{pat['name']}" required>
        <input name="age" value="{pat['age']}" required>
        <input name="gender" value="{pat['gender']}" required>
        <input name="phone" value="{pat['phone']}" required>
        <input name="address" value="{pat['address']}" required>
        <button class="blue-btn">Update</button>
        </form>

        <form method="POST" class="mt-3">
        <input type="hidden" name="delete_my_id" value="1">
        <button class="btn btn-danger w-100">
        Delete My ID
        </button>
        </form>
        </div>
        '''

        return render_page(content, 'my_profile')

    return redirect('/dashboard')
