from fastapi import APIRouter, Depends
from pydantic import BaseModel
from database import db
from auth import get_current_user

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

class RapidAPIKeyRequest(BaseModel):
    value: str

@router.get("/rapidapi-key")
async def get_rapidapi_key(user = Depends(get_current_user)):
    collection = db["settings"]
    doc = await collection.find_one({"key": "rapidapi_key"})
    return {
        "status": "success",
        "data": {
            "value": doc["value"] if doc else ""
        }
    }

@router.put("/rapidapi-key")
async def set_rapidapi_key(body: RapidAPIKeyRequest, user = Depends(get_current_user)):
    collection = db["settings"]
    await collection.update_one(
        {"key": "rapidapi_key"},
        {"$set": {"value": body.value}},
        upsert=True
    )
    return {"status": "success", "message": "API key berhasil disimpan"}
