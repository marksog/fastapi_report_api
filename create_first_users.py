import sys
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import datetime
import bcrypt  # Directly using bcrypt for clarity

# Add your app directory to path
sys.path.append(".")

from app.database import Base
from app.models import User

def get_password_hash(password: str):
    """Standalone hashing function using bcrypt directly"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_first_users():
    # Initialize database
    engine = create_engine("sqlite:///./sql_app.db")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = Session(engine)
    
    try:
        # Sample users data
        users_data = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "location": "headquarters"
            },
            {
                "username": "pastor",
                "password": "pastor123",
                "role": "pastor",
                "location": "main_church"
            },
            {
                "username": "worker",
                "password": "worker123",
                "role": "worker",
                "location": "branch1"
            }
        ]

        for user_data in users_data:
            if not db.query(User).filter(User.username == user_data["username"]).first():
                hashed_pw = get_password_hash(user_data["password"])
                print(f"Hashing password for {user_data['username']}: {hashed_pw}")  # Debug output
                
                db_user = User(
                    username=user_data["username"],
                    hashed_password=hashed_pw,
                    role=user_data["role"],
                    location=user_data["location"],
                    is_active=True
                )
                db.add(db_user)
                print(f"Created user: {user_data['username']}")
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error creating users: {e}")
        raise  # Re-raise to see full error
    finally:
        db.close()

if __name__ == "__main__":
    create_first_users()
    print("Initial users created successfully!")