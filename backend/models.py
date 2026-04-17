from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class APIResponse(BaseModel):
    message: str
    data: Optional[UserResponse] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    error: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ProcessedData(BaseModel):
    raw_text: str
    cleaned_text: str
    score: float
    label: str
    platform: Optional[str] = "tiktok"
    video_id: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
