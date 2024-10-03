from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"
DB_PATH = os.path.join("db", DB_NAME)

# if not os.path.exists("db"):
#     os.makedirs("db")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    # Cấu hình SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:thuong@localhost/qlnhahang'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/view')
    app.register_blueprint(auth, url_prefix='/auth')

    from .models import NguoiDung,NhomNguoiDung
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return NguoiDung.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('db/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
