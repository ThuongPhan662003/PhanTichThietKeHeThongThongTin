from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, cast, Date, or_
from website import db
from datetime import datetime
from website.auth import role_required
from website.models import PHIEUXUAT, CT_PHIEUXUAT
from website.models import *
import json
import pandas as pd
from io import BytesIO

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
@role_required(["Quản lý","Nhân viên kho"])
def delivery_notes():
    page = request.args.get('page', 1, type=int)
    
    results = get_delivery_notes(page)
    
    return render_template('admin/phieuxuat/phieuxuat.html', results=results)

@phieuxuat.route('/filter_delivery_notes', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên kho"])
def filter_delivery_notes():
    page = request.args.get('page', 1, type=int)

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    query_search = request.form.get('query_search', '').strip()
    print(query_search)
    results = get_delivery_notes(page, start_date=start_date, end_date=end_date, query_search=query_search)

    return render_template(
        'admin/phieuxuat/phieuxuat.html',
        results=results,
        start_date=start_date,
        end_date=end_date,
    )

@phieuxuat.route('/delivery_note/<int:note_id>', methods=['GET'])
@role_required(["Quản lý","Nhân viên kho"])
def delivery_note_detail(note_id):
    delivery_note = PHIEUXUAT.query.get_or_404(note_id)
    details = [{
        "stt": idx + 1,
        "ten_nguyen_lieu": ct.nguyen_lieu.TenNguyenLieu,
        "don_vi_tinh": ct.nguyen_lieu.DonViTinh, 
        "so_luong": ct.SoLuong,
        "don_gia": ct.nguyen_lieu.DonGia,
    } for idx, ct in enumerate(delivery_note.chi_tiet_phieu)]
    can_change = delivery_note.NgayXuat.date() == datetime.now().date()

    return render_template(
        'admin/phieuxuat/ctphieuxuat.html',
        delivery_note=delivery_note,
        details=details,
        can_change=can_change
    )


@phieuxuat.route('/add_delivery_notes', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên kho"])
def add_delivery_notes():
    if request.method == 'POST':
        ngay_xuat = request.form.get("ngayXuat")
        ingredient_list_json = request.form.get("ingredientList")

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
            flash('Phiếu xuất và chi tiết phiếu xuất đã được lưu thành công!', 'success')
            return redirect(url_for('phieuxuat.add_delivery_notes'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('phieuxuat.add_delivery_notes'))

    ingredients = NguyenLieu.query.filter(NguyenLieu.SoLuongTon != 0).all()
    return render_template('admin/phieuxuat/formNhapPX.html', ingredients=ingredients)

@phieuxuat.route('/export-to-excel/<int:note_id>')
@role_required(["Quản lý","Nhân viên kho"])
def export_to_excel(note_id):
    delivery_note = PHIEUXUAT.query.get_or_404(note_id)
    
    # Lấy thêm thông tin nhân viên
    nhan_vien = NhanVien.query.get(delivery_note.idNV)
    
    delivery_note_detail = (
        db.session.query(CT_PHIEUXUAT, NguyenLieu)
        .join(NguyenLieu, CT_PHIEUXUAT.idNL == NguyenLieu.MaNL)
        .filter(CT_PHIEUXUAT.idXuat == note_id)
        .all()
    )
    
    details = []
    for idx, (ct, nl) in enumerate(delivery_note_detail, 1):
        details.append({
            "STT": idx,
            "Tên nguyên liệu": nl.TenNguyenLieu,
            "Đơn vị tính": nl.DonViTinh,
            "Số lượng": ct.SoLuong,
            "Đơn giá": nl.DonGia,
        })
    
    df = pd.DataFrame(details)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Chi tiết phiếu xuất', index=False, startrow=4)  # Đẩy xuống 1 dòng để chứa thông tin NV
        
        workbook = writer.book
        worksheet = writer.sheets['Chi tiết phiếu xuất']

        basic_format = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'align': 'center',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        
        money_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'right',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        
        number_format = workbook.add_format({
            'align': 'center',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        
        info_format = workbook.add_format({
            'align': 'left',
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'font_name': 'Times New Roman'
        })
        worksheet.merge_range('A1:E1', f'CHI TIẾT PHIẾU XUẤT SỐ {note_id}', title_format)
        
        worksheet.write('A2', f'Ngày xuất: {delivery_note.NgayXuat.strftime("%d-%m-%Y %H:%M")}', info_format)
        worksheet.write('A3', f'Nhân viên xuất: {nhan_vien.HoNV} {nhan_vien.TenNV}', info_format)
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(4, col_num, value, header_format)
        
        for row_num in range(5, len(df) + 5):
            worksheet.write(row_num, 0, df.iloc[row_num-5]['STT'], number_format)               
            worksheet.write(row_num, 1, df.iloc[row_num-5]['Tên nguyên liệu'], basic_format)  
            worksheet.write(row_num, 2, df.iloc[row_num-5]['Đơn vị tính'], number_format)     
            worksheet.write(row_num, 3, df.iloc[row_num-5]['Số lượng'], number_format)       
            worksheet.write(row_num, 4, df.iloc[row_num-5]['Đơn giá'], money_format)          
        
        worksheet.set_column('A:A', 5)   
        worksheet.set_column('B:B', 20)  
        worksheet.set_column('C:C', 10)  
        worksheet.set_column('D:D', 10) 
        worksheet.set_column('E:E', 15)  
        
    output.seek(0)
    
    filename = f'phieu_xuat_{note_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
@phieuxuat.route('/edit_phieuxuat/<int:note_id>', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên kho"])
def edit_phieuxuat(note_id):
    phieu_xuat = PHIEUXUAT.query.get_or_404(note_id)
    
    if request.method == 'POST':
        try:
            with db.session.begin_nested():
                new_date = datetime.strptime(request.form.get('ngayXuat'), '%d/%m/%Y %H:%M')
                phieu_xuat.NgayXuat = new_date

                material_ids = request.form.getlist('material_id[]')
                quantities = request.form.getlist('quantity[]')

                for ct in phieu_xuat.chi_tiet_phieu:
                    ct.nguyen_lieu.SoLuongTon += ct.SoLuong
                    db.session.delete(ct)

                total_amount = 0
                for material_id, quantity in zip(material_ids, quantities):
                    if material_id and quantity:
                        nguyen_lieu = NguyenLieu.query.get(material_id)
                        if nguyen_lieu:
                            quantity = float(quantity)
                            nguyen_lieu.SoLuongTon -= quantity
                            
                            new_detail = CT_PHIEUXUAT(
                                idXuat=note_id,  # Thêm idNhap vào đây
                                idNL=material_id,
                                SoLuong=quantity,
                            )
                            db.session.add(new_detail)  # Thêm trực tiếp vào session

                db.session.commit()
                flash('Cập nhật phiếu xuất thành công!', 'success')
                return redirect(url_for('phieuxuat.edit_phieuxuat', note_id=note_id)) 

        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật phiếu xuất: {str(e)}', 'danger')
            return redirect(url_for('phieuxuat.edit_phieuxuat', note_id=note_id)) 

    # Lấy tất cả nguyên liệu đang có trong chi tiết phiếu xuất
    existing_materials = [ct.nguyen_lieu.MaNL for ct in phieu_xuat.chi_tiet_phieu]
    
    # Lấy danh sách nguyên liệu có tồn kho hoặc đang có trong phiếu xuất
    ingredients = NguyenLieu.query.filter(
        or_(
            NguyenLieu.SoLuongTon != 0,
            NguyenLieu.MaNL.in_(existing_materials)
        )
    ).all()    
    return render_template(
        'admin/phieuxuat/formUpdatePX.html',
        phieu_xuat=phieu_xuat,
        ingredients=ingredients
    )

import os
from website.utils import BackupUtilsPhieuXuat

@phieuxuat.route('/delete_phieuxuat/<int:note_id>', methods=['POST'])
@role_required(["Quản lý","Nhân viên kho"])
def delete_phieuxuat(note_id):
    try:
        with db.session.begin_nested():
            phieu_xuat = PHIEUXUAT.query.get_or_404(note_id)
            
            for ct in phieu_xuat.chi_tiet_phieu:
                ct.nguyen_lieu.SoLuongTon += ct.SoLuong
                db.session.delete(ct)
                
            db.session.delete(phieu_xuat)
            db.session.flush()
            
            BackupUtilsPhieuXuat.backup_to_file(phieu_xuat, current_user)
            
            db.session.commit()
            
        flash('Đã xóa và backup phiếu xuất thành công!', 'success')
        return redirect(url_for('phieuxuat.delivery_notes'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa phiếu xuất: {str(e)}', 'danger')
        return redirect(url_for('phieuxuat.delivery_notes'))

@phieuxuat.route('/view_backups')
@role_required(["Quản lý","Nhân viên kho"])
def view_backups():
    try:
        backups = BackupUtilsPhieuXuat.get_all_backups()
        return render_template('admin/phieuxuat/backups.html', backups=backups)
        
    except Exception as e:
        flash(f'Lỗi khi tải danh sách backup: {str(e)}', 'danger')
        return redirect(url_for('phieuxuat.delivery_notes'))

@phieuxuat.route('/restore_phieuxuat/<string:filename>', methods=['POST'])
@role_required(["Quản lý","Nhân viên kho"]) 
def restore_phieuxuat(filename):
    try:
        if not BackupUtilsPhieuXuat.can_restore(filename):
            flash('Không thể khôi phục phiếu xuất này vì đã quá hạn hoặc đã được khôi phục!', 'warning')
            return redirect(url_for('phieuxuat.view_backups'))

        filepath = os.path.join(BackupUtilsPhieuXuat.BACKUP_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        phieu_xuat = PHIEUXUAT(
            idNV=backup_data['idNV'],
            NgayXuat=datetime.strptime(backup_data['NgayXuat'], '%d-%m-%Y %H:%M:%S'),
        )
        db.session.add(phieu_xuat)
        db.session.flush()

        for ct_data in backup_data['ChiTiet']:
            ct = CT_PHIEUXUAT(
                idXuat=phieu_xuat.SoPhieuXuat,
                idNL=ct_data['idNL'],
                SoLuong=ct_data['SoLuong'],
            )
            db.session.add(ct)
            
            nguyen_lieu = NguyenLieu.query.get(ct_data['idNL'])
            if nguyen_lieu:
                nguyen_lieu.SoLuongTon -= ct_data['SoLuong']  # Trừ số lượng tồn vì là phiếu xuất

        BackupUtilsPhieuXuat.mark_as_restored(filename)
        
        db.session.commit()
        flash('Khôi phục phiếu xuất thành công!', 'success')
        return redirect(url_for('phieuxuat.delivery_notes'))

    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi khôi phục: {str(e)}', 'danger')
        return redirect(url_for('phieuxuat.view_backups'))
