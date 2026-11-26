
import sqlite3
from flask import g
from datetime import datetime

DB = "master.db"


# Get database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DB,
            timeout=10
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA busy_timeout = 10000")

    return g.db


# Close database connection after request
def close_db(error=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Initialize database
def init_db():

    conn = sqlite3.connect(DB, timeout=10)

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")

    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT,
            phone TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            age INT,
            category TEXT,
            fee INT,
            phone TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS doctor_hospitals (
            id INTEGER PRIMARY KEY,
            doctor_id INTEGER,
            hospital_id INTEGER,
            UNIQUE(doctor_id, hospital_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            age INT,
            gender TEXT,
            phone TEXT,
            address TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            doctor_id INTEGER,
            hospital_id INTEGER,
            date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY,
            appointment_id INTEGER,
            patient_id INTEGER,
            doctor_id INTEGER,
            medicine TEXT,
            notes TEXT,
            date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            hospital_id INTEGER,
            amount INT,
            desc TEXT,
            date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS beds (
            id INTEGER PRIMARY KEY,
            hospital_id INTEGER UNIQUE,
            total_icu INT,
            occupied_icu INT,
            total_general INT,
            occupied_general INT,
            total_emergency INT,
            occupied_emergency INT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            message TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# Send notification using existing connection
def notify(user_id, msg):

    db = get_db()

    db.execute("""
        INSERT INTO notifications
        (user_id, message, status, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        msg,
        'Unread',
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    db.commit()
