from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website.role import role_required
from .models import *
from . import db
import json


views = Blueprint("views", __name__)


@views.route("/")
def homepage():
    print("session")
    menu_items = MonAn.query.all()
    return render_template("user/homepage.html", menu=menu_items,user = current_user)



@views.route("/admin-home")
@role_required(["Nhân viên kho", "Quản lý", "Nhân viên"])
def admin_home():
    print(current_user)
    return render_template("admin/admin-home.html")
