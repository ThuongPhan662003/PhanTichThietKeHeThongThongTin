from flask import Flask, json, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_apscheduler import APScheduler

db = SQLAlchemy()
scheduler = APScheduler()

def create_app():

    # Khởi tạo Flask app
    app = Flask(__name__, static_folder="static")

    # Đọc file JSON để lấy thông tin cấu hình
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
    app.config["SCHEDULER_API_ENABLED"] = True

    db.init_app(app)

    # Định nghĩa function chạy job định kỳ
    def run_scheduled_job():
        with app.app_context():
            from website.controller.dondathang import xoa_don_dat_hang_cu
            xoa_don_dat_hang_cu()

    # Cấu hình scheduler
    app.config['JOBS'] = [
        {
            'id': 'xoa_don_dat_hang',
            'func': run_scheduled_job,
            'trigger': 'cron',
            # 'hour': '0',
            'minute': '*/2' # cho job chạy sau mỗi 2p
        }
    ]
    scheduler.init_app(app)
    scheduler.start()

    # Cấu hình logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/scheduler.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Scheduler startup')

    # Import models và blueprints
    from .models import NguoiDung, NhomNguoiDung
    from .views import views
    from .auth import auth
    from .controller.nguyenlieu import nguyenlieu
    from .controller.phieunhap import phieunhap
    from .controller.phieuxuat import phieuxuat
    from .controller.nguoidung import nguoidung
<<<<<<< HEAD
    from .controller.nhanvien import nhanvien
    from .controller.khachhang import khachhang
=======
    from .controller.dondathang import dondathang
>>>>>>> 12213f8ca82215827581b29b78bf4e90167baf69

    # Đăng ký blueprints
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(nguyenlieu, url_prefix="/nguyenlieu")
    app.register_blueprint(phieunhap, url_prefix="/phieunhap")
    app.register_blueprint(phieuxuat, url_prefix="/phieuxuat")
    app.register_blueprint(nguoidung, url_prefix="/nguoidung")
<<<<<<< HEAD
    app.register_blueprint(nhanvien, url_prefix="/nhanvien")
    app.register_blueprint(khachhang, url_prefix="/khachhang")
=======
    app.register_blueprint(dondathang, url_prefix="/dondathang")
>>>>>>> 12213f8ca82215827581b29b78bf4e90167baf69

    with app.app_context():
        db.create_all()

    # Cấu hình Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Khởi tạo OAuth
    from .auth import init_oauth
    init_oauth(app)

    @login_manager.user_loader
    def load_user(id):
        return NguoiDung.query.get(int(id))

    return app
