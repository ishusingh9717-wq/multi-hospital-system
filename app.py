
from flask import Flask
from database import init_db
from auth import auth_bp
from dashboard import dashboard_bp
from hospitals import hospitals_bp
from patients import patients_bp
from doctors import doctors_bp
from appointments import appointments_bp
from prescriptions import prescriptions_bp
from billing import billing_bp
from beds import beds_bp
from notifications import notifications_bp
import os

app = Flask(__name__)
app.secret_key = "multi_hospital_2026"
init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(hospitals_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(doctors_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(prescriptions_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(beds_bp)
app.register_blueprint(notifications_bp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port = port)
