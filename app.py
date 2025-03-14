from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from manage import create_app
from manage.models import User, Task
from manage.roles import UserRole, viewer_required, collaborator_required, editor_required
from werkzeug.security import generate_password_hash, check_password_hash
from manage import db

app = create_app()
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(user_name=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('all_posts'))  # Chuyển đến trang xem tất cả bài viết
        flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất thành công.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('all_posts'))

# Route để xem tất cả bài viết (Viewer+)
@app.route('/all-posts')
@viewer_required
def all_posts():
    all_tasks = Task.query.order_by(Task.date.desc()).all()
    return render_template('index.html', tasks=all_tasks)

# Route để xem chi tiết bài viết (Viewer+)
@app.route('/view-task/<int:task_id>')
@viewer_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('view_task.html', task=task)

# Route để chỉnh sửa bài viết (Collaborator+)
@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
@collaborator_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    # Collaborator chỉ có thể sửa bài viết của mình
    if task.user_id != current_user.id and not current_user.role == UserRole.EDITOR.value:
        flash('Bạn chỉ có thể chỉnh sửa bài viết của mình!', 'error')
        return redirect(url_for('all_posts'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        if title and body:
            task.title = title
            task.body = body
            db.session.commit()
            flash('Cập nhật bài viết thành công!', 'success')
            return redirect(url_for('view_task', task_id=task.id))
    return render_template('edit_task.html', task=task)

# Route để xóa bài viết (Editor only)
@app.route('/delete-task/<int:task_id>', methods=['POST'])
@editor_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Đã xóa bài viết!', 'success')
    return redirect(url_for('all_posts'))

# Route để tạo bài viết mới (Collaborator+)
@app.route('/create-task', methods=['GET', 'POST'])
@collaborator_required
def create_task():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        if title and body:
            new_task = Task(
                title=title,
                body=body,
                user_id=current_user.id
            )
            db.session.add(new_task)
            db.session.commit()
            flash('Tạo bài viết mới thành công!', 'success')
            return redirect(url_for('all_posts'))
    return render_template('create_task.html')

@app.route('/some-view-only-route')
@viewer_required
def view_only():
    # Mọi user đều có thể truy cập
    return render_template('view.html')

@app.route('/some-edit-route')
@collaborator_required
def edit_something():
    # Chỉ Collaborator và Editor mới có thể truy cập
    return render_template('edit.html')

@app.route('/some-delete-route')
@editor_required
def delete_something():
    # Chỉ Editor mới có thể truy cập
    return render_template('delete.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Tạo tài khoản admin
        admin = User.query.filter_by(email="admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                user_name="admin",
                password=generate_password_hash("admin123", method="pbkdf2:sha256"),
                plain_password="admin123",
                is_admin=True,
                role=UserRole.EDITOR.value  # Admin có quyền cao nhất
            )
            db.session.add(admin)
            db.session.commit()
            print("Created default admin account!")
            print("Email: admin@example.com")
            print("Password: admin123")
        
        # Tạo các tài khoản mẫu
        if not User.query.filter_by(email="viewer@example.com").first():
            viewer = User(
                email="viewer@example.com",
                user_name="viewer",
                password=generate_password_hash("viewer123", method="pbkdf2:sha256"),
                plain_password="viewer123",
                role=UserRole.VIEWER.value  # Chỉ có quyền xem
            )
            db.session.add(viewer)
            
        if not User.query.filter_by(email="collaborator@example.com").first():
            collaborator = User(
                email="collaborator@example.com",
                user_name="collaborator",
                password=generate_password_hash("collaborator123", method="pbkdf2:sha256"),
                plain_password="collaborator123",
                role=UserRole.COLLABORATOR.value  # Có quyền xem và sửa
            )
            db.session.add(collaborator)
            
        if not User.query.filter_by(email="editor@example.com").first():
            editor = User(
                email="editor@example.com",
                user_name="editor",
                password=generate_password_hash("editor123", method="pbkdf2:sha256"),
                plain_password="editor123",
                role=UserRole.EDITOR.value  # Có đầy đủ quyền
            )
            db.session.add(editor)
            
        db.session.commit()
        print("\nCreated sample accounts:")
        print("Viewer - username: viewer, password: viewer123 (Chỉ có quyền xem)")
        print("Collaborator - username: collaborator, password: collaborator123 (Có quyền xem và sửa)")
        print("Editor - username: editor, password: editor123 (Có đầy đủ quyền)")
    
    app.run(debug=True)
