from flask import Flask, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth


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
    db.init_app(app)
    from .models import NguoiDung, NhomNguoiDung
    from .views import views
    from .auth import auth
    from .controller.nguyenlieu import nguyenlieu
    from .controller.phieunhap import phieunhap
    from .controller.phieuxuat import phieuxuat
    from .controller.nguoidung import nguoidung
    from .controller.nhanvien import nhanvien
    from .controller.khachhang import khachhang

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(nguyenlieu, url_prefix="/nguyenlieu")
    app.register_blueprint(phieunhap, url_prefix="/phieunhap")
    app.register_blueprint(phieuxuat, url_prefix="/phieuxuat")
    app.register_blueprint(nguoidung, url_prefix="/nguoidung")
    app.register_blueprint(nhanvien, url_prefix="/nhanvien")
    app.register_blueprint(khachhang, url_prefix="/khachhang")

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
