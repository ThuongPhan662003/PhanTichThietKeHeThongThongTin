import datetime
from flask import Blueprint, jsonify, render_template, request
from flask_mail import Message
from website.__init__ import mail_app

mail_sender = Blueprint("mail_sender", __name__)


@mail_sender.route("/send_email/<email>", methods=["GET"])
def send_email(email):
    global mail_app
    msg_title = "This is a test email"

    sender = "n21dccn184@student.ptithcm.edu.vn"
    msg = Message(msg_title, sender=sender, recipients=[email])
    msg_body = "This is the email body"
    msg.body = ""
    data = {
        "app_name": "REBWAR AI",
        "title": msg_title,
        "body": msg_body,
    }

    msg.html = render_template("mail/email.html", data=data)

    try:
        mail_app.send(msg)
        return "Email sent..."
    except Exception as e:
        print(e)
        return f"the email was not sent {e}"
