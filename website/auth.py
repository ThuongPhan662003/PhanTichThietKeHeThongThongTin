from .models import NguoiDung
from flask import Blueprint, render_template, request, flash, redirect, session, url_for,make_response, render_template
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
        UserName = request.form.get("UserName")
        MatKhau = request.form.get("MatKhau")

        # Retrieve the user from the database
        user = NguoiDung.query.filter_by(UserName=UserName).first()

        # phải check hashpass
        if user and user.MatKhau == MatKhau:
            login_user(user, remember=True)  # Log the user in
            flash("Login successful!", category="success")
            return redirect(url_for("views.admin_home"))
        else:
            flash("Invalid username or password.", category="error")

    return render_template("auth/login.html", user=current_user)




@auth.route("/")
def index():
    email = session.get("email")
    return f"Hello, {email}!" if email else f'Hello, Guest! <a href="{url_for("auth.login")}">Login</a>'



# @auth.route("/login")
# def login():
#     redirect_uri = url_for("auth.authorize", _external=True)
#     return google.authorize_redirect(redirect_uri)




@auth.route("/authorize")
def authorize():
    token = google.authorize_access_token()  # Lấy access token từ Google
    resp = google.get(
        "https://www.googleapis.com/oauth2/v3/userinfo"
    )  # Gọi endpoint userinfo để lấy thông tin người dùng
    user_info = resp.json()  # Chuyển đổi thông tin người dùng sang định dạng JSON

    # Lưu thông tin vào session
    session["email"] = user_info.get("email")  # Lưu email của người dùng vào session
    session["name"] = user_info.get("given_name")  # Lưu tên của người dùng vào session

    return redirect(url_for("auth.protected_area"))


@auth.route("/protected_area")
def protected_area():
    return f"Hello {session.get('name')}! <br/> <a href='{url_for('auth.logout')}'><button>Logout</button></a>"


@auth.route("/logout")
def logout():
    session.pop("email", None)  # Xóa email khỏi session
    session.pop("name", None)  # Xóa tên khỏi session
    return redirect(url_for("views.homepage"))
    # logout_user()
    # return redirect(url_for("auth.login"))



@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        UserName = request.form.get("UserName")
        MatKhau = request.form.get("MatKhau")
        print(UserName, MatKhau)
        user = NguoiDung.query.filter_by(UserName=UserName).first()
        if user:
            flash("Username already exists.", category="error")
        elif len(UserName) < 2:
            flash("UserName must be greater than 2 characters.", category="error")
        else:
            new_user = NguoiDung(
                UserName=UserName,
                TrangThai=1,
                MatKhau=MatKhau,
                VerifyCode=MatKhau,
                idNND=1,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)

