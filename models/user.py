from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class UserRole(Enum):
    VIEWER = "viewer"
    COLLABORATOR = "collaborator"
    EDITOR = "editor"

class User(UserMixin):
    def __init__(self, id, username, password, role=UserRole.VIEWER):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_view_permission(self):
        return True  # All roles can view

    def has_edit_permission(self):
        return self.role in [UserRole.COLLABORATOR, UserRole.EDITOR]

    def has_delete_permission(self):
        return self.role == UserRole.EDITOR

    @staticmethod
    def get_roles():
        return [role.value for role in UserRole] 