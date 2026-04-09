from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorCollection

from database import get_database
from models import UserRegistration, UserLogin, APIResponse
from services.user_service import register_user, login_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def register(user: UserRegistration):
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    return await register_user(users_collection, user)

@router.post("/login", response_model=APIResponse)
async def login(user_credentials: UserLogin):
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    return await login_user(users_collection, user_credentials)
