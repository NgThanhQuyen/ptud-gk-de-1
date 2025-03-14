from math import e
from re import template
from flask import Blueprint, render_template, request, flash, session
from flask.helpers import url_for
from sqlalchemy.sql.expression import false
from werkzeug.utils import redirect
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from manage import views
from .models import User, Task

from . import db

user = Blueprint("user", __name__)


@user.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(user_name=username).first()
        
        if user:
            if user.is_locked:  # Kiểm tra tài khoản có bị khóa hay không
                flash("Your account has been locked.", category="error")
                return redirect(url_for("user.login"))
            
            if check_password_hash(user.password, password):
                session.permanent = True
                login_user(user, remember=True)
                flash("Logged in success!", category="success")
                return redirect(url_for("views.home"))
            else:
                flash("Wrong password, please check again!", category="error")
        else:
            flash("User doesn't exist!", category="error")
    return render_template("login.html", user=current_user)


@user.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(user_name=username).first()

        if user and user.is_admin:
            if check_password_hash(user.password, password):
                session.permanent = True
                login_user(user, remember=True)
                flash("Admin logged in successfully!", category="success")
                return redirect(url_for("views.admin_manage"))
            else:
                flash("Wrong password!", category="error")
        else:
            flash("Invalid admin credentials!", category="error")

    return render_template("admin_login.html", user=current_user)



@user.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user = User.query.filter_by(email=email).first()
        # Validate user
        if user:
            flash("User existed!", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(password) < 7:
            flash("Password must be greater than 6 characters.", category="error")
        elif password != confirm_password:
            flash("Passwords do not match!", category="error")
        else:
            # Lưu mật khẩu gốc trước khi băm
            plain_password = password  
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(
                email=email,
                password=hashed_password,
                user_name=user_name,
                plain_password=plain_password  # lưu mật khẩu gốc (không khuyến khích)
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("User created!", category="success")
                login_user(new_user, remember=True)
                return redirect(url_for("views.home"))
            except Exception as e:
                flash("Error when creating user!", category="error")
                print(e)
    return render_template("signup.html", user=current_user)



@user.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.login"))
