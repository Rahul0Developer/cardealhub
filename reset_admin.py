from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.password_hash = generate_password_hash('admin123')
            admin.is_admin = True
            admin.is_verified = True
            db.session.commit()
            print('Admin credentials reset successfully')
        else:
            print('Admin user not found')

if __name__ == '__main__':
    reset_admin_password()