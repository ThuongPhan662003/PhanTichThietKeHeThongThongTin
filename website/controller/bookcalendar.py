from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user

from website import db
from sqlalchemy import func, cast, Date, text
from datetime import datetime
from website.role import role_required
from website.models import *
from website.models import NguoiDung, NhomNguoiDung
from sqlalchemy.exc import SQLAlchemyError

bookcalendar = Blueprint("bookcalendar", __name__)


@bookcalendar.route("/")
@role_required(["Khách hàng"])
def index():
    khachhang = KhachHang.query.filter_by(idNguoiDung=current_user.MaND).first()
    print(current_user.MaND)
    print(khachhang)
    return render_template("user/book.html", khachhang=khachhang)


@bookcalendar.route("/save_event", methods=["POST"])
@role_required(["Khách hàng"])
def save_event():
    try:
        # Lấy dữ liệu từ request
        data = request.json
        name = data.get("name")
        print("name", name)
        phone = data.get("phone")
        print("phone", phone)
        email = data.get("email")
        print("email", email)
        date = datetime.strptime(data.get("date"), "%Y-%m-%d")
        time = datetime.strptime(data.get("time"), "%H:%M").time().strftime("%H:%M:%S")
        print("time", type(time))
        duration = data.get("duration")
        print("duration", duration)
        number_persons = data.get("number_persons")
        print("number_persons", type(number_persons))

        # Kiểm tra thông tin đầu vào
        if not all([name, phone, email, time, duration, number_persons]):
            return (
                jsonify({"status": "error", "message": "Thiếu thông tin yêu cầu!"}),
                400,
            )

        ghichu = name + "\n" + email + "\n" + phone
        new_event = DonDatHang()
        new_event.set_TrangThai("Chưa bắt đầu")
        new_event.set_Loai(1)
        new_event.set_SoLuongNguoi(int(number_persons))
        new_event.set_ThoiLuong(duration)
        new_event.set_GioDen(time)
        new_event.set_NgayDat(date.date())
        new_event.set_GhiChu(ghichu)
        db.session.add(new_event)

        # Commit giao dịch
        db.session.commit()
        return jsonify({"status": "success", "message": "Sự kiện đã được lưu!"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        error_message = str(e.__dict__.get("orig")) or str(e)
        print(f"Lỗi cơ sở dữ liệu: {error_message}")
        return (
            jsonify(
                {"status": "error", "message": f"Lỗi cơ sở dữ liệu: {error_message}"}
            ),
            500,
        )
    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        # print(new_event)
        print(f"Lỗi không xác định: {error_message}")
        return (
            jsonify(
                {"status": "error", "message": f"Lỗi không xác định: {error_message}"}
            ),
            500,
        )

    finally:
        # Đóng kết nối nếu cần
        db.session.close()


# API to get all events from the database (for refreshing the calendar)
@bookcalendar.route("/get_events", methods=["GET"])
@role_required(["Khách hàng"])
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
@role_required(["Khách hàng"])
def get_unavailable_times():
    try:
        # Gọi Stored Procedure trong MySQL bằng SQLAlchemy, sử dụng text()
        result = db.session.execute(
            text("CALL GetFullyBookedNonOverlappingTimeRanges()")
        )

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
        print("ssusss")
        # Trả về dữ liệu dưới dạng JSON
        return jsonify({"status": "success", "data": unavailable_times})

    except Exception as e:
        # Nếu có lỗi xảy ra, trả về lỗi
        return jsonify({"status": "error", "message": str(e)}), 500
