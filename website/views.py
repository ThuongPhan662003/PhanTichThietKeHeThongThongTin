# from .models import *
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json

views = Blueprint("views", __name__)


# @views.route("/functions")
# def get_functions():
#     functions = ChucNang.query.all()  # Truy vấn tất cả các chúc năng
#     results = [
#         {"MaCN": function.MaCN, "TenManHinh": function.TenManHinh}
#         for function in functions
#     ]
#     return jsonify(results)


# @views.route("/users")
# def get_users():
#     users = NguoiDung.query.all()
#     results = [{"id": user.MaND, "name": user.UserName} for user in users]
#     return jsonify(results)


# @views.route("/tables")
# def get_tables():
#     tables = Ban.query.all()
#     results = [
#         {
#             "idBan": table.MaBan,
#             "name": table.TenBan,
#             "ViTri": table.ViTri,
#             "TrangThai": table.TrangThai,
#         }
#         for table in tables
#     ]
#     return jsonify(results)


# @views.route("/orders")
# def get_orders():
#     orders = DonDatHang.query.all()
#     results = []
#     for order in orders:
#         results.append(
#             {
#                 "idDDH": order.MaDDH,
#                 "NgayDat": order.NgayDat,
#                 "TrangThai": order.TrangThai,
#                 "ThanhTien": str(order.ThanhTien),  # Chuyển đổi thành chuỗi nếu cần
#             }
#         )
#     return jsonify(results)


# @views.route("/staffs")
# def get_staffs():
#     staffs = NhanVien.query.all()
#     results = [
#         {
#             "idNV": staff.MaNV,
#             "HoTen": staff.HoNV + " " + staff.TenNV,
#             "SDT": staff.SDT,
#             "Email": staff.Email,
#             "TinhTrang": staff.TinhTrang,
#         }
#         for staff in staffs
#     ]
#     return jsonify(results)


# @views.route("/dishes")
# def get_dishes():
#     dishes = MonAn.query.all()
#     results = [
#         {
#             "idMA": dish.MaMA,
#             "TenMonAn": dish.TenMonAn,
#             "DonGia": str(dish.DonGia),
#             "Loai": dish.Loai,
#             "TrangThai": dish.TrangThai,
#         }
#         for dish in dishes
#     ]
#     return jsonify(results)


# @views.route("/orderdetails")
# def get_orderdetails():
#     orderdetails = CT_DonDatHang.query.all()
#     results = [
#         {
#             "idDDH": orderdetail.idDDH,
#             "idBan": orderdetail.idBan,
#             "SoLuong": orderdetail.SoLuong,  # Nếu bạn có trường số lượng
#             "Gia": str(orderdetail.Gia),  # Nếu bạn có trường giá
#         }
#         for orderdetail in orderdetails
#     ]
#     return jsonify(results)


# @views.route("/customers")
# def get_customers():
#     customers = KhachHang.query.all()
#     results = [
#         {
#             "idKH": customer.MaKH,
#             "HoTen": customer.HoKH + " " + customer.TenKH,
#             "SDT": customer.SDT,
#             "Email": customer.Email,
#             "DiemTieuDung": customer.DiemTieuDung,
#             "DiemTichLuy": customer.DiemTichLuy,
#         }
#         for customer in customers
#     ]
#     return jsonify(results)


# @views.route("/bills")
# def get_bills():
#     bills = HoaDon.query.all()
#     results = [
#         {
#             "idHD": bill.MaHD,
#             "NgayXuat": bill.NgayXuat,
#             "TongTien": str(bill.TongTien),
#             "TrangThai": bill.TrangThai,
#             "DiemCong": bill.DiemCong,
#             "DiemTru": bill.DiemTru,
#         }
#         for bill in bills
#     ]
#     return jsonify(results)


# @views.route("/", methods=["GET", "POST"])
# # @login_required
# def home():
#     return render_template("home.html")


# @views.route("/homepage", methods=["GET", "POST"])
# def homepage():
#     return render_template("home_test.html")
