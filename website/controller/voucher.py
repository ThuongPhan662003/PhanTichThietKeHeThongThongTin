from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website import db
from website.role import role_required

from website.models import LOAIVOUCHER, VOUCHER

from flask import Blueprint, render_template, request
from flask_paginate import Pagination, get_page_args,get_page_parameter

voucher = Blueprint('voucher', __name__)

@voucher.route('/voucher/list', methods=['GET'])
@role_required(["Quản lý","Nhân viên"])
def danh_sach_vouchers():
    # Lấy từ request để kiểm tra nếu có từ khóa tìm kiếm
    code_voucher = request.args.get('code_voucher', '')
    ten_loai_voucher = request.args.get('ten_loai_voucher', '')
    trang_thai = request.args.get('trang_thai', '')

    # Khởi tạo form (nếu có)
    #form = VoucherForm()

    # Truy vấn danh sách voucher từ cơ sở dữ liệu, lọc theo từ khóa tìm kiếm
    query = VOUCHER.query.join(LOAIVOUCHER, LOAIVOUCHER.MaLoaiVoucher == VOUCHER.idLoaiVoucher)

    if code_voucher:
        query = query.filter(VOUCHER.CodeVoucher.like(f'%{code_voucher}%'))
    
    if ten_loai_voucher:
        query = query.filter(LOAIVOUCHER.TenLoaiVoucher.like(f'%{ten_loai_voucher}%'))
    
    if trang_thai:
        query = query.filter(VOUCHER.TrangThai == (trang_thai.lower() == 'true'))

    # Thiết lập số lượng item mỗi trang
    per_page = 7
    query.order_by(VOUCHER.loai_voucher)
    # Lấy số trang hiện tại từ query string (mặc định là trang 1)
    page = request.args.get(get_page_parameter(), type=int, default=1)

    # Truy vấn dữ liệu cho trang hiện tại
    vouchers = query.paginate(page=page, per_page=per_page, error_out=False)

    # Khởi tạo đối tượng Pagination
    pagination = Pagination(page=page, total=vouchers.total, per_page=per_page, record_name='vouchers', css_framework='bootstrap5')
    vouchers = vouchers.items

    # Trả về trang HTML với danh sách voucher và phân trang
    return render_template('admin/voucher/voucher.html',
                           vouchers=vouchers,
                           pagination=pagination,
                           code_voucher=code_voucher,
                           ten_loai_voucher=ten_loai_voucher,
                           trang_thai=trang_thai

                           )