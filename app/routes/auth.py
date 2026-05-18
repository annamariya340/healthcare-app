from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app import mysql, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(
                   request.form['password']).decode('utf-8')
        role = request.form.get('role', 'patient')
        phone = request.form.get('phone', '')

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO users (name, email, password, role, phone) VALUES (%s,%s,%s,%s,%s)",
                (name, email, password, role, phone)
            )
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Email already exists!', 'danger')
        finally:
            cur.close()

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            session['role'] = user[4]

            if user[4] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user[4] == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            else:
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))