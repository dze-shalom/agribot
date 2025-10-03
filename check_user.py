from app.main import create_app
from database.models.user import User

app = create_app()

with app.app_context():
    user = User.get_by_id(1)
    if user:
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Name: {user.name}")
        print(f"Account Type: {user.account_type}")
    else:
        print("User not found")