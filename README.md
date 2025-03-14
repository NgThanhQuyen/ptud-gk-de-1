# ptud-gk-de-1

## a. Thông tin cá nhân  
- Họ tên: Nguyễn Thanh Quyền
- Mã sinh viên: 21045131
- Stt: 50
## b. Mô tả project 
Blog đơn giản có hỗ trợ bình luận, được xây dựng với Flask cho backend. Blog cho phép người dùng đọc bài viết, bình luận và có hệ thống phân quyền user với ba cấp độ: Viewer, Collaborator và Editor.
## c. Hướng dẫn cài đặt và chạy
### Cài đặt  
```bash
Vào thư mục cần tải về bấm chuột phải -> Open in Terminal
git clone git@github.com:NgThanhQuyen/ptud-gk-de-1.git
```
### Chạy
```bash
Vào thư mục flask-tutorial -> Open in Terminal
pip install flask
python -m venv venv
source venv/bin/activate  # Trên Linux/macOS
venv\Scripts\activate     # Trên Windows
pip install -r requirements.txt
Sau đó vào file app.py để chạy
Truy cập link:
Users: http://127.0.0.1:5000
Admin: http://127.0.0.1:5000/admin
```
## d. Link project
https://github.com/NgThanhQuyen/ptud-gk-de-1.git

Đã làm:
1. Build blog thành công và các bài viết có hiển thị hành ảnh
2. Sidebar (Có Thanh Điều Hướng)
3.Option 3: Phân loại user thông thường thành  
o Viewer: view only 
o Collaborator: can edit, can’t delelte 
o Editor: view, edit, delete permission
