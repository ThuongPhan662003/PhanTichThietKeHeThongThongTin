
from datetime import datetime
import random
import string
from flask import Blueprint
from website.role import role_required

from website.models import LOAIVOUCHER, VOUCHER
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from website import db
from unidecode import unidecode
from flask import render_template, jsonify
from website.models import CT_DonDatHang, db, Ban, LoaiBan
from flask_paginate import Pagination, get_page_parameter

from flask import render_template, request
from website.webforms import LoaiVoucherForm

loaivoucher = Blueprint("loaivoucher", __name__)


@loaivoucher.route('/list', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def danh_sach_loaivoucher():
    # Lấy từ request để kiểm tra nếu có từ khóa tìm kiếm
    ten_loai_voucher = request.args.get('ten_loai_voucher', '')
    loai_kh = request.args.get('loai_kh', '')
    form = LoaiVoucherForm()
    # Truy vấn danh sách loại voucher từ cơ sở dữ liệu, lọc theo từ khóa tìm kiếm
    query = LOAIVOUCHER.query

    if ten_loai_voucher:
        query = query.filter(LOAIVOUCHER.TenLoaiVoucher.like(f'%{ten_loai_voucher}%'))
    
    if loai_kh:
        query = query.filter(LOAIVOUCHER.LoaiKH.like(f'%{loai_kh}%'))

    # Thiết lập số lượng item mỗi trang
    per_page = 5

    # Lấy số trang hiện tại từ query string (mặc định là trang 1)
    page = request.args.get(get_page_parameter(), type=int, default=1)

    # Truy vấn dữ liệu cho trang hiện tại
    loai_vouchers = query.paginate(page=page, per_page=per_page, error_out=False)

    # Khởi tạo đối tượng Pagination
    pagination = Pagination(page=page, total=loai_vouchers.total, per_page=per_page, record_name='loai_vouchers', css_framework='bootstrap5')
    loai_vouchers = loai_vouchers.items
    # Trả về trang HTML với danh sách loại voucher và phân trang
    return render_template('admin/voucher/danh_sach_loaivoucher.html', 
                           loai_vouchers=loai_vouchers, 
                           pagination=pagination, 
                           ten_loai_voucher=ten_loai_voucher, 
                           loai_kh=loai_kh, form=form)

@loaivoucher.route('/add', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def them_loai_voucher():
    form = LoaiVoucherForm()
    if form.SoLuongConLai.data is None:
        form.SoLuongConLai.data = form.SoLuong.data
    
    if form.validate_on_submit():  # Kiểm tra nếu form đã được gửi và hợp lệ
        try:
            # Lấy dữ liệu từ form
            ten_loai_voucher = form.TenLoaiVoucher.data
            phan_tram = form.PhanTram.data
            mo_ta = form.MoTa.data
            so_luong = form.SoLuong.data
            so_luong_con_lai = form.SoLuongConLai.data
            loai_kh = form.LoaiKH.data
            ngay_bat_dau = form.NgayBatDau.data
            ngay_ket_thuc = form.NgayKetThuc.data
            giam_toi_da = form.GiamToiDa.data
            an = form.An.data
            # Đặt thời gian mặc định là 00:00:00



            # Tạo một đối tượng LOAIVOUCHER mới và thêm vào cơ sở dữ liệu
            loai_voucher = LOAIVOUCHER(
                TenLoaiVoucher=ten_loai_voucher,
                PhanTram=phan_tram,
                MoTa=mo_ta,
                SoLuong=so_luong,
                SoLuongConLai=so_luong_con_lai,
                LoaiKH=loai_kh,
                NgayBatDau=ngay_bat_dau,
                NgayKetThuc=ngay_ket_thuc,
                GiamToiDa=giam_toi_da,
                An=an
            )



            # Lưu vào cơ sở dữ liệu
            db.session.add(loai_voucher)
            db.session.commit()

            # Hiển thị thông báo thành công
            flash('Loại voucher đã được thêm thành công!', 'success')
            return redirect(url_for('loaivoucher.danh_sach_loaivoucher'))  # Quay lại danh sách loại voucher
        except SQLAlchemyError as e:
            # Xử lý lỗi nếu có ngoại lệ từ cơ sở dữ liệu
            db.session.rollback()  # Hủy bỏ transaction nếu có lỗi
            flash(f"Đã xảy ra lỗi khi thêm loại voucher: {str(e)}", 'danger')
            return redirect(url_for('loaivoucher.danh_sach_loaivoucher'))
    else:
        # Nếu form không hợp lệ, hiển thị lại form với thông báo lỗi
        return redirect(url_for('loaivoucher.danh_sach_loaivoucher'))

# Route sửa loại voucher
@loaivoucher.route('/edit/<int:id>', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def sua_loai_voucher(id):
    loai_voucher = LOAIVOUCHER.query.get_or_404(id)
    form = LoaiVoucherForm(obj=loai_voucher)
    print(form.SoLuongConLai.data)
    if form.validate_on_submit():
        try:
            loai_voucher.TenLoaiVoucher = form.TenLoaiVoucher.data
            loai_voucher.PhanTram = form.PhanTram.data
            loai_voucher.MoTa = form.MoTa.data
            loai_voucher.SoLuong = form.SoLuong.data
            loai_voucher.SoLuongConLai = form.SoLuongConLai.data
            loai_voucher.LoaiKH = form.LoaiKH.data
            loai_voucher.NgayBatDau = form.NgayBatDau.data
            loai_voucher.NgayKetThuc = form.NgayKetThuc.data
            loai_voucher.GiamToiDa = form.GiamToiDa.data
            loai_voucher.An = form.An.data

            db.session.commit()
            flash('Loại voucher đã được sửa thành công!', 'success')
            return redirect(url_for('loaivoucher.danh_sach_loaivoucher'))  # Quay lại danh sách loại voucher

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Đã xảy ra lỗi khi sửa loại voucher: {str(e)}", 'danger')
            return render_template('admin/voucher/danh_sach_loaivoucher.html', form=form)

    return render_template('admin/voucher/danh_sach_loaivoucher.html', form=form)

@loaivoucher.route('/delete/<int:id>', methods=['POST'])
@role_required(["Quản lý"])
def xoa_loai_voucher(id):
    try:
        # Lấy loại voucher cần xóa từ cơ sở dữ liệu
        loai_voucher = LOAIVOUCHER.query.get_or_404(id)

        # Xóa loại voucher khỏi cơ sở dữ liệu
        db.session.delete(loai_voucher)
        db.session.commit()

        # Thông báo thành công
        flash('Loại voucher đã được xóa thành công!', 'success')
        return redirect(url_for('loaivoucher.danh_sach_loaivoucher'))  # Quay lại danh sách

    except SQLAlchemyError as e:
        db.session.rollback()  # Hủy bỏ transaction nếu có lỗi
        flash(f"Đã xảy ra lỗi khi xóa loại voucher: {str(e)}", 'danger')
        return redirect(url_for('loaivoucher.danh_sach_loaivoucher'))  # Quay lại danh sách
    
@loaivoucher.route('/loaivoucher/<int:id>/init_voucher', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def init_voucher(id):
    # Lấy thông tin loại voucher từ ID
    loai_voucher = LOAIVOUCHER.query.get_or_404(id)
    # Lấy số lượng voucher cần tạo từ SoLuongConLai của loại voucher
    so_luong_voucher = loai_voucher.SoLuongConLai

    if request.method == 'POST':
        # Lấy số lượng voucher cần tạo từ form hoặc mặc định
        so_luong_voucher = int(request.form.get('so_luong_voucher', so_luong_voucher))

        # Tạo các mã voucher
        created_vouchers = []
        for _ in range(so_luong_voucher):
            code_voucher = generate_voucher_code()  # Sinh mã voucher ngẫu nhiên
            voucher = VOUCHER(CodeVoucher=code_voucher, idLoaiVoucher=id)
            db.session.add(voucher)
            created_vouchers.append(voucher)
        loai_voucher.SoLuongConLai -= so_luong_voucher
        # Commit vào cơ sở dữ liệu
        db.session.commit()

        flash(f'Đã tạo {so_luong_voucher} mã voucher thành công!', 'success')
        return redirect(url_for('loaivoucher.danh_sach_loaivoucher'))
    flash(f'Đã tạo {so_luong_voucher} mã voucher không thành công!', 'success')
    return render_template('admin/voucher/danh_sach_loaivoucher.html', loai_voucher=loai_voucher)
# Hàm tạo mã voucher không trùng lặp
def generate_voucher_code(length=10):
    while True:
        code = ''.join(random.choice(string.digits) for _ in range(length))  # Chỉ tạo mã gồm số
        # Kiểm tra xem mã có tồn tại trong cơ sở dữ liệu không
        if not VOUCHER.query.filter_by(CodeVoucher=code).first():
            return code