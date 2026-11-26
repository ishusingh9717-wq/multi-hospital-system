
from flask import Blueprint, redirect, session
from database import get_db
from helpers import render_page, need_login

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
def notifications():
    if need_login():
        return redirect('/login')

    db = get_db()

    rows = db.execute("""
        SELECT * FROM notifications
        WHERE user_id=?
        ORDER BY id DESC
    """, (session['user_id'],)).fetchall()

    tr = "".join([
        f"<tr><td>{r['message']}</td>"
        f"<td>{r['status']}</td>"
        f"<td>{r['created_at']}</td></tr>"
        for r in rows
    ])

    c = f'''
    <h3>Notifications</h3>
    <div class="table-box">
    <table class="table">
    <tr><th>Message</th><th>Status</th><th>Time</th></tr>
    {tr}
    </table></div>
    '''

    return render_page(c, 'notifications')
