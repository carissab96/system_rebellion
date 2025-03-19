from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from core.security import hash_password, verify_password, create_access_token, create_refresh_token
from models.user import User, UserProfile
from schemas.auth import UserCreate, UserProfileCreate

class AuthService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate, profile_data: UserProfileCreate = None):
        """
        User Registration with Quantum-Level Precision
        The Meth Snail optimizes your account creation!
        """
        try:
            # Generate a unique user ID
            user_id = str(uuid.uuid4())
            
            # Hash the password with Sir Hawkington's distinguished method
            hashed_password = hash_password(user_data.password)
            
            # Create user
            db_user = User(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password
            )
            
            db.add(db_user)
            
            # Create user profile if data provided
            if profile_data:
                db_profile = UserProfile(
                    user_id=user_id,
                    **profile_data.dict()
                )
                db.add(db_profile)
            
            db.commit()
            db.refresh(db_user)
            
            return db_user
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists. The Quantum Shadow People are laughing."
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"The Meth Snail crashed during user creation: {str(e)}"
            )
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """
        User Authentication with Sir Hawkington's Seal of Approval
        """
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The Quantum Shadow People have hidden your credentials"
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials. Sir Hawkington is NOT amused."
            )
        
        return user