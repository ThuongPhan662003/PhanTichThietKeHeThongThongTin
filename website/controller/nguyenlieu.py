from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from decimal import Decimal
from website import db
from sqlalchemy import or_, and_
from datetime import datetime
from website.models import *
from website.models import PHIEUNHAP, CT_PHIEUNHAP
from website.webforms import NguyenLieuForm 
import json
import pandas as pd
from io import BytesIO

nguyenlieu = Blueprint("nguyenlieu", __name__)

@nguyenlieu.route("/ingredients", methods=["GET", "POST"])
@nguyenlieu.route("/ingredients/edit/<int:id>", methods=["GET", "POST"])
@login_required
def ingredients(id=None):
    page = request.args.get('page', 1, type=int)
    
    ingredient = NguyenLieu.query.get(id) if id else None
    form = NguyenLieuForm(obj=ingredient)  
    if form.validate_on_submit():
        try:
            # thêm
            if ingredient is None:
                if not form.NgayNhap.data:
                    flash('Ngày nhập không được để trống!', 'danger')
                    return redirect(url_for('nguyenlieu.ingredients'))

                ingredient_name = form.TenNguyenLieu.data
                existing_ingredient = NguyenLieu.query.filter_by(TenNguyenLieu=ingredient_name).first()
                if existing_ingredient:
                    flash('Tên nguyên liệu đã tồn tại!', 'danger')
                    return redirect(url_for('nguyenlieu.ingredients'))

                new_ingredient = NguyenLieu(
                    TenNguyenLieu=form.TenNguyenLieu.data,
                    DonGia=form.DonGia.data,
                    DonViTinh=form.DonViTinh.data,
                    SoLuongTon=form.SoLuongTon.data
                )
                db.session.add(new_ingredient)
                db.session.flush() 

                nhan_vien = NhanVien.query.filter_by(idNguoiDung=current_user.MaND).first()
                if nhan_vien is None:
                    flash('Không tìm thấy nhân viên!', 'danger')
                    db.session.rollback()
                    return redirect(url_for('nguyenlieu.ingredients'))
                
                existing_phieunhap = PHIEUNHAP.query.filter_by(NgayNhap=form.NgayNhap.data, idNV=nhan_vien.MaNV).first()
                if existing_phieunhap:
                    new_phieunhap = existing_phieunhap
                    flash('Phiếu nhập đã tồn tại cho ngày này, sẽ được cập nhật thông tin.', 'info')
                else:
                    new_phieunhap = PHIEUNHAP(
                        NgayNhap=form.NgayNhap.data,
                        idNV=nhan_vien.MaNV
                    )
                    db.session.add(new_phieunhap)
                    db.session.flush()  

                thanh_tien = form.SoLuongTon.data * form.DonGia.data
                new_chitietphieunhap = CT_PHIEUNHAP(
                    SoLuong=form.SoLuongTon.data,
                    ThanhTien=thanh_tien,
                    idNL=new_ingredient.MaNL,
                    idNhap=new_phieunhap.SoPhieuNhap
                )
                db.session.add(new_chitietphieunhap)
                new_phieunhap.TongTien = Decimal((new_phieunhap.TongTien or 0)) + thanh_tien
                message = 'Nguyên liệu mới và thông tin phiếu nhập đã được thêm thành công!'
            
            else:
                ingredient_name = form.TenNguyenLieu.data
                existing_ingredient = NguyenLieu.query.filter(
                    NguyenLieu.TenNguyenLieu == ingredient_name,
                    NguyenLieu.MaNL != id 
                ).first()
                if existing_ingredient:
                    flash('Tên nguyên liệu đã tồn tại!', 'danger')
                    return redirect(url_for('nguyenlieu.ingredients'))

                ingredient.TenNguyenLieu = ingredient_name
                ingredient.DonGia = form.DonGia.data
                ingredient.DonViTinh = form.DonViTinh.data
                message = 'Cập nhật nguyên liệu thành công!'
            
            db.session.commit()
            flash(message, 'success')
            return redirect(url_for('nguyenlieu.ingredients'))

        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm hoặc cập nhật nguyên liệu: {str(e)}', 'danger')
            return redirect(url_for('nguyenlieu.ingredients', id=id if id else None))
   
    ingredients = NguyenLieu.query.order_by(NguyenLieu.MaNL.desc()).paginate(page=page, per_page=8)
    return render_template(
        'admin/nguyenlieu/nguyenlieu.html', 
        ingredients=ingredients, 
        form=form, 
        ingredient=ingredient, 
        endpoint='nguyenlieu.ingredients'
    )

@nguyenlieu.route('/filter_ingredients', methods=['GET', 'POST'])
@login_required
def filter_ingredients():
    form = NguyenLieuForm()
    page = request.args.get('page', 1, type=int)
    units = request.form.getlist('units') or request.args.getlist('units')
    price_min = request.form.get('price_min') or request.args.get('price_min')
    price_max = request.form.get('price_max') or request.args.get('price_max')
    stock = request.form.getlist('stock') or request.args.getlist('stock')
    
    query = NguyenLieu.query
    
    if units:
        query = query.filter(NguyenLieu.DonViTinh.in_(units))
    
    if price_min:
        query = query.filter(NguyenLieu.DonGia >= float(price_min))
    if price_max:
        query = query.filter(NguyenLieu.DonGia <= float(price_max))
    
    # Tạo một danh sách các điều kiện lọc
    filters = []

    if 'out_of_stock' in stock:
        filters.append(NguyenLieu.SoLuongTon == 0)
    if 'under_10' in stock:
        filters.append(and_(NguyenLieu.SoLuongTon >= 1, NguyenLieu.SoLuongTon < 10))
    if '10_20' in stock:
        filters.append(and_(NguyenLieu.SoLuongTon >= 10, NguyenLieu.SoLuongTon <= 20))
    if 'over_20' in stock:
        filters.append(NguyenLieu.SoLuongTon > 20)

    # Áp dụng tất cả các bộ lọc với or_
    if filters:
        query = query.filter(or_(*filters))
    
    filtered_ingredients = query.order_by(NguyenLieu.MaNL.desc()).paginate(page=page, per_page=9)
    
    return render_template('admin/nguyenlieu/nguyenlieu.html', form=form, ingredients=filtered_ingredients, selected_units=units, selected_stock=stock, price_min=price_min, price_max=price_max,  endpoint='nguyenlieu.filter_ingredients')

@nguyenlieu.route('/search_ingredients', methods=['GET'])
@login_required
def search_ingredients():
    form = NguyenLieuForm()
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int) 
    if query:
        ingredients = NguyenLieu.query.filter(NguyenLieu.TenNguyenLieu.ilike(f'%{query}%')).paginate(page=page, per_page=9)
    else:
        ingredients = NguyenLieu.query.order_by(NguyenLieu.MaNL.desc()).paginate(page=page, per_page=8)
    return render_template('admin/nguyenlieu/nguyenlieu.html', form=form, ingredients=ingredients, query=query,  endpoint='nguyenlieu.search_ingredients')


@nguyenlieu.route('/delete_ingredient/<int:id>')
@login_required
def delete_ingredient(id):
    try:
        ingredient = NguyenLieu.query.get_or_404(id)
        
        db.session.delete(ingredient)
        db.session.commit()
        
        flash('Nguyên liệu đã được xóa thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa nguyên liệu: {str(e)}', 'danger')
    
    return redirect(url_for('nguyenlieu.ingredients'))

    
@nguyenlieu.route('/add_ingredients', methods=['GET', 'POST'])
@login_required
def add_ingredients():
    if request.method == 'POST':
        ngay_nhap = request.form.get("ngayNhap")
        ingredient_list_json = request.form.get("ingredientList")
        total_amount = Decimal(0) 
        try:
            ingredients = json.loads(ingredient_list_json)
            existing_phieu_nhap = PHIEUNHAP.query.filter_by(
                NgayNhap= datetime.strptime(ngay_nhap, '%d-%m-%Y %H:%M'),
                idNV=current_user.MaND
            ).first()

            if existing_phieu_nhap:
                new_phieu_nhap = existing_phieu_nhap
            else:
                new_phieu_nhap = PHIEUNHAP(
                    idNV=current_user.MaND,
                    NgayNhap=datetime.strptime(ngay_nhap, '%d-%m-%Y %H:%M'),
                    TongTien=Decimal(0)
                )
                db.session.add(new_phieu_nhap)
                db.session.flush() 

            for item in ingredients:
                ten_nguyen_lieu = item.get("tenNguyenLieu")
                so_luong = item.get("soLuong")

                ingredient = NguyenLieu.query.filter_by(TenNguyenLieu=ten_nguyen_lieu).first()
                if ingredient:
                    don_gia = ingredient.DonGia
                    thanh_tien = don_gia * so_luong
                    total_amount += thanh_tien

                    existing_ct_phieu_nhap = CT_PHIEUNHAP.query.filter_by(
                        idNhap=new_phieu_nhap.SoPhieuNhap,
                        idNL=ingredient.MaNL
                    ).first()

                    if existing_ct_phieu_nhap:
                        existing_ct_phieu_nhap.SoLuong += so_luong
                        existing_ct_phieu_nhap.ThanhTien += float(thanh_tien)
                    else:
                        new_ct_phieu_nhap = CT_PHIEUNHAP(
                            idNhap=new_phieu_nhap.SoPhieuNhap,
                            idNL=ingredient.MaNL,
                            SoLuong=so_luong,
                            ThanhTien=thanh_tien
                        )
                        db.session.add(new_ct_phieu_nhap)

                    ingredient.SoLuongTon += int(so_luong)

            new_phieu_nhap.TongTien = (Decimal(new_phieu_nhap.TongTien) or Decimal(0)) + total_amount

            db.session.commit()
            flash('Phiếu nhập và chi tiết phiếu nhập đã được lưu/cập nhật thành công!', 'success')
            return redirect(url_for('nguyenlieu.add_ingredients'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('nguyenlieu.add_ingredients'))

    ingredients = NguyenLieu.query.all()
    return render_template('admin/nguyenlieu/formNLDaCo.html', ingredients=ingredients)



@nguyenlieu.route('/import-ingredients', methods=['POST'])
@login_required
def import_ingredients():
    if 'excel_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('nguyenlieu.ingredients'))

    file = request.files['excel_file']
    if file.filename == '':
        flash('Bạn chưa chọn file nào! Vui lòng chọn lại!', 'danger')
        return redirect(url_for('nguyenlieu.ingredients'))

    if file and file.filename.endswith(('.xls', '.xlsx')):
        try:
            df = pd.read_excel(file)
            new_count = 0  # Đếm số nguyên liệu thêm mới
            update_count = 0  # Đếm số nguyên liệu được cập nhật

            for _, row in df.iterrows():
                ten_nguyen_lieu = row['Tên nguyên liệu']
                don_vi_tinh = row['Đơn vị tính']
                don_gia = row['Đơn giá']

                existing_ingredient = NguyenLieu.query.filter_by(TenNguyenLieu=ten_nguyen_lieu).first()

                if not existing_ingredient:
                    new_ingredient = NguyenLieu(
                        TenNguyenLieu=ten_nguyen_lieu,
                        DonViTinh=don_vi_tinh,
                        DonGia=don_gia,
                        SoLuongTon=0  
                    )
                    db.session.add(new_ingredient)
                    new_count += 1
                else:
                    existing_ingredient.DonGia = don_gia
                    existing_ingredient.DonViTinh = don_vi_tinh
                    update_count += 1
                    
            db.session.commit()
            
            message = f'Hoàn tất! Đã thêm {new_count} nguyên liệu mới'
            if update_count > 0:
                message += f' và cập nhật {update_count} nguyên liệu'
            flash(message, 'success')

        except KeyError as e:
            db.session.rollback()
            flash('Lỗi: Tên cột không đúng định dạng. Vui lòng kiểm tra lại file mẫu!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm danh sách nguyên liệu: {str(e)}', 'danger')
    else:
        flash('Định dạng file không hợp lệ. Vui lòng tải lên file excel!', 'danger')

    return redirect(url_for('nguyenlieu.ingredients'))

@nguyenlieu.route('/download-template')
@login_required
def download_template():
    sample_data = {
        'Tên nguyên liệu': ['Ví dụ: Cà phê', 'Ví dụ: Sữa'],
        'Đơn vị tính': ['kg', 'lít'],
        'Đơn giá': [100000, 50000]
    }
    df = pd.DataFrame(sample_data)
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='NguyenLieu')
        worksheet = writer.sheets['NguyenLieu']
        
        header_format = writer.book.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        worksheet.set_column('A:A', 30)  
        worksheet.set_column('B:B', 15)  
        worksheet.set_column('C:C', 15)  
            
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='mau_nhap_nguyen_lieu.xlsx'
    )