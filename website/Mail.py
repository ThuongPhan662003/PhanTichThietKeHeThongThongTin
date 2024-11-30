from flask_mail import Message

mail = None


class EmailSender:
    def __init__(self, mail):
        """Khởi tạo đối tượng EmailSender với đối tượng Flask-Mail"""
        self.mail = mail

    def send_email(self, subject, recipient, body, html=None):
        """Phương thức gửi email"""
        try:
            msg = Message(subject, recipients=[recipient])
            msg.body = body  # Nội dung email dạng văn bản
            if html:
                msg.html = html  # Nếu có nội dung HTML, gửi kèm HTML

            # Gửi email
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
