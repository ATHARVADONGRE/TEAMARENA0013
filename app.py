from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_NAME = "gym.db"

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            join_date DATE,
            membership_type TEXT,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')
    
    # Trainers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            phone TEXT,
            email TEXT
        )
    ''')
    
    # Workouts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            trainer_id INTEGER,
            workout_type TEXT,
            duration_minutes INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id),
            FOREIGN KEY (trainer_id) REFERENCES trainers (id)
        )
    ''')
    
    # Memberships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            plan_type TEXT,
            start_date DATE,
            end_date DATE,
            price REAL,
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# Dashboard statistics
@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM members')
    members_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM trainers')
    trainers_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM workouts')
    workouts_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM memberships WHERE end_date >= date('now')")
    active_memberships = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'members': members_count,
        'trainers': trainers_count,
        'workouts': workouts_count,
        'active_memberships': active_memberships
    })

# Members API
@app.route('/api/members', methods=['GET'])
def get_members():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM members ORDER BY id DESC')
    members = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(members)

@app.route('/api/members', methods=['POST'])
def add_member():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO members (name, email, phone, join_date, membership_type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['phone'], data['join_date'], 
              data['membership_type'], data.get('status', 'ACTIVE')))
        conn.commit()
        member_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': member_id})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Email already exists'})

@app.route('/api/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM members WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Trainers API
@app.route('/api/trainers', methods=['GET'])
def get_trainers():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trainers ORDER BY id DESC')
    trainers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(trainers)

@app.route('/api/trainers', methods=['POST'])
def add_trainer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trainers (name, specialty, phone, email)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['specialty'], data['phone'], data['email']))
    conn.commit()
    trainer_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': trainer_id})

@app.route('/api/trainers/<int:id>', methods=['DELETE'])
def delete_trainer(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trainers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Workouts API
@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT w.*, m.name as member_name, t.name as trainer_name
        FROM workouts w
        LEFT JOIN members m ON w.member_id = m.id
        LEFT JOIN trainers t ON w.trainer_id = t.id
        ORDER BY w.date DESC
    ''')
    workouts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(workouts)

@app.route('/api/workouts', methods=['POST'])
def add_workout():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO workouts (member_id, trainer_id, workout_type, duration_minutes, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['member_id'], data['trainer_id'], data['workout_type'], 
          data['duration_minutes'], data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
    conn.commit()
    workout_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': workout_id})

@app.route('/api/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM workouts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Memberships API
@app.route('/api/memberships', methods=['GET'])
def get_memberships():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ms.*, m.name as member_name
        FROM memberships ms
        LEFT JOIN members m ON ms.member_id = m.id
        ORDER BY ms.id DESC
    ''')
    memberships = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(memberships)

@app.route('/api/memberships', methods=['POST'])
def add_membership():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO memberships (member_id, plan_type, start_date, end_date, price)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['member_id'], data['plan_type'], data['start_date'], 
          data['end_date'], data['price']))
    conn.commit()
    membership_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': membership_id})

@app.route('/api/memberships/<int:id>', methods=['DELETE'])
def delete_membership(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM memberships WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
