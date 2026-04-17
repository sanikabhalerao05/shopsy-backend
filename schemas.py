from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from typing import List, Optional
from datetime import date, datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    address: str
    contact: str = Field(..., pattern=r"^\d{10}$")
    dob: date

class UserCreate(UserBase):
    password: str
    profile_photo: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        if not re.search(r"[0-9]", v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = Field(None, pattern=r"^\d{10}$")
    profile_photo: Optional[str] = None
    status: Optional[str] = None

class UserOut(UserBase):
    id: int
    role: str
    status: str
    profile_photo: Optional[str] = None

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int

class ProductCreate(ProductBase):
    image: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image: Optional[str] = None

class ProductOut(ProductBase):
    id: int
    image: str
    created_by: int

    class Config:
        from_attributes = True

class CartBase(BaseModel):
    product_id: int
    quantity: int

class CartOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductOut

    class Config:
        from_attributes = True

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductOut

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    payment_method: str

class OrderOut(BaseModel):
    id: int
    user_id: int
    total: float
    status: str
    payment_method: str
    created_at: datetime
    items: List[OrderItemOut]
    user: UserOut

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
