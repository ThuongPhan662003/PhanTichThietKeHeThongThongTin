from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from flask import render_template, request
from flask_paginate import Pagination, get_page_parameter

from website.models import MonAn

monan = Blueprint("monan", __name__)

@monan.route('/mon-an', methods=['GET'])
def danh_sach_mon_an():
    # Lấy từ khóa tìm kiếm (nếu có)
    ten_mon_an = request.args.get('ten_mon_an', '')

    # Truy vấn danh sách món ăn, nếu có tìm kiếm thì lọc theo tên món ăn
    query = MonAn.query

    if ten_mon_an:
        query = query.filter(MonAn.TenMonAn.like(f'%{ten_mon_an}%'))

    # Thiết lập số lượng món ăn mỗi trang
    per_page = 4  # Số lượng món ăn mỗi trang

    # Lấy số trang hiện tại từ query string (mặc định là trang 1)
    page = request.args.get(get_page_parameter(), type=int, default=1)

    # Truy vấn dữ liệu cho trang hiện tại
    mon_ans = query.paginate(page=page, per_page=per_page, error_out=False)

    # Khởi tạo đối tượng Pagination
    pagination = Pagination(page=page, total=mon_ans.total, per_page=per_page, record_name='mon_ans', css_framework='bootstrap5')
    mon_ans = mon_ans.items  # Lấy danh sách món ăn của trang hiện tại

    # Trả về template với danh sách món ăn và phân trang
    return render_template('admin/MonAn/danh_sach.html',
                           mon_ans=mon_ans,
                           pagination=pagination,
                           ten_mon_an=ten_mon_an)
