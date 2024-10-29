from lib2to3.pgen2.token import AT
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, cast, Date
from website import db
from datetime import datetime
from website.models import PHIEUXUAT, CT_PHIEUXUAT
from website.models import *
import json

phieuxuat = Blueprint("phieuxuat", __name__)

# hàm hỗ trợ phân trang
def get_delivery_notes(page, start_date=None, end_date=None, query_search=None):
    query = db.session.query(
        PHIEUXUAT.SoPhieuXuat,
        PHIEUXUAT.NgayXuat,
        func.concat(NhanVien.HoNV, ' ', NhanVien.TenNV).label("NhanVienXuat")
    ).join(CT_PHIEUXUAT, PHIEUXUAT.SoPhieuXuat == CT_PHIEUXUAT.idXuat) \
     .join(NhanVien, PHIEUXUAT.idNV == NhanVien.MaNV) \
     .group_by(PHIEUXUAT.SoPhieuXuat)

    if query_search:
        query = query.filter(func.concat(NhanVien.HoNV, ' ', NhanVien.TenNV).ilike(f'%{query_search}%'))

    if start_date and end_date:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(cast(PHIEUXUAT.NgayXuat, Date) >= start_date_dt)
        query = query.filter(cast(PHIEUXUAT.NgayXuat, Date) <= end_date_dt)
    elif start_date:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(cast(PHIEUXUAT.NgayXuat, Date) >= start_date_dt)
    elif end_date:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(cast(PHIEUXUAT.NgayXuat, Date) <= end_date_dt)


    return query.order_by(PHIEUXUAT.NgayXuat.desc()).paginate(page=page, per_page=9)

@phieuxuat.route('/delivery_notes', methods=['GET', 'POST'])
@login_required
def delivery_notes():
    page = request.args.get('page', 1, type=int)
    
    results = get_delivery_notes(page)
    
    return render_template('admin/phieuxuat/phieuxuat.html', results=results)

@phieuxuat.route('/filter_delivery_notes', methods=['GET', 'POST'])
@login_required
def filter_delivery_notes():
    # Lấy trang hiện tại từ query parameters
    page = request.args.get('page', 1, type=int)

    # Lấy các tham số lọc từ form
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    query_search = request.form.get('query_search', '').strip()
    print(query_search)
    # Gọi hàm get_received_notes với điều kiện lọc
    results = get_delivery_notes(page, start_date=start_date, end_date=end_date, query_search=query_search)

    return render_template(
        'admin/phieuxuat/phieuxuat.html',
        results=results,
        start_date=start_date,
        end_date=end_date,
    )

@phieuxuat.route('/delivery_note/<int:note_id>', methods=['GET'])
@login_required
def delivery_note_detail(note_id):
    delivery_note = PHIEUXUAT.query.get_or_404(note_id)
    
    delivery_note_detail = (
        db.session.query(CT_PHIEUXUAT, NguyenLieu)
        .join(NguyenLieu, CT_PHIEUXUAT.idNL == NguyenLieu.MaNL)
        .filter(CT_PHIEUXUAT.idXuat == note_id)
        .all()
    )
    
    details = []
    for ct, nl in delivery_note_detail:
        details.append({
            "ten_nguyen_lieu": nl.TenNguyenLieu,
            "don_vi_tinh": nl.DonViTinh,
            "so_luong": ct.SoLuong,
            "don_gia": nl.DonGia,
        })
    
    return render_template(
        'admin/phieuxuat/ctphieuxuat.html', delivery_note=delivery_note, details=details
    )

@phieuxuat.route('/add_delivery_notes', methods=['GET', 'POST'])
@login_required
def add_delivery_notes():
    if request.method == 'POST':
        ngay_xuat = request.form.get("ngayXuat")
        ingredient_list_json = request.form.get("ingredientList")

        print(ingredient_list_json)
        if not ngay_xuat:
            flash('Ngày xuất không được để trống!', 'danger')
            return redirect(url_for('phieuxuat.add_delivery_notes'))
        try:
            ingredients = json.loads(ingredient_list_json)
            existing_phieu_xuat = PHIEUXUAT.query.filter_by(
                NgayXuat= datetime.strptime(ngay_xuat, '%d-%m-%Y %H:%M'),
                idNV=current_user.MaND
            ).first()

            if existing_phieu_xuat:
                new_phieu_xuat = existing_phieu_xuat
                flash('Phiếu xuất đã tồn tại cho ngày này, sẽ được cập nhật thông tin.', 'info')
            else:
                new_phieu_xuat = PHIEUXUAT(
                    idNV=current_user.MaND,
                    NgayXuat=datetime.strptime(ngay_xuat, '%d-%m-%Y %H:%M'),
                )
                db.session.add(new_phieu_xuat)
                db.session.flush() 

            for item in ingredients:
                ten_nguyen_lieu = item.get("tenNguyenLieu")
                so_luong = item.get("soLuong")

                ingredient = NguyenLieu.query.filter_by(TenNguyenLieu=ten_nguyen_lieu).first()
                if ingredient:
                    if (ingredient.SoLuongTon == 0):
                        flash('Nguyên liệu ngày hiện đã hết!', 'info')
                        redirect(url_for('phieuxuat.add_delivery_notes'))
                    if (ingredient.SoLuongTon < so_luong):
                        flash(f'Sản phẩm này chỉ còn {ingredient.SoLuongTon}, vui lòng nhập lại!', 'danger')
                        redirect(url_for('phieuxuat.add_delivery_notes'))
                    
                    existing_ct_phieu_xuat = CT_PHIEUXUAT.query.filter_by(
                        idXuat=new_phieu_xuat.SoPhieuXuat,
                        idNL=ingredient.MaNL
                    ).first()

                    if existing_ct_phieu_xuat:
                        existing_ct_phieu_xuat.SoLuong += so_luong
                    else:
                        new_ct_phieu_xuat = CT_PHIEUXUAT(
                            idXuat=new_phieu_xuat.SoPhieuXuat,
                            idNL=ingredient.MaNL,
                            SoLuong=so_luong,
                        )
                        db.session.add(new_ct_phieu_xuat)

                    ingredient.SoLuongTon -= int(so_luong)

            db.session.commit()
            flash('Phiếu xuất và chi tiết phiếu xuất đã được lưu/cập nhật thành công!', 'success')
            return redirect(url_for('phieuxuat.add_delivery_notes'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('phieuxuat.add_delivery_notes'))

    ingredients = NguyenLieu.query.filter(NguyenLieu.SoLuongTon != 0).all()
    return render_template('admin/phieuxuat/formNhapPX.html', ingredients=ingredients)
