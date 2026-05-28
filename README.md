# 🏥 Healthcare Appointment Booking System

A secure web application developed using **Python Flask** and deployed on **AWS Cloud**. The system allows patients to book appointments, doctors to manage schedules, and administrators to manage the platform.

## 🌐 Live Application

**URL:** https://healthcareapp.ddns.net

## 📌 Features

* Patient Registration and Login
* Doctor Login and Appointment Management
* Admin Dashboard
* Appointment Booking and Cancellation
* Role-Based Access Control
* Secure Password Hashing using bcrypt
* JWT Authentication
* HTTPS Security
* Automated CI/CD Deployment

## 🛠 Technologies Used

* Python Flask
* MySQL (AWS RDS)
* AWS EC2
* AWS S3
* Nginx
* Gunicorn
* Docker
* GitHub Actions
* AWS CloudWatch

## ☁ AWS Services

* EC2 – Application Hosting
* RDS – MySQL Database
* S3 – Backup Storage
* CloudWatch – Monitoring
* SNS – Email Alerts

## 🔐 Security Features

* HTTPS with SSL Certificate
* JWT Authentication
* Password Hashing (bcrypt)
* SQL Injection Prevention
* XSS Protection
* Fail2ban Intrusion Prevention
* UFW Firewall

## 🚀 Project Structure

```text
healthcare-app/
├── app/
├── .github/workflows/
├── Dockerfile
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## 👥 User Roles

### Patient

* Register and Login
* Book Appointments
* Cancel Appointments

### Doctor

* View Appointments
* Manage Appointment Status

### Admin

* Manage Users
* Add Doctors
* View Statistics


