import datetime
from functools import wraps
import re
import secrets
import string

from website.role import role_required
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
from sqlalchemy.exc import SQLAlchemyError

admin = Blueprint("admin", __name__)



# @admin.route("/login", methods=["GET", "POST"])
# @role_required(["Quản lý","Nhân viên kho","Nhân viên"])
# def login():
#     if request.method == "POST":

#         UserName = request.form.get("UserName")
#         MatKhau = request.form.get("MatKhau")
#         print(UserName)
#         user = NguoiDung.query.filter_by(UserName=UserName).first()
#         if user and user.MatKhau == MatKhau:
#             login_user(user, remember=True)
#             flash("Login successful!", category="success")
#             return redirect(url_for("admin.admin_home"))
#         else:
#             flash("Invalid username or password.", category="error")

#     return render_template("admin/auth/login.html", user=current_user)


# @admin.route("/")
# # @admin_required
# def admin_home():
#     print()
#     return render_template("admin/admin-home.html")



@admin.route("/sign-up", methods=["GET", "POST"])
@role_required(["Quản lý"])
def sign_up():

    employees = NhanVien.query.all()
    roles = NhomNguoiDung.query.all()
    if request.method == "POST":
        UserName = request.form.get("UserName")
        MatKhau1 = request.form.get("MatKhau1")
        MatKhau2 = request.form.get("MatKhau2")
        role_name = request.form.get("role")
        selected_employee_id = request.form.get("selectedEmployee")
        print("selected_employee_id", selected_employee_id)

        # Kiểm tra xem username đã tồn tại chưa
        user = NguoiDung.query.filter_by(UserName=UserName).first()

        if user:
            flash("Username already exists.", category="error")
        elif MatKhau1 != MatKhau2:
            flash("Passwords do not match.", category="error")
        else:
            try:
                # Tạo mã xác nhận ngẫu nhiên
                verify_code = "".join(
                    secrets.choice(string.ascii_letters + string.digits)
                    for _ in range(6)
                )
                # Tạo đối tượng người dùng mới
                new_user = NguoiDung(
                    MaND=None,
                    UserName=UserName,
                    TrangThai=1,
                    MatKhau=MatKhau1,
                    VerifyCode=verify_code,
                    idNND=role_name,
                )
                print(new_user)
                db.session.add(new_user)
                db.session.commit()  # Thêm người dùng vào DB

                # Lấy id của người dùng đã thêm vào
                user_id = int(
                    NguoiDung.query.filter_by(UserName=UserName).first().get_id()
                )

                # Lấy thông tin nhân viên đã chọn
                employee = NhanVien.query.filter_by(MaNV=selected_employee_id).first()
                print(employee)

                if employee:
                    # Gán idNguoiDung vào nhân viên
                    employee.idNguoiDung = user_id
                    print("user_id", user_id)
                    db.session.commit()  # Cập nhật nhân viên vào DB

                
                # if (
                #     NhomNguoiDung.query.filter_by(MaNND=role_name)
                #     .first()
                #     .getTenNhomNguoiDung()
                #     == "Khách hàng"
                # ):
                #     return redirect(url_for("views.homepage"))
                # else:
                #     return redirect(url_for("views.admin_home"))

            except SQLAlchemyError as e:
                # Nếu có lỗi xảy ra trong quá trình thêm người dùng hoặc cập nhật nhân viên, rollback
                db.session.rollback()
                flash(
                    "An error occurred while creating the account. Please try again.",
                    category="error",
                )
                print(f"Error occurred: {e}")
                return redirect(url_for("admin.sign_up"))

    return render_template(
        "admin/taikhoan/create_account.html",
        user=current_user,
        employees=employees,
        roles=roles,
    )
