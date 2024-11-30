from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date, text
from datetime import datetime
from website.models import *
from website.models import NguoiDung, NhomNguoiDung

bookcalendar = Blueprint("bookcalendar", __name__)


@bookcalendar.route("/")
def index():
    return render_template("user/book.html")


@bookcalendar.route("/save_event", methods=["POST"])
def save_event():
    # Lấy dữ liệu từ body request dưới dạng JSON
    data = request.get_json()

    # Lấy các thông tin từ dữ liệu gửi lên
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    start_time = data.get("start")
    end_time = data.get("end")
    duration = data.get("duration")

    # Kiểm tra nếu có thiếu thông tin cần thiết
    if not (name and phone and email and start_time and duration):
        return (
            jsonify({"status": "error", "message": "Vui lòng điền đầy đủ thông tin."}),
            400,
        )

    # Xử lý thời gian: Từ ISO 8601 format
    start_time = start_time.rstrip("Z")  # Loại bỏ ký tự 'Z' ở cuối
    start_time_obj = datetime.fromisoformat(start_time)


    # In thông tin sự kiện để kiểm tra
    print(f"Event saved: {name}, {phone}, {email}, {start_time}, {end_time}")
    dondathang = DonDatHang(None, )
    # Trả về phản hồi thành công
    return jsonify({"status": "success", "message": "Sự kiện đã được lưu thành công!"})


# API to get all events from the database (for refreshing the calendar)
@bookcalendar.route("/get_events", methods=["GET"])
def get_events():
    try:
        events = DonDatHang.query.all()
        event_list = [
            {
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
            }
            for event in events
        ]

        return jsonify({"status": "success", "data": event_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bookcalendar.route("/get_unavailable_times", methods=["GET"])
def get_unavailable_times():
    try:
        # Gọi Stored Procedure trong MySQL bằng SQLAlchemy, sử dụng text()
        result = db.session.execute(text("CALL GetFullyBookedTime()"))

        # Lấy kết quả trả về từ stored procedure
        rows = result.fetchall()
        print(rows)
        # Kiểm tra xem có dữ liệu không
        if not rows:
            return jsonify({"status": "success", "data": []})

        # Lấy dữ liệu cho unavailable_times từ kết quả trả về
        unavailable_times = []
        for row in rows:
            # Kiểm tra nếu RangeStart và RangeEnd có trong kết quả
            if "RangeStart" in row and "RangeEnd" in row:
                unavailable_times.append(
                    {"start_time": row["RangeStart"], "end_time": row["RangeEnd"]}
                )
            else:
                # Nếu cột không tồn tại trong kết quả, trả về lỗi
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Cột dữ liệu không hợp lệ trong kết quả từ stored procedure.",
                        }
                    ),
                    500,
                )

        # Trả về dữ liệu dưới dạng JSON
        return jsonify({"status": "success", "data": unavailable_times})

    except Exception as e:
        # Nếu có lỗi xảy ra, trả về lỗi
        return jsonify({"status": "error", "message": str(e)}), 500
