import datetime
from functools import wraps
import re
import secrets
import string
from .models import KhachHang, NguoiDung, NhanVien, NhomNguoiDung
from flask import (
    Blueprint,
    request,
    flash,
    redirect,
    session,
    url_for,
    make_response,
    render_template,
)
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
import os


admin = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)

    return decorated_function


@admin.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        UserName = request.form.get("UserName")
        MatKhau = request.form.get("MatKhau")
        print(UserName)
        user = NguoiDung.query.filter_by(UserName=UserName).first()
        if user and user.MatKhau == MatKhau:
            login_user(user, remember=True)
            flash("Login successful!", category="success")
            return redirect(url_for("admin.admin_home"))
        else:
            flash("Invalid username or password.", category="error")

    return render_template("admin/auth/login.html", user=current_user)


@admin.route("/")
# @admin_required
def admin_home():
    return render_template("admin/admin-home.html")


# @admin.route("/logout")
# @login_required
# def logout():
#     session.pop("email", None)  # Xóa email khỏi session
#     session.pop("name", None)  # Xóa tên khỏi session
#     logout_user()
#     return redirect(url_for("admin.login"))


@admin.route("/sign-up", methods=["GET", "POST"])
# @admin_required
def sign_up():

    employees = NhanVien.query.all()
    roles = NhomNguoiDung.query.all()
    if request.method == "POST":
        UserName = request.form.get("Email")
        MatKhau1 = request.form.get("MatKhau1")
        MatKhau2 = request.form.get("MatKhau2")
        role_name = request.form.get("role")
        user = NguoiDung.query.filter_by(UserName=UserName).first()
        TenNhomNguoiDung = "Khách hàng"
        idNND = int(
            NhomNguoiDung.query.filter_by(TenNhomNguoiDung=TenNhomNguoiDung)
            .first()
            .getMaNND()
        )

        if user:
            flash("Username already exists.", category="error")

        elif MatKhau1 != MatKhau2:
            flash("Passwords do not match.", category="error")
        else:
            verify_code = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(6)
            )

            NgayMoThe = datetime.datetime.now()
            new_user = NguoiDung(
                MaND=None,
                UserName=UserName,
                TrangThai=1,
                MatKhau=MatKhau1,
                VerifyCode=verify_code,
                idNND=int(idNND),
            )
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
            user_id = int(NguoiDung.query.filter_by(UserName=UserName).first().get_id())

            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.homepage"))

    return render_template(
        "admin/taikhoan/create_account.html", user=current_user, employees=employees,roles=roles
    )
