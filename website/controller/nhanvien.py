from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from decimal import Decimal
from website import db
from website.models import NhanVien
from website.webforms import NhanVienForm   
from website.webforms import SearchNhanVienForm


nhanvien = Blueprint("nhanvien", __name__)

# In danh sách nhân viên/ Thêm nhân viên
@nhanvien.route("/", methods=["GET", "POST"])
@login_required
def employee():

    # Tạo nhân viên mới từ form
    form = NhanVienForm()
    formSearch = SearchNhanVienForm()
    formAdd_error = False
    formSearch_error = False

    if request.method == "POST":

        if form.validate_on_submit():

            # Kiểm tra trùng email
            if NhanVien.query.filter_by(Email=form.Email.data).first():
                form.Email.errors.append("Email đã tồn tại")

            # Kiểm tra trùng sdt
            elif NhanVien.query.filter_by(SDT=form.SDT.data).first():
                form.SDT.errors.append("SĐT đã tồn tại")
            
            # Kiểm tra trùng cccd
            elif NhanVien.query.filter_by(CCCD=form.CCCD.data).first():
                form.CCCD.errors.append("CDDD đã tồn tại")

            else:
                nv = NhanVien(
                HoNV=form.HoNV.data,
                TenNV=form.TenNV.data,
                CCCD=form.CCCD.data,
                Email=form.Email.data,
                SDT=form.SDT.data,
                NgaySinh=datetime.strptime(form.NgaySinh.data, '%d/%m/%Y').date(),
                NgayVaoLam=datetime.strptime(form.NgayVaoLam.data, '%d/%m/%Y').date(),
                TinhTrang=form.TinhTrang.data,
                GioiTinh = form.GioiTinh.data
                )
                db.session.add(nv)
                db.session.commit()

                flash('Thêm nhân viên thành công!', 'success')
                return redirect(url_for('nhanvien.employee'))
        
        flash('Thêm nhân viên thất bại', 'error')
        formAdd_error = True

    # Phân trang danh sách khách hàng
    page = request.args.get('page', 1, type=int) 
    per_page = 5
    pagination = NhanVien.query.order_by(NhanVien.MaNV.desc()).paginate(page=page, per_page=per_page)
    nhanvien_list = pagination.items
    return render_template('admin/nhanvien/nhanvien.html', listNV=nhanvien_list,
                        formAdd=form, formSearch=formSearch, pagination=pagination,
                        formAdd_error=formAdd_error, formSearch_error=formSearch_error)

# Chỉnh sửa thông tin nhân viên
@nhanvien.route("/<int:manv>", methods=["GET", "POST"])
@login_required
def nhanvien_info(manv):
    nv = NhanVien.query.get_or_404(manv)
    form = NhanVienForm()
    form_error = False

    if request.method == "POST":
        if form.validate_on_submit():

            cus1 = NhanVien.query.filter_by(Email=form.Email.data).first()
            cus2 = NhanVien.query.filter_by(SDT=form.SDT.data).first()
            cus3 = NhanVien.query.filter_by(CCCD=form.CCCD.data).first()
            
            # Kiểm tra trùng mail khách hàng
            if cus1 and cus1.MaNV != nv.MaNV:
                form.Email.errors.append("Email đã được sử dụng bởi một khách hàng khác")
                
            # Kiểm tra trùng sdt khách hàng
            elif cus2 and cus2.MaNV != nv.MaNV:
                form.SDT.errors.append("SĐT đã được sử dụng bởi một khách hàng khác")
            
            # Kiểm tra trùng sdt khách hàng
            elif cus3 and cus3.MaNV != nv.MaNV:
                form.CCCD.errors.append("CCCD đã được sử dụng bởi một khách hàng khác")

            else:
                nv.HoNV = form.HoNV.data
                nv.TenNV = form.TenNV.data
                nv.CCCD = form.CCCD.data
                nv.Email = form.Email.data
                nv.SDT = form.SDT.data
                nv.NgaySinh = datetime.strptime(form.NgaySinh.data, '%d/%m/%Y').date()
                nv.NgayVaoLam = datetime.strptime(form.NgayVaoLam.data, '%d/%m/%Y').date()
                nv.GioiTinh = form.GioiTinh.data  

                db.session.commit()
                flash("Thông tin đã được cập nhật thành công!", "success")
                return redirect(url_for('nhanvien.nhanvien_info', manv=nv.MaNV))
        else: flash("Cập nhật thông tin thất bại!", "error")
        form_error = True

    form.HoNV.data = nv.HoNV
    form.TenNV.data = nv.TenNV
    form.NgaySinh.data = nv.NgaySinh.strftime('%d/%m/%Y')
    form.CCCD.data = nv.CCCD
    form.Email.data = nv.Email
    form.SDT.data = nv.SDT
    form.NgayVaoLam.data = nv.NgayVaoLam.strftime('%d/%m/%Y')
    form.TinhTrang.data = nv.TinhTrang
    form.GioiTinh.data = nv.GioiTinh
    return render_template('admin/nhanvien/nhanvien_info.html', nv=nv, form=form, form_error=form_error)
        
# Ẩn nhân viên (tinhtrang = 1)
@nhanvien.route("/<int:manv>/an", methods=["GET", "POST"])
@login_required
def an_nhanvien(manv):
    nv = NhanVien.query.get_or_404(manv)
    if request.method == "POST":
        nv.TinhTrang = 1
        db.session.commit()
        flash('Cập nhật tình trạng nhân viên thành công!', 'success')

    return redirect(url_for('nhanvien.nhanvien_info', manv=nv.MaNV))


# Tìm kiếm danh sách nhân viên
@nhanvien.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchNhanVienForm()
    form_NV = NhanVienForm()
    query = NhanVien.query
    formAdd_error = False
    formSearch_error = False

    if request.method == "POST":
        if form.validate_on_submit():
            manv = form.MaNV.data
            honv = form.HoNV.data
            tennv = form.TenNV.data
            ngayvaolam = form.NgayVaoLam.data
            tinhtrang = form.TinhTrang.data

            if manv:
                query = query.filter(NhanVien.MaNV == manv)
            if honv:
                query = query.filter(NhanVien.HoNV == honv)
            if tennv:
                query = query.filter(NhanVien.TenNV == tennv)
            if ngayvaolam:
                query = query.filter(NhanVien.NgayVaoLam == ngayvaolam)
            if tinhtrang:
                query = query.filter(NhanVien.TinhTrang == tinhtrang)
        else: formSearch_error = True
    
    # Phân trang danh sách khách hàng
    page = request.args.get('page', 1, type=int) 
    per_page = 3
    pagination = query.paginate(page=page, per_page=per_page)
    nhanvien_list = pagination.items 

    return render_template('admin/nhanvien/nhanvien.html', listNV=nhanvien_list,
                        formAdd=form_NV, formSearch=form, pagination=pagination,
                        formAdd_error=formAdd_error, formSearch_error=formSearch_error)