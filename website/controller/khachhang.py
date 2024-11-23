import random
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date
from datetime import datetime
from website.models import *
from website.models import NguoiDung, NhomNguoiDung

# from website.webforms import
import json

khachhang = Blueprint("khachhang", __name__)


@khachhang.route("/<int:khachhang_id>")
def khachhang_detail(khachhang_id):
    khachhang = KhachHang.query.get_or_404(khachhang_id)

    # Giả sử bạn có một trường GioiTinh trong database
    gender = int.from_bytes(khachhang.GioiTinh, byteorder="big")  # "Nam" hoặc "Nữ"
    print(gender)
    # Chọn avatar ID dựa trên giới tính
    if gender == 1:
        avatar_id = random.randint(1, 50)  # ID từ 1 đến 50 cho nam
    else:
        avatar_id = random.randint(51, 100)  # ID từ 51 đến 100 cho nữ

    # URL avatar
    avatar_url = f"https://avatar.iran.liara.run/public/{avatar_id}"

    return render_template(
        "user/khachhang/khachhang.html",
        khachhang=khachhang,
        avatar_url=avatar_url,
    )
