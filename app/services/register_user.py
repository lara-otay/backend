from sqlalchemy.orm import Session
from sqlalchemy import text
import hashlib
from fastapi import HTTPException

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user_service(username: str, email: str, password: str, db: Session):
    # Check if email already exists
    query = text("SELECT id FROM users WHERE email = :email")
    result = db.execute(query, {"email": email}).fetchone()
    if result:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_pw = hash_password(password)

    insert_query = text("""
        INSERT INTO users (username, email, password, created_at)
        VALUES (:username, :email, :password, NOW())
    """)
    db.execute(insert_query, {
        "username": username,
        "email": email,
        "password": hashed_pw
    })
    db.commit()
    return {"message": "User registered successfully."}
