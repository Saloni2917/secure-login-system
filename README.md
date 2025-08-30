# Secure Login System (Flask + MongoDB)

## Project Overview
A secure login and registration system with captcha validation, account lockout, and admin panel for managing users. Built using Flask, MongoDB, and Flask-Bcrypt.

---

## Features
- User Registration with validation
- Secure Login with bcrypt hashing
- Captcha validation with reload
- Account lockout after failed attempts
- Admin panel for managing users (lock/unlock)
- Session handling with JWT
- Error messages and form validation

---

## Tech Stack
- **Backend:** Python (Flask)
- **Database:** MongoDB
- **Authentication:** Flask-Bcrypt, JWT
- **Frontend:** HTML, CSS, JS (Jinja2 templates)

---

## Project Structure
project-root/
│── app.py
│── requirements.txt
│── README.md
│── templates/
│ ├── base.html
│ ├── login.html
│ ├── register.html
│ └── admin/
│── static/
│ ├── styles.css
│ └── scripts.js
└── screenshots/
├── login.png
├── register.png
└── admin.png

---

## Setup Instructions

### 1. Clone repository

git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

---
### Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac

### .env file 
# Flask Secret Key 
FLASK_SECRET_KEY=your_flask_secret_key_here
# JWT Secret (token generate/used verify)
JWT_SECRET=your_jwt_secret_key_here

---
### Install dependencies
pip install -r requirements.txt

---
## Run application
flask --app app.py 
