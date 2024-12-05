from datetime import date, time
import datetime
from email.policy import default
import json
import re
import secrets
import string

from flask import flash, url_for

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Boolean,
)
from datetime import datetime, date, time


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
    "PHANQUYEN",
    "PHIEUXUAT",
    "CT_PHIEUXUAT",
    "PHIEUNHAP",
    "CT_PHIEUNHAP",
    "LOAIVOUCHER",
    "VOUCHER",
    "CT_VOUCHER",
    "THAMSO",
]


class ChucNang(db.Model):
    __tablename__ = "ChucNang"

    MaCN = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenManHinh = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<ChucNang(MaCN={self.MaCN}, TenManHinh='{self.TenManHinh}')>"

    def __init__(self, tenmanhinh):
        self.TenManHinh = tenmanhinh
    def setTenManHinh(self,TenManHinh):
        self.TenManHinh = TenManHinh


class CT_MonAn(db.Model):
    __tablename__ = "CT_MonAn"

    idDDH = db.Column(db.Integer, db.ForeignKey("DonDatHang.MaDDH"), primary_key=True)
    idMA = db.Column(db.Integer, db.ForeignKey("MonAn.MaMA"), primary_key=True)
    idBan = db.Column(db.Integer, db.ForeignKey("Ban.MaBan"), primary_key=True)
    SoLuong = db.Column(db.Integer, nullable=False)
    GhiChu = db.Column(db.String(200), nullable=True)

    don_dat_hang = db.relationship("DonDatHang", backref="ct_mon_an")
    mon_an = db.relationship("MonAn", backref="ct_mon_an")

    # Getters
    def get_idDDH(self):
        return self.idDDH

    def get_idMA(self):
        return self.idMA

    def get_idBan(self):
        return self.idBan

    def get_SoLuong(self):
        return self.SoLuong

    def get_GhiChu(self):
        return self.GhiChu

    # Setters
    def set_idDDH(self, idDDH):
        self.idDDH = idDDH

    def set_idMA(self, idMA):
        self.idMA = idMA

    def set_idBan(self, idBan):
        self.idBan = idBan

    def set_SoLuong(self, so_luong):
        self.SoLuong = so_luong

    def set_GhiChu(self, ghi_chu):
        self.GhiChu = ghi_chu

    @db.validates("SoLuong")
    def validate_so_luong(self, key, value):
        if value <= 0:
            raise ValueError("Số lượng phải lớn hơn 0.")
        return value

    @db.validates("GiaMon")
    def validate_gia_mon(self, key, value):
        if value < 1000:
            raise ValueError("Giá món phải lớn hơn hoặc bằng 1000.")
        return value

    def to_dict(self):
        """Chuyển đổi đối tượng thành dictionary để serialize."""
        return {
            "idDDH": self.idDDH,
            "idMA": self.idMA,
            "idBan": self.idBan,
            "SoLuong": self.SoLuong,
            "GiaMon": self.GiaMon,
            "GhiChu": self.GhiChu,
        }

    def to_json(self):
        """Chuyển đổi đối tượng thành JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)


class KhachHang(db.Model):
    __tablename__ = "KhachHang"

    MaKH = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoKH = db.Column(db.String(30), nullable=False)
    TenKH = db.Column(db.String(10), nullable=False)
    SDT = db.Column(db.String(10), nullable=False, unique=True)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    NgayMoThe = db.Column(db.Date, nullable=False)
    DiemTieuDung = db.Column(db.Integer, nullable=False)
    DiemTichLuy = db.Column(db.Integer, nullable=False)
    GioiTinh = db.Column(db.Integer, nullable=True)
    idNguoiDung = db.Column(
        db.Integer,
        db.ForeignKey("NguoiDung.MaND"),
        unique=True,
    )
    LoaiKH = db.Column(db.String(10), nullable=False)
    nguoi_dung = db.relationship("NguoiDung", back_populates="khach_hang")
    hoa_don = db.relationship("HoaDon", backref="khach_hang", uselist=False)

    def __init__(
        self,
        HoKH,
        TenKH,
        SDT,
        Email,
        NgayMoThe,
        DiemTieuDung,
        DiemTichLuy,
        idNguoiDung,
        LoaiKH="Thường",
    ):

        self.HoKH = HoKH
        self.TenKH = TenKH
        self.SDT = SDT
        self.Email = Email
        self.NgayMoThe = NgayMoThe
        self.DiemTieuDung = DiemTieuDung
        self.DiemTichLuy = DiemTichLuy
        self.idNguoiDung = idNguoiDung
        self.LoaiKH = LoaiKH

    # Getters
    def get_MaKH(self):
        return self.MaKH

    def get_HoKH(self):
        return self.HoKH

    def get_TenKH(self):
        return self.TenKH

    def get_SDT(self):
        return self.SDT

    def get_Email(self):
        return self.Email

    def get_NgayMoThe(self):
        return self.NgayMoThe

    def get_DiemTieuDung(self):
        return self.DiemTieuDung

    def get_DiemTichLuy(self):
        return self.DiemTichLuy

    def get_GioiTinh(self):
        return self.GioiTinh

    def get_idNguoiDung(self):
        return self.idNguoiDung

    def get_LoaiKH(self):
        return self.LoaiKH

    # Setters
    def set_HoKH(self, ho_kh):
        self.HoKH = ho_kh

    def set_TenKH(self, ten_kh):
        self.TenKH = ten_kh

    def set_SDT(self, sdt):
        self.SDT = sdt

    def set_Email(self, email):
        self.Email = email

    def set_NgayMoThe(self, ngay_mo_the):
        self.NgayMoThe = ngay_mo_the

    def set_DiemTieuDung(self, diem_tieu_dung):
        self.DiemTieuDung = diem_tieu_dung

    def set_DiemTichLuy(self, diem_tich_luy):
        self.DiemTichLuy = diem_tich_luy

    def set_GioiTinh(self, gioi_tinh):
        self.GioiTinh = gioi_tinh

    def set_idNguoiDung(self, id_nguoi_dung):
        self.idNguoiDung = id_nguoi_dung

    def set_LoaiKH(self, loai_kh):
        self.LoaiKH = loai_kh

    def getHoTen(self):
        return self.HoKH + " " + self.TenKH



class HoaDon(db.Model):
    __tablename__ = "HoaDon"

    MaHD = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idKH = db.Column(db.Integer, db.ForeignKey("KhachHang.MaKH"), nullable=False)
    idDDH = db.Column(
        db.Integer,
        db.ForeignKey("DonDatHang.MaDDH"),
        nullable=False,
    )
    idNV = db.Column(db.Integer, db.ForeignKey("NhanVien.MaNV"), nullable=False)
    NgayXuat = db.Column(db.DateTime, default=func.now())
    TongTienGiam = db.Column(db.Integer, nullable=False)
    TongTien = db.Column(db.Integer, nullable=False)
    TrangThai = db.Column(db.Boolean, default=None)
    TienThue = db.Column(db.Integer, nullable=False)
    DiemCong = db.Column(db.Integer, nullable=False)
    DiemTru = db.Column(db.Integer, nullable=False)
    PhuongThucThanhToan = db.Column(db.Integer, nullable=True)
    don_dat_hang = db.relationship("DonDatHang", backref="hoa_don", uselist=False)

    @db.validates("DiemCong")
    def validate_diem_cong(self, key, value):
        if value < 0:
            raise ValueError("Điểm cộng không được nhỏ hơn 0.")
        return value

    @db.validates("DiemTru")
    def validate_diem_tru(self, key, value):
        if value < 0:
            raise ValueError("Điểm trừ không được nhỏ hơn 0.")
        return value

    def to_dict(self):
        """Chuyển đổi đối tượng thành dictionary để serialize."""
        return {
            "MaHD": self.MaHD,
            "idKH": self.idKH,
            "idDDH": self.idDDH,
            "idNV": self.idNV,
            "NgayXuat": self.NgayXuat.isoformat() if self.NgayXuat else None,
            "TongTienGiam": self.TongTienGiam,
            "TongTien": self.TongTien,
            "TrangThai": self.TrangThai,
            "TienThue": self.TienThue,
            "DiemCong": self.DiemCong,
            "DiemTru": self.DiemTru,
            "PhuongThucThanhToan": self.PhuongThucThanhToan
        }

    def to_json(self):
        """Chuyển đổi đối tượng thành JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)

    # Getters
    def get_MaHD(self):
        return self.MaHD

    def get_idKH(self):
        return self.idKH

    def get_idDDH(self):
        return self.idDDH

    def get_idNV(self):
        return self.idNV

    def get_NgayXuat(self):
        return self.NgayXuat

    def get_TongTienGiam(self):
        return self.TongTienGiam

    def get_TongTien(self):
        return self.TongTien

    def get_TrangThai(self):
        return self.TrangThai

    def get_TienThue(self):
        return self.TienThue

    def get_DiemCong(self):
        return self.DiemCong

    def get_DiemTru(self):
        return self.DiemTru

    # Setters
    def set_idKH(self, id_kh):
        self.idKH = id_kh

    def set_idDDH(self, id_ddh):
        self.idDDH = id_ddh

    def set_idNV(self, id_nv):
        self.idNV = id_nv

    def set_NgayXuat(self, ngay_xuat):
        self.NgayXuat = ngay_xuat

    def set_TongTienGiam(self, tong_tien_giam):
        self.TongTienGiam = tong_tien_giam

    def set_TongTien(self, tong_tien):
        self.TongTien = tong_tien

    def set_TrangThai(self, trang_thai):
        self.TrangThai = trang_thai

    def set_TienThue(self, tien_thue):
        self.TienThue = tien_thue

    def set_DiemCong(self, diem_cong):
        self.DiemCong = diem_cong

    def set_DiemTru(self, diem_tru):
        self.DiemTru = diem_tru


class CT_DonDatHang(db.Model):
    __tablename__ = "CT_DDH"

    idDDH = db.Column(
        db.Integer,
        db.ForeignKey("DonDatHang.MaDDH"),
        primary_key=True,
    )
    idBan = db.Column(db.Integer, db.ForeignKey("Ban.MaBan"), primary_key=True)
    ThanhTien = db.Column(db.Integer, nullable=False, default=0)

    # Getters
    def get_idDDH(self):
        return self.idDDH

    def get_idBan(self):
        return self.idBan

    def get_ThanhTien(self):
        return self.ThanhTien

    # Setters
    def set_idDDH(self, id_ddh):
        self.idDDH = id_ddh

    def set_idBan(self, id_ban):
        self.idBan = id_ban

    def set_ThanhTien(self, thanh_tien):
        self.ThanhTien = thanh_tien


class NhanVien(db.Model):
    __tablename__ = "NhanVien"

    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoNV = db.Column(db.String(30), nullable=False)
    TenNV = db.Column(db.String(10), nullable=False)
    NgaySinh = db.Column(db.Date, nullable=False)
    CCCD = db.Column(db.String(12), nullable=False, unique=True)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    SDT = db.Column(db.String(10), nullable=False, unique=True)
    idNguoiDung = db.Column(db.Integer, db.ForeignKey("NguoiDung.MaND"))
    TinhTrang = db.Column(db.Integer, nullable=False)
    NgayVaoLam = db.Column(db.Date, nullable=False)
    hoa_don = db.relationship("HoaDon", backref="nhan_vien")
    nguoi_dung = db.relationship("NguoiDung", back_populates="nhan_vien")
    GioiTinh = db.Column(db.Integer, nullable=False)

    @db.validates("CCCD")
    def validate_cccd(self, key, value):
        if not value.isdigit() or len(value) != 12:
            raise ValueError("CCCD phải là một chuỗi số 12 chữ số!")
        return value

    @db.validates("SDT")
    def validate_sdt(self, key, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("SDT phải là một chuỗi số 10 chữ số!")
        return value

    def getHoTenNV(self):
        return self.HoNV + " " + self.TenNV

    def set_idNguoiDung(self, idNguoiDung):
        self.idNguoiDung = idNguoiDung

    def get_idNguoiDung(self):
        return self.idNguoiDung


    def get_MaNV(self):
        return self.MaNV

    def get_HoNV(self):
        return self.HoNV

    def get_TenNV(self):
        return self.TenNV

    def get_NgaySinh(self):
        return self.NgaySinh

    def get_CCCD(self):
        return self.CCCD

    def get_Email(self):
        return self.Email

    def get_SDT(self):
        return self.SDT

    def get_TinhTrang(self):
        return self.TinhTrang

    def get_NgayVaoLam(self):
        return self.NgayVaoLam

    def get_GioiTinh(self):
        return self.GioiTinh

    # Setters
    def set_HoNV(self, ho_nv):
        self.HoNV = ho_nv

    def set_TenNV(self, ten_nv):
        self.TenNV = ten_nv

    def set_NgaySinh(self, ngay_sinh):
        self.NgaySinh = ngay_sinh

    def set_CCCD(self, cccd):
        self.CCCD = cccd

    def set_Email(self, email):
        self.Email = email

    def set_SDT(self, sdt):
        self.SDT = sdt

    def set_TinhTrang(self, tinh_trang):
        self.TinhTrang = tinh_trang

    def set_NgayVaoLam(self, ngay_vao_lam):
        self.NgayVaoLam = ngay_vao_lam

    def set_GioiTinh(self, gioi_tinh):
        self.GioiTinh = gioi_tinh


from datetime import datetime, date, time



class DonDatHang(db.Model):
    __tablename__ = "DonDatHang"

    MaDDH = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NgayDat = db.Column(db.Date, nullable=False)
    TrangThai = db.Column(db.String(20), nullable=False)
    Loai = db.Column(db.Integer, nullable=False, default=0)
    GioDen = db.Column(db.Time, nullable=False)
    ThoiLuong = db.Column(db.Float)
    SoLuongNguoi = db.Column(db.Integer)
    idNV = db.Column(db.Integer, db.ForeignKey("NhanVien.MaNV"), nullable=False)
    ThanhTien = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    GhiChu = db.Column(db.String(1000))
    ct_don_dat_hang = db.relationship(
        "CT_DonDatHang", backref="don_dat_hang", lazy=True
    )
    # hoa_don = db.relationship("HoaDon", back_populates="don_dat_hang")

    # def __init__(
    #     self,
    #     NgayDat,
    #     SoLuongNguoi,
    #     TrangThai,
    #     Loai,
    #     GioDen,
    #     ThoiLuong=None,
    #     idNV=None,
    #     ThanhTien=None,
    # ):
    #     # Xác thực và làm sạch dữ liệu
    #     self.NgayDat = self.validate_ngay_dat(NgayDat)
    #     self.TrangThai = self.validate_trang_thai(TrangThai)
    #     self.Loai = self.validate_loai(Loai)
    #     self.GioDen = self.validate_gio_den(GioDen)
    #     self.ThoiLuong = self.validate_thoi_luong(ThoiLuong)
    #     self.idNV = idNV
    #     self.ThanhTien = self.validate_thanh_tien(ThanhTien)

    def validate_ngay_dat(self, value):
        if not value or not isinstance(value, date):
            raise ValueError(
                "Ngày đặt không được bỏ trống và phải là kiểu ngày hợp lệ!"
            )
        if value > datetime.now().date():
            raise ValueError("Ngày đặt không được là ngày trong tương lai!")
        return value

    def validate_ho_ten_nguoi_dat(self, value):
        if not value or not value.strip():
            raise ValueError("Họ tên người đặt không được bỏ trống!")
        if len(value) > 255:
            raise ValueError("Họ tên người đặt không được vượt quá 255 ký tự!")
        return value

    def validate_email(self, value):
        if not value or not value.strip():
            raise ValueError("Email không được bỏ trống!")
        if "@" not in value or "." not in value:
            raise ValueError("Email không hợp lệ!")
        return value

    def validate_sdt(self, value):
        if not value or not value.strip():
            raise ValueError("Số điện thoại không được bỏ trống!")
        if not value.isdigit() or len(value) < 10 or len(value) > 15:
            raise ValueError(
                "Số điện thoại phải là chuỗi số và có độ dài từ 10 đến 15 ký tự!"
            )
        return value

    def validate_trang_thai(self, value):
        valid_trang_thai = ["Đã hủy", "Đang chế biến", "Đã hoàn thành", "Chưa bắt đầu"]
        if value not in valid_trang_thai:
            raise ValueError(f"{value} không phải là trạng thái hợp lệ!")
        return value

    def to_dict(self):
        """Chuyển đổi đối tượng thành dictionary để serialize."""
        return {
            "MaDDH": self.MaDDH,
            "NgayDat": self.NgayDat.isoformat() if self.NgayDat else None,
            "TrangThai": self.TrangThai,
            "Loai": self.Loai,
            "GioDen": self.GioDen.isoformat() if self.GioDen else None,
            "ThoiLuong": self.ThoiLuong,
            "SoLuongNguoi": self.SoLuongNguoi,
            "idNV": self.idNV,
            "ThanhTien": float(self.ThanhTien) if self.ThanhTien else 0.00,
            "GhiChu": self.GhiChu,
        }

    def to_json(self):
        """Chuyển đổi đối tượng thành JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)

    def validate_loai(self, value):
        if value not in [1, 2]:  # Giả sử Loại chỉ có thể là 1 hoặc 2
            raise ValueError("Loại không hợp lệ! Phải là 1 hoặc 2.")
        return value

    def validate_gio_den(self, value):
        if not value or not isinstance(value, time):
            raise ValueError("Giờ đến không được bỏ trống và phải là kiểu giờ hợp lệ!")
        return value

    def validate_thoi_luong(self, value):
        if value is not None and (value < 0 or not isinstance(value, int)):
            raise ValueError("Thời lượng phải là số nguyên không âm!")
        return value

    def validate_thanh_tien(self, value):
        if value is not None and (value < 0 or not isinstance(value, (int, float))):
            raise ValueError("Thành tiền phải là một số không âm!")
        return

    # Getters
    def get_MaDDH(self):
        return self.MaDDH

    def get_NgayDat(self):
        return self.NgayDat

    def get_TrangThai(self):
        return self.TrangThai

    def get_Loai(self):
        return self.Loai

    def get_GioDen(self):
        return self.GioDen

    def get_ThoiLuong(self):
        return self.ThoiLuong

    def get_SoLuongNguoi(self):
        return self.SoLuongNguoi

    def get_idNV(self):
        return self.idNV

    def get_ThanhTien(self):
        return self.ThanhTien

    def get_GhiChu(self):
        return self.GhiChu

    # Setters
    def set_NgayDat(self, ngay_dat):
        self.NgayDat = ngay_dat

    def set_TrangThai(self, trang_thai):
        self.TrangThai = trang_thai

    def set_Loai(self, loai):
        self.Loai = loai

    def set_GioDen(self, gio_den):
        self.GioDen = gio_den

    def set_ThoiLuong(self, thoi_luong):
        self.ThoiLuong = thoi_luong

    def set_SoLuongNguoi(self, so_luong_nguoi):
        self.SoLuongNguoi = so_luong_nguoi

    def set_idNV(self, id_nv):
        self.idNV = id_nv

    def set_ThanhTien(self, thanh_tien):
        self.ThanhTien = thanh_tien

    def set_GhiChu(self, ghi_chu):
        self.GhiChu = ghi_chu


class MonAn(db.Model):
    __tablename__ = "MonAn"

    MaMA = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenMonAn = db.Column(db.String(100), nullable=False, unique=True)
    DonGia = db.Column(db.Text, nullable=False)
    Loai = db.Column(db.String(100), nullable=False)
    TrangThai = db.Column(db.String(20), nullable=False)
    HinhAnh = db.Column(db.String(200), nullable=True)

    @db.validates("TrangThai")
    def validate_trang_thai(self, key, value):
        valid_trang_thai = ["Còn phục vụ", "Ngừng phục vụ", "Tạm hết"]
        if value not in valid_trang_thai:
            raise ValueError(f"{value} không phải là trạng thái hợp lệ!")
        return value

    def to_dict(self):
        return {
            "MaMA": self.MaMA,
            "TenMonAn": self.TenMonAn,
            "DonGia": self.DonGia,
            "Loai": self.Loai,
            "TrangThai": self.TrangThai,
            "HinhAnh": url_for("static", filename=self.HinhAnh),
        }

    # Getters
    def get_MaMA(self):
        return self.MaMA

    def get_TenMonAn(self):
        return self.TenMonAn

    def get_DonGia(self):
        return self.DonGia

    def get_Loai(self):
        return self.Loai

    def get_TrangThai(self):
        return self.TrangThai

    def get_HinhAnh(self):
        return self.HinhAnh

    # Setters
    def set_TenMonAn(self, ten_mon_an):
        self.TenMonAn = ten_mon_an

    def set_DonGia(self, don_gia):
        self.DonGia = don_gia

    def set_Loai(self, loai):
        self.Loai = loai

    def set_TrangThai(self, trang_thai):
        self.TrangThai = trang_thai

    def set_HinhAnh(self, hinh_anh):
        self.HinhAnh = hinh_anh


class NguyenLieu(db.Model):
    __tablename__ = "NguyenLieu"

    MaNL = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenNguyenLieu = db.Column(db.String(100), nullable=False, unique=True)
    DonGia = db.Column(db.Numeric(15, 2), nullable=False)
    DonViTinh = db.Column(db.String(5), nullable=False)
    SoLuongTon = db.Column(db.Integer, nullable=False)

    @db.validates("DonViTinh")
    def validate_don_vi_tinh(self, key, value):
        valid_units = ["kg", "lít", "hộp", "túi", "chai", "thùng", "cái", "quả"]
        if value not in valid_units:
            raise ValueError(f"{value} không phải là đơn vị tính hợp lệ!")
        return value

    @db.validates("SoLuongTon")
    def validate_so_luong_ton(self, key, value):
        if value < 0:
            raise ValueError("Số lượng tồn không được âm!")
        return value

    # Getters
    def get_MaNL(self):
        return self.MaNL

    def get_TenNguyenLieu(self):
        return self.TenNguyenLieu

    def get_DonGia(self):
        return self.DonGia

    def get_DonViTinh(self):
        return self.DonViTinh

    def get_SoLuongTon(self):
        return self.SoLuongTon

    # Setters
    def set_TenNguyenLieu(self, ten_nguyen_lieu):
        self.TenNguyenLieu = ten_nguyen_lieu

    def set_DonGia(self, don_gia):
        self.DonGia = don_gia

    def set_DonViTinh(self, don_vi_tinh):
        self.DonViTinh = don_vi_tinh

    def set_SoLuongTon(self, so_luong_ton):
        self.SoLuongTon = so_luong_ton


class LoaiBan(db.Model):
    __tablename__ = "LoaiBan"
    MaLB = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenLoaiBan = db.Column(db.String(100))
    ban = db.relationship("Ban", backref="loai_ban", lazy=True)

    # Getters
    def get_MaLB(self):
        return self.MaLB

    def get_TenLoaiBan(self):
        return self.TenLoaiBan

    # Setters
    def set_TenLoaiBan(self, ten_loai_ban):
        self.TenLoaiBan = ten_loai_ban


class Ban(db.Model):
    __tablename__ = "Ban"

    MaBan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenBan = db.Column(db.String(30), nullable=False, unique=True)
    ViTri = db.Column(db.String(10), nullable=False)
    TrangThai = db.Column(db.String(30), nullable=False)
    idLoaiBan = db.Column(db.Integer, db.ForeignKey("LoaiBan.MaLB"), nullable=False)

    ct_don_dat_hang = db.relationship("CT_DonDatHang", backref="ban", lazy=True)

    @db.validates("TrangThai")
    def validate_trang_thai(self, key, value):
        valid_trang_thai = ["Còn trống", "Đang dùng bữa", "Đã đặt trước"]
        if value not in valid_trang_thai:
            raise ValueError(f"{value} không phải là trạng thái hợp lệ!")
        return value

    def to_dict(self):
        return {
            "MaBan": self.MaBan,
            "TenBan": self.TenBan,
            "ViTri": self.ViTri,
            "TrangThai": self.TrangThai,
            "idLoaiBan": self.idLoaiBan,
        }
        # Getters

    def get_MaBan(self):
        return self.MaBan

    def get_TenBan(self):
        return self.TenBan

    def get_ViTri(self):
        return self.ViTri

    def get_TrangThai(self):
        return self.TrangThai

    def get_idLoaiBan(self):
        return self.idLoaiBan

    # Setters
    def set_TenBan(self, ten_ban):
        self.TenBan = ten_ban

    def set_ViTri(self, vi_tri):
        self.ViTri = vi_tri

    def set_TrangThai(self, trang_thai):
        self.TrangThai = trang_thai

    def set_idLoaiBan(self, id_loai_ban):
        self.idLoaiBan = id_loai_ban


class NhomNguoiDung(db.Model):
    __tablename__ = "NhomNguoiDung"
    MaNND = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenNhomNguoiDung = db.Column(db.String(100))
    nguoi_dung = db.relationship("NguoiDung", backref="nhom_nguoi_dung", lazy=True)

    def getMaNND(self):
        return self.MaNND

    def getTenNhomNguoiDung(self):
        return self.TenNhomNguoiDung

    # Setters
    def set_TenNhomNguoiDung(self, ten_nhom_nguoi_dung):
        self.TenNhomNguoiDung = ten_nhom_nguoi_dung


class NguoiDung(db.Model, UserMixin):
    __tablename__ = "NguoiDung"
    MaND = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(200), nullable=False)
    TrangThai = db.Column(db.Integer)
    MatKhau = db.Column(db.String(200))
    VerifyCode = db.Column(db.String(150))
    idNND = db.Column(db.Integer, db.ForeignKey("NhomNguoiDung.MaNND"), nullable=False)

    khach_hang = db.relationship(
        "KhachHang", back_populates="nguoi_dung", uselist=False
    )

    nhan_vien = db.relationship("NhanVien", back_populates="nguoi_dung", uselist=False)

    # nhan_vien = db.relationship(
    #     "NhanVien", back_populates="nguoi_dung", uselist=False
    # )
    def __init__(self, MaND, UserName, TrangThai, MatKhau, VerifyCode, idNND):
        self.MaND = MaND
        self.UserName = UserName
        self.TrangThai = TrangThai
        self.MatKhau = MatKhau
        self.VerifyCode = VerifyCode
        self.idNND = idNND

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.MaND

    def has_role(self, role):
        ten_nhom_nguoi_dung = (
            NhomNguoiDung.query.filter(NhomNguoiDung.MaNND == self.idNND)
            .first()
            .getTenNhomNguoiDung()
        )
        return ten_nhom_nguoi_dung == role
    def getUserName(self):
        return self.UserName
    def setVerifyCode(self,VerifyCode):
        self.VerifyCode = VerifyCode
    def get_MatKhau(self):
        return self.MatKhau

    def set_MatKhau(self,MatKhau):
        self.MatKhau = MatKhau

    # def validate(self):
    #     """Method to validate the user input."""
    #     if not self.validate_username():
    #         return False
    #     # if not self.validate_full_name():
    #     #     return False
    #     # if not self.validate_email():
    #     #     return False
    #     # if not self.validate_password():
    #     #     return False
    #     return True

    # def validate_username(self):
    #     """Check if the username already exists in the database."""
    #     user = NguoiDung.query.filter_by(UserName=self.UserName).first()
    #     if user:
    #         flash("Username alrsfsfsfseady exists.", category="error")
    #         return False
    #     return True

    # def validate_email(self):
    #     """Check if the email is in a valid format."""
    #     email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    #     if not re.match(email_regex, self.Email):
    #         flash("Invalid email format.", category="error")
    #         return False
    #     return True

    # def validate_password(self, MatKhau1, MatKhau2):
    #     """Check if passwords match."""
    #     if MatKhau1 != MatKhau2:
    #         flash("Passwords do not match.", category="error")
    #         return False
    #     return True

    # def generate_verify_code(self):
    #     """Generate a verification code."""
    #     return "".join(
    #         secrets.choice(string.ascii_letters + string.digits) for _ in range(6)
    #     )


class PHANQUYEN(db.Model):
    __tablename__ = "PHANQUYEN"
    idNND = db.Column(
        db.Integer,
        db.ForeignKey("NhomNguoiDung.MaNND", ondelete="CASCADE"),
        primary_key=True,
    )
    idCN = db.Column(
        db.Integer, db.ForeignKey("ChucNang.MaCN", ondelete="CASCADE"), primary_key=True
    )

    # Getters
    def get_idNND(self):
        return self.idNND

    def get_idCN(self):
        return self.idCN

    # Setters
    def set_idNND(self, id_nnd):
        self.idNND = id_nnd

    def set_idCN(self, id_cn):
        self.idCN = id_cn


class PHIEUXUAT(db.Model):
    __tablename__ = "PHIEUXUAT"
    SoPhieuXuat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idNV = db.Column(
        db.Integer, db.ForeignKey("NhanVien.MaNV", ondelete="CASCADE"), nullable=False
    )
    NgayXuat = db.Column(db.DateTime, nullable=False)

    nhan_vien = db.relationship(
        "NhanVien", backref=db.backref("ds_phieu_xuat", lazy=True)
    )
    chi_tiet_phieu = db.relationship(
        "CT_PHIEUXUAT", backref="phieu_xuat", lazy=True, cascade="all, delete-orphan"
    )

    # Getters
    def get_SoPhieuXuat(self):
        return self.SoPhieuXuat

    def get_idNV(self):
        return self.idNV

    def get_NgayXuat(self):
        return self.NgayXuat

    # Setters
    def set_idNV(self, id_nv):
        self.idNV = id_nv

    def set_NgayXuat(self, ngay_xuat):
        self.NgayXuat = ngay_xuat


class CT_PHIEUXUAT(db.Model):
    __tablename__ = "CT_PHIEUXUAT"
    idXuat = db.Column(
        db.Integer,
        db.ForeignKey("PHIEUXUAT.SoPhieuXuat", ondelete="CASCADE"),
        primary_key=True,
    )
    idNL = db.Column(
        db.Integer,
        db.ForeignKey("NguyenLieu.MaNL", ondelete="CASCADE"),
        primary_key=True,
    )
    SoLuong = db.Column(db.Float, nullable=False)

    nguyen_lieu = db.relationship(
        "NguyenLieu", backref=db.backref("ds_nguyenlieu_xuat", lazy=True)
    )

    @db.validates("SoLuong")
    def validate_soluong(self, key, value):
        if value <= 0:
            raise ValueError("Số lượng xuất phải lớn hơn 0")
        return value

    # Getters
    def get_idXuat(self):
        return self.idXuat

    def get_idNL(self):
        return self.idNL

    def get_SoLuong(self):
        return self.SoLuong

    # Setters
    def set_idXuat(self, id_xuat):
        self.idXuat = id_xuat

    def set_idNL(self, id_nl):
        self.idNL = id_nl

    def set_SoLuong(self, so_luong):
        self.SoLuong = so_luong


class PHIEUNHAP(db.Model):
    __tablename__ = "PHIEUNHAP"
    SoPhieuNhap = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idNV = db.Column(
        db.Integer, db.ForeignKey("NhanVien.MaNV", ondelete="CASCADE"), nullable=False
    )
    NgayNhap = db.Column(db.DateTime, nullable=False)
    TongTien = db.Column(db.Float, nullable=False, default=0)

    nhan_vien = db.relationship(
        "NhanVien", backref=db.backref("ds_phieu_nhap", lazy=True)
    )
    chi_tiet_phieu = db.relationship(
        "CT_PHIEUNHAP", backref="phieu_nhap", lazy=True, cascade="all, delete-orphan"
    )

    # Getters
    def get_SoPhieuNhap(self):
        return self.SoPhieuNhap

    def get_idNV(self):
        return self.idNV

    def get_NgayNhap(self):
        return self.NgayNhap

    def get_TongTien(self):
        return self.TongTien

    # Setters
    def set_idNV(self, id_nv):
        self.idNV = id_nv

    def set_NgayNhap(self, ngay_nhap):
        self.NgayNhap = ngay_nhap

    def set_TongTien(self, tong_tien):
        self.TongTien = tong_tien


class CT_PHIEUNHAP(db.Model):
    __tablename__ = "CT_PHIEUNHAP"
    idNhap = db.Column(
        db.Integer,
        db.ForeignKey("PHIEUNHAP.SoPhieuNhap", ondelete="CASCADE"),
        primary_key=True,
    )
    idNL = db.Column(
        db.Integer,
        db.ForeignKey("NguyenLieu.MaNL", ondelete="CASCADE"),
        primary_key=True,
    )
    SoLuong = db.Column(db.Float, nullable=False)
    ThanhTien = db.Column(db.Float, nullable=False)

    nguyen_lieu = db.relationship(
        "NguyenLieu", backref=db.backref("ds_nguyenlieu_nhap", lazy=True)
    )

    @db.validates("SoLuong")
    def validate_soluong(self, key, value):
        if value <= 0:
            raise ValueError("Số lượng nhập phải lớn hơn 0")
        return value

    # Getters
    def get_idNhap(self):
        return self.idNhap

    def get_idNL(self):
        return self.idNL

    def get_SoLuong(self):
        return self.SoLuong

    def get_ThanhTien(self):
        return self.ThanhTien

    # Setters
    def set_idNhap(self, id_nhap):
        self.idNhap = id_nhap

    def set_idNL(self, id_nl):
        self.idNL = id_nl

    def set_SoLuong(self, so_luong):
        self.SoLuong = so_luong

    def set_ThanhTien(self, thanh_tien):
        self.ThanhTien = thanh_tien


class LOAIVOUCHER(db.Model):
    __tablename__ = "LOAIVOUCHER"
    MaLoaiVoucher = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenLoaiVoucher = db.Column(db.String(50), nullable=False)
    PhanTram = db.Column(db.Integer, nullable=False)
    MoTa = db.Column(db.String(500))
    SoLuong = db.Column(db.Integer, nullable=False)
    SoLuongConLai = db.Column(db.Integer, nullable=False)
    LoaiKH = db.Column(db.String(10), nullable=False)
    NgayBatDau = db.Column(db.DateTime, nullable=False)
    NgayKetThuc = db.Column(db.DateTime, nullable=False)
    GiamToiDa = db.Column(db.Integer)
    An = db.Column(db.Boolean, default=False, nullable=False)

    @db.validates("PhanTram")
    def validate_phantram(self, key, value):
        if not (0 < value < 100):
            raise ValueError("Phần trăm giảm phải lớn hơn 0 và nhỏ hơn 100")
        return value

    @db.validates("NgayBatDau", "NgayKetThuc")
    def validate_ngay(self, key, value):
        if key == "NgayBatDau" and value >= self.NgayKetThuc:
            raise ValueError("Ngày bắt đầu phải nhỏ hơn ngày kết thúc")
        if key == "NgayKetThuc" and value <= self.NgayBatDau:
            raise ValueError("Ngày kết thúc phải lớn hơn ngày bắt đầu")
        return value

    @db.validates("GiamToiDa")
    def validate_giamtoida(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Giảm tối đa phải lớn hơn hoặc bằng 0")
        return value

    @db.validates("SoLuong", "SoLuongConLai")
    def validate_soluong(self, key, value):
        if value < 0:
            raise ValueError(f"{key} phải lớn hơn hoặc bằng 0")
        return value

    # Getters
    def get_MaLoaiVoucher(self):
        return self.MaLoaiVoucher

    def get_TenLoaiVoucher(self):
        return self.TenLoaiVoucher

    def get_PhanTram(self):
        return self.PhanTram

    def get_MoTa(self):
        return self.MoTa

    def get_SoLuong(self):
        return self.SoLuong

    def get_SoLuongConLai(self):
        return self.SoLuongConLai

    def get_LoaiKH(self):
        return self.LoaiKH

    def get_NgayBatDau(self):
        return self.NgayBatDau

    def get_NgayKetThuc(self):
        return self.NgayKetThuc

    def get_GiamToiDa(self):
        return self.GiamToiDa

    def get_An(self):
        return self.An

    # Setters
    def set_TenLoaiVoucher(self, ten_loai_voucher):
        self.TenLoaiVoucher = ten_loai_voucher

    def set_PhanTram(self, phan_tram):
        self.PhanTram = phan_tram

    def set_MoTa(self, mo_ta):
        self.MoTa = mo_ta

    def set_SoLuong(self, so_luong):
        self.SoLuong = so_luong

    def set_SoLuongConLai(self, so_luong_con_lai):
        self.SoLuongConLai = so_luong_con_lai

    def set_LoaiKH(self, loai_kh):
        self.LoaiKH = loai_kh

    def set_NgayBatDau(self, ngay_bat_dau):
        self.NgayBatDau = ngay_bat_dau

    def set_NgayKetThuc(self, ngay_ket_thuc):
        self.NgayKetThuc = ngay_ket_thuc

    def set_GiamToiDa(self, giam_toi_da):
        self.GiamToiDa = giam_toi_da

    def set_An(self, an):
        self.An = an


class VOUCHER(db.Model):
    __tablename__ = "VOUCHER"
    CodeVoucher = db.Column(db.String(10), primary_key=True)
    idLoaiVoucher = db.Column(
        db.Integer,
        db.ForeignKey("LOAIVOUCHER.MaLoaiVoucher", ondelete="CASCADE"),
        nullable=False,
    )
    TrangThai = db.Column(db.Boolean, default=True)

    # Getters
    def get_CodeVoucher(self):
        return self.CodeVoucher

    def get_idLoaiVoucher(self):
        return self.idLoaiVoucher

    def get_TrangThai(self):
        return self.TrangThai

    # Setters
    def set_idLoaiVoucher(self, id_loai_voucher):
        self.idLoaiVoucher = id_loai_voucher

    def set_TrangThai(self, trang_thai):
        self.TrangThai = trang_thai


class CT_VOUCHER(db.Model):
    __tablename__ = "CT_VOUCHER"
    CodeVoucher = db.Column(
        db.String(10),
        db.ForeignKey("VOUCHER.CodeVoucher", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    idHD = db.Column(
        db.Integer, db.ForeignKey("HoaDon.MaHD", ondelete="CASCADE"), primary_key=True
    )

    # Getters
    def get_CodeVoucher(self):
        return self.CodeVoucher

    def get_idHD(self):
        return self.idHD

    # Setters
    def set_CodeVoucher(self, code_voucher):
        self.CodeVoucher = code_voucher

    def set_idHD(self, id_hd):
        self.idHD = id_hd


class THAMSO(db.Model):
    __tablename__ = "THAMSO"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TuoiToiDa = db.Column(db.Integer, nullable=False)
    TuoiToiThieu = db.Column(db.Integer, nullable=False)
    DiemChiaTichLuy = db.Column(db.Integer, nullable=False)
    SoVoucherApDung_Ngay = db.Column(db.Integer, nullable=False)
    SoNguyenLieuNhap = db.Column(db.Integer, nullable=False)
    PhanTramGiamVoucherToiDa = db.Column(db.Integer, nullable=False)
    Vang = db.Column(db.Integer, nullable=False)
    Bac = db.Column(db.Integer, nullable=False)
    Dong = db.Column(db.Integer, nullable=False)
    PhanTramThue = db.Column(db.Integer, nullable=False)

    # Getters
    def get_id(self):
        return self.id

    def get_TuoiToiDa(self):
        return self.TuoiToiDa

    def get_TuoiToiThieu(self):
        return self.TuoiToiThieu

    def get_DiemChiaTichLuy(self):
        return self.DiemChiaTichLuy

    def get_SoVoucherApDung_Ngay(self):
        return self.SoVoucherApDung_Ngay

    def get_SoNguyenLieuNhap(self):
        return self.SoNguyenLieuNhap

    def get_PhanTramGiamVoucherToiDa(self):
        return self.PhanTramGiamVoucherToiDa

    def get_Vang(self):
        return self.Vang

    def get_Bac(self):
        return self.Bac

    def get_Dong(self):
        return self.Dong

    def get_PhanTramThue(self):
        return self.PhanTramThue

    # Setters
    def set_TuoiToiDa(self, tuoi_toi_da):
        self.TuoiToiDa = tuoi_toi_da

    def set_TuoiToiThieu(self, tuoi_toi_thieu):
        self.TuoiToiThieu = tuoi_toi_thieu

    def set_DiemChiaTichLuy(self, diem_chia_tich_luy):
        self.DiemChiaTichLuy = diem_chia_tich_luy

    def set_SoVoucherApDung_Ngay(self, so_voucher_ap_dung_ngay):
        self.SoVoucherApDung_Ngay = so_voucher_ap_dung_ngay

    def set_SoNguyenLieuNhap(self, so_nguyen_lieu_nhap):
        self.SoNguyenLieuNhap = so_nguyen_lieu_nhap

    def set_PhanTramGiamVoucherToiDa(self, phan_tram_giam_voucher_toi_da):
        self.PhanTramGiamVoucherToiDa = phan_tram_giam_voucher_toi_da

    def set_Vang(self, vang):
        self.Vang = vang

    def set_Bac(self, bac):
        self.Bac = bac

    def set_Dong(self, dong):
        self.Dong = dong

    def set_PhanTramThue(self, phan_tram_thue):
        self.PhanTramThue = phan_tram_thue
