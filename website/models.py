from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class NhomNguoiDung(db.Model):
    __tablename__ = "NhomNguoiDung"
    idNND = db.Column(db.Integer, primary_key=True)
    TenNhomNguoiDung = db.Column(db.String(100))
    NguoiDung_List = db.relationship("NguoiDung", backref="NhomNguoiDung", lazy=True)


class NguoiDung(db.Model, UserMixin):
    __tablename__ = "NguoiDung"
    idND = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(150))
    TrangThai = db.Column(db.Integer)
    MatKhau = db.Column(db.String(150))
    VerifyCode = db.Column(db.String(150))
    idNND = db.Column(db.Integer, db.ForeignKey("NhomNguoiDung.idNND"), nullable=False)
    def get_id(self):
        return self.idND
