import os
import re
import random
import jwt
from datetime import datetime, timedelta, timezone   
from flask import Flask, render_template, request, redirect, url_for, flash, make_response,session
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load from .env
SECRET_KEY = os.getenv("SECRET_KEY")
app.secret_key = SECRET_KEY  

app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)
users = mongo.db.users
bcrypt = Bcrypt(app)

# ---------- JWT helpers ----------
def generate_jwt(user_id, role):
    payload = {
        "user_id": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),  
        "iat": datetime.now(timezone.utc)                       
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect(url_for("login"))
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except jwt.ExpiredSignatureError:
            flash("Session expired, please log in again.", "warning")
            return redirect(url_for("login"))
        except jwt.InvalidTokenError:
            flash("Invalid token. Please log in again.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, "user") or request.user.get("role") != role:
                return render_template("403.html"), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

# ---------- Security helpers ----------
def is_strong_password(password):
    return (len(password) >= 8 and re.search(r"[A-Z]", password) and 
            re.search(r"[a-z]", password) and re.search(r"\d", password) and 
            re.search(r"[!@#$%^&*(),.?\\\":{}|<>]", password))

def generate_captcha():
    a, b = random.randint(1,9), random.randint(1,9)
    return f"{a} + {b}", str(a+b)

# ---------- Make `now` available in templates ----------
@app.context_processor
def inject_now():
    return {'now': lambda: datetime.now(timezone.utc)}   # ✅ fixed

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        captcha = request.form["captcha"]
        captcha_answer = request.form["captcha_answer"]
        if captcha != captcha_answer:
            flash("CAPTCHA failed", "danger")
            return redirect(url_for("register"))
        if not is_strong_password(password):
            flash("Weak password", "danger")
            return redirect(url_for("register"))
        if users.find_one({"email": email}):
            flash("Email already registered", "danger")
            return redirect(url_for("register"))
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw,
            "role": "user",
            "failed_attempts": 0,
            "locked_until": None
        })
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))
    captcha_q, captcha_ans = generate_captcha()
    return render_template("register.html", captcha_q=captcha_q, captcha_a=captcha_ans)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        captcha = request.form["captcha"]
        captcha_answer = request.form["captcha_answer"]

        # ✅ Captcha check
        if captcha != captcha_answer:
            flash("CAPTCHA failed", "danger")
            return redirect(url_for("login"))

        user = users.find_one({"email": email})
        if not user:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))
        
        # ✅ Account lock check
        if user.get("locked_until") and datetime.now(timezone.utc) < (
            user["locked_until"].replace(tzinfo=timezone.utc) if user["locked_until"].tzinfo is None else user["locked_until"]
        ):
            flash("Account locked. Try later.", "danger")
            return redirect(url_for("login"))
        
        # ✅ Password check
        if bcrypt.check_password_hash(user["password"], password):
            # Reset failed attempts
            users.update_one({"_id": user["_id"]}, {"$set": {"failed_attempts": 0, "locked_until": None}})
            
            # Generate JWT
            token = generate_jwt(user["_id"], user["role"])

            # ✅ Set session values
            session['user'] = str(user['_id'])
            session['email'] = user['email']
            session['role'] = user['role']

            # Response with cookie
            resp = make_response(redirect(url_for("dashboard")))
            resp.set_cookie("token", token, httponly=True, samesite="Strict")
            flash("Login successful!", "success")
            return resp

        else:
            # Wrong password → increase attempts
            attempts = user.get("failed_attempts", 0) + 1
            lockout = None
            if attempts >= 5:
                lockout = datetime.now(timezone.utc) + timedelta(minutes=3)
                flash("Too many attempts. Account locked.", "danger")
            users.update_one({"_id": user["_id"]}, {"$set": {"failed_attempts": attempts, "locked_until": lockout}})
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

    # GET request → show login form with captcha
    captcha_q, captcha_ans = generate_captcha()
    return render_template("login.html", captcha_q=captcha_q, captcha_a=captcha_ans)

@app.route("/dashboard")
@token_required
def dashboard():
    return render_template("dashboard.html", role=request.user["role"])

@app.route("/admin/users")
@token_required
@role_required("admin")
def admin_users():
    all_users = list(users.find({}))
    
    # ✅ Normalize locked_until (backward compatibility)
    for u in all_users:
        if u.get("locked_until") and u["locked_until"].tzinfo is None:
            u["locked_until"] = u["locked_until"].replace(tzinfo=timezone.utc)
    
    return render_template("admin_users.html", users=all_users)

@app.route("/logout")
def logout():
    # Clear session
    session.clear()

    # Clear JWT cookie also
    resp = make_response(redirect(url_for("login")))
    resp.delete_cookie("token")

    flash("You have been logged out", "info")
    return resp

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    # Seed default admin if not exists
    if not users.find_one({"email":"admin@example.com"}):
        hashed_pw = bcrypt.generate_password_hash("Admin@123").decode("utf-8")
        users.insert_one({
            "username":"admin",
            "email":"admin@example.com",
            "password":hashed_pw,
            "role":"admin",
            "failed_attempts":0,
            "locked_until":None
        })
    app.run(debug=True)
