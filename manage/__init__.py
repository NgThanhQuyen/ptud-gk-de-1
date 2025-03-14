from flask import Flask
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
migrate = Migrate()

load_dotenv()
SECRET_KEY = os.environ.get("KEY")
DB_NAME = os.environ.get("DB_NAME")

def create_database(app):
    db_path = os.path.join("manage", DB_NAME)
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
        print("Created DB!")

def create_admin():
    from .models import User  
    admin_email = "admin@example.com"
    admin_password = "admin123"

    with db.session.begin():
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                password=generate_password_hash(admin_password, method="pbkdf2:sha256"),
                plain_password=admin_password,
                user_name="Admin",
                is_admin=True,
                is_locked=False
            )
            db.session.add(admin_user)
            print("Admin user created!")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from .models import User, Task  # Import models sau khi db được khởi tạo
        create_database(app)
        create_admin()

    from .user import user
    from .views import views

    app.register_blueprint(user)
    app.register_blueprint(views)

    login_manager = LoginManager()
    login_manager.login_view = "user.login"
    login_manager.init_app(app)
    # Cân nhắc tăng thời gian sống session nếu cần
    app.permanent_session_lifetime = timedelta(minutes=30)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id.isdigit():
            return User.query.get(int(user_id))
        return None

    return app
