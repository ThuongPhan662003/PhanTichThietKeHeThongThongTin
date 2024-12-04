# Flask Web App Tutorial

## Setup & Installation

Make sure you have the latest version of Python installed.

```bash
git clone <repo-url>
```

```bash
pip install -r requirements.txt
```

## Running The App

```bash
python main.py
```

## Change the app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:passwword@localhost/database_name'

## Mọi người thêm một file config.json và thư mục json rồi bổ sung những thông tin như username, password, database

ví dụ:
{
    "username": "root",
    "password": "thuong",
    "database": "qlnh",
    "SQLALCHEMY_TRACK_MODIFICATIONS":"False",
    "SECRET_KEY":"hjshjhdjah kjshkjdhjs",
    "MAIL_USERNAME":"phanthuong2468@gmail.com",
    "MAIL_PORT":587,
    "MAIL_SERVER":"smtp.gmail.com",
    "MAIL_USE_TLS":"True",
    "MAIL_PASSWORD":"pnlf rsqv wowr ljon"


}

## Viewing The App

Go to `http://127.0.0.1:5000/auth/login`

### Chia task

### Chú ý: ghi tên bảng them dạng capital (ví dụ: NhomNguoiDung)

### Chú ý: ghi tên thuộc tính giống như trong db(MySQL)

### Đánh [X] là đã xong

Thương:

- loaiban [x]
- dondathang [x]
- hoadon [x]
- monan [x]
- nguoidung [x]
- nguyenlieu [x]
- ct_dondathang [x]
- ct_monan [x]
- ban [x]
- nhomnguoidung [x]
- chucnang
  Long:
- phieunhap
- phieuxuat
- nhanvien [x]
- khachhang [x]
- voucher
- loaivoucher
- phanquyen
- ct_phieunhap
- ct_phieuxuat
- ct_voucher
- thamso
