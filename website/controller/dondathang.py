from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website import db
from datetime import datetime, timedelta
from website.models import *
from sqlalchemy import func, extract


dondathang = Blueprint("dondathang", __name__)

@dondathang.route("/confirm", methods=["GET"])
@login_required
def confirm():
    current = datetime.now()
    print(current)
    unconfirmed_orders = db.session.query(DonDatHang).outerjoin(
        CT_DonDatHang,
        DonDatHang.MaDDH == CT_DonDatHang.idDDH
    ).filter(
        CT_DonDatHang.idDDH.is_(None),  
        DonDatHang.Loai == 1,  
        DonDatHang.TrangThai != 'Đã hoàn thành'
    ).all()

    return render_template(
        "admin/dondathang/confirm.html",
        orders=unconfirmed_orders,
        customers=KhachHang.query.all(),
        tables=[]  
    )
@dondathang.route("/get-available-tables/<int:order_id>")
@login_required
def get_available_tables(order_id):
    current_order = DonDatHang.query.get_or_404(order_id)
    current_time_start = current_order.GioDen
    current_duration = float(current_order.ThoiLuong)
    
    current_start_minutes = current_time_start.hour * 60 + current_time_start.minute
    current_end_minutes = current_start_minutes + (current_duration * 60)

    other_orders = db.session.query(DonDatHang, CT_DonDatHang).join(
        CT_DonDatHang,
        DonDatHang.MaDDH == CT_DonDatHang.idDDH
    ).filter(
        DonDatHang.NgayDat == current_order.NgayDat,
        DonDatHang.MaDDH != order_id,
        DonDatHang.TrangThai != 'Đã hoàn thành'
    ).all()

    busy_table_ids = set()
    
    for order, ct_order in other_orders:
        other_start = order.GioDen
        other_start_minutes = other_start.hour * 60 + other_start.minute
        other_end_minutes = other_start_minutes + (float(order.ThoiLuong) * 60)
        
        if not (current_end_minutes <= other_start_minutes or other_end_minutes <= current_start_minutes):
            busy_table_ids.add(ct_order.idBan)
    
    available_tables = Ban.query.filter(
        ~Ban.MaBan.in_(busy_table_ids) if busy_table_ids else True
    ).all()

    return jsonify([{
        'MaBan': table.MaBan,
        'TenBan': table.TenBan
    } for table in available_tables])
from datetime import datetime, time

@dondathang.route("/luu-chi-tiet-ban/<int:ma_ddh>", methods=["POST"])
@login_required
def luu_chi_tiet_ban(ma_ddh):
    try:
        don_dat_hang = DonDatHang.query.get_or_404(ma_ddh)

        ma_ban_list = request.form.get('maBan', '').split(',')
        if not ma_ban_list or ma_ban_list[0] == '':
            flash('Vui lòng chọn ít nhất một bàn', 'danger')
            return redirect(url_for('dondathang.confirm'))

        other_bookings = db.session.query(DonDatHang, CT_DonDatHang).join(
            CT_DonDatHang,
            DonDatHang.MaDDH == CT_DonDatHang.idDDH
        ).filter(
            DonDatHang.NgayDat == don_dat_hang.NgayDat,
            DonDatHang.MaDDH != ma_ddh,
            DonDatHang.TrangThai != 'Đã hoàn thành',
            CT_DonDatHang.idBan.in_([int(ma_ban) for ma_ban in ma_ban_list if ma_ban])
        ).all()

        current_start = don_dat_hang.GioDen.hour * 60 + don_dat_hang.GioDen.minute
        current_end = current_start + int(float(don_dat_hang.ThoiLuong) * 60)

        for booking, ct_booking in other_bookings:
            booking_start = booking.GioDen.hour * 60 + booking.GioDen.minute
            booking_end = booking_start + int(float(booking.ThoiLuong) * 60)

            if (current_start < booking_end and current_end > booking_start):
                flash(f'Bàn {ct_booking.idBan} đã được đặt trong khoảng thời gian từ {booking.GioDen} đến {booking_end//60}:{booking_end%60}', 'danger')
                return redirect(url_for('dondathang.confirm'))
        if request.form.get('ngayDat'):
            don_dat_hang.NgayDat = datetime.strptime(request.form.get('ngayDat'), '%Y-%m-%d').date()
            
        if request.form.get('gioDen'):
            gio_den_str = request.form.get('gioDen')
            try:
                don_dat_hang.GioDen=gio_den_str
              
            except ValueError as ve:
                parts = gio_den_str.split(':')
                if len(parts) != 3:  
                    raise ValueError("Giờ đến không đúng định dạng HH:mm:ss!")
                hour, minute, second = map(int, parts)
                don_dat_hang.GioDen = time(hour, minute, second)

        if request.form.get('soLuongNguoi'):
            don_dat_hang.SoLuongNguoi = int(request.form.get('soLuongNguoi'))
            
        if request.form.get('thoiluong'):
            don_dat_hang.ThoiLuong = float(request.form.get('thoiluong'))
            
        if request.form.get('ghiChu'):
            don_dat_hang.GhiChu = request.form.get('ghiChu')

        for ma_ban in ma_ban_list:
            if ma_ban: 
                existing_detail = CT_DonDatHang.query.filter_by(
                    idDDH=ma_ddh,
                    idBan=int(ma_ban)
                ).first()
                
                if not existing_detail:
                    chi_tiet = CT_DonDatHang(
                        idDDH=ma_ddh,
                        idBan=int(ma_ban),
                        ThanhTien=0  
                    )
                    db.session.add(chi_tiet)

        ma_kh = request.form.get('maKH')

        if not ma_kh:
            flash('Vui lòng chọn khách hàng', 'danger')
            return redirect(url_for('dondathang.confirm'))

        hoa_don = HoaDon(
            idKH=int(ma_kh),
            idDDH=ma_ddh,
            idNV=current_user.MaND,
            NgayXuat=datetime.now(),
            TongTienGiam=0,  
            TongTien=0,
            TrangThai=0,
            TienThue='0',   
            DiemCong=0,     
            DiemTru=0     
        )
        db.session.add(hoa_don)
        
        db.session.commit()
        
        flash('Đã xác nhận đơn đặt hàng và tạo hóa đơn thành công!', 'success')
        return redirect(url_for('dondathang.confirm'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Đã có lỗi xảy ra: {str(e)}', 'danger')
        return redirect(url_for('dondathang.confirm'))

@dondathang.route("/ds-dondathang", methods=["GET"])
@login_required
def ds_dondathang():
    now = datetime.now()
    page = request.args.get("page", 1, type=int)
    per_page = 10
    customers = KhachHang.query.order_by(KhachHang.NgayMoThe).all()
    query = DonDatHang.query.join(
        CT_DonDatHang,
        DonDatHang.MaDDH == CT_DonDatHang.idDDH
    ).distinct()

    show_all = request.args.get("show_all") == "1"
    selected_status = request.args.getlist("status")
    selected_types = request.args.getlist("type")
    selected_year = request.args.get("year", "")
    selected_month = request.args.get("month", "")
    selected_day = request.args.get("day", "")
    price_min = request.args.get("price_min", "")
    price_max = request.args.get("price_max", "")

    # Chỉ áp dụng filter ngày hiện tại nếu không có lọc thời gian và không show_all
    if not show_all and not (selected_year or selected_month or selected_day):
        query = query.filter(DonDatHang.NgayDat == now.date())

    if selected_status:
        query = query.filter(DonDatHang.TrangThai.in_(selected_status))

    if selected_types:
        query = query.filter(DonDatHang.Loai.in_([t == "1" for t in selected_types]))

    # Lọc theo thời gian (luôn hiển thị tất cả)
    if selected_year and selected_month and selected_day:
        query = query.filter(
            extract("year", DonDatHang.NgayDat) == int(selected_year),
            extract("month", DonDatHang.NgayDat) == int(selected_month),
            extract("day", DonDatHang.NgayDat) == int(selected_day)
        )
    elif selected_year and selected_month:
        query = query.filter(
            extract("year", DonDatHang.NgayDat) == int(selected_year),
            extract("month", DonDatHang.NgayDat) == int(selected_month)
        )
    elif selected_year:
        query = query.filter(
            extract("year", DonDatHang.NgayDat) == int(selected_year)
        )
    elif selected_month:
        query = query.filter(
            extract("month", DonDatHang.NgayDat) == int(selected_month)
        )
    elif selected_day:
        query = query.filter(
            extract("day", DonDatHang.NgayDat) == int(selected_day)
        )
    try:
        if price_min:
            price_min_value = float(price_min.replace(".", "").replace(",", ""))
            query = query.filter(DonDatHang.ThanhTien >= price_min_value)
    except ValueError:
        price_min = ""

    try:
        if price_max:
            price_max_value = float(price_max.replace(".", "").replace(",", ""))
            query = query.filter(DonDatHang.ThanhTien <= price_max_value)
    except ValueError:
        price_max = ""

    pagination = query.order_by(DonDatHang.MaDDH.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    orders = pagination.items

    try:
        if price_min and float(price_min.replace(".", "").replace(",", "")):
            price_min = "{:,.0f}".format(
                float(price_min.replace(".", "").replace(",", ""))
            )
    except ValueError:
        pass

    try:
        if price_max and float(price_max.replace(".", "").replace(",", "")):
            price_max = "{:,.0f}".format(
                float(price_max.replace(".", "").replace(",", ""))
            )
    except ValueError:
        pass

    def make_query_string(**new_values):
        args = request.args.copy()
        for key, value in new_values.items():
            args[key] = value
        return args

    return render_template(
         "admin/dondathang/dsDonDatHang.html",
        orders=orders,
        pagination=pagination,
        now=now,
        selected_status=selected_status,
        selected_types=selected_types,
        selected_year=(int(selected_year) if selected_year and selected_year.isdigit() else None),
        selected_month=(int(selected_month) if selected_month and selected_month.isdigit() else None),
        selected_day=(int(selected_day) if selected_day and selected_day.isdigit() else None),
        price_min=price_min,
        price_max=price_max,
        make_query_string=make_query_string,
        show_all=show_all,
        customers=customers
    )


@dondathang.route("/quan-ly-dat-ban")
@login_required
def manage_booking():
    orders = DonDatHang.query.order_by(DonDatHang.MaDDH.desc()).all()
    customers = KhachHang.query.all()
    # tables = Ban.query.order_by(Ban.MaBan.asc()).all()
    tables = Ban.query.filter(
                ~Ban.TenBan.ilike('%Bàn chờ%')
            ).all()
    print(tables)
    events = []

    for order in orders:
        if order.ThoiLuong is not None:
            start_time = datetime.combine(order.NgayDat, order.GioDen)
            end_time = start_time + timedelta(hours=order.ThoiLuong)

            table_names = [ct.ban.TenBan for ct in order.ct_don_dat_hang]
            table_ids = [ct.idBan for ct in order.ct_don_dat_hang]

            STATUS_STYLES = {
                "Chưa bắt đầu": {
                    "backgroundColor": "#fff3e0",
                    "borderColor": "#FFA500",
                    "textColor": "#f57c00",
                },
                "Đang chế biến": {
                    "backgroundColor": "#e3f2fd",
                    "borderColor": "#3498db",
                    "textColor": "#1976d2",
                },
                "Đã hoàn thành": {
                    "backgroundColor": "#e8f5e9",
                    "borderColor": "#2ecc71",
                    "textColor": "#388e3c",
                },
                "Đã hủy": {
                    "backgroundColor": "#ffebee",
                    "borderColor": "#e74c3c",
                    "textColor": "#d32f2f",
                },
            }

            for ct in order.ct_don_dat_hang:
                status_style = STATUS_STYLES.get(
                    order.TrangThai,
                    {
                        "backgroundColor": "#13795b",
                        "borderColor": "#13795b",
                        "textColor": "#ffffff",
                    },
                )

                event = {
                    "id": order.MaDDH,
                    "title": f"{order.TrangThai}",
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "resourceId": ct.idBan,
                    "backgroundColor": status_style["backgroundColor"],
                    "borderColor": status_style["borderColor"],
                    "textColor": status_style["textColor"],
                    "extendedProps": {
                        "maDDH": order.MaDDH,
                        "soKhach": order.SoLuongNguoi,
                        "tableIds": table_ids,
                        "tableNames": table_names,
                        "thoiLuong": order.ThoiLuong,
                    },
                }
                events.append(event)

    resources = []
    for table in tables:
        resources.append(
            {
                "id": table.MaBan,
                "title": table.TenBan,
                "loaiBanId": table.idLoaiBan,
                "loaiBanName": table.loai_ban.TenLoaiBan,
            }
        )

    loai_ban = LoaiBan.query.all()
    resource_groups = []
    for loai in loai_ban:
        resource_groups.append({"id": loai.MaLB, "title": loai.TenLoaiBan})

    return render_template(
        "admin/dondathang/dondathang.html",
        tables=tables,
        events=events,
        orders=orders,
        customers=customers,
        tables_data=resources,
        loai_ban_data=resource_groups,
    )


@dondathang.route("/them-don-dat-hang", methods=["POST"])
@login_required
def them_don_dat_hang():
    try:
        maKH = request.form.get("maKH")
        ngayDat = datetime.strptime(request.form.get("ngayDat"), "%Y-%m-%d")
        gioDen = datetime.strptime(request.form.get("gioDen"), "%H:%M").time()
        thoiLuong = float(request.form.get("thoiLuong"))
        soLuongNguoi = int(request.form.get("soLuongNguoi"))
        ghiChu = request.form.get("ghiChu")
        maBanList = request.form.get("maBan").split(",")

        start_time = datetime.combine(ngayDat, gioDen)
        end_time = start_time + timedelta(hours=thoiLuong)
        current_time = datetime.now()

        if start_time < current_time:
            flash("Không thể đặt bàn cho thời điểm trong quá khứ", "danger")
            return redirect(url_for("dondathang.manage_booking"))

        for maBan in maBanList:
            if not maBan:
                continue

            overlapping_orders = (
                DonDatHang.query.join(CT_DonDatHang)
                .filter(
                    CT_DonDatHang.idBan == int(maBan),
                    DonDatHang.NgayDat == ngayDat,
                    DonDatHang.TrangThai != "Đã hủy",
                )
                .all()
            )

            for order in overlapping_orders:
                order_start = datetime.combine(order.NgayDat, order.GioDen)
                order_end = order_start + timedelta(hours=order.ThoiLuong)

                if start_time < order_end and end_time > order_start:
                    ban = Ban.query.get(int(maBan))
                    flash(
                        f"{ban.TenBan} đã được đặt trong khoảng thời gian này", "danger"
                    )
                    return redirect(url_for("dondathang.manage_booking"))

        don_dat_hang = DonDatHang(
            NgayDat=ngayDat,
            TrangThai="Chưa bắt đầu",
            Loai=True,
            GioDen=gioDen,
            ThoiLuong=thoiLuong,
            SoLuongNguoi=soLuongNguoi,
            idNV=current_user.MaND,
            ThanhTien=0.00,
            GhiChu=ghiChu if ghiChu else None,
        )

        db.session.add(don_dat_hang)
        db.session.flush()

        hoa_don = HoaDon(
            idKH=maKH,
            idDDH=don_dat_hang.MaDDH,
            idNV=current_user.MaND,
            TongTienGiam=0,
            TongTien=0,
            TrangThai=False,
            TienThue=0,
            DiemCong=0,
            DiemTru=0,
        )

        db.session.add(hoa_don)
        db.session.flush()

        for maBan in maBanList:
            if maBan:
                ct_ddh = CT_DonDatHang(idDDH=don_dat_hang.MaDDH, idBan=int(maBan))
                db.session.add(ct_ddh)

        db.session.commit()

        flash("Thêm đơn đặt hàng thành công!", "success")
        return redirect(url_for("dondathang.manage_booking"))

    except ValueError as ve:
        db.session.rollback()
        flash(f"Lỗi dữ liệu không hợp lệ: {str(ve)}", "danger")
        return redirect(url_for("dondathang.manage_booking"))

    except Exception as e:
        db.session.rollback()
        flash(f"Có lỗi xảy ra khi tạo đơn hàng: {str(e)}", "danger")
        return redirect(url_for("dondathang.manage_booking"))


@dondathang.route("/sua-don-dat-hang", methods=["POST"])
@login_required
def sua_don_dat_hang():
    try:
        ma_ddh = request.form.get("maDDH")
        gio_den = request.form.get("gioDen")
        thoi_luong = float(request.form.get("thoiLuong"))
        so_khach = int(request.form.get("soKhach"))
        trang_thai = request.form.get("trangThai")

        don_dat_hang = DonDatHang.query.get(ma_ddh)
        if not don_dat_hang:
            flash("Không tìm thấy đơn đặt hàng!", "danger")
            return redirect(url_for("dondathang.manage_booking"))

        if don_dat_hang.TrangThai == "Đã hoàn thành":
            flash("Không thể sửa đơn đã hoàn thành!", "danger")
            return redirect(url_for("dondathang.manage_booking"))

        gio_moi = datetime.strptime(gio_den, "%H:%M").time()
        start_time = datetime.combine(don_dat_hang.NgayDat, gio_moi)
        end_time = start_time + timedelta(hours=thoi_luong)

        if start_time < datetime.now():
            flash("Không thể đặt bàn cho thời điểm trong quá khứ", "danger")
            return redirect(url_for("dondathang.manage_booking"))

        for ct in don_dat_hang.ct_don_dat_hang:
            overlapping_orders = (
                DonDatHang.query.join(CT_DonDatHang)
                .filter(
                    CT_DonDatHang.idBan == ct.idBan,
                    DonDatHang.NgayDat == don_dat_hang.NgayDat,
                    DonDatHang.MaDDH != ma_ddh,
                    DonDatHang.TrangThai != "Đã hủy",
                )
                .all()
            )

            for order in overlapping_orders:
                order_start = datetime.combine(order.NgayDat, order.GioDen)
                order_end = order_start + timedelta(hours=order.ThoiLuong)

                if start_time < order_end and end_time > order_start:
                    flash(
                        f"{ct.ban.TenBan} đã được đặt trong khoảng thời gian này",
                        "danger",
                    )
                    return redirect(url_for("dondathang.manage_booking"))

        don_dat_hang.GioDen = gio_moi
        don_dat_hang.ThoiLuong = thoi_luong
        don_dat_hang.SoLuongNguoi = so_khach
        if trang_thai:
            don_dat_hang.TrangThai = trang_thai

        db.session.commit()
        if trang_thai == "Đã hủy":
            flash("Đã hủy đơn hàng thành công!", "success")
        else:
            flash("Cập nhật thành công!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Có lỗi xảy ra: {str(e)}", "danger")

    return redirect(url_for("dondathang.manage_booking"))


@dondathang.route("/cap-nhat-ban", methods=["POST"])
@login_required
def cap_nhat_ban():
    try:
        ma_ddh = request.form.get("maDDH")
        ban_cu = request.form.get("banCu")
        ban_moi = request.form.get("banMoi")
        gio_den_moi = datetime.strptime(request.form.get("gioDen"), "%H:%M").time()

        don_dat_hang = DonDatHang.query.get(ma_ddh)
        if not don_dat_hang:
            flash("Không tìm thấy đơn đặt hàng", "danger")
            return redirect(url_for("dondathang.manage_booking"))

        if (
            don_dat_hang.TrangThai == "Đã hoàn thành"
            or don_dat_hang.TrangThai == "Đã hủy"
        ):
            flash("Không thể chỉnh sửa đơn đã hoàn thành hoặc đã hủy", "danger")
            return redirect(url_for("dondathang.manage_booking"))
        if len(don_dat_hang.ct_don_dat_hang) > 1:
            flash("Không thể di chuyển đơn có nhiều bàn", "danger")
            return redirect(url_for("dondathang.manage_booking"))

        is_table_change = ban_cu != ban_moi
        target_ban = ban_moi if is_table_change else ban_cu
        action_type = "bàn" if is_table_change else "giờ"

        start_time = datetime.combine(don_dat_hang.NgayDat, gio_den_moi)
        end_time = start_time + timedelta(hours=don_dat_hang.ThoiLuong)

        overlapping_orders = (
            DonDatHang.query.join(CT_DonDatHang)
            .filter(
                CT_DonDatHang.idBan == target_ban,
                DonDatHang.NgayDat == don_dat_hang.NgayDat,
                DonDatHang.MaDDH != ma_ddh,
                DonDatHang.TrangThai != "Đã hủy",
            )
            .all()
        )

        has_overlap = False
        for order in overlapping_orders:
            order_start = datetime.combine(order.NgayDat, order.GioDen)
            order_end = order_start + timedelta(hours=order.ThoiLuong)

            if start_time < order_end and end_time > order_start:
                has_overlap = True
                break

        if has_overlap:
            if is_table_change:
                flash(f"Bàn đã được đặt trong khoảng thời gian này", "danger")
            else:
                flash(f"Khung giờ này đã có đơn đặt khác", "danger")
            return redirect(url_for("dondathang.manage_booking"))

        if is_table_change:
            ct_ddh = CT_DonDatHang.query.filter_by(idDDH=ma_ddh, idBan=ban_cu).first()
            if ct_ddh:
                ct_ddh.idBan = ban_moi
            else:
                flash("Không tìm thấy chi tiết đơn đặt hàng", "danger")
                return redirect(url_for("dondathang.manage_booking"))

        don_dat_hang.GioDen = gio_den_moi
        db.session.commit()

        if is_table_change:
            flash(f"Đã chuyển bàn và cập nhật giờ đến thành công", "success")
        else:
            flash(f"Đã cập nhật giờ đến thành công", "success")

        return redirect(url_for("dondathang.manage_booking"))

    except Exception as e:
        db.session.rollback()
        flash(f"Có lỗi xảy ra: {str(e)}", "danger")
        return redirect(url_for("dondathang.manage_booking"))


def xoa_don_dat_hang_cu():
    from website import db  # Import db
    from website.models import DonDatHang, HoaDon, CT_DonDatHang
    from datetime import datetime

    print("Bắt đầu xóa đơn đặt hàng cũ")
    try:
        don_dat_hangs = DonDatHang.query.filter(
            DonDatHang.NgayDat < datetime.now().date(),
            DonDatHang.ThanhTien == 0,
            DonDatHang.TrangThai.in_(["Đã hủy", "Chưa bắt đầu", "Đang chế biến"]),
        ).all()

        count = 0
        for don in don_dat_hangs:
            try:
                CT_DonDatHang.query.filter_by(idDDH=don.MaDDH).delete()
                HoaDon.query.filter_by(idDDH=don.MaDDH).delete()

                db.session.delete(don)
                db.session.commit()
                count += 1
            except Exception as e:
                print(f"Lỗi khi xóa đơn đặt hàng {don.MaDDH}: {str(e)}")
                db.session.rollback()
                continue

        db.session.commit()
        print(f"Đã xóa thành công {count} đơn đặt hàng cũ")

    except Exception as e:
        print(f"Lỗi trong quá trình xóa đơn đặt hàng: {str(e)}")
        db.session.rollback()
