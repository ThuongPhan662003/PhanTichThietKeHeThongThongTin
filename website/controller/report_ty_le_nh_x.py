from flask import session
from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func
from website.role import role_required
from website.models import CT_PHIEUNHAP, CT_PHIEUXUAT, PHIEUNHAP, PHIEUXUAT, NguyenLieu
from website import db
from flask import make_response
nhp_xuat = Blueprint("report_ty_le_nhap_xuat", __name__)



@nhp_xuat.route('/bao-cao-phieu', methods=['GET', 'POST'])
@role_required(["Quản lý"])
def bao_cao_phieu():
    start_date = request.form.get('start_date', None)
    end_date = request.form.get('end_date', None)

    # Truy vấn dữ liệu
    reports = db.session.query(
        NguyenLieu.TenNguyenLieu,
        func.sum(CT_PHIEUNHAP.SoLuong).label('total_imported'),
        func.sum(CT_PHIEUXUAT.SoLuong).label('total_exported')
    ).join(CT_PHIEUNHAP, NguyenLieu.MaNL == CT_PHIEUNHAP.idNL) \
     .join(CT_PHIEUXUAT, NguyenLieu.MaNL == CT_PHIEUXUAT.idNL, isouter=True) \
     .join(PHIEUNHAP, PHIEUNHAP.SoPhieuNhap == CT_PHIEUNHAP.idNhap) \
     .join(PHIEUXUAT, PHIEUXUAT.SoPhieuXuat == CT_PHIEUXUAT.idXuat) \
     .filter(PHIEUNHAP.NgayNhap.between(start_date, end_date) | PHIEUXUAT.NgayXuat.between(start_date, end_date)) \
     .group_by(NguyenLieu.TenNguyenLieu).all()

    # Xử lý dữ liệu
    report_data = []
    for report in reports:
        total_imported = report.total_imported if report.total_imported else 0
        total_exported = report.total_exported if report.total_exported else 0
        ratio = total_exported / total_imported if total_imported > 0 else 0
        report_data.append({
            'ten_nguyen_lieu': report.TenNguyenLieu,
            'total_imported': total_imported,
            'total_exported': total_exported,
            'ratio': ratio
        })

    # Lưu vào session
    session['report_data'] = report_data
    session['start_date'] = start_date
    session['end_date'] = end_date

    return render_template('admin/report/bao_cao_phieu.html', report_data=report_data, start_date=start_date, end_date=end_date)


from flask import make_response
from io import BytesIO
from xhtml2pdf import pisa

from weasyprint import HTML
from flask import make_response, session

@nhp_xuat.route('/bao-cao-phieu-pdf', methods=['GET'])
@role_required(["Quản lý"])
def bao_cao_phieu_pdf():
    # Lấy dữ liệu từ session
    report_data = session.get('report_data', [])
    start_date = session.get('start_date', None)
    end_date = session.get('end_date', None)

    if not report_data or not start_date or not end_date:
        return "No report data available. Please generate the report first.", 400

    # Render HTML từ template
    html = render_template(
        'admin/report/bao_cao_phieu_pdf.html',
        report_data=report_data,
        start_date=start_date,
        end_date=end_date
    )

    # Tạo PDF với WeasyPrint
    pdf = HTML(string=html).write_pdf()

    # Trả về PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=bao_cao_phieu.pdf'

    # Xóa dữ liệu trong session
    session.pop('report_data', None)
    session.pop('start_date', None)
    session.pop('end_date', None)
    return response
