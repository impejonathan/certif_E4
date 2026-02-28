from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr, Field


class Produit(BaseModel):
    ID_Produit: int
    URL_Produit: str
    Prix: int
    Info_generale: str
    Descriptif: str
    Note: str
    Marque: str
    Date_scrap: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    username: str
    password: str

class User(UserBase):
    username: str
    hashed_password: str

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
    

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=3)
    new_password: str = Field(..., min_length=3)
    confirm_password: str = Field(..., min_length=3)
