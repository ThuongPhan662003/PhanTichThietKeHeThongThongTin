from functools import wraps
from os import abort
from flask import (
    Blueprint,
    abort,
    redirect,url_for
)

from flask_login import current_user



def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("chưa")
            if not current_user.is_authenticated:
                
                return redirect(url_for("auth.login"))  # Trang đăng nhập

            if isinstance(required_roles, list):
                print("đăng nhâp")
                # Kiểm tra nếu người dùng có ít nhất một vai trò yêu cầu
                if not any(current_user.has_role(role) for role in required_roles):
                    abort(403)  # Truy cập bị cấm
            else:
                # Kiểm tra một vai trò duy nhất
                if not current_user.has_role(required_roles):
                    abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator