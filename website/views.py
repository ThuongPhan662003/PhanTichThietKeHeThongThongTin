from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import NguoiDung,NhomNguoiDung
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/users')
def get_users():
    users = NguoiDung.query.all()
    results = [{"id": user.MaND, "name": user.UserName} for user in users]
    return jsonify(results)
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    return render_template("home.html")

