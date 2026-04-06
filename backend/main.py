import os
import logging
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorCollection

from database import get_database
from models import UserRegistration, UserLogin, UserResponse, APIResponse, Token
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AS Project API - Issue #4")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_user_response(user_data) -> UserResponse:
    return UserResponse(
        id=str(user_data["_id"]),
        username=user_data["username"],
        email=user_data["email"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the AS Project API V1"}

@app.post("/api/v1/users", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def register(user: UserRegistration):
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    
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

@app.post("/api/v1/users/login", response_model=APIResponse)
async def login(user_credentials: UserLogin):
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    
    user = await users_collection.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for email: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "User not found", "error": "Bad Request"}
        )
    
    # Update updated_at on login if needed, or keep as is
    
    logger.info(f"User Logged In: {user['email']}")
    return APIResponse(
        message="User logged in successfully",
        data=format_user_response(user)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
