from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website import db
from datetime import datetime, timedelta
from website.models import *
from sqlalchemy import func, extract


nhomnguoidung = Blueprint("nhomnguoidung", __name__)


@nhomnguoidung.route("/")
def list_nhom_nguoi_dung():
    # Lấy danh sách nhóm người dùng
    nhom_nguoi_dung = NhomNguoiDung.query.all()

    # Tạo một dictionary chứa tài khoản theo nhóm
    accounts_by_group = {}
    for nhom in nhom_nguoi_dung:
        accounts = NguoiDung.query.filter_by(idNND=nhom.MaNND).all()
        accounts_by_group[nhom.MaNND] = accounts

    return render_template(
        "admin/nhomnguoidung/list.html",
        nhom_nguoi_dung=nhom_nguoi_dung,
        accounts_by_group=accounts_by_group,
    )


@nhomnguoidung.route("/add", methods=["GET", "POST"])
def add_nhom_nguoi_dung():
    if request.method == "POST":
        ten_nhom = request.form["TenNhomNguoiDung"]
        if ten_nhom.strip():
            nnd = NhomNguoiDung.query.filter(NhomNguoiDung.TenNhomNguoiDung == ten_nhom).first()
            if nnd:
                flash("Tên nhóm người dùng là duy nhất!", "danger")
                return render_template("admin/nhomnguoidung/add.html")
            else:
                try:
                    new_nhom = NhomNguoiDung(TenNhomNguoiDung=ten_nhom.strip())
                    db.session.add(new_nhom)
                    db.session.commit()
                    flash("Thêm nhóm người dùng thành công!", "success")
                except Exception as e:
                    flash(f"Lỗi khi thêm nhóm: {e}", "danger")
        else:
            flash("Tên nhóm không được để trống.", "warning")
        return redirect(url_for("nhomnguoidung.list_nhom_nguoi_dung"))

    return render_template("admin/nhomnguoidung/add.html")


@nhomnguoidung.route("/delete/<int:id>", methods=["GET"])
def delete_nhom_nguoi_dung(id):
    nhom = NhomNguoiDung.query.get_or_404(id)
    if PHANQUYEN.query.filter(PHANQUYEN.idNND == id).first() :
        flash("Nhóm người dùng đã được phân quyền!", "danger")
        return redirect(url_for("nhomnguoidung.list_nhom_nguoi_dung"))
    elif NguoiDung.query.filter(NguoiDung.idNND == id).first():
        flash("Nhóm người dùng đã có tài khoản!", "danger")
        return redirect(url_for("nhomnguoidung.list_nhom_nguoi_dung"))
    else:
        try:
            db.session.delete(nhom)
            db.session.commit()
            flash("Xóa nhóm người dùng thành công!", "success")
        except Exception as e:
            flash(f"Lỗi khi xóa nhóm: {e}", "danger")

    return redirect(url_for("nhomnguoidung.list_nhom_nguoi_dung"))
