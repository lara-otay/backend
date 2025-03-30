import hashlib
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session



def compute_file_hash_from_bytes(file_bytes: bytes) :
    
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()



BASE_UPLOAD_FOLDER = Path("Upload_system") / "schemas"
BASE_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

async def handle_schema_upload(service_name: str, file: UploadFile, db: Session):
    service_name = service_name.strip()
    
    
    file.file.seek(0)
    file_content = await file.read()
    
    
    file_hash = compute_file_hash_from_bytes(file_content)

    #deactivate all schemas
    deactivate_query = text("UPDATE SCHEMSYS SET active = False WHERE service_name = :service_name")
    db.execute(deactivate_query, {"service_name": service_name})
    db.commit()

    #  for duplicate
    query = text("SELECT file_path FROM SCHEMSYS WHERE schema_hash = :schema_hash")
    result = db.execute(query, {"schema_hash": file_hash}).fetchone()

    if result:
        
        update_query = text("UPDATE SCHEMSYS SET active = True WHERE schema_hash = :schema_hash")
        db.execute(update_query, {"schema_hash": file_hash})
        db.commit()
        return {
            "message": "Duplicate schema found; reactivated existing schema.",
            "schema_hash": file_hash,
            "file_path": result[0]
        }

    # Save new file
    service_folder = BASE_UPLOAD_FOLDER / service_name
    service_folder.mkdir(parents=True, exist_ok=True)
    new_file_name = f"{service_name}_{file_hash}.json"
    new_file_path = service_folder / new_file_name

    with new_file_path.open("wb") as f:
        f.write(file_content)

    # Insert new schema
    insert_query = text("""
        INSERT INTO SCHEMSYS (id, service_name, schema_hash, file_path, active)
        VALUES (:id, :service_name, :schema_hash, :file_path, :active)
    """)
    db.execute(insert_query, {
        "id": file_hash,
        "service_name": service_name,
        "schema_hash": file_hash,
        "file_path": str(new_file_path),
        "active": True
    })
    db.commit()

    return {
        "message": "Schema uploaded and activated successfully.",
        "schema_hash": file_hash,
        "file_path": str(new_file_path)
    }

