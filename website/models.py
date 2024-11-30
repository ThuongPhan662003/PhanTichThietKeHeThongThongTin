
from datetime import date, time
import datetime
from email.policy import default

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Boolean


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


class CT_MonAn(db.Model):
    __tablename__ = "CT_MonAn"

    idDDH = db.Column(db.Integer, db.ForeignKey("DonDatHang.MaDDH"), primary_key=True)
    idMA = db.Column(db.Integer, db.ForeignKey("MonAn.MaMA"), primary_key=True)
    SoLuong = db.Column(db.Integer, nullable=False)
    GiaMon = db.Column(db.Text, nullable=False)
    GhiChu = db.Column(db.String(200), nullable=True)

    don_dat_hang = db.relationship("DonDatHang", backref="ct_mon_an")
    mon_an = db.relationship("MonAn", backref="ct_mon_an")

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
    GioiTinh = db.Column(db.Integer,nullable=False)
    idNguoiDung = db.Column(
        db.Integer,
        db.ForeignKey("NguoiDung.MaND"),
        unique=True,
    )
    LoaiKH = db.Column(db.String(10), nullable=False)
    nguoi_dung = db.relationship("NguoiDung", back_populates="khach_hang")
    hoa_don = db.relationship("HoaDon", backref="khach_hang")


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
    TienThue = db.Column(db.Text, nullable=False)
    DiemCong = db.Column(db.Integer, nullable=False)
    DiemTru = db.Column(db.Integer, nullable=False)

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


class CT_DonDatHang(db.Model):
    __tablename__ = "CT_DonDatHang"

    idDDH = db.Column(
        db.Integer,
        db.ForeignKey("DonDatHang.MaDDH"),
        primary_key=True,
    )
    idBan = db.Column(db.Integer, db.ForeignKey("Ban.MaBan"), primary_key=True)


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
        return self.HoNV + " "+ self.TenNV
    def set_idNguoiDung(self,idNguoiDung):
        self.idNguoiDung = idNguoiDung

    def get_idNguoiDung(self):
        return self.idNguoiDung

from datetime import datetime, date, time



class DonDatHang(db.Model):
    __tablename__ = "DonDatHang"

    MaDDH = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NgayDat = db.Column(db.Date, nullable=False)
    HoTenNguoiDat = db.Column(db.String, nullable=False)
    Email = db.Column(db.String, nullable=False)
    SDT = db.Column(db.String, nullable=False)
    TrangThai = db.Column(db.String(20), nullable=False)
    Loai = db.Column(db.Integer, nullable=False, default=1)
    GioDen = db.Column(db.Time, nullable=False)
    ThoiLuong = db.Column(db.Float) 
    SoLuongNguoi = db.Column(db.Integer)
    idNV = db.Column(db.Integer, db.ForeignKey("NhanVien.MaNV"), nullable=False)
    ThanhTien = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    GhiChu = db.Column(db.String(1000))
    ct_don_dat_hang = db.relationship("CT_DonDatHang", backref="don_dat_hang")
    hoa_don = db.relationship("HoaDon", backref="don_dat_hang")

    def __init__(
        self,
        NgayDat,
        HoTenNguoiDat,
        Email,
        SDT,
        TrangThai,
        Loai,
        GioDen,
        ThoiLuong=None,
        idNV=None,
        ThanhTien=None,
    ):
        # Xác thực và làm sạch dữ liệu
        self.NgayDat = self.validate_ngay_dat(NgayDat)
        self.HoTenNguoiDat = self.validate_ho_ten_nguoi_dat(HoTenNguoiDat)
        self.Email = self.validate_email(Email)
        self.SDT = self.validate_sdt(SDT)
        self.TrangThai = self.validate_trang_thai(TrangThai)
        self.Loai = self.validate_loai(Loai)
        self.GioDen = self.validate_gio_den(GioDen)
        self.ThoiLuong = self.validate_thoi_luong(ThoiLuong)
        self.idNV = idNV
        self.ThanhTien = self.validate_thanh_tien(ThanhTien)

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
        return value


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


class LoaiBan(db.Model):
    __tablename__ = "LoaiBan"
    MaLB = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenLoaiBan = db.Column(db.String(100))
    ban = db.relationship("Ban", backref="loai_ban", lazy=True)


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


class NhomNguoiDung(db.Model):
    __tablename__ = "NhomNguoiDung"
    MaNND = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenNhomNguoiDung = db.Column(db.String(100))
    nguoi_dung = db.relationship("NguoiDung", backref="nhom_nguoi_dung", lazy=True)
    def getMaNND(self):
        return self.MaNND
    def getTenNhomNguoiDung(self):
        return self.TenNhomNguoiDung


class NguoiDung(db.Model, UserMixin):
    __tablename__ = "NguoiDung"
    MaND = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(150), nullable=False)
    TrangThai = db.Column(db.Integer)
    MatKhau = db.Column(db.String(150))
    VerifyCode = db.Column(db.String(150))
    idNND = db.Column(db.Integer, db.ForeignKey("NhomNguoiDung.MaNND"), nullable=False)

    khach_hang = db.relationship(
        "KhachHang", back_populates="nguoi_dung", uselist=False
    )

    nhan_vien = db.relationship("NhanVien", back_populates="nguoi_dung", uselist=False)

    # nhan_vien = db.relationship(
    #     "NhanVien", back_populates="nguoi_dung", uselist=False
    # )
    @property
    def is_authenticated(self):
        return True
    def get_id(self):
        return self.MaND

    def has_role(self, role):
        ten_nhom_nguoi_dung = NhomNguoiDung.query.filter(
            NhomNguoiDung.MaNND==self.idNND
        ).first().getTenNhomNguoiDung()
        return ten_nhom_nguoi_dung == role


class PHANQUYEN(db.Model):
    __tablename__ = 'PHANQUYEN'
    idNND = db.Column(db.Integer, db.ForeignKey('NHOMNGUOIDUNG.MaNND', ondelete='CASCADE'), primary_key=True)
    idCN = db.Column(db.Integer, db.ForeignKey('CHUCNANG.MaCN', ondelete='CASCADE'), primary_key=True)

class PHIEUXUAT(db.Model):
    __tablename__ = 'PHIEUXUAT'
    SoPhieuXuat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idNV = db.Column(db.Integer, db.ForeignKey('NhanVien.MaNV', ondelete='CASCADE'), nullable=False)
    NgayXuat = db.Column(db.DateTime, nullable=False)

    nhan_vien = db.relationship('NhanVien', backref=db.backref('ds_phieu_xuat', lazy=True))
    chi_tiet_phieu = db.relationship('CT_PHIEUXUAT', backref='phieu_xuat', lazy=True, cascade='all, delete-orphan')

class CT_PHIEUXUAT(db.Model):
    __tablename__ = 'CT_PHIEUXUAT'
    idXuat = db.Column(db.Integer, db.ForeignKey('PHIEUXUAT.SoPhieuXuat', ondelete='CASCADE'), primary_key=True)
    idNL = db.Column(db.Integer, db.ForeignKey('NguyenLieu.MaNL', ondelete='CASCADE'), primary_key=True)
    SoLuong = db.Column(db.Float, nullable=False)
    
    nguyen_lieu = db.relationship('NguyenLieu', backref=db.backref('ds_nguyenlieu_xuat', lazy=True))
    @db.validates('SoLuong')
    def validate_soluong(self, key, value):
        if value <= 0:
            raise ValueError("Số lượng xuất phải lớn hơn 0")
        return value

class PHIEUNHAP(db.Model):
    __tablename__ = 'PHIEUNHAP'
    SoPhieuNhap = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idNV = db.Column(db.Integer, db.ForeignKey('NhanVien.MaNV', ondelete='CASCADE'), nullable=False)
    NgayNhap = db.Column(db.DateTime, nullable=False)
    TongTien = db.Column(db.Float, nullable=False, default=0)

    nhan_vien = db.relationship('NhanVien', backref=db.backref('ds_phieu_nhap', lazy=True))
    chi_tiet_phieu = db.relationship('CT_PHIEUNHAP', backref='phieu_nhap', lazy=True, cascade='all, delete-orphan')

class CT_PHIEUNHAP(db.Model):
    __tablename__ = 'CT_PHIEUNHAP'
    idNhap = db.Column(db.Integer, db.ForeignKey('PHIEUNHAP.SoPhieuNhap', ondelete='CASCADE'), primary_key=True)
    idNL = db.Column(db.Integer, db.ForeignKey('NguyenLieu.MaNL', ondelete='CASCADE'), primary_key=True)
    SoLuong = db.Column(db.Float, nullable=False)
    ThanhTien = db.Column(db.Float, nullable=False)
    
    nguyen_lieu = db.relationship('NguyenLieu', backref=db.backref('ds_nguyenlieu_nhap', lazy=True))

    @db.validates('SoLuong')
    def validate_soluong(self, key, value):
        if value <= 0:
            raise ValueError("Số lượng nhập phải lớn hơn 0")
        return value

class LOAIVOUCHER(db.Model):
    __tablename__ = 'LOAIVOUCHER'
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
    
    @db.validates('PhanTram')
    def validate_phantram(self, key, value):
        if not (0 < value < 100):
            raise ValueError("Phần trăm giảm phải lớn hơn 0 và nhỏ hơn 100")
        return value

    @db.validates('NgayBatDau', 'NgayKetThuc')
    def validate_ngay(self, key, value):
        if key == 'NgayBatDau' and value >= self.NgayKetThuc:
            raise ValueError("Ngày bắt đầu phải nhỏ hơn ngày kết thúc")
        if key == 'NgayKetThuc' and value <= self.NgayBatDau:
            raise ValueError("Ngày kết thúc phải lớn hơn ngày bắt đầu")
        return value

    @db.validates('GiamToiDa')
    def validate_giamtoida(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Giảm tối đa phải lớn hơn hoặc bằng 0")
        return value

    @db.validates('SoLuong', 'SoLuongConLai')
    def validate_soluong(self, key, value):
        if value < 0:
            raise ValueError(f"{key} phải lớn hơn hoặc bằng 0")
        return value

class VOUCHER(db.Model):
    __tablename__ = 'VOUCHER'
    CodeVoucher = db.Column(db.String(10), primary_key=True)
    idLoaiVoucher = db.Column(db.Integer, db.ForeignKey('LOAIVOUCHER.MaLoaiVoucher', ondelete='CASCADE'), nullable=False)
    TrangThai = db.Column(db.Boolean, default=True)

class CT_VOUCHER(db.Model):
    __tablename__ = 'CT_VOUCHER'
    CodeVoucher = db.Column(db.String(10), db.ForeignKey('VOUCHER.CodeVoucher', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    idHD = db.Column(db.Integer, db.ForeignKey('HOADON.MaHD', ondelete='CASCADE'), primary_key=True)

class THAMSO(db.Model):
    __tablename__ = 'THAMSO'
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
