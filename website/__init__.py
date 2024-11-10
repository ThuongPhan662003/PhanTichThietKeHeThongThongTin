from flask import Flask, json, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager, current_user
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail


db = SQLAlchemy()

def create_app():

    # global db
    app = Flask(__name__, static_folder="static")

    with open("json/config.json") as config_file:
        config_data = json.load(config_file)

    # Cấu hình SQLAlchemy dựa trên file JSON
    username = config_data["username"]
    password = config_data["password"]
    database = config_data["database"]

    app.config["SECRET_KEY"] = "hjshjhdjah kjshkjdhjs"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{username}:{password}@localhost/{database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Cấu hình email trong Flask app
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = "n21dccn184@student.ptithcm.edu.vn"
    app.config["MAIL_PASSWORD"] = "irzy hzyd qrms eapz"
    app.config["MAIL_DEFAULT_SENDER"] = "n21dccn184@student.ptithcm.edu.vn"
    mail = Mail(app)
    db.init_app(app)
    from .models import NguoiDung, NhomNguoiDung
    from .views import views
    from .auth import auth
    from .admin import admin
    from .controller.nguyenlieu import nguyenlieu
    from .controller.phieunhap import phieunhap
    from .controller.phieuxuat import phieuxuat
    from .controller.nguoidung import nguoidung

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(nguyenlieu, url_prefix="/nguyenlieu")
    app.register_blueprint(phieunhap, url_prefix="/phieunhap")
    app.register_blueprint(phieuxuat, url_prefix="/phieuxuat")
    app.register_blueprint(nguoidung, url_prefix="/nguoidung")
    app.register_blueprint(admin, url_prefix="/admin")
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .auth import init_oauth

    init_oauth(app)

    @login_manager.user_loader
    def load_user(id):
        return NguoiDung.query.get(int(id))

    return app
