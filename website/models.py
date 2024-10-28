from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

__all__ = [
    "NguoiDung",
    "KhachHang",
    "DonDatHang",
    "CT_DonDatHang",
    "NhanVien",
    "NhomNguoiDung",
    "LoaiBan",
    "Ban",
    "NguyenLieu",
    "MonAn",
    "HoaDon",
    "ChucNang",
]


# class ChucNang(db.Model):
#     __tablename__ = "ChucNang"

#     MaCN = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     TenManHinh = db.Column(db.String(50), nullable=False, unique=True)

#     def __repr__(self):
#         return f"<ChucNang(MaCN={self.MaCN}, TenManHinh='{self.TenManHinh}')>"


# class CT_MonAn(db.Model):
#     __tablename__ = "CT_MonAn"

#     idDDH = db.Column(db.Integer, db.ForeignKey("DonDatHang.MaDDH"), primary_key=True)
#     idMA = db.Column(db.Integer, db.ForeignKey("MonAn.MaMA"), primary_key=True)
#     SoLuong = db.Column(db.Integer, nullable=False)
#     GiaMon = db.Column(db.Text, nullable=False)
#     GhiChu = db.Column(db.String(200), nullable=True)

#     don_dat_hang = db.relationship("DonDatHang", backref="ct_mon_an")
#     mon_an = db.relationship("MonAn", backref="ct_mon_an")

#     @db.validates("SoLuong")
#     def validate_so_luong(self, key, value):
#         if value <= 0:
#             raise ValueError("Số lượng phải lớn hơn 0.")
#         return value

#     @db.validates("GiaMon")
#     def validate_gia_mon(self, key, value):
#         if value < 1000:
#             raise ValueError("Giá món phải lớn hơn hoặc bằng 1000.")
#         return value


# class KhachHang(db.Model):
#     __tablename__ = "KhachHang"

#     MaKH = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     HoKH = db.Column(db.String(30), nullable=False)
#     TenKH = db.Column(db.String(10), nullable=False)
#     SDT = db.Column(db.String(10), nullable=False, unique=True)
#     Email = db.Column(db.String(100), nullable=False, unique=True)
#     NgayMoThe = db.Column(db.Date, nullable=False)
#     DiemTieuDung = db.Column(db.Integer, nullable=False)
#     DiemTichLuy = db.Column(db.Integer, nullable=False)
#     idNguoiDung = db.Column(
#         db.Integer,
#         db.ForeignKey("NguoiDung.MaND"),
#         nullable=False,
#         unique=True,
#     )
#     LoaiKH = db.Column(db.String(10), nullable=False)
#     nguoi_dung = db.relationship("NguoiDung", back_populates="khach_hang")
#     hoa_don = db.relationship("HoaDon", backref="khach_hang")

#     @db.validates("DiemTieuDung")
#     def validate_diem_tieu_dung(self, key, value):
#         if value < 0:
#             raise ValueError("Điểm tiêu dùng không được nhỏ hơn 0.")
#         return value

#     @db.validates("DiemTichLuy")
#     def validate_diem_tich_luy(self, key, value):
#         if value < 0:
#             raise ValueError("Điểm tích lũy không được nhỏ hơn 0.")
#         return value

#     @db.validates("SDT")
#     def validate_sdt(self, key, value):
#         if not value.isdigit():
#             raise ValueError("SDT chỉ được phép chứa số.")
#         return value


# class HoaDon(db.Model):
#     __tablename__ = "HoaDon"

#     MaHD = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     idKH = db.Column(db.Integer, db.ForeignKey("KhachHang.MaKH"), nullable=False)
#     idDDH = db.Column(
#         db.Integer,
#         db.ForeignKey("DonDatHang.MaDDH"),
#         nullable=False,
#     )
#     idNV = db.Column(db.Integer, db.ForeignKey("NhanVien.MaNV"), nullable=False)
#     NgayXuat = db.Column(db.DateTime, default=func.now())
#     TongTienGiam = db.Column(db.Integer, nullable=False)
#     TongTien = db.Column(db.Integer, nullable=False)
#     TrangThai = db.Column(db.Boolean, default=None)
#     TienThue = db.Column(db.Text, nullable=False)
#     DiemCong = db.Column(db.Integer, nullable=False)
#     DiemTru = db.Column(db.Integer, nullable=False)

#     @db.validates("DiemCong")
#     def validate_diem_cong(self, key, value):
#         if value < 0:
#             raise ValueError("Điểm cộng không được nhỏ hơn 0.")
#         return value

#     @db.validates("DiemTru")
#     def validate_diem_tru(self, key, value):
#         if value < 0:
#             raise ValueError("Điểm trừ không được nhỏ hơn 0.")
#         return value


# class CT_DonDatHang(db.Model):
#     __tablename__ = "CT_DonDatHang"

#     idDDH = db.Column(
#         db.Integer,
#         db.ForeignKey("DonDatHang.MaDDH"),
#         primary_key=True,
#     )
#     idBan = db.Column(db.Integer, db.ForeignKey("Ban.MaBan"), primary_key=True)


# class NhanVien(db.Model):
#     __tablename__ = "NhanVien"

#     MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     HoNV = db.Column(db.String(30), nullable=False)
#     TenNV = db.Column(db.String(10), nullable=False)
#     NgaySinh = db.Column(db.Date, nullable=False)
#     CCCD = db.Column(db.String(12), nullable=False, unique=True)
#     Email = db.Column(db.String(100), nullable=False, unique=True)
#     SDT = db.Column(db.String(10), nullable=False, unique=True)
#     idNguoiDung = db.Column(db.Integer, db.ForeignKey("NguoiDung.MaND"), nullable=False)
#     TinhTrang = db.Column(db.Boolean, nullable=False, default=False)
#     NgayVaoLam = db.Column(db.Date, nullable=False)
#     hoa_don = db.relationship("HoaDon", backref="nhan_vien")
#     nguoi_dung = db.relationship("NguoiDung", backref="nhan_vien")

#     @db.validates("CCCD")
#     def validate_cccd(self, key, value):
#         if not value.isdigit() or len(value) != 12:
#             raise ValueError("CCCD phải là một chuỗi số 12 chữ số!")
#         return value

#     @db.validates("SDT")
#     def validate_sdt(self, key, value):
#         if not value.isdigit() or len(value) != 10:
#             raise ValueError("SDT phải là một chuỗi số 10 chữ số!")
#         return value


# class DonDatHang(db.Model):
#     __tablename__ = "DonDatHang"

#     MaDDH = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     NgayDat = db.Column(db.Date, nullable=False)
#     TrangThai = db.Column(db.String(20), nullable=False)
#     Loai = db.Column(db.Boolean, nullable=False)
#     GioDen = db.Column(db.Time, nullable=False)
#     ThoiLuong = db.Column(db.Integer)
#     idNV = db.Column(db.Integer, db.ForeignKey("NhanVien.MaNV"), nullable=False)
#     ThanhTien = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
#     ct_don_dat_hang = db.relationship("CT_DonDatHang", backref="don_dat_hang")
#     hoa_don = db.relationship("HoaDon", backref="don_dat_hang")

#     @db.validates("TrangThai")
#     def validate_trang_thai(self, key, value):
#         valid_trang_thai = ["Đã hủy", "Đang chế biến", "Đã hoàn thành", "Chưa bắt đầu"]
#         if value not in valid_trang_thai:
#             raise ValueError(f"{value} không phải là trạng thái hợp lệ!")
#         return value


# class MonAn(db.Model):
#     __tablename__ = "MonAn"

#     MaMA = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     TenMonAn = db.Column(db.String(100), nullable=False, unique=True)
#     DonGia = db.Column(db.Text, nullable=False)
#     Loai = db.Column(db.String(100), nullable=False)
#     TrangThai = db.Column(db.String(20), nullable=False)
#     HinhAnh = db.Column(db.String(200), nullable=True)

#     @db.validates("TrangThai")
#     def validate_trang_thai(self, key, value):
#         valid_trang_thai = ["Còn phục vụ", "Ngừng phục vụ", "Tạm hết"]
#         if value not in valid_trang_thai:
#             raise ValueError(f"{value} không phải là trạng thái hợp lệ!")
#         return value


# class NguyenLieu(db.Model):
#     __tablename__ = "NguyenLieu"

#     MaNL = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     TenNguyenLieu = db.Column(db.String(100), nullable=False, unique=True)
#     DonGia = db.Column(db.Numeric(15, 2), nullable=False)
#     DonViTinh = db.Column(db.String(5), nullable=False)
#     SoLuongTon = db.Column(db.Integer, nullable=False)

#     @db.validates("DonViTinh")
#     def validate_don_vi_tinh(self, key, value):
#         valid_units = ["kg", "lít", "hộp", "túi", "chai", "thùng", "cái", "quả"]
#         if value not in valid_units:
#             raise ValueError(f"{value} không phải là đơn vị tính hợp lệ!")
#         return value

#     @db.validates("SoLuongTon")
#     def validate_so_luong_ton(self, key, value):
#         if value < 0:
#             raise ValueError("Số lượng tồn không được âm!")
#         return value


# class LoaiBan(db.Model):
#     __tablename__ = "LoaiBan"
#     MaLB = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     TenLoaiBan = db.Column(db.String(100))
#     ban = db.relationship("Ban", backref="loai_ban", lazy=True)


# class Ban(db.Model):
#     __tablename__ = "Ban"

#     MaBan = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     TenBan = db.Column(db.String(30), nullable=False, unique=True)
#     ViTri = db.Column(db.String(10), nullable=False)
#     TrangThai = db.Column(db.String(30), nullable=False)
#     idLoaiBan = db.Column(db.Integer, db.ForeignKey("LoaiBan.MaLB"), nullable=False)

#     ct_don_dat_hang = db.relationship("CT_DonDatHang", backref="ban", lazy=True)

#     @db.validates("TrangThai")
#     def validate_trang_thai(self, key, value):
#         valid_trang_thai = ["Còn trống", "Đang dùng bữa", "Đã đặt trước"]
#         if value not in valid_trang_thai:
#             raise ValueError(f"{value} không phải là trạng thái hợp lệ!")
#         return value


# class NhomNguoiDung(db.Model):
#     __tablename__ = "NhomNguoiDung"
#     MaNND = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     TenNhomNguoiDung = db.Column(db.String(100))
#     nguoi_dung = db.relationship("NguoiDung", backref="nhom_nguoi_dung", lazy=True)


# class NguoiDung(db.Model, UserMixin):
#     __tablename__ = "NguoiDung"
#     MaND = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     UserName = db.Column(db.String(150), nullable=False)
#     TrangThai = db.Column(db.Integer)
#     MatKhau = db.Column(db.String(150))
#     VerifyCode = db.Column(db.String(150))
#     idNND = db.Column(db.Integer, db.ForeignKey("NhomNguoiDung.MaNND"), nullable=False)

#     khach_hang = db.relationship(
#         "KhachHang", back_populates="nguoi_dung", uselist=False
#     )

#     def get_id(self):
#         return self.MaND
