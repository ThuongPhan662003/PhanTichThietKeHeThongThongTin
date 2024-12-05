from flask import Flask, json, jsonify, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_login import LoginManager, current_user
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
import redis
from flask_session import Session  # Đảm bảo đây là flask_session
from flask_apscheduler import APScheduler

from flask_mail import Mail

db = SQLAlchemy()
scheduler = APScheduler()
mail_app = Mail()


def create_app():

    # Khởi tạo Flask app
    app = Flask(__name__, static_folder="static")

    with open("json/config.json") as config_file:
        config_data = json.load(config_file)

    # Cấu hình SQLAlchemy dựa trên file JSON
    username = config_data["username"]
    password = config_data["password"]
    database = config_data["database"]
    secret = config_data["SECRET_KEY"]
    mail_username = config_data["MAIL_USERNAME"]
    mail_port = config_data["MAIL_PORT"]
    mail_server = config_data["MAIL_SERVER"]
    mail_use_tls = config_data["MAIL_USE_TLS"]

    # mail_use_ssl = config_data["MAIL_USE_SSL"]
    mail_password = config_data["MAIL_PASSWORD"]
    # mail_default_sender = config_data["MAIL_DEFAULT_SENDER"]

    sqlalchemy_track_modifications = config_data["SQLALCHEMY_TRACK_MODIFICATIONS"]
    app.config["SECRET_KEY"] = secret
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{username}:{password}@localhost/{database}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = sqlalchemy_track_modifications

    # Cấu hình email trong Flask app
    app.config["MAIL_SERVER"] = mail_server
    app.config["MAIL_PORT"] = mail_port
    app.config["MAIL_USE_TLS"] = mail_use_tls

    # app.config["MAIL_USE_SSL"] = mail_use_ssl
    app.config["MAIL_USERNAME"] = mail_username
    app.config["MAIL_PASSWORD"] = mail_password
    # app.config["MAIL_DEFAULT_SENDER"] = mail_default_sender

    # mail = Mail(app)
    db.init_app(app)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SCHEDULER_API_ENABLED"] = True

    # Định nghĩa function chạy job định kỳ
    def run_scheduled_job():
        with app.app_context():
            from website.controller.dondathang import xoa_don_dat_hang_cu

            xoa_don_dat_hang_cu()

    # Cấu hình scheduler
    app.config["JOBS"] = [
        {
            "id": "xoa_don_dat_hang",
            "func": run_scheduled_job,
            "trigger": "cron",
            # 'hour': '0',
            "minute": "*/2",  # cho job chạy sau mỗi 2p
        }
    ]
    scheduler.init_app(app)
    scheduler.start()

    # Cấu hình logging
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler(
        "logs/scheduler.log", maxBytes=10240, backupCount=10
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Scheduler startup")

    # Import models và blueprints
    from .models import NguoiDung, NhomNguoiDung

    from .controller.nguyenlieu import nguyenlieu
    from .controller.phieunhap import phieunhap
    from .controller.phieuxuat import phieuxuat
    from .controller.nguoidung import nguoidung
    from .controller.dondathang import dondathang

    from .controller.nhanvien import nhanvien
    from .controller.khachhang import khachhang
    from .controller.dondathang import dondathang
    from .controller.order import order
    from .controller.checkout import checkout

    from .controller.bookcalendar import bookcalendar
    from .controller.dondathang import dondathang
    from .controller.report import report
    from .controller.khachhang import khachhang

    from .controller.nhanvien import nhanvien
    from .controller.khachhang import khachhang
    from .controller.chucnang import chucnang
    from .controller.nhomnguoidung import nhomnguoidung
    from .controller.monan import monan
    from .controller.loaiban import loaiban
    from .controller.ban import ban
    from .controller.loaivoucher import loaivoucher
    from .controller.voucher import voucher
    from .controller.report_ty_le_nh_x import nhp_xuat
    from .controller.report_KH_tiem_nang import kh_tiemng
    from .controller.user_bill import user_bill
    from .controller.user_voucher import user_voucher

    # Đăng ký blueprints
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(nguyenlieu, url_prefix="/nguyenlieu")
    app.register_blueprint(phieunhap, url_prefix="/phieunhap")
    app.register_blueprint(phieuxuat, url_prefix="/phieuxuat")
    app.register_blueprint(nguoidung, url_prefix="/nguoidung")
    app.register_blueprint(nhanvien, url_prefix="/nhanvien")
    app.register_blueprint(khachhang, url_prefix="/khachhang")

    app.register_blueprint(dondathang, url_prefix="/dondathang")
    app.register_blueprint(order, url_prefix="/order")
    app.register_blueprint(checkout, url_prefix="/checkout")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(bookcalendar, url_prefix="/bookcalendar")
    app.register_blueprint(report, url_prefix="/report")
    app.register_blueprint(chucnang, url_prefix="/chucnang")
    app.register_blueprint(nhomnguoidung, url_prefix="/nhomnguoidung")
    app.register_blueprint(monan, url_prefix="/monan")
    app.register_blueprint(loaiban, url_prefix="/loaiban")
    app.register_blueprint(ban, url_prefix="/ban")
    app.register_blueprint(loaivoucher, url_prefix="/loaivoucher")
    app.register_blueprint(voucher, url_prefix="/voucher")
    app.register_blueprint(nhp_xuat, url_prefix="/report_ty_le_nhap_xuat")
    app.register_blueprint(kh_tiemng, url_prefix="/report_KH")
    app.register_blueprint(user_bill, url_prefix="/user_bill")
    app.register_blueprint(user_voucher, url_prefix="/user_voucher")
    with app.app_context():
        db.create_all()

    # Cấu hình Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Khởi tạo OAuth
    from .auth import init_oauth

    global mail_app
    init_oauth(app)
    mail_app = Mail(app)
    from .controller.mail import mail_sender

    app.register_blueprint(mail_sender, url_prefix="/mail")

    @login_manager.user_loader
    def load_user(id):
        return NguoiDung.query.get(int(id))

    return app
