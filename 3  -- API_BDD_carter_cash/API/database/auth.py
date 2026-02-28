# auth.py
from models import User, UserCreate, PasswordChange
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from .db_connection import db
import pyodbc


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str):
    query = """
    SELECT username, email, full_name, hashed_password 
    FROM USER_API WHERE username = ?
    """
    with db.get_cursor() as cursor:
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if user:
            return User(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password
            )
    return None

def create_user(user: UserCreate):
    query = """
    INSERT INTO USER_API (username, email, full_name, hashed_password, Date_Création)
    VALUES (?, ?, ?, ?, ?)
    """
    hashed_password = get_password_hash(user.password)
    current_date = datetime.now().date()
    
    with db.get_cursor() as cursor:
        try:
            cursor.execute(query, (
                user.username,
                user.email,
                user.full_name,
                hashed_password,
                current_date
            ))
            return user
        except pyodbc.IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )

