from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date
from datetime import datetime
from website.models import *
from website.models import PHIEUNHAP, CT_PHIEUNHAP

phieunhap = Blueprint("phieunhap", __name__)

# hàm hỗ trợ phân trang
def get_received_notes(page, start_date=None, end_date=None, min_amount=None, max_amount=None, query_search=None):
    query = db.session.query(
        PHIEUNHAP.SoPhieuNhap,
        PHIEUNHAP.NgayNhap,
        func.sum(CT_PHIEUNHAP.ThanhTien).label("TongTien"),
        func.concat(NhanVien.HoNV, ' ', NhanVien.TenNV).label("NhanVienNhap")
    ).join(CT_PHIEUNHAP, PHIEUNHAP.SoPhieuNhap == CT_PHIEUNHAP.idNhap) \
     .join(NhanVien, PHIEUNHAP.idNV == NhanVien.MaNV) \
     .group_by(PHIEUNHAP.SoPhieuNhap)

    if query_search:
        query = query.filter(func.concat(NhanVien.HoNV, ' ', NhanVien.TenNV).ilike(f'%{query_search}%'))

    if start_date and end_date:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(cast(PHIEUNHAP.NgayNhap, Date) >= start_date_dt)
        query = query.filter(cast(PHIEUNHAP.NgayNhap, Date) <= end_date_dt)
    elif start_date:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(cast(PHIEUNHAP.NgayNhap, Date) >= start_date_dt)
    elif end_date:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(cast(PHIEUNHAP.NgayNhap, Date) <= end_date_dt)

    if min_amount:
        query = query.having(func.sum(CT_PHIEUNHAP.ThanhTien) >= float(min_amount))
    if max_amount:
        query = query.having(func.sum(CT_PHIEUNHAP.ThanhTien) <= float(max_amount))

    return query.order_by(PHIEUNHAP.NgayNhap.desc()).paginate(page=page, per_page=9)

@phieunhap.route('/received_notes', methods=['GET', 'POST'])
@login_required
def received_notes():
    page = request.args.get('page', 1, type=int)
    
    results = get_received_notes(page)
    
    return render_template('admin/phieunhap/phieunhap.html', results=results)

@phieunhap.route('/received_note/<int:note_id>', methods=['GET'])
@login_required
def received_note_detail(note_id):
    received_note = PHIEUNHAP.query.get_or_404(note_id)
    
    received_note_detail = (
        db.session.query(CT_PHIEUNHAP, NguyenLieu)
        .join(NguyenLieu, CT_PHIEUNHAP.idNL == NguyenLieu.MaNL)
        .filter(CT_PHIEUNHAP.idNhap == note_id)
        .all()
    )
    
    tong_tien = sum(ct.ThanhTien for ct, nl in received_note_detail)
    details = []
    for ct, nl in received_note_detail:
        details.append({
            "ten_nguyen_lieu": nl.TenNguyenLieu,
            "don_vi_tinh": nl.DonViTinh,
            "so_luong": ct.SoLuong,
            "don_gia": nl.DonGia,
            "thanh_tien": ct.ThanhTien
        })
    
    return render_template(
        'admin/phieunhap/ctphieunhap.html', received_note=received_note, details=details, tong_tien=tong_tien
    )

@phieunhap.route('/filter_received_notes', methods=['GET', 'POST'])
@login_required
def filter_received_notes():
    # Lấy trang hiện tại từ query parameters
    page = request.args.get('page', 1, type=int)

    # Lấy các tham số lọc từ form
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    min_amount = request.form.get('min_amount')
    max_amount = request.form.get('max_amount')
    query_search = request.form.get('query_search', '').strip()
    print(query_search)
    # Gọi hàm get_received_notes với điều kiện lọc
    results = get_received_notes(page, start_date=start_date, end_date=end_date, min_amount=min_amount, max_amount=max_amount, query_search=query_search)

    return render_template(
        'admin/phieunhap/phieunhap.html',
        results=results,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount
    )

