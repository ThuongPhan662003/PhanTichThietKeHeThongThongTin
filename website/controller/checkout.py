from collections import defaultdict
from datetime import date, datetime
import json
import os
from flask import Blueprint, render_template, request, flash, jsonify, redirect, send_file, url_for, session
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from website.auth import role_required

# pdfmetrics.registerFont(TTFont("Arial", '/website/static/fonts/arial-unicode-ms-regular.ttf'))

# Đường dẫn font hỗ trợ tiếng Việt
FONT_PATH = os.path.join(os.getcwd(), "website", "static", "fonts", "arial-unicode-ms-regular.ttf")

# import pdfkit
# from weasyprint import HTML
from website import db
from website.models import VOUCHER, LOAIVOUCHER, Ban, CT_DonDatHang, DonDatHang, KhachHang, CT_VOUCHER, HoaDon, CT_MonAn, MonAn, THAMSO

# pdfkit_config = pdfkit.configuration(wkhtmltopdf='/wkhtmltopdf')

checkout = Blueprint("checkout", __name__)

@checkout.route("/", methods=["GET", "POST"])
@role_required(["Quản lý","Nhân viên"])
def index():
    idDDH = request.args.get("maddh")       
    don_dat_hang = DonDatHang.query.get(idDDH)
    khach_hang = don_dat_hang.hoa_don[0].khach_hang

    # Lấy danh sách loại voucher
    loai_vouchers = LOAIVOUCHER.query.filter(
        LOAIVOUCHER.NgayKetThuc >= date.today(),
        LOAIVOUCHER.NgayBatDau <= date.today(),
        LOAIVOUCHER.An == 0,
        LOAIVOUCHER.LoaiKH == khach_hang.LoaiKH,
        LOAIVOUCHER.SoLuongConLai > 0
    ).all()

    list_loai_voucher = []
    ## Kiểm tra xem khách hàng đó đã từng dùng loại voucher đó chưa
    for loai_voucher in loai_vouchers:
        try:
            if CT_VOUCHER.query.filter(
                CT_VOUCHER.CodeVoucher == VOUCHER.query.filter(VOUCHER.idLoaiVoucher == loai_voucher.MaLoaiVoucher, VOUCHER.TrangThai == 0).first().CodeVoucher,
                CT_VOUCHER.idHD == HoaDon.query.filter_by(idKH = khach_hang.MaKH).first().MaHD
            ).first():
                pass
            else: 
                list_loai_voucher.append(loai_voucher)
        except Exception as e:
            ValueError(e)

    # Truyền dữ liệu đơn hàng
    ct_monan = CT_MonAn.query.filter_by(idDDH=idDDH).all()

    data = defaultdict(lambda: defaultdict(list))

    for row in ct_monan:
        idDDH = row.idDDH
        idBan = row.idBan
        data[idDDH][idBan].append({
            "mon_an": MonAn.query.get(row.idMA).to_dict(),
            "so_luong": row.SoLuong
        })

    result = {}
    for idDDH, ban_dict in data.items():
        order = {"idDDH": idDDH, "DiemTD": khach_hang.DiemTieuDung, "ban": []}
        for idBan, mon_an_list in ban_dict.items():
            order["ban"].append({
                "Ban": Ban.query.get(idBan).to_dict(),
                "mon_an": mon_an_list,
            })
        result[idDDH] = order
    print(result)

    thue = THAMSO.query.get(1).PhanTramThue
    phantramvoucher = LOAIVOUCHER.query.filter()           
    return render_template("admin/checkout/checkout.html", 
                            list_loai_voucher=list_loai_voucher, result=result, thue=thue) 

# Xem danh sách hóa đơn
@checkout.route("/xemdshoadon", methods=["GET", "POST"])
@role_required(["Quản lý","Nhân viên"])
def xem_hoa_don():
    # Phân trang danh sách khách hàng
    page = request.args.get('page', 1, type=int) 
    per_page = 5
    pagination = HoaDon.query.order_by(HoaDon.MaHD.desc()).paginate(page=page, per_page=per_page)
    hoadon_list = pagination.items
    return render_template('admin/checkout/xem_hoa_don.html', listHD=hoadon_list, pagination=pagination)


# Lưu dữ liệu vào database
@checkout.route("/save", methods=["GET", "POST"])
@role_required(["Quản lý","Nhân viên"])
def save():
    try:
        data = request.get_json()
        print("Dữ liệu nhận được từ client:", data)
        
        idDDH = data.get('idDDH')
        TongTienGiam = data.get('TongTienGiam')
        TongTien = data.get('TongTien')
        TienThue = data.get('TienThue')
        DiemCong = data.get('DiemCong')
        DiemTru = data.get('DiemTru')
        idLoaiVoucher = data.get('idLoaiVoucher')
        payment = data.get('PhuongThucThanhToan')

        print(f"idDDH: {idDDH}, TongTienGiam: {TongTienGiam}, TongTien: {TongTien}, TienThue: {TienThue}, DiemCong: {DiemCong}, DiemTru: {DiemTru}, idLoaiVoucher: {idLoaiVoucher}")

        if None in [idDDH, TongTienGiam, TongTien, TienThue, DiemCong, DiemTru, idLoaiVoucher]:
            print("Lỗi: Thiếu thông tin yêu cầu")
            return jsonify({'error': 'Thiếu thông tin yêu cầu'}), 400

        # Lập hóa đơn
        hoa_don = HoaDon.query.filter_by(idDDH=idDDH).first()
        if not hoa_don:
            print("Lỗi: Không tìm thấy hóa đơn với idDDH:", idDDH)
            return jsonify({'error': 'Hóa đơn không tồn tại'}), 400
        
        hoa_don.TongTienGiam = TongTienGiam
        hoa_don.TongTien = TongTien
        hoa_don.TrangThai = 1  # Đã thanh toán
        hoa_don.TienThue = TienThue
        hoa_don.DiemCong = DiemCong
        hoa_don.DiemTru = DiemTru
        hoa_don.NgayXuat = datetime.now()
        hoa_don.PhuongThucThanhToan = payment

        print("Cập nhật hóa đơn thành công:", hoa_don)

        # Thay đổi trạng thái bàn
        list_ctddh = CT_DonDatHang.query.filter_by(idDDH=idDDH).all()
        print("Danh sách chi tiết đơn đặt hàng:", list_ctddh)
        for ct in list_ctddh:
            ban = ct.ban
            if not ban:
                print("Lỗi: Không tìm thấy thông tin bàn cho chi tiết đơn đặt hàng:", ct)
                return jsonify({'error': 'Không tìm thấy thông tin bàn'}), 400
            ban.TrangThai = "Còn trống"

        print("Cập nhật trạng thái bàn thành công")

        # Trừ số lượng loại voucher
        loai_voucher = LOAIVOUCHER.query.get(idLoaiVoucher)
        if loai_voucher:
            loai_voucher.SoLuongConLai -= 1      

            print("Cập nhật loại voucher thành công:", loai_voucher)

            # Set trạng thái cho voucher
            voucher = VOUCHER.query.filter_by(idLoaiVoucher=idLoaiVoucher).first()
            if not voucher:
                print("Lỗi: Không tìm thấy voucher với idLoaiVoucher:", idLoaiVoucher)
                return jsonify({'error': 'Voucher không tồn tại'}), 400
            voucher.TrangThai = 1

            print("Cập nhật trạng thái voucher thành công:", voucher)

            # Thêm bảng ghi cho CT_VOUCHER
            ct_voucher = CT_VOUCHER(CodeVoucher=voucher.CodeVoucher, idHD=hoa_don.MaHD)
            db.session.add(ct_voucher)

            print("Thêm bảng ghi CT_VOUCHER thành công:", ct_voucher)

        # Cộng/trừ điểm tiêu dùng cho khách hàng
        khach_hang = KhachHang.query.get(hoa_don.idKH)
        if not khach_hang:
            print("Lỗi: Không tìm thấy khách hàng:", hoa_don.idKH)
            return jsonify({'error': 'Khách hàng không tồn tại'}), 400
        khach_hang.DiemTieuDung += (DiemCong - DiemTru)
        khach_hang.DiemTichLuy += DiemCong

        db.session.flush()
        tham_so = THAMSO.query.get(1)
        if khach_hang.DiemTichLuy >= tham_so.Vang:
            khach_hang.LoaiKH = 'Vàng'
        elif khach_hang.DiemTichLuy >= tham_so.Bac:
            khach_hang.LoaiKH = 'Bạc'
        elif khach_hang.DiemTichLuy >= tham_so.Dong:
            khach_hang.LoaiKH = 'Đồng'
        else: khach_hang.LoaiKH = 'Thường'
        
        print("Cập nhật điểm khách hàng thành công:", khach_hang)

        # Commit dữ liệu
        db.session.commit()
        return jsonify({'message': 'Thanh toán thành công!', 'status': 'success'}), 200

    except Exception as e:
        db.session.rollback()
        print("Lỗi xảy ra:", str(e))
        return jsonify({'error': str(e)}), 500

# Xem hóa đơn
@checkout.route('/viewInvoice', methods=["GET", "POST"])
@role_required(["Quản lý","Nhân viên"])
def trang_hoa_don():
    maddh = request.args.get('maddh')

    # Lấy thông tin hóa đơn
    hoa_don = HoaDon.query.filter_by(idDDH = maddh).first()
    khach_hang = hoa_don.khach_hang

    # Lấy thông tin đơn hàng
    ct_monan = CT_MonAn.query.filter_by(idDDH=maddh).all()

    data = defaultdict(lambda: defaultdict(list))

    for row in ct_monan:
        idDDH = row.idDDH
        idBan = row.idBan
        data[idDDH][idBan].append({
            "mon_an": MonAn.query.get(row.idMA).to_dict(),
            "so_luong": row.SoLuong
        })

    result = {}
    for idDDH, ban_dict in data.items():
        order = {"idDDH": idDDH, "ban": []}
        for idBan, mon_an_list in ban_dict.items():
            order["ban"].append({
                "Ban": Ban.query.get(idBan).to_dict(),
                "mon_an": mon_an_list,
            })
        result[idDDH] = order
    print("Đây là chi tiết đơn đặt hàng")
    print(result)

    # Truyền dữ liệu vào invoice
    invoice = {
        "info": {
            "hoadon": hoa_don.to_dict(),
            "khachhang": khach_hang.HoKH + ' ' + khach_hang.TenKH,
            "ngaylaphd": hoa_don.NgayXuat,
            "nhanvien": current_user.nhan_vien.HoNV + ' ' + current_user.nhan_vien.TenNV 
        },
        "data": result 
    }

    print("Invoice trả về")
    print(invoice)

    return render_template("admin/checkout/invoice.html", invoice=invoice) 

# Xuất pdf
from flask import Response, request
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import io

@checkout.route("/export_pdf", methods=["GET", "POST"])
@role_required(["Quản lý","Nhân viên"])
def export_invoice_pdf():
    invoice_data = request.json
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    page_width, page_height = letter

    # Font setup
    font_path_regular = os.path.join(
        os.getcwd(), "website", "static", "fonts", "arial-unicode-ms-regular.ttf"
    )
    font_path_bold = os.path.join(
        os.getcwd(), "website", "static", "fonts", "arial-unicode-ms-bold.ttf"
    )
    pdfmetrics.registerFont(TTFont("VietFont", font_path_regular))
    pdfmetrics.registerFont(TTFont("VietFont-Bold", font_path_bold))

    def draw_header():
        c.setFont("VietFont-Bold", 16)
        text = "HÓA ĐƠN CHI TIẾT"
        c.drawCentredString(page_width / 2, 750, text)
        c.line(50, 740, page_width - 50, 740)

    def draw_invoice_info(y_position):
        c.setFont("VietFont-Bold", 12)
        c.drawString(50, y_position, "Số hóa đơn:")
        c.setFont("VietFont", 12)
        c.drawString(130, y_position, f"{invoice_data['info']['hoadon']['MaHD']}")
        y_position -= 20

        c.setFont("VietFont-Bold", 12)
        c.drawString(50, y_position, "Khách hàng:")
        c.setFont("VietFont", 12)
        c.drawString(130, y_position, f"{invoice_data['info']['khachhang']}")
        y_position -= 20

        ngaylaphd_str = invoice_data['info']['ngaylaphd']
        try:
            ngaylaphd = datetime.strptime(ngaylaphd_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            ngaylaphd = datetime.now()
        ngaylaphd_formatted = ngaylaphd.strftime("%d/%m/%Y %H:%M:%S")
        
        c.setFont("VietFont-Bold", 12)
        c.drawString(50, y_position, "Ngày lập:")
        c.setFont("VietFont", 12)
        c.drawString(130, y_position, f"{ngaylaphd_formatted}")
        y_position -= 20

        c.setFont("VietFont-Bold", 12)
        c.drawString(50, y_position, "Nhân viên:")
        c.setFont("VietFont", 12)
        c.drawString(130, y_position, f"{invoice_data['info']['nhanvien']}")
        return y_position - 40

    def draw_order_details(y_position):
        y_position -= 20  # Thêm khoảng trống thay cho "Chi tiết đơn hàng"
        c.setFont("VietFont-Bold", 14)
        c.drawString(50, y_position, "Món ăn")
        c.drawString(250, y_position, "Số lượng")
        c.drawString(350, y_position, "Đơn giá")
        c.drawString(450, y_position, "Thành tiền")
        c.line(50, y_position - 5, page_width - 50, y_position - 5)
        y_position -= 20
        c.setFont("VietFont-Bold", 12)
        for order in invoice_data["data"].values():
            for ban in order["ban"]:
                c.setFont("VietFont-Bold", 12)
                c.drawString(50, y_position, "Bàn:")
                c.setFont("VietFont", 12)
                c.drawString(100, y_position, f"{ban['Ban']['TenBan']}")
                y_position -= 20
                for item in ban["mon_an"]:
                    c.drawString(50, y_position, item["mon_an"]["TenMonAn"])
                    c.drawString(250, y_position, str(item["so_luong"]))
                    c.drawString(350, y_position, f"{item['mon_an']['DonGia']} VND")
                    c.drawString(450, y_position, f"{item['so_luong'] * int(item['mon_an']['DonGia'])} VND")
                    y_position -= 20
                    if y_position < 50:  # Nếu tràn trang
                        c.showPage()
                        draw_header()
                        y_position = 720

        return y_position

    def draw_summary(y_position):

        c.line(50, y_position, page_width - 50, y_position)
        c.setFont("VietFont", 12)
        y_position -= 20
        voucher_discount = (
            int(invoice_data['info']['hoadon']['DiemCong'] * 100) +
            int(invoice_data['info']['hoadon']['TienThue']) -
            int(float(invoice_data['info']['hoadon']['TongTien'])) -
            int(invoice_data['info']['hoadon']['DiemTru'])
        )

        c.setFont("VietFont-Bold", 12)
        text = "TỔNG KẾT"
        text_width = c.stringWidth(text, "VietFont-Bold", 12)
        c.drawString((page_width - text_width) / 2, y_position, text)
        y_position -= 20

        c.setFont("VietFont", 12)
        c.drawString(50, y_position, f"Tổng số món:")
        c.drawString(170, y_position, f"{sum(item['so_luong'] for order in invoice_data['data'].values() for ban in order['ban'] for item in ban['mon_an'])}")
        y_position -= 20
        c.drawString(50, y_position, f"Tổng tiền:")
        c.drawString(170, y_position, f"{int(float(invoice_data['info']['hoadon']['DiemCong']) * 100)} VND")
        y_position -= 20
        c.drawString(50, y_position, f"Thuế (VAT):")
        c.drawString(170, y_position, f"{invoice_data['info']['hoadon']['TienThue']} VND")
        y_position -= 20
        c.drawString(50, y_position, f"Giảm bằng voucher:")
        c.drawString(170, y_position, f"{voucher_discount} VND")
        y_position -= 20
        c.drawString(50, y_position, f"Giảm bằng điểm:")
        c.drawString(170, y_position, f"{invoice_data['info']['hoadon']['DiemTru']} VND")
        y_position -= 20

        # Tổng thanh toán
        c.setFont("VietFont-Bold", 12)
        c.line(50, y_position - 5, page_width - 50, y_position - 5)  # Kẻ đường làm nổi bật
        c.drawString(50, y_position - 20, f"TỔNG THANH TOÁN:")
        c.drawString(180, y_position - 20, f"{int(float(invoice_data['info']['hoadon']['TongTien']))} VND")
        y_position -= 20
        c.drawString(50, y_position - 20, f"Phương thức thanh toán: {invoice_data['info']['hoadon']['PhuongThucThanhToan']}")
        
        return y_position - 40

    # Draw content
    draw_header()
    y_position = 720
    y_position = draw_invoice_info(y_position)
    y_position = draw_order_details(y_position)
    draw_summary(y_position)

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=invoice.pdf"},
    )

