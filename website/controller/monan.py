import time
import os
from flask import Blueprint, current_app, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from flask import render_template, request
from flask_paginate import Pagination, get_page_parameter
from website.auth import role_required

from website.models import MonAn,CT_MonAn
from website.webforms import MonAnForm
from werkzeug.utils import secure_filename
from website import db

monan = Blueprint("monan", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@monan.route('/mon-an', methods=['GET'])
@role_required(["Quản lý"])
def danh_sach_mon_an():
    # Lấy từ khóa tìm kiếm (nếu có)
    ten_mon_an = request.args.get('ten_mon_an', '')
    loai_mon_an = request.args.get('loai_mon_an', '')
    form = MonAnForm()
    
    # Truy vấn danh sách món ăn, nếu có tìm kiếm thì lọc theo tên món ăn
    query = MonAn.query

    if ten_mon_an:
        query = query.filter(MonAn.TenMonAn.like(f'%{ten_mon_an}%'))
 # Lọc theo loại món ăn nếu có lựa chọn loại
    if loai_mon_an:
        query = query.filter(MonAn.Loai.like(f'%{loai_mon_an}%'))

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
                           ten_mon_an=ten_mon_an, form=form)

@monan.route('/them-mon-an', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def them_mon_an():
    form = MonAnForm()
    if form.validate_on_submit():
        # Lấy dữ liệu từ form
        ten_mon_an = form.TenMonAn.data
        don_gia = form.DonGia.data
        loai = form.Loai.data
        trang_thai = form.TrangThai.data
        hinh_anh = form.HinhAnh.data
        # Kiểm tra xem món ăn đã tồn tại chưa (Dựa trên tên món ăn)
        existing_mon_an = MonAn.query.filter_by(TenMonAn=ten_mon_an).first()
        if existing_mon_an:
            flash('Món ăn với tên này đã tồn tại!', 'danger')
            return redirect(url_for('monan.danh_sach_mon_an'))
        # Tạo một đối tượng món ăn mới (lưu trước để tạo MaMA)
        mon_an = MonAn(
            TenMonAn=ten_mon_an,
            DonGia=don_gia,
            Loai=loai,
            TrangThai=trang_thai
        )
        db.session.add(mon_an)
        db.session.commit()

        # Xử lý upload hình ảnh (nếu có)
        if hinh_anh and allowed_file(hinh_anh.filename):
            # Đảm bảo thư mục tồn tại
            image_folder = os.path.join(current_app.root_path, 'static/images/monan')
            os.makedirs(image_folder, exist_ok=True)

            # Đặt tên tệp là MaMA và lưu
            filename = secure_filename(f"{mon_an.MaMA}_{int(time.time())}.jpg")
            hinh_anh.save(os.path.join(image_folder, filename))
            mon_an.HinhAnh = filename
            db.session.commit()  # Cập nhật tên tệp vào cơ sở dữ liệu

        flash('Thêm món ăn thành công!', 'success')
        return redirect(url_for('monan.danh_sach_mon_an'))

    # Hiển thị form thêm món ăn
    return render_template('admin/MonAn/danh_sach.html', form=form)

@monan.route('/sua-mon-an/<int:ma_ma>', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def sua_mon_an(ma_ma):
    mon_an = MonAn.query.get_or_404(ma_ma)
    form = MonAnForm(obj=mon_an)  # Đổ dữ liệu từ món ăn vào form

    if form.validate_on_submit():
        ten_mon_an = form.TenMonAn.data
        existing_mon_an = MonAn.query.filter(MonAn.TenMonAn == ten_mon_an, MonAn.MaMA != ma_ma).first()
        
        if existing_mon_an:
            flash('Tên món ăn đã tồn tại. Vui lòng chọn tên khác!', 'danger')
            return redirect(url_for('monan.danh_sach_mon_an'))

        # Cập nhật thông tin món ăn từ form
        mon_an.TenMonAn = form.TenMonAn.data
        mon_an.DonGia = form.DonGia.data
        mon_an.Loai = form.Loai.data
        mon_an.TrangThai = form.TrangThai.data
        
        # Xử lý ảnh (nếu có upload mới)
        hinh_anh = form.HinhAnh.data
        if hinh_anh and allowed_file(hinh_anh.filename):
            image_folder = os.path.join(current_app.root_path, 'static/images/monan')
            os.makedirs(image_folder, exist_ok=True)

            # Lưu ảnh với tên là MaMA
            filename = secure_filename(f"{mon_an.MaMA}_{int(time.time())}.jpg")
            hinh_anh.save(os.path.join(image_folder, filename))
            mon_an.HinhAnh = filename

        db.session.commit()
        flash('Cập nhật món ăn thành công!', 'success')
        return redirect(url_for('monan.danh_sach_mon_an'))
    flash('Cập nhật món ăn không thành công!', 'success')
    return render_template('admin/MonAn/danh_sach.html')
@monan.route('/xoa-mon-an/<int:ma_ma>', methods=['POST'])
@role_required(["Quản lý"])
def xoa_mon_an(ma_ma):
    mon_an = MonAn.query.get_or_404(ma_ma)  # Lấy món ăn cần xóa

    # Kiểm tra nếu món ăn có tồn tại trong bảng CT_MONAN
    if CT_MonAn.query.filter_by(idMA=ma_ma).first():
        flash('Không thể xóa món ăn vì nó đang tồn tại trong đơn đặt hàng!', 'danger')
        return redirect(url_for('monan.danh_sach_mon_an'))

    # Nếu món ăn không có liên kết trong CT_MONAN, thực hiện xóa
    try:
        db.session.delete(mon_an)
        db.session.commit()
        flash('Xóa món ăn thành công!', 'success')
    except Exception as e:
        db.session.rollback()  # Đảm bảo commit lại nếu có lỗi
        flash(f'Lỗi khi xóa món ăn: {str(e)}', 'danger')

    return redirect(url_for('monan.danh_sach_mon_an'))
