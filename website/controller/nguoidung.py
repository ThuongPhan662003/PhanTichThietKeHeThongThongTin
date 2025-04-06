import random
import re
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from website import db
from sqlalchemy import func, cast, Date
from datetime import datetime
from website.role import role_required
from website.models import NguoiDung, KhachHang, NhanVien, NhomNguoiDung

# from website.webforms import

# Tạo Blueprint
nguoidung = Blueprint("nguoidung", __name__)


@nguoidung.route("/")
@role_required(["Nhân viên","Quản lý","Khách hàng","Nhân viên kho"])
def account():
    # Lấy thông tin username từ cookie
    username = current_user.UserName
    # Kiểm tra nếu username không hợp lệ hoặc không có
    if not username:
        flash("Bạn chưa đăng nhập!", "danger")
        return redirect(url_for("auth.login"))  # Chuyển hướng đến trang đăng nhập

    # Kiểm tra người dùng trong cơ sở dữ liệu
    user = NguoiDung.query.filter_by(UserName=username).first()
    MaND = user.get_id()
    if not user:
        flash("Không tìm thấy tài khoản. Vui lòng kiểm tra lại.", "danger")
        return redirect(url_for("auth.login"))
    TenNhomND = (
        NhomNguoiDung.query.filter_by(MaNND=current_user.idNND)
        .first()
        .getTenNhomNguoiDung()
    )
    print("TenNhomND", TenNhomND)

    # Kiểm tra vai trò của người dùng (Nhân viên hoặc khách hàng)
    if TenNhomND == "Khách hàng":
        khachhang = KhachHang.query.filter_by(idNguoiDung=MaND).first()
        GioiTinh = khachhang.GioiTinh
        print(khachhang.getHoTen())
        if GioiTinh == 1:
            random_number = random.randint(0, 50)
        else:
            random_number = random.randint(51, 100)
        avatar_url = "https://avatar.iran.liara.run/public/" + str(random_number)

        return render_template(
            "/user/nguoidung/khachhang.html",
            user=user,
            khachhang=khachhang,
            avatar_url=avatar_url,
        )
    else:
        print("")
        employee = NhanVien.query.filter_by(idNguoiDung=MaND).first()
        print("employee",employee)
        GioiTinh = employee.get_GioiTinh()
        print("GioiTinh",GioiTinh)
        if GioiTinh:
            if GioiTinh == 1:
                random_number = random.randint(51, 100)
            else:
                random_number = random.randint(0, 50)
            avatar_url = "https://avatar.iran.liara.run/public/" + str(random_number)
            return render_template(
                "/admin/nguoidung/nguoidung.html",
                user=user,
                employee=employee,
                avatar_url=avatar_url,
            )
        else:
            avatar_url = "https://avatar.iran.liara.run/public/" 
            return render_template(
                "/admin/nguoidung/nguoidung.html",
                user=user,
                employee=employee,
                avatar_url=avatar_url,
            )

    return redirect(url_for("auth.login"))


@nguoidung.route("/khachhang/<int:khachhang_id>")
@role_required(["Khách hàng"])
def khachhang_detail(khachhang_id):
    # Lấy thông tin khách hàng theo ID
    khachhang = KhachHang.query.get_or_404(khachhang_id)

    # Truyền dữ liệu vào template
    return render_template(
        "/admin/nguoidung/khachhang_detail.html", khachhang=khachhang
    )


@nguoidung.route("/edit_employee/<int:employee_id>", methods=["GET", "POST"])
@role_required(["Nhân viên","Quản lý","Nhân viên kho"])
def edit_employee(employee_id):
    # Truy xuất thông tin nhân viên
    employee = NhanVien.query.get_or_404(employee_id)

    if request.method == "POST":
        # Lấy dữ liệu từ form và cập nhật thông tin nhân viên
        employee.set_HoNV(request.form["HoNV"])
        employee.set_TenNV(request.form["TenNV"])
        employee.set_Email(request.form["Email"])
        employee.set_SDT(request.form["SDT"])

        # Xử lý ngày sinh và ngày vào làm
        employee.set_NgaySinh(datetime.strptime(request.form["NgaySinh"], "%Y-%m-%d"))
        employee.set_NgayVaoLam(datetime.strptime(request.form["NgayVaoLam"], "%Y-%m-%d"))

        # Cập nhật tình trạng
        employee.set_TinhTrang(bool(request.form["TinhTrang"]))
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, employee.get_Email()):
            flash("Email không hợp lệ.", category="danger")
            return render_template("/admin/nguoidung/edit_employee.html", employee=employee)
        elif len(employee.get_SDT()) != 10:
            flash("Số điện thoại phải là 10 chữ số.", category="danger")
            return render_template("/admin/nguoidung/edit_employee.html", employee=employee)

        db.session.commit()
        flash("Cập nhật thông tin thành công!", "success")
        return redirect(url_for("nguoidung.account"))

    return render_template("/admin/nguoidung/edit_employee.html", employee=employee)


@nguoidung.route("/edit_account_employee/<int:user_id>", methods=["GET", "POST"])
@role_required(["Nhân viên","Quản lý","Nhân viên kho"])
def edit_account_employee(user_id):
    # Truy xuất thông tin người dùng
    user = NguoiDung.query.get_or_404(user_id)

    if request.method == "POST":
        # Cập nhật thông tin tài khoản
        user.UserName = request.form["UserName"]
        user.MatKhau = request.form["MatKhau"]
        db.session.commit()
        flash("Cập nhật tài khoản thành công!", "success")
        return redirect(url_for("nguoidung.account"))

    return render_template("/admin/nguoidung/edit_account.html", user=user)


@nguoidung.route("/edit_customer/<int:khachhang_id>", methods=["GET", "POST"])
@role_required(["Khách hàng"])
def edit_customer(khachhang_id):
    khachhang = KhachHang.query.get_or_404(khachhang_id)

    if request.method == "POST":
        # Cập nhật thông tin khách hàng
        khachhang.set_HoKH(request.form["HoKH"])
        khachhang.set_TenKH(request.form["TenKH"])
        khachhang.set_Email(request.form["Email"])
        khachhang.set_SDT(request.form["SDT"])
        khachhang.set_DiemTieuDung(request.form["DiemTieuDung"])
        khachhang.set_DiemTichLuy(request.form["DiemTichLuy"])
        khachhang.set_LoaiKH(request.form["LoaiKH"])

        # Lưu thay đổi vào cơ sở dữ liệu
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, khachhang.get_Email()):
            flash("Email không hợp lệ.", category="danger")
            return render_template("/user/nguoidung/edit_customer.html", khachhang=khachhang)
        elif len(khachhang.get_SDT()) != 10:
            flash("Số điện thoại phải là 10 chữ số.", category="danger")
            return render_template("/user/nguoidung/edit_customer.html", khachhang=khachhang)
        db.session.commit()
        flash("Cập nhật thông tin khách hàng thành công!", "success")
        return redirect(url_for("nguoidung.account"))

    return render_template("/user/nguoidung/edit_customer.html", khachhang=khachhang)


@nguoidung.route("/edit_account_customer/<int:user_id>", methods=["GET", "POST"])
@role_required(["Khách hàng"])
def edit_account_customer(user_id):
    print("đsd")
    user = NguoiDung.query.get_or_404(user_id)
    print(user)
    if request.method == "POST":
        # Cập nhật thông tin tài khoản
        user.UserName = request.form["UserName"]
        user.MatKhau = request.form["MatKhau"]

        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()
        flash("Cập nhật tài khoản thành công!", "success")
        return redirect(url_for("nguoidung.account"))

    return render_template("/user/nguoidung/edit_account.html", user=user)
