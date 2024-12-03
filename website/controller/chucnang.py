from asyncio.windows_events import NULL
from re import I
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website import db
from datetime import datetime, timedelta
from website.auth import role_required
from website.models import *
from sqlalchemy import func, extract

chucnang = Blueprint("chucnang", __name__)


@chucnang.route("/", methods=["GET"])
@role_required(["Quản lý"])
def list_chucnang():
    search = request.args.get("search", "")
    role = request.args.get("role", "")

    # Lọc theo nhóm quyền nếu có
    if role:
        nhom_nguoi_dung = NhomNguoiDung.query.filter_by(MaNND=role).first()
        if nhom_nguoi_dung:
            # Lấy các chức năng được phân quyền cho nhóm người dùng này
            phan_quyen = PHANQUYEN.query.filter_by(idNND=nhom_nguoi_dung.MaNND).all()
            ma_cns = [pq.idCN for pq in phan_quyen]
            funcs = ChucNang.query.filter(
                ChucNang.MaCN.in_(ma_cns), ChucNang.TenManHinh.contains(search)
            ).paginate(page=1, per_page=10)
        else:
            funcs = ChucNang.query.filter(
                ChucNang.TenManHinh.contains(search)
            ).paginate(page=1, per_page=10)
    else:
        funcs = ChucNang.query.filter(ChucNang.TenManHinh.contains(search)).paginate(
            page=1, per_page=10
        )

    nhom_nguoi_dung_list = NhomNguoiDung.query.all()
    return render_template(
        "admin/chucnang/chucnang.html",
        funcs=funcs,
        search=search,
        role=role,  # Trả về giá trị 'role' đã lọc
        nhom_nguoi_dung=nhom_nguoi_dung_list,
    )


@chucnang.route("/add", methods=["GET", "POST"])
@role_required(["Quản lý"])
def add():
    nhom_nguoi_dung = NhomNguoiDung.query.all()
    if request.method == "POST":
        ten_mh = request.form["TenManHinh"]

        new_chucnang = ChucNang(ten_mh)
        db.session.add(new_chucnang)
        db.session.commit()
        flash("Thêm chức năng thành công!", "success")
        return redirect(url_for("chucnang.list_chucnang"))

    return render_template("admin/chucnang/add.html", nhom_nguoi_dung=nhom_nguoi_dung)


@chucnang.route("/edit/<int:id>", methods=["GET", "POST"])
@role_required(["Quản lý"])
def edit(id):
    chucnang = ChucNang.query.get_or_404(id)
    nhom_nguoi_dung = NhomNguoiDung.query.all()
    if request.method == "POST":

        chucnang.TenManHinh = request.form["TenManHinh"]
        chucnang.Quyen = request.form["Quyen"]
        db.session.commit()
        flash("Cập nhật chức năng thành công!", "success")
        return redirect(url_for("chucnang.list_chucnang"))

    return render_template(
        "admin/chucnang/edit.html", chucnang=chucnang, nhom_nguoi_dung=nhom_nguoi_dung
    )


@chucnang.route("/delete/<int:id>", methods=["GET"])
@role_required(["Quản lý"])
def delete(id):
    chucnang = ChucNang.query.get_or_404(id)
    db.session.delete(chucnang)
    db.session.commit()
    flash("Xóa chức năng thành công!", "success")
    return redirect(url_for("chucnang.list_chucnang"))


@chucnang.route("/assign_role/<int:id>", methods=["POST"])
@role_required(["Quản lý"])
def assign_role(id):
    role_id = request.form.get("role")
    chucnang = ChucNang.query.get_or_404(id)

    # Kiểm tra nếu đã tồn tại phân quyền
    existing_permission = PHANQUYEN.query.filter_by(
        idCN=chucnang.MaCN, idNND=role_id
    ).first()
    if existing_permission:
        flash("Quyền đã được gán trước đó!", "warning")
        return redirect(url_for("chucnang.list_chucnang"))

    # Tạo phân quyền mới
    new_permission = PHANQUYEN(idCN=chucnang.MaCN, idNND=role_id)
    db.session.add(new_permission)
    db.session.commit()

    flash("Phân quyền thành công!", "success")
    return redirect(url_for("chucnang.list_chucnang"))
