import os
from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    flash,
    jsonify,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
import pandas as pd
from prompt_toolkit import HTML

from website import db
from sqlalchemy import func, cast, Date, text
from datetime import datetime
from website.auth import admin_required
from website.models import *
from website.models import NguoiDung, NhomNguoiDung
from flask import Response, render_template, request

import io
from flask import Response, request
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# from website.webforms import
import json

report = Blueprint("report", __name__)


def convert_date_format(date_str):
    """Chuyển đổi ngày từ định dạng dd-mm-yyyy sang yyyy-mm-dd."""
    if date_str:  # Kiểm tra nếu date_str không phải None hoặc rỗng
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    return None  # Trả về None nếu không có ngày


@report.route("/", methods=["GET"])
@admin_required
def report_list():
    """
    Hiển thị danh sách các báo cáo
    """
    # Danh sách các báo cáo với tiêu đề và route liên quan
    reports = [
        {
            "name": "Doanh thu theo tháng",
            "route": url_for("report.report_page_revenue"),
        },
        {
            "name": "Top món ăn bán chạy",
            "route": url_for("report.report_topdishes_page"),
        },
    ]

    return render_template("admin/report/report_list.html", reports=reports)


def get_dishes_data(start_date, end_date, limit_number=10):
    """
    Gọi stored procedure `GetTopSellingDishes` để lấy dữ liệu món ăn bán chạy.
    Nếu tham số ngày không được truyền vào, nó sẽ là None.
    """
    # Chuyển đổi ngày từ định dạng dd-mm-yyyy sang yyyy-mm-dd
    start_date = convert_date_format(start_date)
    end_date = convert_date_format(end_date)

    # Thực thi stored procedure với các tham số đã chuyển đổi
    result = db.session.execute(
        text(
            """
            CALL GetTopSellingDishes(:start_date, :end_date, :limit_number)
            """
        ),
        {
            "start_date": start_date,
            "end_date": end_date,
            "limit_number": limit_number,
        },
    )

    rows = result.fetchall()  # Đọc hết dữ liệu từ câu lệnh

    # Kiểm tra dữ liệu
    print(rows)  # In ra kết quả để kiểm tra cấu trúc dữ liệu (rows)

    # Chuyển đổi kết quả thành danh sách dict
    if rows:
        columns = result.keys()  # Lấy tên các cột từ kết quả SQL
        return [
            dict(zip(columns, row)) for row in rows
        ]  # Kết hợp cột và dữ liệu thành dict

    return []  # Trả về danh sách rỗng nếu không có dữ liệu


@report.route("/dishes", methods=["GET", "POST"])
def report_topdishes_page():
    if request.method == "POST":
        # Lấy thông tin từ form

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        limit_number = int(request.form.get("limit_number", 10))

        # Gọi hàm lấy dữ liệu
        dishes = get_dishes_data(start_date, end_date, limit_number)
        print(dishes)
        return render_template(
            "/admin/report/report_topdishes.html",
            dishes=dishes,
            start_date=start_date,
            end_date=end_date,
        )

    return render_template("/admin/report/form_topdishes.html")


@report.route("/pdf_topdishes")
def report_pdf_dishes():
    # Lấy tham số từ URL (GET request)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit_number = request.args.get("limit_number", default=10, type=int)

    # Lấy dữ liệu món ăn
    dishes = get_dishes_data(start_date, end_date, limit_number)

    # Tạo đối tượng In PDF (canvas) từ ReportLab
    buffer = io.BytesIO()  # Để ghi file PDF vào bộ nhớ
    c = canvas.Canvas(buffer, pagesize=letter)
    font_path = os.path.join(
        os.getcwd(), "website", "static", "fonts", "arial-unicode-ms-regular.ttf"
    )  # Đường dẫn tương đối đến font trong thư mục 'static/fonts'
    pdfmetrics.registerFont(TTFont("VietFont", font_path))
    c.setFont("VietFont", 12)

    # In tiêu đề
    c.drawString(200, 750, "Top Selling Dishes Report")
    c.drawString(200, 730, f"From: {start_date} To: {end_date}")

    # Tạo bảng dữ liệu
    y_position = 680
    table_data = [["Dish Name", "Total Quantity"]]  # Tiêu đề bảng

    for dish in dishes:
        table_data.append([dish["TenMonAn"], str(dish["totalQuantity"])])

    # Vẽ bảng
    x_position = 50
    width = 500
    height = 20
    row_height = 25

    # Vẽ các dòng của bảng
    for row_index, row in enumerate(table_data):
        y_position = 680 - row_index * row_height
        c.rect(x_position, y_position, width, row_height)  # Vẽ khung ô
        for col_index, cell in enumerate(row):
            c.drawString(
                x_position + 5 + col_index * (width / 2), y_position + 5, cell
            )  # Đặt nội dung vào ô

    # Kết thúc việc tạo PDF
    c.showPage()
    c.save()

    # Lấy nội dung PDF từ bộ nhớ
    pdf = buffer.getvalue()
    buffer.close()

    # Trả về file PDF dưới dạng response
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report_top_dishes.pdf"},
    )


@report.route("/excel_topdishes")
def report_excel_dishes():
    # Lấy tham số từ URL (GET request)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit_number = request.args.get("limit_number", default=10, type=int)

    # Lấy dữ liệu món ăn
    dishes = get_dishes_data(start_date, end_date, limit_number)

    # Tạo DataFrame từ kết quả
    df = pd.DataFrame(dishes)

    # Xuất file Excel từ DataFrame
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")

    # Quay lại đầu file và trả về dữ liệu Excel dưới dạng response
    output.seek(0)
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report_top_dishes.xlsx"},
    )


###report doanh thu


def get_revenue_data(start_date, end_date):

    # Chuyển đổi ngày từ định dạng dd-mm-yyyy sang yyyy-mm-dd
    start_date = convert_date_format(start_date)
    end_date = convert_date_format(end_date)

    # Thực thi stored procedure với các tham số đã chuyển đổi
    result = db.session.execute(
        text(
            """
            CALL TinhDoanhThuTheoThang(:start_date, :end_date)
            """
        ),
        {
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    rows = result.fetchall()  # Đọc hết dữ liệu từ câu lệnh

    # Kiểm tra dữ liệu
    print(rows)  # In ra kết quả để kiểm tra cấu trúc dữ liệu (rows)

    # Chuyển đổi kết quả thành danh sách dict
    if rows:
        columns = result.keys()  # Lấy tên các cột từ kết quả SQL
        return [
            dict(zip(columns, row)) for row in rows
        ]  # Kết hợp cột và dữ liệu thành dict

    return []  # Trả về danh sách rỗng nếu không có dữ liệu


@report.route("/revenue", methods=["GET", "POST"])
def report_page_revenue():
    if request.method == "POST":
        # Lấy thông tin từ form

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Gọi hàm lấy dữ liệu
        revenue = get_revenue_data(start_date, end_date)
        print(revenue)
        return render_template(
            "/admin/report/report_monthrevenue.html",
            revenue=revenue,
            start_date=start_date,
            end_date=end_date,
        )

    return render_template("/admin/report/form_monthrevenue.html")


@report.route("/pdf_monthlyrevenue")
def report_pdf_revenue():
    # Lấy tham số từ URL (GET request)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Lấy dữ liệu món ăn
    revenue = get_revenue_data(start_date, end_date)

    # Tạo đối tượng In PDF (canvas) từ ReportLab
    buffer = io.BytesIO()  # Để ghi file PDF vào bộ nhớ
    c = canvas.Canvas(buffer, pagesize=letter)
    font_path = os.path.join(
        os.getcwd(), "website", "static", "fonts", "arial-unicode-ms-regular.ttf"
    )  # Đường dẫn tương đối đến font trong thư mục 'static/fonts'
    pdfmetrics.registerFont(TTFont("VietFont", font_path))
    c.setFont("VietFont", 12)

    # In tiêu đề
    c.drawString(200, 750, "Top Selling Dishes Report")
    c.drawString(200, 730, f"From: {start_date} To: {end_date}")

    # Tạo bảng dữ liệu
    y_position = 680
    table_data = [["Month/Year", "Monthly Revenue"]]  # Tiêu đề bảng

    for dish in revenue:
        table_data.append([dish["YearMonth"], str(dish["MonthlyRevenue"])])

    # Vẽ bảng
    x_position = 50
    width = 500
    height = 20
    row_height = 25

    # Vẽ các dòng của bảng
    for row_index, row in enumerate(table_data):
        y_position = 680 - row_index * row_height
        c.rect(x_position, y_position, width, row_height)  # Vẽ khung ô
        for col_index, cell in enumerate(row):
            c.drawString(
                x_position + 5 + col_index * (width / 2), y_position + 5, cell
            )  # Đặt nội dung vào ô

    # Kết thúc việc tạo PDF
    c.showPage()
    c.save()

    # Lấy nội dung PDF từ bộ nhớ
    pdf = buffer.getvalue()
    buffer.close()

    # Trả về file PDF dưới dạng response
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=report_monthly_revenue.pdf"
        },
    )


@report.route("/excel_monthlyrevenue")
def report_excel_revenue():
    # Lấy tham số từ URL (GET request)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Lấy dữ liệu món ăn
    revenue = get_revenue_data(start_date, end_date)

    # Tạo DataFrame từ kết quả
    df = pd.DataFrame(revenue)

    # Xuất file Excel từ DataFrame
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")

    # Quay lại đầu file và trả về dữ liệu Excel dưới dạng response
    output.seek(0)
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=report_monthly_revenue.xlsx"
        },
    )
