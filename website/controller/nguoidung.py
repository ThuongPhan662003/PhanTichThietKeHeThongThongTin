from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date
from datetime import datetime
from website.models import *
from website.models import NguoiDung, NhomNguoiDung
# from website.webforms import  
import json

nguoidung = Blueprint("nguoidung", __name__)

@nguoidung.route("/")
def account():
    username = request.cookies.get('username') 
    if not username.isdigit():
        user = NguoiDung.query.filter(NguoiDung.UserName == username).first()
        nhan_vien = user.nhan_vien
        if not nhan_vien:
            print("No one here")
        else:
            print(nhan_vien.HoNV)
            return render_template("nguoidung/nguoidung.html", 
                               user = user, employee = nhan_vien)
    else: flash("Bạn đang đăng nhập vào tài khoản khách hàng", 'message')
        

@nguoidung.route("/<int:khachhang_id>")

def khachhang_detail(khachhang_id):
    # Lấy thông tin khách hàng theo ID
    khachhang = KhachHang.query.get_or_404(khachhang_id)

    # Truyền dữ liệu vào template
    return render_template("user/nguoidung/nguoidung.html", khachhang=khachhang)
