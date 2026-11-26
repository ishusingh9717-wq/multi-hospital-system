
from flask import Blueprint, request, redirect, session
from database import get_db
from helpers import render_page, need_login

hospitals_bp = Blueprint('hospitals', __name__)

@hospitals_bp.route('/hospitals', methods=['GET', 'POST'])
def hospitals():
    if need_login():
        return redirect('/login')

    db = get_db()

    if request.method == 'POST' and session.get('role') == 'admin':
        name = request.form['name']
        location = request.form['location']
        phone = request.form['phone']

        db.execute(
            "INSERT INTO hospitals (name, location, phone) VALUES (?,?,?)",
            (name, location, phone)
        )
        db.commit()

    rows = db.execute("SELECT * FROM hospitals").fetchall()

    form = ""
    if session.get('role') == 'admin':
        form = """
        <div class="form-card">
        <h5>Add Hospital</h5>
        <form method="post">
        <input name="name" placeholder="Hospital Name" required>
        <input name="location" placeholder="Location" required>
        <input name="phone" placeholder="Phone Number" required>
        <button class="blue-btn">Add Hospital</button>
        </form>
        </div>
        """

    table = """
    <div class="table-box">
    <h5>Hospital List</h5>
    <table class="table">
    <tr><th>ID</th><th>Name</th><th>Location</th><th>Phone</th></tr>
    """

    for r in rows:
        table += f"<tr><td>{r['id']}</td><td>{r['name']}</td><td>{r['location']}</td><td>{r['phone']}</td></tr>"

    table += "</table></div>"

    content = f"""
    <h2>Hospitals</h2>
    <div class="d-flex gap-3 flex-wrap mt-4">
    {form}
    {table}
    </div>
    """

    return render_page(content, 'hospitals')
