import json
import os
from datetime import datetime

class BackupUtils:
    BACKUP_DIR = 'backups/phieunhap'
    
    @staticmethod
    def backup_to_file(phieu_nhap, current_user):
        if not os.path.exists(BackupUtils.BACKUP_DIR):
            os.makedirs(BackupUtils.BACKUP_DIR)
        
        backup_data = {
            'SoPhieuNhap': phieu_nhap.SoPhieuNhap,
            'idNV': phieu_nhap.idNV,
            'NgayNhap': phieu_nhap.NgayNhap.strftime('%d-%m-%Y %H:%M:%S'),
            'TongTien': float(phieu_nhap.TongTien),
            'NgayXoa': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'NguoiXoa': current_user.MaND,
            'DaKhoiPhuc': False,  # Thêm trạng thái đã khôi phục
            'ChiTiet': [{
                'idNL': ct.idNL,
                'SoLuong': float(ct.SoLuong),
                'ThanhTien': float(ct.ThanhTien)
            } for ct in phieu_nhap.chi_tiet_phieu]
        }
        
        filename = f"{BackupUtils.BACKUP_DIR}/PN_{phieu_nhap.SoPhieuNhap}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        return filename

    @staticmethod 
    def mark_as_restored(filename):
        filepath = os.path.join(BackupUtils.BACKUP_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['DaKhoiPhuc'] = True
        data['NgayKhoiPhuc'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get_all_backups():
        if not os.path.exists(BackupUtils.BACKUP_DIR):
            os.makedirs(BackupUtils.BACKUP_DIR)
            
        backup_files = []
        today = datetime.now().date()
        
        for filename in os.listdir(BackupUtils.BACKUP_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(BackupUtils.BACKUP_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ngay_xoa = datetime.strptime(data['NgayXoa'], '%d-%m-%Y %H:%M:%S')
                    
                    data['filename'] = filename
                    data['can_restore'] = (
                        ngay_xoa.date() == today and 
                        not data.get('DaKhoiPhuc', False)  # Kiểm tra trạng thái đã khôi phục
                    )
                    
                    backup_files.append(data)
                    
        return sorted(backup_files, key=lambda x: x['NgayXoa'], reverse=True)

    @staticmethod
    def can_restore(filename):
        filepath = os.path.join(BackupUtils.BACKUP_DIR, filename)
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ngay_xoa = datetime.strptime(data['NgayXoa'], '%d-%m-%Y %H:%M:%S')
            return (
                ngay_xoa.date() == datetime.now().date() and 
                not data.get('DaKhoiPhuc', False)  # Kiểm tra trạng thái đã khôi phục
            )
        
class BackupUtilsPhieuXuat:
    BACKUP_DIR = 'backups/phieuxuat'
    
    @staticmethod
    def backup_to_file(phieu_xuat, current_user):
        if not os.path.exists(BackupUtilsPhieuXuat.BACKUP_DIR):
            os.makedirs(BackupUtilsPhieuXuat.BACKUP_DIR)
        
        backup_data = {
            'SoPhieuXuat': phieu_xuat.SoPhieuXuat,
            'idNV': phieu_xuat.idNV,
            'NgayXuat': phieu_xuat.NgayXuat.strftime('%d-%m-%Y %H:%M:%S'),
            'NgayXoa': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'NguoiXoa': current_user.MaND,
            'DaKhoiPhuc': False,
            'ChiTiet': [{
                'idNL': ct.idNL,
                'SoLuong': float(ct.SoLuong),
            } for ct in phieu_xuat.chi_tiet_phieu]
        }
        
        filename = f"{BackupUtilsPhieuXuat.BACKUP_DIR}/PX_{phieu_xuat.SoPhieuXuat}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        return filename

    @staticmethod 
    def mark_as_restored(filename):
        filepath = os.path.join(BackupUtilsPhieuXuat.BACKUP_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['DaKhoiPhuc'] = True
        data['NgayKhoiPhuc'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get_all_backups():
        if not os.path.exists(BackupUtilsPhieuXuat.BACKUP_DIR):
            os.makedirs(BackupUtilsPhieuXuat.BACKUP_DIR)
            
        backup_files = []
        today = datetime.now().date()
        
        for filename in os.listdir(BackupUtilsPhieuXuat.BACKUP_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(BackupUtilsPhieuXuat.BACKUP_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ngay_xoa = datetime.strptime(data['NgayXoa'], '%d-%m-%Y %H:%M:%S')
                    
                    data['filename'] = filename
                    data['can_restore'] = (
                        ngay_xoa.date() == today and 
                        not data.get('DaKhoiPhuc', False)
                    )
                    
                    backup_files.append(data)
                    
        return sorted(backup_files, key=lambda x: x['NgayXoa'], reverse=True)

    @staticmethod
    def can_restore(filename):
        filepath = os.path.join(BackupUtilsPhieuXuat.BACKUP_DIR, filename)
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ngay_xoa = datetime.strptime(data['NgayXoa'], '%d-%m-%Y %H:%M:%S')
            return (
                ngay_xoa.date() == datetime.now().date() and 
                not data.get('DaKhoiPhuc', False)
            )