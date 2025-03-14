from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
                return redirect(url_for('login'))
            
            if permission == 'view' and not current_user.has_view_permission():
                flash('Bạn không có quyền xem nội dung này.', 'error')
                return redirect(url_for('index'))
            elif permission == 'edit' and not current_user.has_edit_permission():
                flash('Bạn không có quyền chỉnh sửa nội dung này.', 'error')
                return redirect(url_for('index'))
            elif permission == 'delete' and not current_user.has_delete_permission():
                flash('Bạn không có quyền xóa nội dung này.', 'error')
                return redirect(url_for('index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def viewer_required(f):
    return permission_required('view')(f)

def collaborator_required(f):
    return permission_required('edit')(f)

def editor_required(f):
    return permission_required('delete')(f)
