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
- **Authentication:** RBAC,Flask-Bcrypt, JWT
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

### Clone repository

git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

---
### Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows


### .env file setup
create the env file after launching the peoject in editor
MONGO_URI = "your db connection string"
# JWT Secret (token generate/used verify)
JWT_SECRET=your_jwt_secret_key_here

---
### Install dependencies
pip install -r requirements.txt

---
## Run application
flask --app app.py 
