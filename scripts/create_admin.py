#!/usr/bin/env python3
"""Script to create an admin user"""

import argparse
import getpass
import os
import sys
from pathlib import Path

# Get the project root directory (parent of scripts/)
project_root = Path(__file__).parent.parent

# Change to project root so database is created in the correct location
os.chdir(project_root)

# Add project root to path to import app modules
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session  # noqa: E402
from app.auth import hash_password  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import SessionLocal, User, init_db  # noqa: E402
from app.logging import get_logger  # noqa: E402

# Initialize logger using app's logging configuration
logger = get_logger("create_admin")


def create_admin_user(username: str, password: str) -> None:
    """Create an admin user in the database"""
    logger.info("Initializing database...")
    init_db()

    db: Session = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.error(f"User '{username}' already exists!")
            print(f"Error: User '{username}' already exists!")
            return

        # Create new user
        logger.info(f"Creating admin user: {username}")
        hashed_password = hash_password(password)
        new_user = User(
            username=username, hashed_password=hashed_password, is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"Successfully created admin user: {username} (ID: {new_user.id})")
        print(f"Successfully created admin user: {username}")
        print(f"User ID: {new_user.id}")
    except Exception as e:
        db.rollback()
        logger.exception(f"Error creating user: {e}")
        print(f"Error creating user: {e}")
    finally:
        db.close()


def main():
    """Main function to prompt for user credentials and create admin"""
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--username", help="Username for the admin user")
    parser.add_argument("--password", help="Password for the admin user")
    args = parser.parse_args()

    logger.info("=== Create Admin User Script Started ===")
    logger.info(f"Database URL: {settings.database_url}")
    print("=== Create Admin User ===\n")

    # Get username
    if args.username:
        username = args.username
    else:
        username = input("Enter username: ").strip()

    if not username:
        print("Error: Username cannot be empty!")
        sys.exit(1)

    # Get password
    if args.password:
        password = args.password
        password_confirm = args.password
    else:
        password = getpass.getpass("Enter password: ")
        if not password:
            print("Error: Password cannot be empty!")
            sys.exit(1)
        password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("Error: Passwords do not match!")
        sys.exit(1)

    if len(password) < 8:
        print("Warning: Password is shorter than 8 characters!")
        if not args.password:
            proceed = input("Continue anyway? (y/N): ").strip().lower()
            if proceed != "y":
                print("Cancelled.")
                sys.exit(0)

    create_admin_user(username, password)


if __name__ == "__main__":
    main()
