from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date
from datetime import datetime
from website.auth import role_required
from website.models import *

# from website.webforms import
import json

dondathang = Blueprint("dondathang", __name__)


@dondathang.route("/")
@role_required(["Quản lý"])
def index():
    orders = DonDatHang.query.all()
    results = []
    for order in orders:
        results.append(
            {
                "MaDDH": order.MaDDH,
                "HoTenNguoiDat": order.HoTenNguoiDat,
                "Email": order.Email,
                "SDT": order.SDT,
                "NgayDat": order.NgayDat,
                "GioDen": order.GioDen,
                "ThoiLuong": order.ThoiLuong,
                "Loai": int.from_bytes(order.Loai, byteorder="big"),
                "idNV": NhanVien.query.filter(NhanVien.MaNV == order.idNV)
                .first()
                .getHoTenNV(),
                "TrangThai": order.TrangThai,
                "ThanhTien": str(order.ThanhTien),
            }
        )
        print("l", order.Loai)
    return render_template("admin/dondathang/dondathang.html", orders=results)


from sqlalchemy.exc import IntegrityError


@dondathang.route("/edit-order", methods=["POST"])
@role_required(["Quản lý"])
def edit_order():
    if request.method == "POST":
        # Lấy ID đơn hàng từ form
        order_id = request.form["MaDDH"]

        # Tìm đơn hàng trong DB
        order = DonDatHang.query.filter_by(MaDDH=order_id).first()

        if order:
            # Cập nhật thông tin đơn hàng
            try:
                # Lấy và kiểm tra các giá trị từ form
                order.HoTenNguoiDat = request.form["HoTenNguoiDat"]
                order.Email = request.form["Email"]
                order.SDT = request.form["SDT"]
                order.NgayDat = datetime.strptime(
                    request.form["NgayDat"], "%Y-%m-%d"
                )  # Kiểm tra định dạng ngày
                order.GioDen = request.form[
                    "GioDen"
                ]  # Nếu cần, có thể kiểm tra thời gian hợp lệ
                order.ThoiLuong = int(
                    request.form["ThoiLuong"]
                )  # Đảm bảo giá trị ThoiLuong là số
                order.TrangThai = request.form[
                    "TrangThai"
                ]  # Có thể kiểm tra tính hợp lệ của TrangThai
                order.ThanhTien = float(
                    request.form["ThanhTien"]
                )  # Chuyển đổi ThanhTien sang float
                order.Loai = int(request.form["Loai"])  # Chuyển Loai sang kiểu int

                # Lưu thay đổi vào DB
                db.session.commit()
                flash("Cập nhật đơn hàng thành công!", "success")

            except ValueError as e:
                # Nếu có lỗi trong việc chuyển kiểu hoặc dữ liệu không hợp lệ
                db.session.rollback()
                flash(f"Lỗi dữ liệu: {str(e)}", "danger")
            except IntegrityError:
                # Nếu có lỗi liên quan đến tính toàn vẹn (ví dụ: trùng lặp dữ liệu)
                db.session.rollback()
                flash(
                    "Đã có lỗi trong quá trình lưu dữ liệu, vui lòng thử lại.", "danger"
                )
        else:
            # Nếu không tìm thấy đơn hàng
            flash("Không tìm thấy đơn hàng với mã đã nhập.", "danger")

        # Chuyển hướng về trang danh sách đơn hàng
        return redirect(url_for("dondathang.index"))


@dondathang.route("/delete-order", methods=["POST"])
@role_required(["Quản lý"])
def delete_order():
    order_id = request.form["MaDDH"]
    order = DonDatHang.query.filter_by(MaDDH=order_id).first()
    if order:
        db.session.delete(order)
        db.session.commit()  # Xóa đơn hàng khỏi DB
    return redirect(url_for("dondathang.index"))
