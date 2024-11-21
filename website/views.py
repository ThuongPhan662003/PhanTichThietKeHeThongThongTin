from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import *
from . import db
import json


views = Blueprint("views", __name__)


@views.route("/functions")
def get_functions():
    functions = ChucNang.query.all()  # Truy vấn tất cả các chúc năng
    results = [
        {"MaCN": function.MaCN, "TenManHinh": function.TenManHinh}
        for function in functions
    ]
    return jsonify(results)


@views.route("/users")
def get_users():
    users = NguoiDung.query.all()
    results = [{"id": user.MaND, "name": user.UserName} for user in users]
    return jsonify(results)


@views.route("/tables")
def get_tables():
    tables = Ban.query.all()
    results = [
        {
            "idBan": table.MaBan,
            "name": table.TenBan,
            "ViTri": table.ViTri,
            "TrangThai": table.TrangThai,
        }
        for table in tables
    ]
    return jsonify(results)


@views.route("/orders")
def get_orders():
    orders = DonDatHang.query.all()
    results = []
    for order in orders:
        results.append(
            {
                "idDDH": order.MaDDH,
                "NgayDat": order.NgayDat,
                "TrangThai": order.TrangThai,
                "ThanhTien": str(order.ThanhTien),  # Chuyển đổi thành chuỗi nếu cần
            }
        )
    return jsonify(results)


@views.route("/staffs")
def get_staffs():
    staffs = NhanVien.query.all()
    results = [
        {
            "idNV": staff.MaNV,
            "HoTen": staff.HoNV + " " + staff.TenNV,
            "SDT": staff.SDT,
            "Email": staff.Email,
            "TinhTrang": staff.TinhTrang,
        }
        for staff in staffs
    ]
    return jsonify(results)


@views.route("/dishes")
def get_dishes():
    dishes = MonAn.query.all()
    results = [
        {
            "idMA": dish.MaMA,
            "TenMonAn": dish.TenMonAn,
            "DonGia": str(dish.DonGia),
            "Loai": dish.Loai,
            "TrangThai": dish.TrangThai,
        }
        for dish in dishes
    ]
    return jsonify(results)


@views.route("/orderdetails")
def get_orderdetails():
    orderdetails = CT_DonDatHang.query.all()
    results = [
        {
            "idDDH": orderdetail.idDDH,
            "idBan": orderdetail.idBan,
            "SoLuong": orderdetail.SoLuong,  # Nếu bạn có trường số lượng
            "Gia": str(orderdetail.Gia),  # Nếu bạn có trường giá
        }
        for orderdetail in orderdetails
    ]
    return jsonify(results)


@views.route("/customers")
def get_customers():
    customers = KhachHang.query.all()
    results = [
        {
            "idKH": customer.MaKH,
            "HoTen": customer.HoKH + " " + customer.TenKH,
            "SDT": customer.SDT,
            "Email": customer.Email,
            "DiemTieuDung": customer.DiemTieuDung,
            "DiemTichLuy": customer.DiemTichLuy,
        }
        for customer in customers
    ]
    return jsonify(results)


@views.route("/bills")
def get_bills():
    bills = HoaDon.query.all()
    results = [
        {
            "idHD": bill.MaHD,
            "NgayXuat": bill.NgayXuat,
            "TongTien": str(bill.TongTien),
            "TrangThai": bill.TrangThai,
            "DiemCong": bill.DiemCong,
            "DiemTru": bill.DiemTru,
        }
        for bill in bills
    ]
    return jsonify(results)

# Route để xem dữ liệu bảng PHANQUYEN
@views.route('/phanquyen')
#@login_required
def get_phanquyen():
    phanquyen = PHANQUYEN.query.all()
    result = [{'idNND': pq.idNND, 'idCN': pq.idCN} for pq in phanquyen]
    return jsonify(result)

# Route để xem dữ liệu bảng PHIEUXUAT
@views.route('/phieuxuat', methods=['GET'])
#@login_required
def get_phieuxuat():
    phieuxuat = PHIEUXUAT.query.all()
    result = [{'SoPhieuXuat': px.SoPhieuXuat, 'idNV': px.idNV, 'NgayXuat': px.NgayXuat} for px in phieuxuat]
    return jsonify(result)

# Route để xem dữ liệu bảng CT_PHIEUXUAT
@views.route('/ct_phieuxuat', methods=['GET'])
#@login_required
def get_ct_phieuxuat():
    ct_phieuxuat = CT_PHIEUXUAT.query.all()
    result = [{'idXuat': ct.idXuat, 'idNL': ct.idNL, 'SoLuong': ct.SoLuong} for ct in ct_phieuxuat]
    return jsonify(result)

# Route để xem dữ liệu bảng PHIEUNHAP
@views.route('/phieunhap', methods=['GET'])
#@login_required
def get_phieunhap():
    phieunhap = PHIEUNHAP.query.all()
    result = [{'SoPhieuNhap': pn.SoPhieuNhap, 'idNV': pn.idNV, 'NgayNhap': pn.NgayNhap} for pn in phieunhap]
    return jsonify(result)

# Route để xem dữ liệu bảng CT_PHIEUNHAP
@views.route('/ct_phieunhap', methods=['GET'])
#@login_required
def get_ct_phieunhap():
    ct_phieunhap = CT_PHIEUNHAP.query.all()
    result = [{'idNhap': ct.idNhap, 'idNL': ct.idNL, 'SoLuong': ct.SoLuong, 'ThanhTien': ct.ThanhTien} for ct in ct_phieunhap]
    return jsonify(result)

# Route để xem dữ liệu bảng LOAIVOUCHER
@views.route('/loaivoucher', methods=['GET'])
#@login_required
def get_loaivoucher():
    loaivoucher = LOAIVOUCHER.query.all()
    result = [{
        'MaLoaiVoucher': lv.MaLoaiVoucher,
        'TenLoaiVoucher': lv.TenLoaiVoucher,
        'PhanTram': lv.PhanTram,
        'MoTa': lv.MoTa,
        'SoLuong': lv.SoLuong,
        'SoLuongConLai': lv.SoLuongConLai,
        'LoaiKH': lv.LoaiKH,
        'NgayBatDau': lv.NgayBatDau,
        'NgayKetThuc': lv.NgayKetThuc,
        'GiamToiDa': lv.GiamToiDa,
        'An': lv.An
    } for lv in loaivoucher]
    return jsonify(result)

# Route để xem dữ liệu bảng VOUCHER
@views.route('/voucher', methods=['GET'])
#@login_required
def get_voucher():
    voucher = VOUCHER.query.all()
    result = [{'CodeVoucher': v.CodeVoucher, 'idLoaiVoucher': v.idLoaiVoucher, 'TrangThai': v.TrangThai} for v in voucher]
    return jsonify(result)

# Route để xem dữ liệu bảng CT_VOUCHER
@views.route('/ct_voucher', methods=['GET'])
#@login_required
def get_ct_voucher():
    ct_voucher = CT_VOUCHER.query.all()
    result = [{'CodeVoucher': ct.CodeVoucher, 'idHD': ct.idHD} for ct in ct_voucher]
    return jsonify(result)

# Route để xem dữ liệu bảng THAMSO
@views.route('/thamso', methods=['GET'])
#@login_required
def get_thamso():
    thamso = THAMSO.query.all()
    result = [{
        'id': ts.id,
        'TuoiToiDa': ts.TuoiToiDa,
        'TuoiToiThieu': ts.TuoiToiThieu,
        'DiemChiaTichLuy': ts.DiemChiaTichLuy,
        'SoVoucherApDung_Ngay': ts.SoVoucherApDung_Ngay,
        'SoNguyenLieuNhap': ts.SoNguyenLieuNhap,
        'PhanTramGiamVoucherToiDa': ts.PhanTramGiamVoucherToiDa,
        'Vang': ts.Vang,
        'Bac': ts.Bac,
        'Dong': ts.Dong,
        'PhanTramThue': ts.PhanTramThue
    } for ts in thamso]
    return jsonify(result)


@views.route("/homepage")
def homepage():
    return render_template("user/homepage.html")


@views.route("/admin-home")
def admin_home():
    return render_template("admin/admin-home.html")







