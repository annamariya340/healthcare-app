from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from functools import wraps

doctor_bp = Blueprint('doctor', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@doctor_bp.route('/doctor/dashboard')
@login_required
def dashboard():
    if session['role'] != 'doctor':
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()

    # Get doctor id
    cur.execute("SELECT id FROM doctors WHERE user_id=%s",
                (session['user_id'],))
    doctor = cur.fetchone()

    if not doctor:
        flash('Doctor profile not found!', 'danger')
        return redirect(url_for('auth.logout'))

    doctor_id = doctor[0]

    # Get all appointments
    cur.execute("""
        SELECT a.id, u.name, u.phone,
               a.appointment_date, a.time_slot,
               a.status, a.reason
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date DESC
    """, (doctor_id,))
    appointments = cur.fetchall()

    # Count stats
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status='confirmed' THEN 1 ELSE 0 END) as confirmed,
            SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled
        FROM appointments WHERE doctor_id=%s
    """, (doctor_id,))
    stats = cur.fetchone()
    cur.close()

    return render_template('doctor/dashboard.html',
                           appointments=appointments,
                           stats=stats)

@doctor_bp.route('/doctor/confirm/<int:appointment_id>')
@login_required
def confirm_appointment(appointment_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE appointments SET status='confirmed'
        WHERE id=%s
    """, (appointment_id,))
    mysql.connection.commit()
    cur.close()

    flash('Appointment confirmed!', 'success')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/doctor/reject/<int:appointment_id>')
@login_required
def reject_appointment(appointment_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE appointments SET status='cancelled'
        WHERE id=%s
    """, (appointment_id,))
    mysql.connection.commit()
    cur.close()

    flash('Appointment rejected!', 'warning')
    return redirect(url_for('doctor.dashboard'))