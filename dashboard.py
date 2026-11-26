
from flask import Blueprint, redirect
from database import get_db
from helpers import render_page, need_login

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if need_login():
        return redirect('/login')

    db = get_db()

    hospitals = db.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
    doctors = db.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    patients = db.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    appointments = db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]

    content = f"""
    <h2>Dashboard</h2>
    <p>Welcome, {__import__('flask').session.get('name')}!</p>

    <div class="d-flex flex-wrap gap-3 mt-4">
        <div class="dash-card">
            <h3>{hospitals}</h3>
            <p>Total Hospitals</p>
        </div>
        <div class="dash-card">
            <h3>{doctors}</h3>
            <p>Total Doctors</p>
        </div>
        <div class="dash-card">
            <h3>{patients}</h3>
            <p>Total Patients</p>
        </div>
        <div class="dash-card">
            <h3>{appointments}</h3>
            <p>Total Appointments</p>
        </div>
    </div>
    """
    return render_page(content, 'dashboard')
