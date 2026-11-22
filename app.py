from flask import Flask, request, render_template_string
from prometheus_flask_exporter import PrometheusMetrics
import sqlite3
app = Flask(__name__)
metrics = PrometheusMetrics(app)
app.secret_key = "super_secreto_hardcodeado_123"
def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, password TEXT)')
    conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()
@app.route('/')
def index():
    user = request.args.get('user', 'Invitado')
    template = f"<h1>Bienvenido a SecureDev, {user}</h1><p>Sistema operativo.</p>"
    return render_template_string(template)
@app.route('/login')
def login():
    username = request.args.get('username', '')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return {"resultado": str(result)}
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
