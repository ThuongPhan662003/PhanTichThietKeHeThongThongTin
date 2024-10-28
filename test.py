from flask import Flask, session, redirect, url_for, request
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Sử dụng một secret key ngẫu nhiên để tăng cường bảo mật

# Đăng ký OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='593025830495-3305kaj27epnmf86e16tckvbhbnq9d7v.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo',
    client_kwargs={'scope': 'openid profile email'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

@app.route('/')
def index():
    email = session.get('email')
    return f'Hello, {email}!' if email else 'Hello, Guest! <a href="/login">Login</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)
@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()  # Lấy access token từ Google
    resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')  # Gọi endpoint userinfo để lấy thông tin người dùng
    user_info = resp.json()  # Chuyển đổi thông tin người dùng sang định dạng JSON

    # Lưu thông tin vào session
    session['email'] = user_info.get("email")  # Lưu email của người dùng vào session
    session['name'] = user_info.get("given_name")  # Lưu tên của người dùng vào session

    return redirect("/protected_area")


@app.route("/protected_area", methods=["GET", "POST"])
def protected_area():
    # return (
    #     f"Hello {session.get('name')}! <br/> <a href='/logout'><button>Logout</button></a>"
    # )
    return "khun"

@app.route('/logout')
def logout():
    session.pop('email', None)  # Xóa email khỏi session
    session.pop('name', None)   # Xóa tên khỏi session
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
