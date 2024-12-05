from flask import render_template, Blueprint
from flask_login import login_required, current_user
from website.models import *
from website.role import role_required

user_bill = Blueprint("user_bill", __name__)


@user_bill.route("/")
@role_required(["Khách hàng"])
def xem_hoa_don():
    # Lấy danh sách hóa đơn theo idKH của khách hàng hiện tại
    cus = KhachHang.query.filter(KhachHang.idNguoiDung == current_user.get_id()).first()
    hoa_dons = HoaDon.query.filter_by(idKH=cus.get_MaKH()).all()
    return render_template("user/hoadon/xem_hoa_don.html", hoa_dons=hoa_dons)


@user_bill.route("/<int:mahd>")
def chi_tiet_hoa_don(mahd):
    # Lấy hóa đơn theo mã hóa đơn
    cus = KhachHang.query.filter(KhachHang.idNguoiDung == current_user.get_id()).first()
    hoa_don = HoaDon.query.filter_by(MaHD=mahd, idKH=cus.get_MaKH()).first()
    if not hoa_don:
        return "Không tìm thấy hóa đơn hoặc bạn không có quyền xem hóa đơn này", 404

    # Lấy chi tiết đơn đặt hàng
    ct_ddh = CT_DonDatHang.query.filter_by(idDDH=hoa_don.idDDH).all()
    return render_template(
        "user/hoadon/chi_tiet_hoa_don.html", hoa_don=hoa_don, ct_ddh=ct_ddh
    )
