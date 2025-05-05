from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.register_user import register_user_service
from app.services.login_user import login_user_service

router = APIRouter()

@router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    return register_user_service(username, email, password, db)

@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    return login_user_service(email, password, db)
