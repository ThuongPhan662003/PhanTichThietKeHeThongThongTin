from flask_wtf import FlaskForm
from wtforms.widgets import TextArea
from wtforms import StringField, DecimalField, IntegerField, DateTimeField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from datetime import datetime


# Create login form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

class NguyenLieuForm(FlaskForm):
	TenNguyenLieu = StringField('Tên Nguyên Liệu', validators=[DataRequired(), Length(max=100)])
	DonGia = DecimalField('Đơn Giá', places=2, validators=[DataRequired(), NumberRange(min=1000, message="Đơn giá phải lớn hơn hoặc bằng 1000")])
	DonViTinh = SelectField('Đơn Vị Tính', choices=[('kg', 'Kg'), ('lít', 'Lít'), ('hộp', 'Hộp'), ('túi', 'Túi'), ('thùng', 'Thùng'), ('cái', 'Cái'), ('quả', 'Quả')], validators=[DataRequired()])
	SoLuongTon = IntegerField('Số Lượng', validators=[Optional(), NumberRange(min=0, message="Số lượng tồn phải là số dương")])
	NgayNhap = DateTimeField('Ngày Nhập', format='%d-%m-%Y %H:%M', validators=[Optional()])
	submit = SubmitField('Lưu thông tin')