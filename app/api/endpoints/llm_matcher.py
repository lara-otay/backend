from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.schema_fetch import get_trimmed_active_schemas
from app.services.llm_engine import generate_structured_request
from app.services.request_handler import send_structured_request
from app.services.conversation import (
    get_user_id_by_email,
    create_conversation,
    add_message,
    get_conversation_messages,
    get_conversation_context,
    get_conversation_summary
)

router = APIRouter()

@router.post("/match-and-send/")
async def match_and_send(
    user_prompt: str = Query(..., description="Prompt like 'get all products'"),
    user_email: str = Query(..., description="User email to track conversation"),
    conversation_name: str = Query(..., description="Name of the conversation"),
    conversation_id: int = Query(None, description="Existing conversation ID to continue"),
    db: Session = Depends(get_db)
):
    try:
        # 1. Get the user (must already exist)
        user_id = get_user_id_by_email(db, user_email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 2. Get or create conversation
    if conversation_id:
        # Verify conversation belongs to user
        conversation = get_conversation_summary(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
    else:
        conversation_id = create_conversation(db, user_id, conversation_name)

    # 3. Get conversation context for LLM
    context = get_conversation_context(db, conversation_id) if conversation_id else None

    # 4. Save the user's message
    add_message(db, conversation_id, "user", user_prompt)

    # 5. Generate structured API request using LLM with context
    trimmed = get_trimmed_active_schemas(db)
    structured = generate_structured_request(
        user_prompt=user_prompt,
        trimmed_schema=trimmed,
        context=context
    )

    # 6. Make the actual API call
    api_response = await send_structured_request(structured)

    # 7. Save the assistant's response
    add_message(db, conversation_id, "assistant", str(api_response))

    # 8. Fetch full conversation history
    history = get_conversation_messages(db, conversation_id)

    return {
        "conversation_id": conversation_id,
        "user_prompt": user_prompt,
        "structured_request": structured,
        "api_response": api_response,
        "conversation_history": history
    }