from flask import Blueprint, make_response, render_template, request, session
from sqlalchemy import func
from weasyprint import HTML
from website import db
from website.role import role_required
from website.models import KhachHang, HoaDon
from flask_login import login_required

kh_tiemng = Blueprint("report_KH", __name__)

@kh_tiemng.route('/bao-cao-khach-hang', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def bao_cao_khach_hang():
    start_date = request.form.get('start_date', None)
    end_date = request.form.get('end_date', None)

    # Truy vấn khách hàng và tính toán điểm tích lũy, số hóa đơn thanh toán
    reports = db.session.query(
        KhachHang.MaKH,
        KhachHang.HoKH,
        KhachHang.TenKH,
        KhachHang.DiemTichLuy,
        KhachHang.DiemTieuDung,
        KhachHang.LoaiKH,
        func.count(HoaDon.MaHD).label('so_hoa_don')
    ).join(HoaDon, HoaDon.idKH == KhachHang.MaKH) \
    .filter(HoaDon.NgayXuat.between(start_date, end_date)) \
    .group_by(KhachHang.MaKH, KhachHang.HoKH, KhachHang.TenKH, KhachHang.DiemTichLuy, KhachHang.DiemTieuDung, KhachHang.LoaiKH) \
    .order_by(KhachHang.DiemTichLuy.desc(), func.count(HoaDon.MaHD).desc()) \
    .limit(50) \
    .all()


    report_data = []
    for report in reports:
        report_data.append({
            'ma_kh': report.MaKH,
            'ho_kh': report.HoKH,
            'ten_kh': report.TenKH,
            'diem_tich_luy': report.DiemTichLuy,
            'diem_tieu_dung': report.DiemTieuDung,
            'loai_kh': report.LoaiKH,
            'so_hoa_don': report.so_hoa_don
        })
            # Lưu dữ liệu vào session
    session['report_data'] = report_data
    session['start_date'] = start_date
    session['end_date'] = end_date


    return render_template('admin/report/bao_cao_khach_hang.html', report_data=report_data, start_date=start_date, end_date=end_date)
@kh_tiemng.route('/bao-cao-khach-hang-pdf', methods=['GET'])
@role_required(["Quản lý"])
def bao_cao_khach_hang_pdf():
    # Lấy dữ liệu từ session
    report_data = session.get('report_data', [])
    start_date = session.get('start_date', None)
    end_date = session.get('end_date', None)

    if not report_data or not start_date or not end_date:
        return "No report data available. Please generate the report first.", 400

    # Render template thành HTML
    html = render_template('admin/report/bao_cao_khach_hang_pdf.html', 
                           report_data=report_data, start_date=start_date, end_date=end_date)

    # Chuyển đổi HTML thành PDF
    pdf = HTML(string=html).write_pdf()

    # Trả về PDF cho trình duyệt
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=bao_cao_khach_hang.pdf'

    # Xóa dữ liệu báo cáo trong session
    session.pop('report_data', None)
    session.pop('start_date', None)
    session.pop('end_date', None)

    return response