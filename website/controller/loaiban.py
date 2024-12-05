from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required
from website import db
from website.role import role_required
from website.webforms import  LoaiBanForm
from unidecode import unidecode
from website.models import LoaiBan
from flask import Blueprint, render_template, request
from flask_paginate import Pagination, get_page_parameter

loaiban = Blueprint("loaiban", __name__)
@loaiban.route('/loaiban')
@role_required(["Quản lý","Nhân viên"])
def danh_sach_loai_ban():
# Lấy tham số trang hiện tại từ URL
    form = LoaiBanForm()
    search = request.args.get('search', '').strip()  # Lấy từ khóa tìm kiếm
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 4  # Số dòng mỗi trang
    
    if search:
        query = LoaiBan.query.filter(LoaiBan.TenLoaiBan.ilike(f"%{search}%"))  # Tìm kiếm không phân biệt chữ hoa/thường
    else:
        query = LoaiBan.query.order_by(LoaiBan.MaLB)
    
    total = query.count()
    ds_loai_ban = query.paginate(page=page, per_page=per_page, error_out=False).items

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap5')


    return render_template('admin/loaiban/danh_sach.html', 
                           ds_loai_ban=ds_loai_ban, 
                           pagination=pagination,form=form)

@loaiban.route('/loaiban/add', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên"])
def add_loai_ban():
    form = LoaiBanForm()
    if form.validate_on_submit():
        existing_loai_ban = LoaiBan.query.filter(LoaiBan.TenLoaiBan == form.TenLoaiBan.data).first()
        if existing_loai_ban:
            flash("Tên loại bàn đã tồn tại, vui lòng chọn tên khác.", "danger")
            return redirect(url_for('loaiban.danh_sach_loai_ban')) # Quay lại trang chỉnh sửa khi trùng tên
        loai_ban = LoaiBan(TenLoaiBan=form.TenLoaiBan.data)
        db.session.add(loai_ban)
        db.session.commit()
        flash("Thêm loại bàn thành công!", "success")
        return redirect(url_for('loaiban.danh_sach_loai_ban'))  # Sau khi thêm, chuyển về danh sách
    return render_template('admin/loaiban/danh_sach.html', form=form)


@loaiban.route('/loaiban/edit/<int:id>', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên"])
def edit_loai_ban(id):
    loai_ban = LoaiBan.query.get_or_404(id)  # Lấy loại bàn theo ID
    form = LoaiBanForm(obj=loai_ban)  # Gắn dữ liệu của loại bàn vào form
    # print(form.TenLoaiBan.data)
    # print(loai_ban.TenLoaiBan)
    # print(LoaiBan.query.filter_by(TenLoaiBan=form.TenLoaiBan.data).first())
    # Kiểm tra nếu tên loại bàn mới đã tồn tại trong cơ sở dữ liệu (trừ chính loại bàn hiện tại)
    if form.validate_on_submit():
        existing_loai_ban = LoaiBan.query.filter(LoaiBan.TenLoaiBan == form.TenLoaiBan.data, LoaiBan.MaLB != id).first()
        if existing_loai_ban:
            flash("Tên loại bàn đã tồn tại, vui lòng chọn tên khác.", "danger")
            return redirect(url_for('loaiban.danh_sach_loai_ban')) # Quay lại trang chỉnh sửa khi trùng tên

 
        loai_ban.TenLoaiBan = form.TenLoaiBan.data
        db.session.commit()  # Cập nhật vào cơ sở dữ liệu
        flash("Cập nhật loại bàn thành công!", "success")
        return redirect(url_for('loaiban.danh_sach_loai_ban'))  # Sau khi cập nhật, quay lại danh sách loại bàn

    # Nếu form chưa được submit hoặc có lỗi, render lại trang
    return render_template('admin/loaiban/danh_sach.html', form=form, loai_ban=loai_ban)


from flask_wtf.csrf import validate_csrf
from flask import abort

@loaiban.route('/loaiban/delete/<int:id>', methods=['POST'])
@role_required(["Quản lý","Nhân viên"])
def delete_loai_ban(id):
    try:
        validate_csrf(request.form.get('csrf_token'))  # Kiểm tra token CSRF
    except:
        flash("Yêu cầu không hợp lệ!", "danger")
        return redirect(url_for('loaiban.danh_sach_loai_ban'))

    loai_ban = LoaiBan.query.get_or_404(id)

    # Kiểm tra phụ thuộc (nếu có)
    if loai_ban.ban:  # Giả sử bảng 'LoaiBan' liên kết với bảng 'Ban'
        #print(loai_ban.ban)
        flash("Không thể xóa vì loại bàn này đang được sử dụng!", "warning")
        return redirect(url_for('loaiban.danh_sach_loai_ban'))

    db.session.delete(loai_ban)
    db.session.commit()
    flash("Xóa loại bàn thành công!", "success")
    return redirect(url_for('loaiban.danh_sach_loai_ban'))

