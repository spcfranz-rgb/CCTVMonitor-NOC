import os
import time
import sqlite3
import subprocess
import threading
import requests
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, abort, flash, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cctv-super-secret-key') 
DB_PATH = '/app/data/cctv.db'

# ==========================================
# AUTHENTICATION SETUP
# ==========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# DATABASE INITIALIZATION
# ==========================================
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS switches (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, ip TEXT, status TEXT DEFAULT 'UNKNOWN'
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cameras (
        id INTEGER PRIMARY KEY AUTOINCREMENT, switch_id INTEGER, name TEXT UNIQUE, 
        ip TEXT, stream_url TEXT, status TEXT DEFAULT 'UNKNOWN',
        FOREIGN KEY(switch_id) REFERENCES switches(id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT
    )""")
    
    # Defaults from .env file
    cursor.execute("SELECT count(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        settings = [
            ('mqtt_broker', os.environ.get('DEFAULT_MQTT_BROKER', '192.168.1.50')),
            ('mqtt_port', os.environ.get('DEFAULT_MQTT_PORT', '1883')),
            ('mqtt_prefix', os.environ.get('DEFAULT_MQTT_PREFIX', 'zabbix/cctv')),
            ('check_interval', os.environ.get('DEFAULT_CHECK_INTERVAL', '60'))
        ]
        cursor.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", settings)
        
    cursor.execute("SELECT count(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_user = os
