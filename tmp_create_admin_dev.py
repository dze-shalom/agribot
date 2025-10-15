from app.main import create_app
from database import db
from database.models.user import User, AccountType
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = 'admin@local.test'
    existing = User.get_by_email(email)
    if existing:
        print('Admin already exists:', existing.id)
    else:
        user = User(
            name='Local Admin',
            email=email,
            phone=None,
            country='Cameroon',
            region='Centre',
            account_type=AccountType.ADMIN,
            created_at=None
        )
        user.password_hash = generate_password_hash('admin123')
        db.session.add(user)
        db.session.commit()
        print('Created admin:', user.id)
