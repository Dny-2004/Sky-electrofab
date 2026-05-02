import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

DB_FILE = 'database.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Enquiries table
    c.execute('''CREATE TABLE IF NOT EXISTS enquiries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, phone TEXT, location TEXT, requirement TEXT, status TEXT DEFAULT 'New')''')
    # Customers table
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE, password TEXT, name TEXT, phone TEXT,
                  step1 TEXT DEFAULT 'Pending',
                  step2 TEXT DEFAULT 'Pending',
                  step3 TEXT DEFAULT 'Pending',
                  step4 TEXT DEFAULT 'Pending',
                  step5 TEXT DEFAULT 'Pending',
                  step6 TEXT DEFAULT 'Pending',
                  step7 TEXT DEFAULT 'Pending',
                  step8 TEXT DEFAULT 'Pending',
                  step9 TEXT DEFAULT 'Pending',
                  step10 TEXT DEFAULT 'Pending',
                  step11 TEXT DEFAULT 'Pending',
                  step12 TEXT DEFAULT 'Pending',
                  step13 TEXT DEFAULT 'Pending')''')
    # Admin
    c.execute('''CREATE TABLE IF NOT EXISTS admin
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
                 
    # Projects
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT, description TEXT, image_path TEXT)''')
                  
    # Add total_cost to customers if not exists
    try:
        c.execute("ALTER TABLE customers ADD COLUMN total_cost REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
        
    # Add branch to customers if not exists
    try:
        c.execute("ALTER TABLE customers ADD COLUMN branch TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
        
    # Payments Table
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_id INTEGER,
                  amount REAL,
                  mode TEXT,
                  date TEXT,
                  description TEXT)''')
    
    # Insert default admin if not exists
    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
        
    conn.commit()
    conn.close()

init_db()

@app.route('/api/enquiries', methods=['POST'])
def submit_enquiry():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    location = data.get('location')
    requirement = data.get('requirement', '')
    
    if not name or not phone:
        return jsonify({'success': False, 'message': 'Name and phone are required'}), 400
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO enquiries (name, phone, location, requirement) VALUES (?, ?, ?, ?)",
              (name, phone, location, requirement))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Enquiry submitted successfully'})

@app.route('/api/enquiries', methods=['GET'])
def get_enquiries():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM enquiries ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    branch = data.get('branch', '')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO customers (username, password, name, phone, branch) VALUES (?, ?, ?, ?, ?)",
                  (username, password, name, phone, branch))
        conn.commit()
        success = True
        msg = "Customer created successfully"
    except sqlite3.IntegrityError:
        success = False
        msg = "Username already exists"
    conn.close()
    
    return jsonify({'success': success, 'message': msg})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, name, phone, branch, total_cost, step1, step2, step3, step4, step5, step6, step7, step8, step9, step10, step11, step12, step13 FROM customers ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/customer/status', methods=['POST'])
def update_status():
    data = request.json
    customer_id = data.get('id')
    step = data.get('step') # e.g. "step1"
    status = data.get('status') # e.g. "Completed"
    
    allowed_steps = [f'step{i}' for i in range(1, 14)]
    if step not in allowed_steps:
        return jsonify({'success': False, 'message': 'Invalid step'}), 400
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"UPDATE customers SET {step}=? WHERE id=?", (status, customer_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Status updated'})

@app.route('/api/login/admin', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
    admin = c.fetchone()
    conn.close()
    
    if admin:
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/login/customer', methods=['POST'])
def customer_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM customers WHERE username=? AND password=?", (username, password))
    customer = c.fetchone()
    conn.close()
    
    if customer and customer['password'] == password:
        return jsonify({'success': True, 'customer': dict(customer)})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/projects', methods=['POST'])
def add_project():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image part'}), 400
    file = request.files['image']
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        import time
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO projects (title, description, image_path) VALUES (?, ?, ?)",
                  (title, description, filename))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Project uploaded successfully'})

@app.route('/api/projects', methods=['GET'])
def get_projects():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT image_path FROM projects WHERE id=?", (id,))
    row = c.fetchone()
    if row:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], row[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        c.execute("DELETE FROM projects WHERE id=?", (id,))
        conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Project deleted'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/customer/cost', methods=['POST'])
def set_customer_cost():
    data = request.json
    cid = data.get('id')
    cost = data.get('cost')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE customers SET total_cost=? WHERE id=?", (cost, cid))
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
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO payments (customer_id, amount, mode, date, description) VALUES (?, ?, ?, ?, ?)",
              (cid, amount, mode, date, description))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Payment added'})

@app.route('/api/payments/<int:customer_id>', methods=['GET'])
def get_payments(customer_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get total cost
    c.execute("SELECT total_cost FROM customers WHERE id=?", (customer_id,))
    cost_row = c.fetchone()
    total_cost = cost_row['total_cost'] if cost_row and cost_row['total_cost'] else 0
    
    # Get payments
    c.execute("SELECT * FROM payments WHERE customer_id=? ORDER BY date DESC, id DESC", (customer_id,))
    payments = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return jsonify({'success': True, 'total_cost': total_cost, 'payments': payments})

@app.route('/api/branch_summary', methods=['GET'])
def get_branch_summary():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get all customers with their total cost
    c.execute("SELECT id, name, branch, total_cost FROM customers")
    customers = c.fetchall()
    
    # Get all payments grouped by customer_id
    c.execute("SELECT customer_id, SUM(amount) as total_paid FROM payments GROUP BY customer_id")
    payments = c.fetchall()
    conn.close()
    
    paid_map = {p['customer_id']: p['total_paid'] for p in payments}
    
    result = []
    for cust in customers:
        cost = float(cust['total_cost'] or 0)
        paid = float(paid_map.get(cust['id'], 0))
        remaining = cost - paid
        
        result.append({
            'id': cust['id'],
            'name': cust['name'],
            'branch': cust['branch'] or 'Unassigned',
            'total_cost': cost,
            'total_paid': paid,
            'remaining': remaining
        })
        
    return jsonify(result)

if __name__ == '__main__':
    print("Starting Sky Electrofab Solar Full-Stack Backend on http://localhost:5000")
    app.run(port=5000, debug=True)
