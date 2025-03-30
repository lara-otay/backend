from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.schema_fetch import get_active_schema_paths , trim_schema_file , build_engineered_prompt

router = APIRouter()

@router.get("/active-schemas/")
def fetch_active_schema_paths(db: Session = Depends(get_db)):
    paths = get_active_schema_paths(db)
    return {
        "active_schema_paths": [str(p) for p in paths]
    }

@router.get("/trimmed-schemas/")
def get_trimmed_schemas(db: Session = Depends(get_db)):
    paths = get_active_schema_paths(db)
    trimmed_dict = {}

    for path in paths:
        trimmed = trim_schema_file(path)
        service_name = path.parent.name.lower()
        trimmed_dict[service_name] = trimmed

    prompt = build_engineered_prompt(trimmed_dict)

    return {
        "trimmed_schemas": trimmed_dict,
        "engineered_prompt": prompt
    }
    
    



