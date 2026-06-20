from fastapi import APIRouter, UploadFile, File
from services.upload_service import parse_uploaded_file
from services.pipeline_service import set_current_data

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    allowed_extensions = ["csv", "json", "xlsx", "xls"]
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in allowed_extensions:
        return {
            "status": "error",
            "message": f"Tipe file '.{ext}' tidak didukung. Gunakan: {', '.join(allowed_extensions)}",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        return {
            "status": "error",
            "message": f"Ukuran file terlalu besar ({len(file_bytes) // 1024 // 1024}MB). Maksimal 10MB.",
            "total": 0,
            "signal_quality": 0,
            "data": []
        }

    result = parse_uploaded_file(file_bytes, filename)

    if result["status"] == "success":
        set_current_data(result["data"])

    return result
