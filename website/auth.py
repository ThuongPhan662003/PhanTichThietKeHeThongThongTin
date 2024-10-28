from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import NguoiDung
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("Username")
        MatKhau = request.form.get("MatKhau")
        user = NguoiDung.query.filter_by(UserName=username).first()
        print(check_password_hash(user.MatKhau, MatKhau))
        if user and user.MatKhau==MatKhau:
            login_user(user)
            return redirect(url_for("views.home")) 

        else:
            flash("Sai thông tin đăng nhập, vui lòng thử lại.", "error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        UserName = request.form.get("UserName")
        MatKhau = request.form.get("MatKhau")
        print(UserName, MatKhau)
        user = NguoiDung.query.filter_by(UserName=UserName).first()
        if user:
            flash("Username already exists.", category="error")
        elif len(UserName) < 2:
            flash("UserName must be greater than 2 characters.", category="error")
        else:
            new_user = NguoiDung(
                UserName=UserName,
                TrangThai=1,
                MatKhau=MatKhau,
                VerifyCode=MatKhau,
                idNND=1,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)
