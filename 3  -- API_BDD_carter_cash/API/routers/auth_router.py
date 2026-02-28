# auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta

from database.auth import (
    verify_password, create_user, get_user, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
)
from models import UserCreate, Token, PasswordChange, User
from database.db_connection import db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Mise à jour de la dernière connexion
    update_query = """
    UPDATE USER_API 
    SET Date_Derniere_Connexion = ? 
    WHERE username = ?
    """
    with db.get_cursor() as cursor:
        cursor.execute(update_query, (datetime.now(), user.username))

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserCreate)
async def register_new_user(user: UserCreate):
    # Vérification si l'utilisateur existe déjà
    check_query = "SELECT 1 FROM USER_API WHERE username = ? OR email = ?"
    with db.get_cursor() as cursor:
        cursor.execute(check_query, (user.username, user.email))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered"
            )
    
    return create_user(user)

@router.put("/users/me/password")
async def change_user_password(
    password_change: PasswordChange,
    current_user: str = Depends(oauth2_scheme)
):
    user = get_user(current_user)
    if not user or not verify_password(password_change.current_password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    if password_change.new_password != password_change.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="New passwords don't match"
        )

    new_hashed_password = get_password_hash(password_change.new_password)
    update_query = """
    UPDATE USER_API 
    SET hashed_password = ? 
    WHERE username = ?
    """
    
    with db.get_cursor() as cursor:
        cursor.execute(update_query, (new_hashed_password, current_user))
    
    return {"message": "Password updated successfully"}
