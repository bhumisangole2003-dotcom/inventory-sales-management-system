from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    category: str = "General"
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    reorder_level: int = Field(default=5, ge=0)


class ProductOut(ProductCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SaleCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class SaleOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=100)


class TokenOut(BaseModel):
    token: str
    username: str
