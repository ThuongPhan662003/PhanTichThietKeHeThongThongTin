from datetime import date, datetime
import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from decimal import Decimal
from website import db
from website.models import Ban, CT_DonDatHang, CT_MonAn, HoaDon, MonAn
from website.models import KhachHang
from website.models import DonDatHang

order = Blueprint("order", __name__)    

@order.route("/", methods=["GET", "POST"])
@login_required
def index():
    action = request.args.get('action') 
    id_order = request.args.get('maddh')
    ct_don_dat_hang_list = CT_DonDatHang.query.filter_by(idDDH=id_order).all()
    if action == "takeaway":
        try:
            id_khach_hang = request.form.get("maKH")
            ghi_chu = request.form.get("ghiChu")
              # Validate id_khach_hang
            if not id_khach_hang or not KhachHang.query.get(id_khach_hang):
                flash("Vui lòng chọn khách hàng hợp lệ từ danh sách!", "danger")
                return redirect(url_for('dondathang.ds_dondathang'))

            # Lấy bàn chờ còn trống
            ban_cho = Ban.query.filter(
                Ban.TenBan.ilike('%Bàn chờ%'),
                Ban.TrangThai == "Còn trống"
            ).first()
        
            if not ban_cho:
                flash("Không có bàn chờ nào còn trống!", "danger")
                return redirect(url_for('dondathang.ds_dondathang'))
            don_dat_hang = DonDatHang(
                NgayDat = date.today(),
                TrangThai = "Chưa bắt đầu",
                Loai = False,
                GioDen = datetime.now().time(),
                ThoiLuong = 0,
                SoLuongNguoi = 1,
                idNV = current_user.nhan_vien.MaNV,
                ThanhTien = 0.00,
                GhiChu = ghi_chu)
            
            db.session.add(don_dat_hang)
            db.session.flush() 

            hoa_don = HoaDon(idKH = id_khach_hang,
                            idDDH = don_dat_hang.MaDDH,
                            idNV = current_user.MaND,
                            TongTienGiam = 0,
                            TongTien = 0,
                            TrangThai = False,
                            TienThue = 0,
                            DiemCong = 0,
                            DiemTru = 0)

            db.session.add(hoa_don)
            db.session.flush()
            
            ct_don_dat_hang = CT_DonDatHang(
                idDDH = don_dat_hang.MaDDH,
                idBan = ban_cho.MaBan,
                ThanhTien = 0
            )

            db.session.add(ct_don_dat_hang)
            db.session.flush()

            ban_cho.TrangThai = "Đang dùng bữa"
            db.session.commit()

            ct_don_dat_hang_list = [ct_don_dat_hang]
            print("ma ddh: ", don_dat_hang.MaDDH )
            return redirect(url_for('order.takeaway', maddh=don_dat_hang.MaDDH, action=action))

        except Exception as e:
            db.session.rollback()
            print(str(e))
            return
        
    return render_template('admin/orderdoan/order.html', action=action, ctddh=ct_don_dat_hang_list)



@order.route("/takeaway", methods=["GET"])
@login_required
def takeaway():
    maddh = request.args.get('maddh')
    action = request.args.get('action')

    ct_don_dat_hang_list = CT_DonDatHang.query.filter_by(idDDH=maddh).all()
    print(ct_don_dat_hang_list)
    return render_template(
        'admin/orderdoan/order.html',
        maddh=maddh,
        action=action,
        ctddh=ct_don_dat_hang_list
    )


@order.route("/products/grouped", methods=["GET"])
def get_grouped_products():
    # Lấy tất cả các món ăn từ cơ sở dữ liệu
    all_products = MonAn.query.all()
    
    # Sắp xếp món ăn theo từng loại
    grouped_products = {}
    for product in all_products:
        loai = product.Loai
        if loai not in grouped_products:
            grouped_products[loai] = []
        
        # Thêm món ăn vào loại tương ứng
        grouped_products[loai].append({
            "MaMA": product.MaMA,
            "TenMonAn": product.TenMonAn,
            "DonGia": product.DonGia,
            "TrangThai": product.TrangThai,
            "HinhAnh": url_for('static', filename=product.HinhAnh)
        })
    
    # Trả về JSON
    return jsonify(grouped_products)


@order.route('/getCustomerData', methods=['GET'])
def get_customer_data():
    maddh = request.args.get('maddh')
    
    if not maddh:
        return jsonify({"message": "Mã đơn đặt hàng không hợp lệ."}), 400

    # Lấy đơn đặt hàng dựa trên maDDH
    don_dat_hang = DonDatHang.query.filter_by(MaDDH=maddh).first()
    
    if not don_dat_hang:
        return jsonify({"message": "Không tìm thấy đơn đặt hàng với mã này."}), 404
    
    # Lấy thông tin khách hàng từ đơn đặt hàng
    khach_hang = don_dat_hang.hoa_don[0].khach_hang

    if not khach_hang:
        return jsonify({"message": "Không tìm thấy khách hàng cho đơn đặt hàng này."}), 404

    # Trả về dữ liệu khách hàng và thông tin đơn đặt hàng
    return jsonify({
        "KhachHang": {
            "MaKH": khach_hang.MaKH,
            "TenKH": f"{khach_hang.HoKH} {khach_hang.TenKH}",
            "SoDienThoai": khach_hang.SDT,
        },
        "DonDatHang": {
            "MaDDH": maddh,
            "NgayDat": don_dat_hang.NgayDat.strftime('%Y-%m-%d') if don_dat_hang.NgayDat else "N/A",
            "TrangThai": don_dat_hang.TrangThai,
            "Ban": [chitiet.ban.TenBan for chitiet in don_dat_hang.ct_don_dat_hang],
            "TrangThaiHD": "Chưa thanh toán" if don_dat_hang.hoa_don[0].TrangThai == 0 else "Đã thanh toán",
            "DaOrder": 1 if CT_MonAn.query.filter_by(idDDH=don_dat_hang.MaDDH).first() else 0
        }
    }), 200


# Lưu thông tin order đơn hàng
@order.route("/save", methods=["POST"])
def save_order():
    try:
        order_data = request.get_json()
        if not order_data or 'tables' not in order_data or not order_data['tables']:
            return jsonify({"success": False, "message": "Giỏ hàng trống hoặc dữ liệu không hợp lệ!"})
        
        idDDH = order_data.get("idDDH")
        action = order_data.get("action")

        print("idDDH: " + str(idDDH) + ", action: " + str(action))

        if not idDDH:
            return jsonify({"success": False, "message": "Thiếu thông tin idDDH!"}), 400
        
        CT_MonAn.query.filter_by(idDDH=idDDH).delete()

        tongtien_ddh = 0
        for table_id, ds_monan in order_data['tables'].items():
            thanhtien = 0 # Lưu thành tiền của từng bàn
            for id_monan, ct_monan in ds_monan.items():
                quantity = ct_monan.get('quantity')
                note = ct_monan.get('note', None)
                dongia = int(ct_monan.get('price'))

                if not id_monan or not quantity:
                    continue 

                if action == "same":
                    quantity *= len(order_data['tables'])
                thanhtien += quantity * dongia

                ct_mon_an = CT_MonAn(
                    idDDH=idDDH,
                    idMA=id_monan,
                    idBan=table_id,
                    SoLuong=quantity,
                    GhiChu=note
                )
                db.session.add(ct_mon_an)
            
            # Lưu thành tiền vào ct_dondathang
            ct_don_dat_hang = CT_DonDatHang.query.filter_by(idDDH=idDDH, idBan=table_id).first()
            if ct_don_dat_hang:
                ct_don_dat_hang.ThanhTien = thanhtien
                tongtien_ddh += thanhtien

        # Lưu thành tiền cho DonDatHang
        don_dat_hang = DonDatHang.query.get(idDDH)
        don_dat_hang.ThanhTien = tongtien_ddh
        
        db.session.commit()
        return jsonify({"success": True, "message": "Đơn hàng đã được tạo thành công!"}), 201

    except Exception as e:
        db.session.rollback()
        print(str(e))
        return jsonify({"success": False, "message": f"Lỗi xảy ra: {str(e)}"}), 500
    
# Cập nhật trạng thái đơn hàng
@order.route('/updateStatus', methods=['GET', 'POST'])
def update_order_status():
    order_id = request.args.get('maddh')
    status = request.args.get('status')

    if not order_id or not status:
        flash("Không tìm thấy thông tin mã đơn hàng hoặc trạng thái đơn", "error")
        return redirect(url_for('dondathang.ds_dondathang'))

    don_dat_hang = DonDatHang.query.get(order_id)
    if not order:
        flash("Không tìm thấy đơn đặt hàng", "error")
        return redirect(url_for('dondathang.ds_dondathang'))
    print(don_dat_hang.MaDDH, don_dat_hang.NgayDat)
    try:
        # Cập nhật trạng thái đơn hàng
        if status == "start_cooking":
            don_dat_hang.TrangThai = "Đang chế biến"
        elif status == "complete":
            don_dat_hang.TrangThai = "Đã hoàn thành"
        elif status == "cancel":
            don_dat_hang.TrangThai = "Đã hủy"
            
        db.session.commit()

        flash(f"Đơn hàng số {order_id} đã cập nhật trạng thái thành công", "success")
        return redirect(url_for('dondathang.ds_dondathang'))
    except Exception as e:
        print(str(e))
        db.session.rollback()
        flash(f"Đơn hàng số {order_id} đã cập nhật trạng thái thất bại", "error")
        return redirect(url_for('dondathang.ds_dondathang'))

    
