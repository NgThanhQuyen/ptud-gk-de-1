from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql.functions import user
from sqlalchemy.sql import func
from werkzeug.exceptions import RequestURITooLarge
from .models import Task, User, Comment
from datetime import timedelta
from . import db
import json
import random
import string

views = Blueprint("views", __name__)

@views.route("/home", methods=["GET"])
@views.route("/", methods=["GET"])
@login_required
def home():
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Số lượng task trên mỗi trang
    
    pagination = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template("index.html", user=current_user, pagination=pagination, timedelta=timedelta)


@views.route("/add-task", methods=["POST"])
@login_required
def add_task():
    data = request.get_json()
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    image_url = data.get("image_url", "").strip()  # Lấy URL hình ảnh từ request

    if not title or not body:
        return jsonify({"success": False, "message": "The title and details cannot be empty."}), 400

    new_task = Task(
        title=title, 
        body=body, 
        user_id=current_user.id,
        image_url=image_url  # Thêm URL hình ảnh vào task mới
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "success": True, 
        "task_id": new_task.id, 
        "title": new_task.title, 
        "body": new_task.body,
        "image_url": new_task.image_url,  # Thêm URL hình ảnh vào response
        "date": new_task.date.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

@views.route("/update-task/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Kiểm tra quyền chỉnh sửa
    if task.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    data = request.get_json()
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    image_url = data.get("image_url", "").strip()  # Lấy URL hình ảnh từ request
    
    if not title or not body:
        return jsonify({"success": False, "message": "Title and body cannot be empty"}), 400
    
    task.title = title
    task.body = body
    task.image_url = image_url  # Cập nhật URL hình ảnh
    db.session.commit()
    
    return jsonify({
        "success": True,
        "title": task.title,
        "body": task.body,
        "image_url": task.image_url,  # Thêm URL hình ảnh vào response
        "date": task.date.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

@views.route("/delete-tasks", methods=["POST"])
@login_required
def delete_tasks():
    data = request.get_json()
    task_ids = data.get("task_ids", [])

    if not task_ids:
        return jsonify({"success": False, "message": "No task is selected"}), 400

    Task.query.filter(Task.id.in_(task_ids), Task.user_id == current_user.id).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({"success": True, "deleted_tasks": task_ids}), 200


# Định nghĩa route để xóa nhiều task
@views.route("/delete-notes", methods=["POST"])
def delete_notes():
    data = json.loads(request.data)
    note_ids = data.get("note_ids", [])

    print("Received task IDs:", note_ids)  # Debug xem có nhận đủ ID không

    if not note_ids:
        return jsonify({"code": 400, "message": "No notes provided"})

    notes = Task.query.filter(Task.id.in_(note_ids), Task.user_id == current_user.id).all()

    if notes:
        for task in notes:
            db.session.delete(task)
        db.session.commit()

    return jsonify({"code": 200, "message": "Tasks deleted successfully"})

#Chọn tất cả tasktask
@views.route("/get-all-tasks", methods=["GET"])
@login_required
def get_all_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    task_ids = [task.id for task in tasks]
    return jsonify({"task_ids": task_ids})

# Ngăn user bị khóa đăng nhập
def check_user_status(user):
    if user.is_locked:
        flash("Tài khoản của bạn đã bị khóa!", "error")
        return redirect(url_for("user.login"))
    return None

# Trang quản lý của adminadmin
@views.route("/admin/manage")
@login_required
def admin_manage():
    if not current_user.is_admin:
        flash("You don't have access!", "error")
        return redirect(url_for("views.home"))

    users = User.query.filter_by(is_admin=False).all()
    return render_template("admin_manage.html", users=users, user=current_user)  # 🔹 Đảm bảo truyền user


@views.route("/admin/lock/<int:user_id>")
@login_required
def lock_user(user_id):
    if not current_user.is_admin:
        flash("You don't have the right to do this!", "error")
        return redirect(url_for("views.admin_manage"))
    user = User.query.get(user_id)
    if user:
        user.is_locked = True
        db.session.commit()
        flash(f"The account has been locked: {user.email}", "success")

    return redirect(url_for("views.admin_manage"))


@views.route("/admin/unlock/<int:user_id>")
@login_required
def unlock_user(user_id):
    if not current_user.is_admin:
        flash("You don't have the right to do this!", "error")
        return redirect(url_for("views.admin_manage"))

    user = User.query.get(user_id)
    if user:
        user.is_locked = False
        db.session.commit()
        flash(f"Account unlocked: {user.email}", "success")

    return redirect(url_for("views.admin_manage"))


@views.route("/admin/reset-password/<int:user_id>")
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        flash("You don't have the right to do this!", "error")
        return redirect(url_for("views.admin_manage"))

    user = User.query.get(user_id)
    if user:
        # Tạo mật khẩu ngẫu nhiên gồm 8 ký tự (bao gồm chữ hoa, chữ thường và số)
        characters = string.ascii_letters + string.digits
        new_password = ''.join(random.choices(characters, k=8))
        user.plain_password = new_password  # lưu mật khẩu gốc
        user.password = generate_password_hash(new_password, method="pbkdf2:sha256")
        db.session.commit()
        flash(f"The password for {user.email} has been changed to {new_password}", "success")

    return redirect(url_for("views.admin_manage"))

@views.route("/add-comment/<int:task_id>", methods=["POST"])
@login_required
def add_comment(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    content = data.get("content", "").strip()
    
    if not content:
        return jsonify({"success": False, "message": "Comment cannot be empty"}), 400
        
    new_comment = Comment(
        content=content,
        user_id=current_user.id,
        task_id=task_id
    )
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "comment_id": new_comment.id,
        "content": new_comment.content,
        "date": new_comment.date.strftime("%Y-%m-%d %H:%M:%S"),
        "user_name": current_user.user_name
    }), 200

@views.route("/delete-comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the user is the comment owner or an admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"success": True}), 200
