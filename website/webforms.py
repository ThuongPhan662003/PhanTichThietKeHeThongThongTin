from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms import StringField, DecimalField, IntegerField, DateTimeField, SubmitField, TimeField, TextAreaField, HiddenField, DateField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from datetime import datetime


class NguyenLieuForm(FlaskForm):
	TenNguyenLieu = StringField('Tên Nguyên Liệu', validators=[DataRequired(), Length(max=100)])
	DonGia = DecimalField('Đơn Giá', places=2, validators=[DataRequired(), NumberRange(min=1000, message="Đơn giá phải lớn hơn hoặc bằng 1000")])
	DonViTinh = SelectField('Đơn Vị Tính', choices=[('kg', 'Kg'), ('lít', 'Lít'), ('hộp', 'Hộp'), ('túi', 'Túi'), ('thùng', 'Thùng'), ('cái', 'Cái'), ('quả', 'Quả')], validators=[DataRequired()])
	SoLuongTon = IntegerField('Số Lượng', validators=[Optional(), NumberRange(min=0, message="Số lượng tồn phải là số dương")])
	NgayNhap = DateTimeField('Ngày Nhập', format='%d-%m-%Y %H:%M', validators=[Optional()])
	submit = SubmitField('Lưu thông tin')

class DonDatHangForm(FlaskForm):
    # Trường tìm kiếm khách hàng
    khach_hang = StringField(
        'Khách hàng',
        validators=[DataRequired(message="Vui lòng chọn khách hàng")]
    )
    
    # Hidden field cho mã khách hàng
    maKH = HiddenField('Mã khách hàng')
    
    # Ngày đặt
    ngayDat = DateField(
        'Ngày đặt',
        validators=[DataRequired(message="Vui lòng chọn ngày đặt")],
        default=datetime.now()
    )
    
    # Nhân viên đặt
    nhanVienDat = SelectField(
        'NV nhận đặt',
        coerce=int,
        validators=[DataRequired(message="Vui lòng chọn nhân viên")]
    )
    
    # Giờ đến
    gioDen = TimeField(
        'Giờ đến',
        validators=[DataRequired(message="Vui lòng chọn giờ đến")]
    )

    # Bàn đã chọn (từ datalist)
    ban = StringField(
        'Chọn bàn',
        validators=[DataRequired(message="Vui lòng chọn ít nhất một bàn")]
    )
    
    # Hidden field cho mã bàn (có thể chứa nhiều mã bàn phân cách bởi dấu phẩy)
    maBan = HiddenField('Mã bàn')
    
    # Thời lượng 
    thoiLuong = IntegerField(
        'Thời lượng (giờ)',
        validators=[
            DataRequired(message="Vui lòng nhập thời lượng"),
            NumberRange(min=2.5, max=10, message="Thời lượng phải từ 2.5 đến 10 giờ")
        ]
    )

    # Số lượng người
    soLuongNguoi = IntegerField(
        'Số lượng người',
        validators=[
            DataRequired(message="Vui lòng nhập số lượng người"),
            NumberRange(min=1, message="Số lượng người phải lớn hơn 0")
        ]
    )

    # Ghi chú
    ghiChu = TextAreaField(
        'Ghi chú',
        validators=[Optional()]
    )

    def __init__(self, *args, **kwargs):
        super(DonDatHangForm, self).__init__(*args, **kwargs)
        # Load danh sách nhân viên
        from .models import NhanVien
        self.nhanVienDat.choices = [
            (nv.MaNV, f"{nv.HoNV} {nv.TenNV}") 
            for nv in NhanVien.query.filter_by(TinhTrang=True).all()
        ]