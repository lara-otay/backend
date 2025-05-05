from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.schema_fetch import get_trimmed_active_schemas
from app.services.llm_engine import generate_structured_request
from app.services.request_handler import send_structured_request
from app.services.conversation import (fetch_user_id,create_conversation,add_message,get_conversation_messages)

router = APIRouter()

@router.post("/match-and-send/")
async def match_and_send(
    user_prompt: str = Query(..., description="Prompt like 'get all products'"),
    user_email: str = Query(..., description="User email to track conversation"),
    conversation_name: str = Query(..., description="Name of the conversation"),
    db: Session = Depends(get_db)
):
    try:
        # 1. Get the user (must already exist)
        user_id = fetch_user_id(db, user_email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 2. Create a conversation for the user
    conversation_id = create_conversation(user_id, conversation_name, db)

    # 3. Save the user's message
    add_message(conversation_id, "user", user_prompt, db)

    # 4. Generate structured API request using LLM
    trimmed = get_trimmed_active_schemas(db)
    structured = generate_structured_request(user_prompt, trimmed)

    # 5. Make the actual API call
    api_response = await send_structured_request(structured)

    # 6. Save the assistant's response
    add_message(conversation_id, "assistant", str(api_response), db)

    # 7. Fetch full conversation history
    history = get_conversation_messages(conversation_id, db)

    return {
        "user_prompt": user_prompt,
        "structured_request": structured,
        #"api_response": api_response,
        "conversation_history": history
    }
