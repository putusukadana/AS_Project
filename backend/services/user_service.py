from datetime import datetime, timezone
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

from models import UserRegistration, UserLogin, UserResponse, APIResponse
from auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)

def format_user_response(user_data) -> UserResponse:
    return UserResponse(
        id=str(user_data["_id"]),
        username=user_data["username"],
        email=user_data["email"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )

async def register_user(users_collection: AsyncIOMotorCollection, user: UserRegistration):
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail={"message": "User already exists", "error": "Bad Request"}
        )
    
    # Hash password and create user
    now = datetime.now(timezone.utc)
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": now,
        "updated_at": now
    }
    
    result = await users_collection.insert_one(new_user)
    new_user["_id"] = result.inserted_id
    
    logger.info(f"User Created: {user.email}")
    return APIResponse(
        message="User created successfully",
        data=format_user_response(new_user)
    )

async def login_user(users_collection: AsyncIOMotorCollection, user_credentials: UserLogin):
    user = await users_collection.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for email: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "User not found", "error": "Bad Request"}
        )
    
    logger.info(f"User Logged In: {user['email']}")
    return APIResponse(
        message="User logged in successfully",
        data=format_user_response(user)
    )
