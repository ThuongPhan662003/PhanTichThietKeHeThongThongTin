from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date
from datetime import datetime
from website.models import *
from website.models import PHIEUNHAP, CT_PHIEUNHAP
import pandas as pd
from io import BytesIO

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
    page = request.args.get('page', 1, type=int)

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    min_amount = request.form.get('min_amount')
    max_amount = request.form.get('max_amount')
    query_search = request.form.get('query_search', '').strip()
    print(query_search)
    results = get_received_notes(page, start_date=start_date, end_date=end_date, min_amount=min_amount, max_amount=max_amount, query_search=query_search)

    return render_template(
        'admin/phieunhap/phieunhap.html',
        results=results,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount
    )

@phieunhap.route('/export-to-excel/<int:note_id>')
@login_required
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