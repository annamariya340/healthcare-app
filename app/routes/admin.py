from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql, bcrypt
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'danger')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Access denied!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    # Get stats
    cur.execute("SELECT COUNT(*) FROM users WHERE role='patient'")
    total_patients = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role='doctor'")
    total_doctors = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments WHERE status='pending'")
    pending_appointments = cur.fetchone()[0]

    # Get all users
    cur.execute("""
        SELECT id, name, email, role, phone, created_at 
        FROM users ORDER BY created_at DESC
    """)
    users = cur.fetchall()

    # Get all appointments
    cur.execute("""
        SELECT a.id, p.name, d.name, 
               a.appointment_date, a.time_slot, a.status
        FROM appointments a
        JOIN users p ON a.patient_id = p.id
        JOIN doctors doc ON a.doctor_id = doc.id
        JOIN users d ON doc.user_id = d.id
        ORDER BY a.created_at DESC
    """)
    appointments = cur.fetchall()
    cur.close()

    return render_template('admin/dashboard.html',
                           total_patients=total_patients,
                           total_doctors=total_doctors,
                           total_appointments=total_appointments,
                           pending_appointments=pending_appointments,
                           users=users,
                           appointments=appointments)

@admin_bp.route('/admin/add-doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(
                   request.form['password']).decode('utf-8')
        phone = request.form['phone']
        specialization = request.form['specialization']
        experience = request.form['experience']
        fee = request.form['fee']

        cur = mysql.connection.cursor()
        try:
            # Add to users table
            cur.execute("""
                INSERT INTO users (name, email, password, role, phone)
                VALUES (%s, %s, %s, 'doctor', %s)
            """, (name, email, password, phone))
            mysql.connection.commit()

            # Get new user id
            user_id = cur.lastrowid

            # Add to doctors table
            cur.execute("""
                INSERT INTO doctors 
                (user_id, specialization, experience_years, consultation_fee)
                VALUES (%s, %s, %s, %s)
            """, (user_id, specialization, experience, fee))
            mysql.connection.commit()

            flash('Doctor added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cur.close()

    return render_template('admin/add_doctor.html')

@admin_bp.route('/admin/delete-user/<int:user_id>')
@login_required
def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    mysql.connection.commit()
    cur.close()

    flash('User deleted!', 'warning')
    return redirect(url_for('admin.dashboard'))