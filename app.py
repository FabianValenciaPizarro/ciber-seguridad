import os
import secrets
import sqlite3
from flask import Flask, request, render_template_string
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

DB_PATH = os.environ.get("DB_PATH", "users.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)"
        )
        default_user = os.environ.get("DEFAULT_ADMIN_USER", "admin")
        default_pass = os.environ.get("DEFAULT_ADMIN_PASS")
        if default_pass:
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                (default_user, default_pass),
            )
    conn.close()


@app.route("/")
def index():
    user = request.args.get("user", "Invitado")
    html = """
    <h1>Bienvenido a SecureDev, {{ user }}</h1>
    <p>Sistema operativo.</p>
    """
    return render_template_string(html, user=user)


@app.route("/login")
def login():
    username = request.args.get("username", "")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    safe_result = [{"id": row["id"], "username": row["username"]} for row in rows]
    return {"resultado": safe_result}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
