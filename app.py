import os
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, origins="*")

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_conn():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    conn.autocommit = False
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS enquiries (
                   id SERIAL PRIMARY KEY,
                   name TEXT, phone TEXT, location TEXT,
                   requirement TEXT, status TEXT DEFAULT 'New')''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                   id SERIAL PRIMARY KEY,
                   username TEXT UNIQUE, password TEXT, name TEXT, phone TEXT,
                   step1 TEXT DEFAULT 'Pending', step2 TEXT DEFAULT 'Pending',
                   step3 TEXT DEFAULT 'Pending', step4 TEXT DEFAULT 'Pending',
                   step5 TEXT DEFAULT 'Pending', step6 TEXT DEFAULT 'Pending',
                   step7 TEXT DEFAULT 'Pending', step8 TEXT DEFAULT 'Pending',
                   step9 TEXT DEFAULT 'Pending', step10 TEXT DEFAULT 'Pending',
                   step11 TEXT DEFAULT 'Pending', step12 TEXT DEFAULT 'Pending',
                   step13 TEXT DEFAULT 'Pending',
                   total_cost REAL DEFAULT 0,
                   branch TEXT DEFAULT '')''')
    c.execute('''CREATE TABLE IF NOT EXISTS admin (
                   id SERIAL PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                   id SERIAL PRIMARY KEY,
                   title TEXT, description TEXT, image_path TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
                   id SERIAL PRIMARY KEY,
                   customer_id INTEGER,
                   amount REAL, mode TEXT, date TEXT, description TEXT)''')
    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"DB init error: {e}")

@app.route('/api/enquiries', methods=['POST'])
def submit_enquiry():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    location = data.get('location')
    requirement = data.get('requirement', '')
    if not name or not phone:
        return jsonify({'success': False, 'message': 'Name and phone are required'}), 400
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO enquiries (name, phone, location, requirement) VALUES (%s, %s, %s, %s)",
              (name, phone, location, requirement))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Enquiry submitted successfully'})

@app.route('/api/enquiries', methods=['GET'])
def get_enquiries():
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT * FROM enquiries ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    branch = data.get('branch', '')
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO customers (username, password, name, phone, branch) VALUES (%s, %s, %s, %s, %s)",
                  (username, password, name, phone, branch))
        conn.commit()
        success, msg = True, "Customer created successfully"
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        success, msg = False, "Username already exists"
    conn.close()
    return jsonify({'success': success, 'message': msg})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT id, username, name, phone, branch, total_cost, step1, step2, step3, step4, step5, step6, step7, step8, step9, step10, step11, step12, step13 FROM customers ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/customer/status', methods=['POST'])
def update_status():
    data = request.json
    customer_id = data.get('id')
    step = data.get('step')
    status = data.get('status')
    allowed_steps = [f'step{i}' for i in range(1, 14)]
    if step not in allowed_steps:
        return jsonify({'success': False, 'message': 'Invalid step'}), 400
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"UPDATE customers SET {step}=%s WHERE id=%s", (status, customer_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Status updated'})

@app.route('/api/login/admin', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
    admin = c.fetchone()
    conn.close()
    if admin:
        return jsonify({'success': True, 'message': 'Login successful'})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/login/customer', methods=['POST'])
def customer_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT * FROM customers WHERE username=%s AND password=%s", (username, password))
    customer = c.fetchone()
    conn.close()
    if customer:
        return jsonify({'success': True, 'customer': dict(customer)})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/projects', methods=['GET'])
def get_projects():
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id=%s", (project_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Project deleted'})

@app.route('/api/customer/cost', methods=['POST'])
def set_customer_cost():
    data = request.json
    cid = data.get('id')
    cost = data.get('cost')
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE customers SET total_cost=%s WHERE id=%s", (cost, cid))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Cost updated'})

@app.route('/api/payments', methods=['POST'])
def add_payment():
    data = request.json
    cid = data.get('customer_id')
    amount = data.get('amount')
    mode = data.get('mode')
    date = data.get('date')
    description = data.get('description', '')
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO payments (customer_id, amount, mode, date, description) VALUES (%s, %s, %s, %s, %s)",
              (cid, amount, mode, date, description))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Payment added'})

@app.route('/api/payments/<int:customer_id>', methods=['GET'])
def get_payments(customer_id):
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT total_cost FROM customers WHERE id=%s", (customer_id,))
    cost_row = c.fetchone()
    total_cost = float(cost_row['total_cost']) if cost_row and cost_row['total_cost'] else 0
    c.execute("SELECT * FROM payments WHERE customer_id=%s ORDER BY date DESC, id DESC", (customer_id,))
    payments = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'total_cost': total_cost, 'payments': payments})

@app.route('/api/branch_summary', methods=['GET'])
def get_branch_summary():
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT id, name, branch, total_cost FROM customers")
    customers = c.fetchall()
    c.execute("SELECT customer_id, SUM(amount) as total_paid FROM payments GROUP BY customer_id")
    payments = c.fetchall()
    conn.close()
    paid_map = {p['customer_id']: float(p['total_paid']) for p in payments}
    result = []
    for cust in customers:
        cost = float(cust['total_cost'] or 0)
        paid = paid_map.get(cust['id'], 0.0)
        result.append({
            'id': cust['id'],
            'name': cust['name'],
            'branch': cust['branch'] or 'Unassigned',
            'total_cost': cost,
            'total_paid': paid,
            'remaining': cost - paid
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
