from fastapi import APIRouter , Depends
from sqlalchemy.orm import session
from app.db.database import get_db 
from app.services.schema_fetch import get_trimmed_active_schemas 
from app.services.llm_engine import ask_llm_for_endpoint

router =APIRouter ()

@router.post ("/match-endpoint/")
def match_endpoint (user_prompt : str , db: session =Depends(get_db)):

    trimmed =get_trimmed_active_schemas(db)

    suggestion = ask_llm_for_endpoint(user_prompt , trimmed)

    return {
        "user_prompt":user_prompt ,
        "suggested_endpoint": suggestion
    }
