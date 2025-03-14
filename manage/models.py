from datetime import timezone
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    image_url = db.Column(db.String(500))  # Thêm trường để lưu URL hình ảnh
    comments = db.relationship('Comment', backref='task', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user = db.relationship('User', backref='comments')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    plain_password = db.Column(db.String(150))
    user_name = db.Column(db.String(150))
    notes = db.relationship("Task")
    is_locked = db.Column(db.Boolean, default=False)  # Cột để xác định user có bị khóa không
    is_admin = db.Column(db.Boolean, default=False)   # Cột để xác định user có là admin không
    
    def __init__(self, email, password,plain_password, user_name, is_admin=False, is_locked=False):
        self.email = email
        self.password = password
        self.plain_password = plain_password
        self.user_name = user_name
        self.is_admin = is_admin
        self.is_locked = is_locked
