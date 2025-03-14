from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from manage import create_app
from models.user import User, UserRole
from utils.decorators import viewer_required, collaborator_required, editor_required

app = create_app()
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Temporary user storage (replace with database in production)
users = {
    'viewer': User(1, 'viewer', 'password', UserRole.VIEWER),
    'collaborator': User(2, 'collaborator', 'password', UserRole.COLLABORATOR),
    'editor': User(3, 'editor', 'password', UserRole.EDITOR)
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.get(username)
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
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
    return render_template('index.html')

@app.route('/students')
@viewer_required
def students():
    return render_template('students.html')

@app.route('/classes')
@viewer_required
def classes():
    return render_template('classes.html')

@app.route('/subjects')
@viewer_required
def subjects():
    return render_template('subjects.html')

@app.route('/grades')
@viewer_required
def grades():
    return render_template('grades.html')

@app.route('/reports')
@viewer_required
def reports():
    return render_template('reports.html')

if __name__ == "__main__":
    app.run(debug=True)
