from asyncio.windows_events import NULL
from re import I
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website import db
from datetime import datetime, timedelta
from website.models import *
from sqlalchemy import func, extract

chucnang = Blueprint("chucnang", __name__)


@chucnang.route("/chucnang", methods=["GET"])
@login_required
def index():
    chucnangs = ChucNang.query.all()  # Lấy tất cả chức năng từ cơ sở dữ liệu
    return render_template("chucnang.html", chucnangs=chucnangs)
