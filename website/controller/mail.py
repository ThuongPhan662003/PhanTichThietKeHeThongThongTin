import datetime
from flask import Blueprint, jsonify, render_template, request
from flask_mail import Message
from website.__init__ import mail_app
from website.role import role_required

mail_sender = Blueprint("mail_sender", __name__)


@mail_sender.route("/send_email/<email>", methods=["GET"])
@role_required(["Quản lý","Nhân viên","Khách hàng"])
def send_email(email, msg_title, msg_body, msg_link, msg_namelink):
    global mail_app
    # msg_title = "This is a test email"

    sender = "n21dccn184@student.ptithcm.edu.vn"
    msg = Message(msg_title, sender=sender, recipients=[email])
    # msg_body = "This is the email body"
    # msg_link = ""
    # msg.body = ""
    # msg_namelink = ""
    data = {
        "app_name": "Grilli - Amazing & Delicious Food",
        "title": msg_title,
        "body": msg_body,
        "link":msg_link,
        "namelink":msg_namelink,
    }

    msg.html = render_template("mail/email.html", data=data)

    try:
        mail_app.send(msg)
        return "successfully"
    except Exception as e:
        print(e)
        return f"the email was not sent {e}"
