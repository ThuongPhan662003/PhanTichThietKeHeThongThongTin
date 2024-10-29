from flask import Blueprint, make_response, render_template, request, flash, redirect, url_for
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
        
        if user and MatKhau == user.MatKhau:
            login_user(user)
            # Tạo một phản hồi để lưu trữ thông tin vào cookie
            response = make_response(redirect(url_for("views.home")))
            response.set_cookie('username', user.UserName)  # Lưu tên người dùng vào cookie
            return response
        else:
            flash("Sai thông tin đăng nhập, vui lòng thử lại.", "error")

    return render_template("login.html", user=current_user)

@auth.route("/logout")
def logout():
    logout_user()
    response = make_response(redirect(url_for("views.home")))
    response.delete_cookie('username')  # Xóa cookie
    return response



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
