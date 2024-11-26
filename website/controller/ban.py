
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from website import db
from unidecode import unidecode
from flask import render_template, jsonify
from website.models import CT_DonDatHang, db, Ban, LoaiBan
from flask_paginate import Pagination, get_page_parameter

from website.webforms import BanForm

ban = Blueprint("ban", __name__)


@ban.route("/ban", methods=["GET"])
def danh_sach_ban():
    # try:
        # Lấy tham số tìm kiếm và trang hiện tại từ URL
        search = request.args.get('search', '').strip()  # Từ khóa tìm kiếm
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # Số dòng mỗi trang
        form = BanForm()
        # Truy vấn với điều kiện tìm kiếm
        if search:
            query = db.session.query(
                Ban.MaBan,
                Ban.TenBan,
                Ban.ViTri,
                Ban.TrangThai,
                Ban.idLoaiBan,
                LoaiBan.TenLoaiBan
            ).join(LoaiBan, Ban.idLoaiBan == LoaiBan.MaLB).filter(
                Ban.TenBan.ilike(f"%{search}%") | LoaiBan.TenLoaiBan.ilike(f"%{search}%")
            )
        else:
            query = db.session.query(
                Ban.MaBan,
                Ban.TenBan,
                Ban.ViTri,
                Ban.TrangThai,
                Ban.idLoaiBan,
                LoaiBan.TenLoaiBan
            ).join(LoaiBan, Ban.idLoaiBan == LoaiBan.MaLB)

        # Sắp xếp theo MaBan để đảm bảo thứ tự đúng
        query = query.order_by(Ban.MaBan)

        # Đếm tổng số bản ghi
        total = query.count()

        # Lấy danh sách theo trang hiện tại
        ds_ban = query.paginate(page=page, per_page=per_page, error_out=False).items

        # Sử dụng Flask-Paginate
        pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')

        # Trả kết quả về template
        return render_template(
            'admin/loaiban/danh_sach_ban.html',form=form,
            ds_ban=ds_ban,
            pagination=pagination,
            search=search
        )
    # except Exception as e:
    #     # Xử lý lỗi
    #     return jsonify({"error": str(e)}), 500
    
@ban.route("/add", methods=["GET", "POST"])
def add_ban():
    form = BanForm()
    if form.validate_on_submit():
        try:
            new_ban = Ban(
                TenBan=form.TenBan.data,
                ViTri=form.ViTri.data,
                TrangThai=form.TrangThai.data,
                idLoaiBan=form.idLoaiBan.data.MaLB  # Lấy mã loại bàn từ QuerySelectField
            )
            db.session.add(new_ban)
            db.session.commit()
            flash("Thêm bàn mới thành công!", "success")
            return redirect(url_for("ban.danh_sach_ban"))
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi: {str(e)}", "danger")
    return render_template("admin/loaiban/danh_sach_ban.html", form=form)

@ban.route("/ban/edit/<int:id>", methods=["GET", "POST"])
def edit_ban(id):
    ban = Ban.query.get_or_404(id)  # Tìm bàn theo ID, nếu không có thì trả về 404
    form = BanForm(obj=ban)  # Khởi tạo form với dữ liệu hiện tại của bàn

    if request.method == "POST" and form.validate_on_submit():
        try:
            # Kiểm tra xem tên bàn mới có trùng với tên bàn nào khác không
            if Ban.query.filter_by(TenBan=form.TenBan.data).first() != None:  
                flash("Tên bàn đã tồn tại, vui lòng chọn tên khác!", "danger")
                return redirect(url_for("ban.danh_sach_ban"))
            
            # Cập nhật dữ liệu bàn
            ban.TenBan = form.TenBan.data
            ban.ViTri = form.ViTri.data
            ban.TrangThai = form.TrangThai.data
            ban.idLoaiBan = form.idLoaiBan.data.MaLB  # Lấy mã loại bàn từ QuerySelectField
            
            db.session.commit()
            flash("Cập nhật thông tin bàn thành công!", "success")
            return redirect(url_for("ban.danh_sach_ban"))
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi: {str(e)}", "danger")
    
    return render_template("admin/loaiban/danh_sach_ban.html", form=form, edit_ban=True, ban=ban)


@ban.route('/ban/delete/<int:id>', methods=['POST'])
def delete_ban(id):
    ban = Ban.query.get_or_404(id)  # Lấy thông tin bàn cần xóa

    # Kiểm tra xem bàn có tồn tại trong CT_DON_DAT_HANG không
    if db.session.query(CT_DonDatHang).filter_by(idBan=id).first():
        flash("Không thể xóa bàn vì bàn đã được đặt trong đơn đặt hàng!", "danger")
        return redirect(url_for('ban.danh_sach_ban'))

    try:
        db.session.delete(ban)
        db.session.commit()
        flash("Xóa bàn thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi: {str(e)}", "danger")

    return redirect(url_for('ban.danh_sach_ban'))

