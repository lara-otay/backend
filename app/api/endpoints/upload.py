# app/api/endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.schema_upload import handle_schema_upload

router = APIRouter()

@router.post("/upload-schema/")
async def upload_schema(service_name: str,file: UploadFile ,db: Session = Depends(get_db)):
    try:
        return await handle_schema_upload(service_name, file, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
