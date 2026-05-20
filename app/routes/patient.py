from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from functools import wraps

patient_bp = Blueprint('patient', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@patient_bp.route('/patient/dashboard')
@login_required
def dashboard():
    if session['role'] != 'patient':
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT u.id, u.name, d.specialization, 
               d.experience_years, d.consultation_fee 
        FROM users u 
        JOIN doctors d ON u.id = d.user_id 
        WHERE u.role = 'doctor'
    """)
    doctors = cur.fetchall()

    cur.execute("""
        SELECT a.id, doc_user.name, doc.specialization,
               a.appointment_date, a.time_slot, a.status, a.reason
        FROM appointments a
        JOIN doctors doc ON a.doctor_id = doc.id
        JOIN users doc_user ON doc.user_id = doc_user.id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC
    """, (session['user_id'],))
    appointments = cur.fetchall()
    cur.close()

    return render_template('patient/dashboard.html',
                           doctors=doctors,
                           appointments=appointments)

@patient_bp.route('/patient/book/<int:doctor_user_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_user_id):
    if session['role'] != 'patient':
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM doctors WHERE user_id=%s", (doctor_user_id,))
    doctor_record = cur.fetchone()

    if not doctor_record:
        flash('Doctor not found!', 'danger')
        return redirect(url_for('patient.dashboard'))

    doctor_id = doctor_record[0]

    if request.method == 'POST':
        appointment_date = request.form['appointment_date']
        time_slot = request.form['time_slot']
        reason = request.form['reason']

        cur.execute("""
            INSERT INTO appointments 
            (patient_id, doctor_id, appointment_date, time_slot, reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], doctor_id,
              appointment_date, time_slot, reason))
        mysql.connection.commit()
        cur.close()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient.dashboard'))

    cur.execute("""
        SELECT u.name, d.specialization, d.consultation_fee
        FROM users u JOIN doctors d ON u.id = d.user_id
        WHERE u.id = %s
    """, (doctor_user_id,))
    doctor = cur.fetchone()
    cur.close()

    return render_template('patient/book.html', doctor=doctor,
                           doctor_id=doctor_id)

@patient_bp.route('/patient/cancel/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE appointments SET status='cancelled'
        WHERE id=%s AND patient_id=%s
    """, (appointment_id, session['user_id']))
    mysql.connection.commit()
    cur.close()

    flash('Appointment cancelled!', 'warning')
    return redirect(url_for('patient.dashboard'))