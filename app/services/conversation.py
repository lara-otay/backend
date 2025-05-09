from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import List, Dict, Any, Optional

def get_user_id_by_email(db: Session, email: str) -> int:
    query = text("SELECT id FROM users WHERE email = :email")
    result = db.execute(query, {"email": email}).fetchone()
    if result:
        return result[0]
    raise ValueError("User not found")

def list_conversations(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    query = text("""
        SELECT c.id, c.title, c.created_at, c.last_updated,
               (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count,
               (SELECT content FROM messages 
                WHERE conversation_id = c.id 
                ORDER BY created_at DESC LIMIT 1) as last_message
        FROM conversations c
        WHERE c.user_id = :user_id
        ORDER BY c.last_updated DESC
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {
        "user_id": user_id,
        "limit": limit,
        "skip": skip
    }).fetchall()
    return [dict(row._mapping) for row in result]

def get_conversation_messages(
    db: Session, 
    conversation_id: int, 
    skip: int = 0, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    query = text("""
        SELECT id, sender, content, created_at
        FROM messages
        WHERE conversation_id = :conversation_id
        ORDER BY created_at ASC
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {
        "conversation_id": conversation_id,
        "limit": limit,
        "skip": skip
    }).fetchall()
    return [dict(row._mapping) for row in result]

def create_conversation(
    db: Session, 
    user_id: int, 
    title: str
) -> int:
    now = datetime.utcnow()
    insert_query = text("""
        INSERT INTO conversations (user_id, title, created_at, last_updated)
        VALUES (:user_id, :title, :created_at, :last_updated)
    """)
    db.execute(insert_query, {
        "user_id": user_id,
        "title": title,
        "created_at": now,
        "last_updated": now
    })
    db.commit()
    return db.execute(text("SELECT LAST_INSERT_ID()")).scalar()

def add_message(
    db: Session, 
    conversation_id: int, 
    sender: str, 
    content: str
) -> int:
    now = datetime.utcnow()
    
    # Insert the message
    insert_message = text("""
        INSERT INTO messages (conversation_id, sender, content, created_at)
        VALUES (:conversation_id, :sender, :content, :created_at)
    """)
    db.execute(insert_message, {
        "conversation_id": conversation_id,
        "sender": sender,
        "content": content,
        "created_at": now
    })
    
    # Update conversation's last_updated timestamp
    update_conversation = text("""
        UPDATE conversations 
        SET last_updated = :last_updated
        WHERE id = :conversation_id
    """)
    db.execute(update_conversation, {
        "conversation_id": conversation_id,
        "last_updated": now
    })
    
    db.commit()
    return db.execute(text("SELECT LAST_INSERT_ID()")).scalar()

def get_conversation_context(
    db: Session, 
    conversation_id: int, 
    max_messages: int = 10
) -> List[Dict[str, Any]]:
    query = text("""
        SELECT sender, content, created_at
        FROM messages
        WHERE conversation_id = :conversation_id
        ORDER BY created_at DESC
        LIMIT :max_messages
    """)
    result = db.execute(query, {
        "conversation_id": conversation_id,
        "max_messages": max_messages
    }).fetchall()
    return [dict(row._mapping) for row in reversed(result)]

def get_conversation_summary(
    db: Session, 
    conversation_id: int
) -> Dict[str, Any]:
    query = text("""
        SELECT 
            c.id,
            c.user_id,
            c.title,
            c.created_at,
            c.last_updated,
            COUNT(m.id) as message_count,
            (SELECT content 
             FROM messages 
             WHERE conversation_id = c.id 
             ORDER BY created_at DESC 
             LIMIT 1) as last_message
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.id = :conversation_id
        GROUP BY c.id
    """)
    result = db.execute(query, {"conversation_id": conversation_id}).fetchone()
    return dict(result._mapping) if result else None

def delete_conversation(
    db: Session, 
    conversation_id: int
) -> bool:
    try:
        # Delete messages first (due to foreign key constraint)
        delete_messages = text("""
            DELETE FROM messages 
            WHERE conversation_id = :conversation_id
        """)
        db.execute(delete_messages, {"conversation_id": conversation_id})
        
        # Delete conversation
        delete_conversation = text("""
            DELETE FROM conversations 
            WHERE id = :conversation_id
        """)
        db.execute(delete_conversation, {"conversation_id": conversation_id})
        
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False