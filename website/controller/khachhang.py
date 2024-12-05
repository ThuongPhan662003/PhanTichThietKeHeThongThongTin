from datetime import datetime
import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from decimal import Decimal
from website import db
from website.webforms import KhachHangForm
from website.webforms import SearchKhachHangForm
from website.models import THAMSO, KhachHang
from unidecode import unidecode
import os

khachhang = Blueprint("khachhang", __name__)

# In danh sách khách hàng/ Thêm khách hàng
@khachhang.route("/", methods=["GET", "POST"])
@login_required
def customer():

    # Tạo khách hàng mới từ form
    form = KhachHangForm()
    formSearch = SearchKhachHangForm()
    formAdd_error = False
    formSearch_error = False

    if request.method == "POST":

        if form.validate_on_submit():

            # Kiểm tra trùng email
            if KhachHang.query.filter_by(Email=form.Email.data).first():
                form.Email.errors.append("Email đã tồn tại")

            # Kiểm tra trùng sdt
            if KhachHang.query.filter_by(SDT=form.SDT.data).first():
                form.SDT.errors.append("SĐT đã tồn tại")

            else:
                kh = KhachHang (
                HoKH=form.HoKH.data,
                TenKH=form.TenKH.data,
                Email=form.Email.data,  
                SDT=form.SDT.data,
                NgayMoThe=datetime.strptime(form.NgayMoThe.data, '%d/%m/%Y').date(),
                DiemTieuDung=form.DiemTieuDung.data,
                DiemTichLuy=form.DiemTichLuy.data,
                LoaiKH=form.LoaiKH.data,
                GioiTinh = form.GioiTinh.data
                )
                db.session.add(kh)
                db.session.commit()

                flash('Thêm khách hàng thành công!', 'success')
                return redirect(url_for('khachhang.customer'))
            
        flash('Thêm khách hàng thất bại', 'danger')
        formAdd_error = True

    # Phân trang danh sách khách hàng
    page = request.args.get('page', 1, type=int) 
    per_page = 8
    pagination = KhachHang.query.order_by(KhachHang.MaKH.desc()).paginate(page=page, per_page=per_page)
    khachhang_list = pagination.items

    return render_template('admin/khachhang/khachhang.html', listKH=khachhang_list,
                           formAdd=form, formSearch=formSearch, pagination=pagination, 
                           formAdd_error=formAdd_error, formSearch_error=formSearch_error)

# Chỉnh sửa thông tin nhân viên
@khachhang.route("/<int:makh>", methods=["GET", "POST"])
@login_required
def khachhang_info(makh):
    kh = KhachHang.query.get_or_404(makh)
    form = KhachHangForm()
    form_error = False

    mess = request.args.get('mess')
    print (mess)
    if mess:
        flash(mess, 'danger')

    if request.method == "POST":
        if form.validate_on_submit():
            
            try: 
                cus1 = KhachHang.query.filter_by(Email=form.Email.data).first()
                cus2 = KhachHang.query.filter_by(SDT=form.SDT.data).first()

                # Kiểm tra trùng mail khách hàng
                if cus1 and cus1.MaKH != kh.MaKH:
                    form.Email.errors.append("Email đã được sử dụng bởi một khách hàng khác")
                    
                # Kiểm tra trùng sdt khách hàng
                elif cus2 and cus2.MaKH != kh.MaKH:
                    form.SDT.errors.append("SĐT đã được sử dụng bởi một khách hàng khác")

                else:
                    kh.HoKH = form.HoKH.data
                    kh.TenKH = form.TenKH.data
                    kh.Email=form.Email.data 
                    kh.SDT=form.SDT.data
                    kh.NgayMoThe=datetime.strptime(form.NgayMoThe.data, '%d/%m/%Y').date()
                    kh.DiemTieuDung=form.DiemTieuDung.data
                    kh.DiemTichLuy=form.DiemTichLuy.data
                    kh.GioiTinh=form.GioiTinh.data

                    tham_so = THAMSO.query.get(1)
                    if kh.DiemTichLuy >= tham_so.Vang:
                        kh.LoaiKH = 'Vàng'
                    elif kh.DiemTichLuy >= tham_so.Bac:
                        kh.LoaiKH = 'Bạc'
                    elif kh.DiemTichLuy >= tham_so.Dong:
                        kh.LoaiKH = 'Đồng'
                    else: kh.LoaiKH = 'Thường'

                    db.session.commit()
                    flash("Thông tin đã được cập nhật thành công!", "success")
                    return redirect(url_for('khachhang.khachhang_info', makh=kh.MaKH))
            except Exception as e:
                flash("Cập nhật thông tin thất bại!", "danger")
                print(str(e))
                db.session.rollback()
                form_error = True
                

    form.HoKH.data = kh.HoKH
    form.TenKH.data = kh.TenKH
    form.NgayMoThe.data = kh.NgayMoThe.strftime('%d/%m/%Y')
    form.Email.data = kh.Email
    form.SDT.data = kh.SDT
    form.DiemTieuDung.data = kh.DiemTieuDung
    form.DiemTichLuy.data = kh.DiemTichLuy
    form.LoaiKH.data = kh.LoaiKH
    form.GioiTinh.data = kh.GioiTinh
    loaikh = unidecode(form.LoaiKH.data)
    return render_template('admin/khachhang/khachhang_info.html', kh=kh, form=form, loaikh=loaikh, form_error=form_error)


# Tìm kiếm danh sách nhân viên
@khachhang.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchKhachHangForm()
    form_KH = KhachHangForm()
    query = KhachHang.query
    formAdd_error = False
    formSearch_error = False

    makh = hokh = tenkh = ngaymothe = loaikh = None

    if request.method == "POST":
        if form.validate_on_submit():
            makh = form.MaKH.data
            hokh = form.HoKH.data
            tenkh = form.TenKH.data
            from datetime import datetime
            ngaymothe = datetime.strptime(form.NgayMoThe.data, '%d/%m/%Y').date() if form.NgayMoThe.data and form.NgayMoThe.data != '' else None
            loaikh = form.LoaiKH.data

            if makh:
                query = query.filter(KhachHang.MaKH == makh)
            if hokh:
                query = query.filter(KhachHang.HoKH == hokh)
            if tenkh:
                query = query.filter(KhachHang.TenKH == tenkh)
            if ngaymothe:
                query = query.filter(KhachHang.NgayMoThe == ngaymothe)
            if loaikh:
                query = query.filter(KhachHang.LoaiKH == loaikh)
        else: formSearch_error = True
    else:
        # Lấy thông tin từ URL nếu không phải POST
        print("Có dô hàm này hong")
        makh = request.args.get('MaKH')
        hokh = request.args.get('HoKH')
        tenkh = request.args.get('TenKH')
        ngaymothe = request.args.get('NgayMoThe')
        loaikh = request.args.get('LoaiKH')

        if makh:
            query = query.filter(KhachHang.MaKH == makh)
        if hokh:
            query = query.filter(KhachHang.HoKH == hokh)
        if tenkh:
            query = query.filter(KhachHang.TenKH == tenkh)
        if ngaymothe:
            query = query.filter(KhachHang.NgayMoThe == ngaymothe)
        if loaikh:
            query = query.filter(KhachHang.LoaiKH == loaikh)

        # Chuyển đổi ngày nếu cần thiết
        if ngaymothe:
            from datetime import datetime
            try:
                ngaymothe = datetime.strptime(ngaymothe, '%d/%m/%Y').date()
            except ValueError:
                ngaymothe = None
    # Phân trang danh sách khách hàng
    page = request.args.get('page', 1, type=int) 
    per_page = 8
    pagination = query.order_by(KhachHang.MaKH.desc()).paginate(page=page, per_page=per_page)
    khachhang_list = pagination.items 

    # Truyền các thông tin tìm kiếm qua URL
    search_params = {
        'MaKH': makh,
        'HoKH': hokh,
        'TenKH': tenkh,
        'NgayMoThe': form.NgayMoThe.data if request.method == "POST" else ngaymothe,
        'LoaiKH': loaikh
    }

    return render_template('admin/khachhang/khachhang.html', listKH=khachhang_list,
                        formAdd=form_KH, formSearch=form, pagination=pagination,
                        formAdd_error=formAdd_error, formSearch_error=formSearch_error, search_params=search_params)


# Xóa khách hàng 
@khachhang.route("/<int:makh>/xoa", methods=["GET", "POST"])
@login_required
def xoa_kh(makh):
    form = KhachHangForm()
    form_error = False
    kh = KhachHang.query.get_or_404(makh)
    loaikh = unidecode(kh.LoaiKH)

    print(kh.hoa_don)
    print(kh.nguoi_dung)
 
    # Kiểm tra khách hàng có hóa đơn hoặc tài khoản không, có thì không được xóa
    if kh.hoa_don or kh.nguoi_dung:
        mess = "Không thể xóa khách hàng do đã có đơn đặt hàng/ tài khoản"
        print(f"Không thể xóa {mess}")
        return redirect(url_for('khachhang.khachhang_info', makh=makh, mess=mess))
    else: 
        try:
            db.session.delete(kh)
            db.session.commit()
            flash('Xóa khách hàng thành công!', 'success')
            return redirect(url_for('khachhang.customer'))
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi xóa khách hàng {e}", 'error')
            mess = f"Lỗi xóa khách hàng {e}"
            return redirect(url_for('khachhang.khachhang_info', makh=makh, mess=mess))

    return redirect(url_for('khachhang.khachhang_info', makh=kh.MaKH))

