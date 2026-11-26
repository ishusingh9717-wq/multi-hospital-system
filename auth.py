
import sqlite3

from flask import Blueprint, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from helpers import AUTH
from flask import render_template_string

auth_bp = Blueprint('auth', __name__)


# Connect Doctor Login with Existing Doctor Profile
def link_doctor_profile(db, user_id, name):

    doctor = db.execute("""
        SELECT id FROM doctors
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
        AND user_id IS NULL
        ORDER BY id DESC
        LIMIT 1
    """, (name,)).fetchone()

    if doctor:
        db.execute("""
            UPDATE doctors
            SET user_id=?
            WHERE id=? AND user_id IS NULL
        """, (user_id, doctor['id']))

    db.commit()


@auth_bp.route('/')
def home():
    return redirect('/login')


# REGISTER
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    msg = ''

    if request.method == 'POST':

        name = request.form['name'].strip()
        username = request.form['username'].strip()
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        db = get_db()

        try:

            cursor = db.execute("""
                INSERT INTO users
                (name, username, password, role)
                VALUES (?, ?, ?, ?)
            """, (name, username, password, role))

            user_id = cursor.lastrowid

            if role == 'doctor':
                link_doctor_profile(db, user_id, name)
            else:
                db.commit()

            return redirect('/login')

        except sqlite3.IntegrityError:
            db.rollback()
            msg = 'Username already exists!'

    content = f"""
    <form method="post">

    <input name="name" class="form-control mb-2"
    placeholder="Full Name" required>

    <input name="username" class="form-control mb-2"
    placeholder="Username" required>

    <input name="password" type="password"
    class="form-control mb-2"
    placeholder="Password" required>

    <select name="role" class="form-control mb-2">
    <option value="patient">Patient</option>
    <option value="doctor">Doctor</option>
    <option value="admin">Admin</option>
    </select>

    <button class="btn btn-primary w-100">Register</button>

    <p class="text-danger">{msg}</p>

    </form>

    <a href="/login">Already have an account? Login</a>
    """

    return render_template_string(
        AUTH, title="Register", content=content
    )


# LOGIN
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    msg = ''

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        db = get_db()

        user = db.execute("""
            SELECT * FROM users WHERE username=?
        """, (username,)).fetchone()

        if user and check_password_hash(user['password'], password):

            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']

            # Automatically link existing Doctor profile
            if user['role'] == 'doctor':
                link_doctor_profile(
                    db,
                    user['id'],
                    user['name']
                )

            return redirect('/dashboard')

        else:
            msg = 'Invalid username or password!'

    content = f"""
    <form method="post">

    <input name="username" class="form-control mb-2"
    placeholder="Username" required>

    <input name="password" type="password"
    class="form-control mb-2"
    placeholder="Password" required>

    <button class="btn btn-primary w-100">Login</button>

    <p class="text-danger">{msg}</p>

    </form>

    <a href="/register">Create New Account</a>
    """

    return render_template_string(
        AUTH, title="Login", content=content
    )


# LOGOUT
@auth_bp.route('/logout')
def logout():

    session.clear()
    return redirect('/login')
