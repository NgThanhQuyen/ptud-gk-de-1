from enum import Enum
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

class UserRole(Enum):
    VIEWER = 1      # Chỉ xem
    COLLABORATOR = 2  # Xem và sửa
    EDITOR = 3      # Xem, sửa và xóa

def viewer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập.', 'error')
            return redirect(url_for('login'))
        # Viewer trở lên đều có thể xem
        if not current_user.role or current_user.role < UserRole.VIEWER.value:
            flash('Bạn không có quyền xem trang này.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def collaborator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập.', 'error')
            return redirect(url_for('login'))
        # Chỉ Collaborator và Editor mới có thể sửa
        if not current_user.role or current_user.role < UserRole.COLLABORATOR.value:
            flash('Bạn không có quyền chỉnh sửa.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập.', 'error')
            return redirect(url_for('login'))
        # Chỉ Editor mới có quyền xóa
        if not current_user.role or current_user.role < UserRole.EDITOR.value:
            flash('Bạn không có quyền xóa.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function 