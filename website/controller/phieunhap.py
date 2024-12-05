from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date
from datetime import datetime
from website.role import role_required
from website.models import *
from website.models import PHIEUNHAP, CT_PHIEUNHAP
import pandas as pd
from io import BytesIO
from decimal import Decimal

phieunhap = Blueprint("phieunhap", __name__)

# hàm hỗ trợ phân trang
def get_received_notes(page, start_date=None, end_date=None, min_amount=None, max_amount=None, query_search=None):
    query = PHIEUNHAP.query.with_entities(
        PHIEUNHAP.SoPhieuNhap,
        PHIEUNHAP.NgayNhap,
        PHIEUNHAP.TongTien, 
        func.concat(NhanVien.HoNV, ' ', NhanVien.TenNV).label("NhanVienNhap")
    ).join(PHIEUNHAP.nhan_vien) 
    if query_search:
        query = query.filter(func.concat(NhanVien.HoNV, ' ', NhanVien.TenNV).ilike(f'%{query_search}%'))

    if start_date or end_date:
        if start_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(cast(PHIEUNHAP.NgayNhap, Date) >= start_date_dt)
        if end_date:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(cast(PHIEUNHAP.NgayNhap, Date) <= end_date_dt)

    if min_amount or max_amount:
        if min_amount:
            query = query.filter(PHIEUNHAP.TongTien >= float(min_amount))
        if max_amount:
            query = query.filter(PHIEUNHAP.TongTien <= float(max_amount))

    return query.order_by(PHIEUNHAP.NgayNhap.desc()).paginate(page=page, per_page=9)

@phieunhap.route('/received_notes', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên kho"])
def received_notes():
    page = request.args.get('page', 1, type=int)

    results = get_received_notes(page)

    return render_template('admin/phieunhap/phieunhap.html', results=results)

@phieunhap.route('/received_note/<int:note_id>', methods=['GET'])
@role_required(["Quản lý","Nhân viên kho"])
def received_note_detail(note_id):
    received_note = PHIEUNHAP.query.get_or_404(note_id)

    details = [{
        "stt": idx + 1,
        "ten_nguyen_lieu": ct.nguyen_lieu.TenNguyenLieu,
        "don_vi_tinh": ct.nguyen_lieu.DonViTinh, 
        "so_luong": ct.SoLuong,
        "don_gia": ct.nguyen_lieu.DonGia,
        "thanh_tien": ct.ThanhTien
    } for idx, ct in enumerate(received_note.chi_tiet_phieu)]
    can_change = received_note.NgayNhap.date() == datetime.now().date()

    tong_tien = sum(ct.ThanhTien for ct in received_note.chi_tiet_phieu)

    return render_template(
        'admin/phieunhap/ctphieunhap.html',
        received_note=received_note,
        details=details,
        tong_tien=tong_tien,
        can_change=can_change
    )

@phieunhap.route('/filter_received_notes', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên kho"])
def filter_received_notes():
    page = request.args.get('page', 1, type=int)

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    min_amount = request.form.get('min_amount')
    max_amount = request.form.get('max_amount')
    query_search = request.form.get('query_search', '').strip()
    results = get_received_notes(page, start_date=start_date, end_date=end_date, min_amount=min_amount, max_amount=max_amount, query_search=query_search)

    return render_template(
        'admin/phieunhap/phieunhap.html',
        results=results,
        query_search=query_search,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount
    )

@phieunhap.route('/export-to-excel/<int:note_id>')
@role_required(["Quản lý","Nhân viên kho"])
def export_to_excel(note_id):
    received_note = PHIEUNHAP.query.get_or_404(note_id)
    
    nhan_vien = NhanVien.query.get(received_note.idNV)
    
    received_note_detail = (
        db.session.query(CT_PHIEUNHAP, NguyenLieu)
        .join(NguyenLieu, CT_PHIEUNHAP.idNL == NguyenLieu.MaNL)
        .filter(CT_PHIEUNHAP.idNhap == note_id)
        .all()
    )
    
    tong_tien = sum(ct.ThanhTien for ct, nl in received_note_detail)
    details = []
    for idx, (ct, nl) in enumerate(received_note_detail, 1):
        details.append({
            "STT": idx,
            "Tên nguyên liệu": nl.TenNguyenLieu,
            "Đơn vị tính": nl.DonViTinh,
            "Số lượng": ct.SoLuong,
            "Đơn giá": nl.DonGia,
            "Thành tiền": ct.ThanhTien
        })
    
    df = pd.DataFrame(details)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Chi tiết phiếu nhập', index=False, startrow=4)  
        
        workbook = writer.book
        worksheet = writer.sheets['Chi tiết phiếu nhập']

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
        worksheet.merge_range('A1:F1', f'CHI TIẾT PHIẾU NHẬP SỐ {note_id}', title_format)
        
        worksheet.write('A2', f'Ngày nhập: {received_note.NgayNhap.strftime("%d-%m-%Y %H:%M")}', info_format)
        worksheet.write('A3', f'Nhân viên nhập: {nhan_vien.HoNV} {nhan_vien.TenNV}', info_format)
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(4, col_num, value, header_format)
        
        for row_num in range(5, len(df) + 5):
            worksheet.write(row_num, 0, df.iloc[row_num-5]['STT'], number_format)               
            worksheet.write(row_num, 1, df.iloc[row_num-5]['Tên nguyên liệu'], basic_format)  
            worksheet.write(row_num, 2, df.iloc[row_num-5]['Đơn vị tính'], number_format)     
            worksheet.write(row_num, 3, df.iloc[row_num-5]['Số lượng'], number_format)       
            worksheet.write(row_num, 4, df.iloc[row_num-5]['Đơn giá'], money_format)          
            worksheet.write(row_num, 5, df.iloc[row_num-5]['Thành tiền'], money_format)       
        
        worksheet.set_column('A:A', 5)  
        worksheet.set_column('B:B', 20) 
        worksheet.set_column('C:C', 10) 
        worksheet.set_column('D:D', 10)  
        worksheet.set_column('E:E', 15) 
        worksheet.set_column('F:F', 15)  
        
        last_row = len(df) + 5  
        total_format = workbook.add_format({
            'bold': True,
            'num_format': '#,##0',
            'align': 'right',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        
        total_label_format = workbook.add_format({
            'bold': True,
            'align': 'right',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 12
        })
        
        worksheet.merge_range(f'A{last_row}:E{last_row}', 'Tổng tiền:', total_label_format)
        worksheet.write(last_row - 1, 5, f'=SUM(F5:F{last_row-1})', total_format)
        
    output.seek(0)
    
    filename = f'phieu_nhap_{note_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@phieunhap.route('/edit_phieunhap/<int:note_id>', methods=['GET', 'POST'])
@role_required(["Quản lý","Nhân viên kho"])
def edit_phieunhap(note_id):
    phieu_nhap = PHIEUNHAP.query.get_or_404(note_id)
    
    if request.method == 'POST':
        try:
            with db.session.begin_nested():
                new_date = datetime.strptime(request.form.get('ngayNhap'), '%d/%m/%Y %H:%M')
                phieu_nhap.NgayNhap = new_date

                material_ids = request.form.getlist('material_id[]')
                quantities = request.form.getlist('quantity[]')

                for ct in phieu_nhap.chi_tiet_phieu:
                    ct.nguyen_lieu.SoLuongTon -= ct.SoLuong
                    db.session.delete(ct)

                total_amount = 0
                for material_id, quantity in zip(material_ids, quantities):
                    if material_id and quantity:
                        nguyen_lieu = NguyenLieu.query.get(material_id)
                        if nguyen_lieu:
                            quantity = float(quantity)
                            nguyen_lieu.SoLuongTon += quantity
                            
                            thanh_tien = quantity * float(nguyen_lieu.DonGia)
                            new_detail = CT_PHIEUNHAP(
                                idNhap=note_id,  # Thêm idNhap vào đây
                                idNL=material_id,
                                SoLuong=quantity,
                                ThanhTien=thanh_tien
                            )
                            db.session.add(new_detail)  # Thêm trực tiếp vào session
                            total_amount += thanh_tien

                phieu_nhap.TongTien = total_amount
                db.session.commit()
                flash('Cập nhật phiếu nhập thành công!', 'success')
                return redirect(url_for('phieunhap.edit_phieunhap', note_id=note_id)) 

        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật phiếu nhập: {str(e)}', 'danger')
            return redirect(url_for('phieunhap.edit_phieunhap', note_id=note_id)) 

    ingredients = NguyenLieu.query.filter(
        ~NguyenLieu.MaNL.in_(
            db.session.query(CT_PHIEUNHAP.idNL).filter_by(idNhap=note_id)
        )
    ).all()
    
    return render_template(
        'admin/phieunhap/formUpdatePN.html',
        phieu_nhap=phieu_nhap,
        ingredients=ingredients
    )

@phieunhap.route('/delete_phieunhap/<int:note_id>', methods=['POST'])
@role_required(["Quản lý","Nhân viên kho"])
def delete_phieunhap(note_id):
    try:
        with db.session.begin_nested():
            phieu_nhap = PHIEUNHAP.query.get_or_404(note_id)
            
            for ct in phieu_nhap.chi_tiet_phieu:
                ct.nguyen_lieu.SoLuongTon -= ct.SoLuong
                db.session.delete(ct)
                
            db.session.delete(phieu_nhap)
            db.session.flush()
            
            BackupUtils.backup_to_file(phieu_nhap, current_user)
            
            db.session.commit()
            
        flash('Đã xóa và backup phiếu nhập thành công!', 'success')
        return redirect(url_for('phieunhap.received_notes'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa phiếu nhập: {str(e)}', 'danger')
        return redirect(url_for('phieunhap.received_notes'))

import os, json
from website.utils import BackupUtils

@phieunhap.route('/view_backups')
@role_required(["Quản lý","Nhân viên kho"])
def view_backups():
    try:
        backups = BackupUtils.get_all_backups()
        return render_template('admin/phieunhap/backups.html', backups=backups)
        
    except Exception as e:
        flash(f'Lỗi khi tải danh sách backup: {str(e)}', 'danger')
        return redirect(url_for('nguyenlieu.ingredients'))

@phieunhap.route('/restore_phieunhap/<string:filename>', methods=['POST'])
@role_required(["Quản lý","Nhân viên kho"]) 
def restore_phieunhap(filename):
    try:
        if not BackupUtils.can_restore(filename):
            flash('Không thể khôi phục phiếu nhập này vì đã quá hạn hoặc đã được khôi phục!', 'warning')
            return redirect(url_for('phieunhap.view_backups'))

        filepath = os.path.join(BackupUtils.BACKUP_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        phieu_nhap = PHIEUNHAP(
            idNV=backup_data['idNV'],
            NgayNhap=datetime.strptime(backup_data['NgayNhap'], '%d-%m-%Y %H:%M:%S'),
            TongTien=backup_data['TongTien']
        )
        db.session.add(phieu_nhap)
        db.session.flush()

        for ct_data in backup_data['ChiTiet']:
            ct = CT_PHIEUNHAP(
                idNhap=phieu_nhap.SoPhieuNhap,
                idNL=ct_data['idNL'],
                SoLuong=ct_data['SoLuong'],
                ThanhTien=ct_data['ThanhTien']
            )
            db.session.add(ct)
            
            nguyen_lieu = NguyenLieu.query.get(ct_data['idNL'])
            if nguyen_lieu:
                nguyen_lieu.SoLuongTon += ct_data['SoLuong']

        BackupUtils.mark_as_restored(filename)
        
        db.session.commit()
        flash('Khôi phục phiếu nhập thành công!', 'success')
        return redirect(url_for('phieunhap.received_notes'))

    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi khôi phục: {str(e)}', 'danger')
        return redirect(url_for('phieunhap.view_backups'))
