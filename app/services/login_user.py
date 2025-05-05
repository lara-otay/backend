# app/services/login_user.py
from sqlalchemy.orm import Session
from sqlalchemy import text
import hashlib
from fastapi import HTTPException

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def login_user_service(email: str, password: str, db: Session):
    hashed_pw = hash_password(password)

    query = text("SELECT id FROM users WHERE email = :email AND password = :password")
    result = db.execute(query, {
        "email": email,
        "password": hashed_pw
    }).fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {"message": "Login successful", "user_id": result[0]}
