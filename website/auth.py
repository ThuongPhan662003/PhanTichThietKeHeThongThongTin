import datetime
from functools import wraps
import re
import secrets
import string

from website.controller.mail import send_email
from website.role import role_required
from website.webforms import SignUpForm
from .models import KhachHang, NguoiDung, NhomNguoiDung
from flask import (
    Blueprint,
    abort,
    render_template,
    request,
    flash,
    redirect,
    session,
    url_for,
    make_response,
    render_template,
)
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
import os


auth = Blueprint("auth", __name__)
oauth = OAuth()
google = None


def init_oauth(app):
    global oauth
    oauth = OAuth(app)
    global google
    google = oauth.register(
        name="google",
        client_id="593025830495-3305kaj27epnmf86e16tckvbhbnq9d7v.apps.googleusercontent.com",
        client_secret="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",
        access_token_url="https://oauth2.googleapis.com/token",
        access_token_params=None,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params=None,
        userinfo_endpoint="https://www.googleapis.com/oauth2/v3/userinfo",
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    )





@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("current_user", current_user)
        UserName = request.form.get("UserName")
        MatKhau = request.form.get("MatKhau")
        print(UserName)
        user = NguoiDung.query.filter_by(UserName=UserName).first()
        print(user)
        if user and user.MatKhau == MatKhau:
            tenNND = (
                NhomNguoiDung.query.filter_by(MaNND=user.idNND)
                .first()
                .getTenNhomNguoiDung()
            )
            print("current_user", current_user.get_id())
            if tenNND != "Khách hàng":
                login_user(user, remember=True)
                flash("Login successful!", category="success")
                return redirect(url_for("nguoidung.account"))
            else:
                login_user(user, remember=True)
                flash("Login successful!", category="success")
                return redirect(url_for("views.homepage"))
        else:
            flash("Invalid username or password.", category="error")

    return render_template("auth/login.html", user=current_user)


@auth.route("/google_login")
def google_login():
    # session["next"] = request.args.get("next")
    redirect_uri = url_for("auth.authorize", _external=True)
    return google.authorize_redirect(redirect_uri)


# @auth.route("/")
# def index():
#     email = session.get("email")
#     return (
#         f"Hello, {email}!"
#         if email
#         else f'Hello, Guest! <a href="{url_for("auth.login")}">Login</a>'
#     )


@auth.route("/authorize")
def authorize():
    token = google.authorize_access_token()  # Lấy access token từ Google
    resp = google.get(
        "https://www.googleapis.com/oauth2/v3/userinfo"
    )  # Gọi endpoint userinfo để lấy thông tin người dùng
    user_info = resp.json()
    user_id = int(
        NguoiDung.query.filter_by(UserName=user_info.get("email")).first().get_id()
    )
    if user_id is None:
        TenNhomNguoiDung = "Khách hàng"
        idNND = int(
            NhomNguoiDung.query.filter_by(TenNhomNguoiDung=TenNhomNguoiDung)
            .first()
            .getMaNND()
        )
        new_user = NguoiDung(
            MaND=None,
            UserName=user_info.get("email"),
            TrangThai=1,
            MatKhau="".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(6)
            ),
            VerifyCode="".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(6)
            ),
            idNND=int(idNND),
        )
        db.session.add(new_user)
        NgayMoThe = datetime.datetime.now()

        new_customer = KhachHang(
            HoKH=user_info.get("family_name"),
            TenKH=user_info.get("given_name"),
            SDT="",
            Email=user_info.get("email"),
            NgayMoThe=NgayMoThe,
            DiemTieuDung=0,
            DiemTichLuy=0,
            idNguoiDung=user_id,
            LoaiKH="Thường",
        )
        db.session.add(new_customer)
        db.session.commit()
        login_user(new_user, remember=True)
        flash("Account created!", category="success")
    else:
        login_user(new_user, remember=True)
    return redirect(url_for("auth.protected_area"))


@auth.route("/protected_area")
def protected_area():
    # next_page = session.pop("next", url_for("views.homepage"))
    # print("nexxt", next_page, url_for("views.homepage"))

    return redirect(url_for("views.homepage"))


@auth.route("/logout")
# @role_required(["Nhân viên","Nhân viên kho" "Quản lý", "Khách hàng"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        SDT = request.form.get("SDT")
        HoTen = request.form.get("HoTen")
        print(HoTen)
        UserName = request.form.get("Email")
        MatKhau1 = request.form.get("MatKhau1")
        MatKhau2 = request.form.get("MatKhau2")
        Email = request.form.get("Email")
        GioiTinh = request.form.get("gender")
        ten_parts = str(HoTen).split()
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        print(SDT)
        user = NguoiDung.query.filter_by(UserName=UserName).first()
        TenNhomNguoiDung = "Khách hàng"
        idNND = int(
            NhomNguoiDung.query.filter_by(TenNhomNguoiDung=TenNhomNguoiDung)
            .first()
            .getMaNND()
        )
        if user:
            flash("Username already exists.", category="error")
        elif len(ten_parts) < 2:
            flash("Your full name is invalid.", category="error")
        elif not re.match(email_regex, Email):
            flash("Invalid email format.", category="error")
        elif MatKhau1 != MatKhau2:
            flash("Passwords do not match.", category="error")
        else:
            verify_code = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(6)
            )
            ten = ten_parts[-1]  # Tên là phần cuối cùng
            ho = " ".join(ten_parts[:-1])
            NgayMoThe = datetime.datetime.now()
            new_user = NguoiDung(
                MaND=None,
                UserName=UserName,
                TrangThai=1,
                MatKhau=MatKhau1,
                VerifyCode=verify_code,
                idNND=int(idNND),
            )
            print(new_user)
            db.session.add(new_user)
            # db.session.commit()
            user_id = int(NguoiDung.query.filter_by(UserName=UserName).first().get_id())
            customer = KhachHang(
                HoKH=ho,
                TenKH=ten,
                SDT=SDT,
                Email=UserName,
                NgayMoThe=NgayMoThe,
                DiemTieuDung=0,
                DiemTichLuy=0,
                idNguoiDung=user_id,
                LoaiKH="Thường",
            )
            customer.set_GioiTinh(GioiTinh)
            print(customer)
            db.session.add(customer)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.homepage"))
    return render_template("auth/sign_up.html")


@auth.route("/forgot_password", methods=["GET", "POST"])
@role_required(["Khách hàng"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("UserName")

        # Kiểm tra xem người dùng có tồn tại trong cơ sở dữ liệu không
        user = NguoiDung.query.filter(NguoiDung.UserName == username).first()

        if user:
            # Lấy email của người dùng
            email = (
                KhachHang.query.filter(KhachHang.idNguoiDung == user.get_id())
                .first()
                .get_Email()
            )

            # Tạo mật khẩu mới ngẫu nhiên
            new_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(8)
            )

            # Băm mật khẩu mới và lưu vào cơ sở dữ liệu
            user.set_MatKhau(new_password)
            db.session.commit()

            # Tạo nội dung email
            msg_title = "Quên mật khẩu"
            msg_body = f"""
            Chào bạn, bạn đã yêu cầu thay đổi mật khẩu. Dưới đây là mật khẩu mới của bạn:

            Mật khẩu mới: {new_password}

            Hãy sử dụng mật khẩu này để đăng nhập vào tài khoản của bạn.
            """

            msg_link = url_for("auth.login", _external=True)  # Link tới trang đăng nhập
            msg_namelink = "Click here to login"

            # Gửi email cho người dùng
            flag = send_email(email, msg_title, msg_body, msg_link, msg_namelink)

            if flag == "successfully":
                flash("Mật khẩu mới đã được gửi qua email của bạn.", category="success")
                return redirect(url_for("auth.login"))
            else:
                flash(
                    "Có vấn đề với việc gửi email. Vui lòng thử lại sau.",
                    category="error",
                )
                return redirect(url_for("auth.forgot_password"))
        else:
            flash("Tài khoản không tồn tại.", category="error")

    return render_template("auth/forgot_pass.html")
