#!/usr/bin/env python3
"""
Grant admin privileges to a user
Usage: python grant_admin.py [email_or_user_id]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from database import db
from database.models.user import User, AccountType
from app.main import create_app

def grant_admin_privileges(identifier=None):
    """Grant admin privileges to a user"""
    app = create_app()

    with app.app_context():
        if identifier is None:
            # Get all users and show options
            users = User.query.all()
            if not users:
                print("No users found in the database.")
                return

            print("Available users:")
            for user in users:
                status = "ADMIN" if user.account_type.value == 'admin' else "USER"
                print(f"  ID: {user.id}, Email: {user.email}, Name: {user.name}, Status: {status}")

            # Prompt for user selection
            try:
                user_input = input("\nEnter user ID or email to grant admin privileges: ").strip()
                if user_input.isdigit():
                    user = User.query.get(int(user_input))
                else:
                    user = User.query.filter_by(email=user_input).first()
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
        else:
            # Use provided identifier
            if identifier.isdigit():
                user = User.query.get(int(identifier))
            else:
                user = User.query.filter_by(email=identifier).first()

        if not user:
            print(f"User not found: {identifier}")
            return

        # Check current status
        current_status = user.account_type.value
        print(f"\nUser: {user.name} ({user.email})")
        print(f"Current status: {current_status.upper()}")

        if current_status == 'admin':
            print("User already has admin privileges.")
            return

        # Grant admin privileges
        user.account_type = AccountType.ADMIN

        try:
            db.session.commit()
            print(f"SUCCESS: Admin privileges granted to {user.name} ({user.email})")
            print("The user can now access analytics and admin features.")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Error granting admin privileges: {e}")

if __name__ == "__main__":
    identifier = sys.argv[1] if len(sys.argv) > 1 else None
    grant_admin_privileges(identifier)