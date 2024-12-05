from flask import render_template, Blueprint
from flask_login import current_user, login_required
from datetime import datetime
from website.models import LOAIVOUCHER, KhachHang
from website.role import role_required

user_voucher = Blueprint("user_voucher", __name__)


@user_voucher.route("/")
@role_required(["Khách hàng"])
def hien_thi_voucher():
    # Lấy danh sách voucher còn hiệu lực và có số lượng còn lại
    now = datetime.now()
    cus_type = KhachHang.query.filter(KhachHang.idNguoiDung == current_user.get_id()).first().get_LoaiKH()
    vouchers = LOAIVOUCHER.query.filter(
        LOAIVOUCHER.SoLuongConLai > 0,
        LOAIVOUCHER.NgayBatDau <= now,
        LOAIVOUCHER.NgayKetThuc >= now,
        LOAIVOUCHER.An == False,
        LOAIVOUCHER.LoaiKH == cus_type
    ).all()
    return render_template("user/voucher/hien_thi_voucher.html", vouchers=vouchers)
