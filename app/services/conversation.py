from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException

# a function to interact with user table 

def fetch_user_id(db: Session, email: str) -> int:
    """
    Fetch the user ID by email. Raise error if user not found.
    """
    query = text("SELECT id FROM users WHERE email = :email")
    result = db.execute(query, {"email": email}).fetchone()
    if result:
        return result[0]
    
    raise HTTPException(status_code=404, detail="User not found. Please sign up first.")


# a funnction to interact with conversation tabel 

def create_conversation (user_id : int , title : str ,db : Session) -> int :
    insert_query = text("""
        INSERT INTO conversations (user_id, title, created_at)
        VALUES (:user_id, :title, NOW())
    """)
    db.execute(insert_query, {"user_id": user_id, "title": title})
    db.commit()
    return db.execute(text("SELECT LAST_INSERT_ID()")).scalar()

# a function to handle interactiion with messages tabel 

def add_message(conversation_id: int, sender: str, content: str, db: Session):
    insert_query = text("""
        INSERT INTO messages (conversation_id, sender, content, created_at)
        VALUES (:cid, :sender, :content, NOW())
    """)
    db.execute(insert_query, {
        "cid": conversation_id,
        "sender": sender,
        "content": content
    })
    db.commit()

# function that fetch the conversation 
def get_conversation_messages(conversation_id: int, db: Session):
    query = text("""
        SELECT sender, content, created_at
        FROM messages
        WHERE conversation_id = :cid
        ORDER BY created_at ASC
    """)
    result = db.execute(query, {"cid": conversation_id}).mappings().fetchall()
    return [dict(row) for row in result]
