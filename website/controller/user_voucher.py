from flask import render_template, Blueprint
from flask_login import login_required
from datetime import datetime
from website.models import LOAIVOUCHER

user_voucher = Blueprint("user_voucher", __name__)


@user_voucher.route("/")
def hien_thi_voucher():
    # Lấy danh sách voucher còn hiệu lực và có số lượng còn lại
    now = datetime.now()
    vouchers = LOAIVOUCHER.query.filter(
        LOAIVOUCHER.SoLuongConLai > 0,
        LOAIVOUCHER.NgayBatDau <= now,
        LOAIVOUCHER.NgayKetThuc >= now,
        LOAIVOUCHER.An == False,
    ).all()
    return render_template("user/voucher/hien_thi_voucher.html", vouchers=vouchers)
