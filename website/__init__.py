from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from .auth import init_oauth

db = SQLAlchemy()
DB_NAME = "database.db"
DB_PATH = os.path.join("db", DB_NAME)


def create_app():
    # from .models import NguoiDung, NhomNguoiDung

    app = Flask(__name__, static_folder="assets")

    app.config["SECRET_KEY"] = "hjshjhdjah kjshkjdhjs"
    # Cấu hình SQLAlchemy

    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost/qlnh"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .controller.nguyenlieu import nguyenlieu
    from .controller.phieunhap import phieunhap
    from .controller.nguoidung import nguoidung
    from .controller.phieuxuat import phieuxuat
    from .controller.nguoidung import nguoidung

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(nguyenlieu, url_prefix="/nguyenlieu")
    app.register_blueprint(phieunhap, url_prefix="/phieunhap")
    app.register_blueprint(phieuxuat, url_prefix="/phieuxuat")
    app.register_blueprint(nguoidung, url_prefix="/nguoidung")

    from .models import NguoiDung, NhomNguoiDung


    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    init_oauth(app)
    # @login_manager.user_loader
    # def load_user(id):
    #     return NguoiDung.query.get(int(id))
    return app


def create_database(app):
    if not path.exists("db/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
