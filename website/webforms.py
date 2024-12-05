from winreg import REG_EXPAND_SZ
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea

from wtforms import BooleanField, FileField, FloatField, RadioField, StringField, DateField, DecimalField, IntegerField, DateTimeField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, Optional, Regexp
from wtforms import (
    RadioField,
    StringField,
    DateField,
    DecimalField,
    IntegerField,
    DateTimeField,
    SubmitField,
    PasswordField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    ValidationError,
    Optional,
    Regexp,
)

from wtforms import (
    StringField,
    DecimalField,
    IntegerField,
    DateTimeField,
    SubmitField,
    TimeField,
    TextAreaField,
    HiddenField,
    DateField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    ValidationError,
    Optional,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length

from datetime import datetime
from website.models import THAMSO
from wtforms.validators import ValidationError

from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm
from .models import Ban, LoaiBan, MonAn  
from wtforms_sqlalchemy.fields import QuerySelectField

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, IntegerField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class MonAnForm(FlaskForm):
    TenMonAn = StringField('Tên Món Ăn', validators=[DataRequired()])
    DonGia = DecimalField('Đơn Giá', validators=[DataRequired()])
    Loai = SelectField('Loại', choices=[], coerce=str)  # Dùng SelectField với choices động
    TrangThai = SelectField('Trạng Thái', choices=[('Còn phục vụ', 'Còn phục vụ'), 
                                                   ('Ngừng phục vụ', 'Ngừng phục vụ'), 
                                                   ('Tạm hết', 'Tạm hết')], validators=[DataRequired()])
    HinhAnh = FileField('Hình Ảnh')
    Submit = SubmitField('Thêm')

    def __init__(self, *args, **kwargs):
        super(MonAnForm, self).__init__(*args, **kwargs)
        # Truy vấn để lấy các giá trị duy nhất cho Loai
        loai_choices = MonAn.query.with_entities(MonAn.Loai).distinct().all()
        self.Loai.choices = [(loai.Loai, loai.Loai) for loai in loai_choices]

class LoaiVoucherForm(FlaskForm):
    TenLoaiVoucher = StringField(
        "Tên Loại Voucher",
        validators=[
            DataRequired(message="Tên loại voucher không được để trống."),
            Length(max=50, message="Tên loại voucher không được vượt quá 50 ký tự.")
        ]
    )
    PhanTram = IntegerField(
        "Phần Trăm Giảm",
        validators=[
            DataRequired(message="Phần trăm giảm không được để trống."),
            NumberRange(min=1, max=99, message="Phần trăm giảm phải từ 1 đến 99.")
        ]
    )
    MoTa = TextAreaField("Mô Tả", validators=[Optional(), Length(max=500)])
    SoLuong = IntegerField(
        "Số Lượng",
        validators=[
            DataRequired(message="Số lượng không được để trống."),
            NumberRange(min=0, message="Số lượng phải lớn hơn hoặc bằng 0.")
        ]
    )
    SoLuongConLai = IntegerField(
        "Số Lượng Còn Lại"
        # validators=[
        #     DataRequired(message="Số lượng còn lại không được để trống."),
        #     NumberRange(min=-1, message="Số lượng còn lại phải lớn hơn hoặc bằng 0.")
        # ]
    )
    LoaiKH = SelectField(
        "Loại Khách Hàng",
        choices=[
            ("Thường", "Thường"),
            ("Đồng", "Đồng"),
            ("Bạc", "Bạc"),
            ("Vàng", "Vàng"),
            ("Bạch kim", "Bạch kim"),
            ("Kim Cương", "Kim Cương")
        ],
        validators=[DataRequired(message="Loại khách hàng không được để trống.")]
    )
    NgayBatDau = DateTimeField(
        "Ngày Bắt Đầu",
        validators=[DataRequired(message="Ngày bắt đầu không được để trống.")]
    )
    NgayKetThuc = DateTimeField(
        "Ngày Kết Thúc",
        validators=[DataRequired(message="Ngày kết thúc không được để trống.")]
    )
    GiamToiDa = IntegerField(
        "Giảm Tối Đa",
        validators=[Optional(), NumberRange(min=0, message="Giảm tối đa phải lớn hơn hoặc bằng 0.")]
    )
    An = BooleanField("Ẩn")
    def validate_NgayKetThuc(form, field):
        if form.NgayBatDau.data <form.NgayBatDau.data: 
                raise ValidationError('Ngày kết thúc không thể nhỏ hơn ngày bắt đầu.')

class LoaiBanForm(ModelForm, FlaskForm):
    class Meta:
        model = LoaiBan
        include_primary_keys = False  # Không hiển thị trường khóa chính (nếu cần)

class BanForm(FlaskForm):
    MaBan = IntegerField("Mã bàn", render_kw={"readonly": True})  # Thông thường không cho phép chỉnh sửa
    TenBan = StringField(
        "Tên bàn",
        validators=[
            DataRequired(message="Tên bàn không được để trống."),
            Length(max=30, message="Tên bàn không được vượt quá 30 ký tự.")
        ]
    )
    ViTri = StringField(
        "Vị trí",
        validators=[
            DataRequired(message="Vị trí không được để trống."),
            Length(max=10, message="Vị trí không được vượt quá 10 ký tự.")
        ]
    )
    TrangThai = SelectField(
        "Trạng thái",
        choices=[("Còn trống", "Còn trống"), ("Đang dùng bữa", "Đang dùng bữa"), ("Đã đặt trước", "Đã đặt trước")],
        validators=[DataRequired(message="Vui lòng chọn trạng thái.")]
    )
    idLoaiBan = QuerySelectField(
         "Loại Bàn",
        query_factory=lambda: LoaiBan.query.all(),  # Truy vấn tất cả loại bàn
        get_label="TenLoaiBan",  # Hiển thị tên loại bàn
        allow_blank=True,
        blank_text="-- Chọn loại bàn --",
        validators=[DataRequired("Vui lòng chọn loại bàn")]
    )
    submit = SubmitField("Lưu")

    # Custom validation for TrangThai (nếu cần thêm logic)
    def validate_TrangThai(self, field):
        valid_trang_thai = ["Còn trống", "Đang dùng bữa", "Đã đặt trước"]
        if field.data not in valid_trang_thai:
            raise ValidationError(f"{field.data} không phải là trạng thái hợp lệ!")



class NguyenLieuForm(FlaskForm):
    TenNguyenLieu = StringField(
        "Tên Nguyên Liệu", validators=[DataRequired(), Length(max=100)]
    )
    DonGia = DecimalField(
        "Đơn Giá",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=1000, message="Đơn giá phải lớn hơn hoặc bằng 1000"),
        ],
    )
    DonViTinh = SelectField(
        "Đơn Vị Tính",
        choices=[
            ("kg", "Kg"),
            ("lít", "Lít"),
            ("hộp", "Hộp"),
            ("túi", "Túi"),
            ("thùng", "Thùng"),
            ("cái", "Cái"),
            ("quả", "Quả"),
        ],
        validators=[DataRequired()],
    )
    SoLuongTon = IntegerField(
        "Số Lượng",
        validators=[
            Optional(),
            NumberRange(min=0, message="Số lượng tồn phải là số dương"),
        ],
    )
    NgayNhap = DateTimeField(
        "Ngày Nhập", format="%d-%m-%Y %H:%M", validators=[Optional()]
    )
    submit = SubmitField("Lưu thông tin")


class NhanVienForm(FlaskForm):
    HoNV = StringField("Họ", id="honv", validators=[DataRequired(), Length(max=30)])
    TenNV = StringField("Tên", id="tennv", validators=[DataRequired(), Length(max=10)])
    NgaySinh = StringField("Ngày Sinh", id="ngaysinh", validators=[DataRequired()])
    CCCD = StringField(
        "CCCD",
        id="cccd",
        validators=[
            DataRequired(),
            Length(min=12, max=12),
            Regexp(r"^\d{12}$", message="CCCD phải là 12 chữ số"),
        ],
    )
    Email = StringField(
        "Email",
        id="email",
        validators=[
            DataRequired(),
            Email(message="Vui lòng nhập đúng định dạng email!"),
            Length(max=100),
        ],
    )
    SDT = StringField(
        "Số Điện Thoại",
        id="sdt",
        validators=[
            DataRequired(),
            Length(min=10, max=10),
            Regexp(r"^\d{10}$", message="Số điện thoại phải là 10 chữ số"),
        ],
    )
    NgayVaoLam = StringField(
        "Ngày vào làm", id="ngayvaolam", validators=[DataRequired()]
    )
    TinhTrang = RadioField(
        "Tình trạng",
        choices=[("0", "Đang làm"), ("1", "Đã nghỉ")],
        default="0",
        coerce=int,
    )
    submit = SubmitField("Lưu Thông Tin", id="saveBtn")

    def validate_NgaySinh(self, field):
        # Kiểm tra độ tuổi có nhỏ hơn tuổi tối thiểu không
        print("Kiểm tra tuổi")
        tuoi_min = THAMSO.query.first().TuoiToiThieu
        if tuoi_min and tuoi_min > datetime.now().year - int(field.data[-4:]):
            raise ValidationError(f"Tuổi phải lớn hơn {tuoi_min} tuổi!")


class SearchNhanVienForm(FlaskForm):
    MaNV = IntegerField(
        "Mã NV",
        id="manv",
        validators=[Optional(), NumberRange(min=1, message="Mã phải lớn hơn 0")],
        filters=[lambda x: int(x) if x and x.isdigit() else None],
    )
    HoNV = StringField("Họ", id="honv", validators=[Optional(), Length(max=30)])
    TenNV = StringField("Tên", id="tennv", validators=[Optional(), Length(max=10)])
    NgayVaoLam = DateField(
        "Ngày vào làm", id="ngayvaolam", format="%d/%m/%Y", validators=[Optional()]
    )
    TinhTrang = RadioField(
        "Tình trạng",
        choices=[("0", "Đang làm"), ("1", "Đã nghỉ")],
        default="0",
        coerce=int,
    )
    submit = SubmitField("Tìm kiếm")


class KhachHangForm(FlaskForm):
    MaKH = StringField("Mã KH", id="makh")
    HoKH = StringField("Họ", id="hokh", validators=[DataRequired(), Length(max=30)])
    TenKH = StringField("Tên", id="tenkh", validators=[DataRequired(), Length(max=10)])
    NgayMoThe = StringField("Ngày mở thẻ", id="ngaymothe", validators=[DataRequired()])
    Email = StringField(
        "Email",
        id="email",
        validators=[
            DataRequired(),
            Email(message="Vui lòng nhập đúng định dạng email"),
            Length(max=100),
        ],
    )
    SDT = StringField(
        "Số Điện Thoại",
        id="sdt",
        validators=[
            DataRequired(),
            Length(min=10, max=10),
            Regexp(r"^\d{10}$", message="Số điện thoại phải là 10 chữ số"),
        ],
    )
    DiemTieuDung = IntegerField(
        "Điểm Tiêu Dùng",
        default=0,
        validators=[
            Optional(),
            NumberRange(min=0, message="Điểm tiêu dùng phải lớn hơn hoặc bằng 0"),
        ],
    )
    DiemTichLuy = IntegerField(
        "Điểm Tích Lũy",
        default=0,
        validators=[
            Optional(),
            NumberRange(min=0, message="Điểm tích lũy phải lớn hơn hoặc bằng 0"),
        ],
    )
    LoaiKH = SelectField(
        "Loại khách hàng",
        choices=[
            ("Vàng", "Vàng"),
            ("Bạc", "Bạc"),
            ("Đòng", "Đồng"),
            ("Thường", "Thường"),
        ],
        default="Thường",
        validators=[DataRequired()],
    )
    submit = SubmitField("Lưu Thông Tin", id="saveBtn")


class SearchKhachHangForm(FlaskForm):
    MaKH = StringField(
        "Mã KH",
        id="makh",
        validators=[Optional(), NumberRange(min=1, message="Mã phải lớn hơn 0")],
        filters=[lambda x: int(x) if x and x.isdigit() else None],
    )
    HoKH = StringField("Họ", id="hokh", validators=[Optional(), Length(max=30)])
    TenKH = StringField("Tên", id="tenkh", validators=[Optional(), Length(max=10)])
    NgayMoThe = StringField("Ngày mở thẻ", id="ngaymothe", validators=[Optional()])
    LoaiKH = SelectField(
        "Loại khách hàng",
        choices=[
            ("Vàng ", "Vàng"),
            ("Bạc", "Bạc"),
            ("Đồng", "Đồng"),
            ("Thường", "Thường"),
        ],
        default=None,
        validators=[Optional()],
    )
    submit = SubmitField("Tìm kiếm")


class DonDatHangForm(FlaskForm):
    # Trường tìm kiếm khách hàng
    khach_hang = StringField(
        "Khách hàng", validators=[DataRequired(message="Vui lòng chọn khách hàng")]
    )

    # Hidden field cho mã khách hàng
    maKH = HiddenField("Mã khách hàng")

    # Ngày đặt
    ngayDat = DateField(
        "Ngày đặt",
        validators=[DataRequired(message="Vui lòng chọn ngày đặt")],
        default=datetime.now(),
    )

    # Nhân viên đặt
    nhanVienDat = SelectField(
        "NV nhận đặt",
        coerce=int,
        validators=[DataRequired(message="Vui lòng chọn nhân viên")],
    )

    # Giờ đến
    gioDen = TimeField(
        "Giờ đến", validators=[DataRequired(message="Vui lòng chọn giờ đến")]
    )

    # Bàn đã chọn (từ datalist)
    ban = StringField(
        "Chọn bàn", validators=[DataRequired(message="Vui lòng chọn ít nhất một bàn")]
    )

    # Hidden field cho mã bàn (có thể chứa nhiều mã bàn phân cách bởi dấu phẩy)
    maBan = HiddenField("Mã bàn")

    # Thời lượng
    thoiLuong = IntegerField(
        "Thời lượng (giờ)",
        validators=[
            DataRequired(message="Vui lòng nhập thời lượng"),
            NumberRange(min=2.5, max=10, message="Thời lượng phải từ 2.5 đến 10 giờ"),
        ],
    )

    # Số lượng người
    soLuongNguoi = IntegerField(
        "Số lượng người",
        validators=[
            DataRequired(message="Vui lòng nhập số lượng người"),
            NumberRange(min=1, message="Số lượng người phải lớn hơn 0"),
        ],
    )

    # Ghi chú
    ghiChu = TextAreaField("Ghi chú", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(DonDatHangForm, self).__init__(*args, **kwargs)
        # Load danh sách nhân viên
        from .models import NhanVien

        self.nhanVienDat.choices = [
            (nv.MaNV, f"{nv.HoNV} {nv.TenNV}")
            for nv in NhanVien.query.filter_by(TinhTrang=True).all()
        ]


class SignUpForm(FlaskForm):
    ho_ten = StringField(
        "Họ và Tên", validators=[DataRequired(message="Vui lòng điền họ tên yêu quý khách")]
    )
    sdt = StringField("Số điện thoại", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    mat_khau = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(),
            Length(min=6, message="Mật khẩu phải dài ít nhất 6 ký tự."),
        ],
    )
    mat_khau_confirm = PasswordField(
        "Xác nhận mật khẩu",
        validators=[
            DataRequired(),
            EqualTo("mat_khau", message="Mật khẩu xác nhận không khớp."),
        ],
    )
    gioi_tinh = StringField("Giới tính", validators=[DataRequired()])
    submit = SubmitField("Đăng ký")
