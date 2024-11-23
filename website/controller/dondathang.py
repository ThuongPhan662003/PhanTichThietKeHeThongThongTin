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


@dondathang.route("/edit-order", methods=["POST"])
@role_required(["Quản lý"])
def edit_order():
    if request.method == "POST":
        order_id = request.form["MaDDH"]
        order = DonDatHang.query.filter_by(MaDDH=order_id).first()
        if order:
            order.HoTenNguoiDat = request.form["HoTenNguoiDat"]
            order.Email = request.form["Email"]
            order.SDT = request.form["SDT"]
            order.NgayDat = request.form["NgayDat"]
            order.GioDen = request.form["GioDen"]
            order.ThoiLuong = request.form["ThoiLuong"]
            order.TrangThai = request.form["TrangThai"]
            order.ThanhTien = request.form["ThanhTien"]
            order.Loai = int(request.form["Loai"])
            db.session.commit()  # Lưu thay đổi vào DB
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
