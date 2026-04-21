#!/usr/bin/env python3
"""
Development user seeding script.

This script creates test users in the database for development purposes only.
It is idempotent - running it multiple times will not duplicate users or break state.

Usage (manual):
    python scripts/seed_dev_users
    or
    docker exec cyclo-veda-backend-dev python scripts/seed_dev_users

Docker Compose (dev):
    Runs automatically on docker compose up as part of the startup sequence
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.database import get_db
from app.models.user import UserORM
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository


async def seed_dev_users():
    """
    Create development users if they don't exist.
    
    This function is idempotent - it uses find-or-create logic so running it
    multiple times will not duplicate users or break state.
    """
    
    # Development user credentials
    dev_users = [
        {
            "email": "admin@cycloveda.com",
            "username": "admin", 
            "password": "password",
            "full_name": "Admin User",
            "is_superuser": True
        },
        {
            "email": "user@example.com",
            "username": "user",
            "password": "password", 
            "full_name": "Test User",
            "is_superuser": False
        }
    ]
    
    async for db in get_db():
        created_count = 0
        skipped_count = 0
        
        try:
            for user_data in dev_users:
                # Find-or-create pattern - check if user already exists
                existing_user = await UserRepository.get_by_email(db, user_data["email"])
                
                if existing_user:
                    skipped_count += 1
                    print(f"✓ User {user_data['email']} already exists (ID: {existing_user.id})")
                    continue
                
                # Hash the password
                hashed_password = AuthService.get_password_hash(user_data["password"])
                
                # Create user record
                user_orm = UserORM(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=hashed_password,
                    full_name=user_data["full_name"],
                    is_active=True,
                    is_superuser=user_data["is_superuser"]
                )
                
                db.add(user_orm)
                await db.commit()
                await db.refresh(user_orm)
                
                created_count += 1
                print(f"✓ Created user: {user_data['email']} (ID: {user_orm.id})")
            
            print(f"\n{'='*60}")
            print(f"Seeding completed: {created_count} created, {skipped_count} skipped")
            print(f"{'='*60}")
            print("Login credentials:")
            print("  Email: admin@cycloveda.com  | Password: password")
            print("  Email: user@example.com   | Password: password")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"ERROR: Failed to seed users: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
        break


if __name__ == "__main__":
    # Safety check - only run in development
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env not in ("development", "dev", "local"):
        print("ERROR: This script should only be run in development environments")
        print("Set ENVIRONMENT=development to override this safety check")
        sys.exit(1)
    
    try:
        asyncio.run(seed_dev_users())
    except KeyboardInterrupt:
        print("\nSeeding interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nSeeding failed: {e}")
        sys.exit(1)
