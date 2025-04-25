from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.schema_fetch import get_trimmed_active_schemas
from app.services.llm_engine import generate_structured_request
from app.services.request_handler import send_structured_request

router = APIRouter()

@router.post("/match-and-send/")
async def match_and_send(
    user_prompt: str = Query(..., description="What action do you want to do?"),
    db: Session = Depends(get_db)
):
    # 1. Trim all active schemas
    trimmed = get_trimmed_active_schemas(db)

    # 2. Ask LLM to match the best API endpoint and return a structured request
    structured = generate_structured_request(user_prompt, trimmed)

    # 3. Send the real API call using that structured request
    response = await send_structured_request(structured)

    # 4. Return the final response to the user
    return {
        "user_prompt": user_prompt,
        "structured_request": structured,
        "api_response": response
    }
