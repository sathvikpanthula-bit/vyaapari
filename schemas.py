from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ─── Auth Schemas ────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    vendor_name: str
    business_name: str
    business_type: str
    city: str
    area: str
    primary_language: str = "English"
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    vendor_name: str
    business_name: str
    business_type: str
    city: str
    area: str
    primary_language: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# ─── Inventory Schemas ────────────────────────────────────────────────────────
class InventoryCreate(BaseModel):
    item_name: str
    category: str
    stock_qty: float
    unit: str = "kg"
    price_per_unit: float
    low_stock_threshold: float = 5.0

class InventoryUpdate(BaseModel):
    item_name: Optional[str] = None
    category: Optional[str] = None
    stock_qty: Optional[float] = None
    unit: Optional[str] = None
    price_per_unit: Optional[float] = None
    low_stock_threshold: Optional[float] = None

class InventoryOut(BaseModel):
    id: int
    item_name: str
    category: str
    stock_qty: float
    unit: str
    price_per_unit: float
    low_stock_threshold: float
    updated_at: datetime

    class Config:
        from_attributes = True

# ─── Sales Schemas ────────────────────────────────────────────────────────────
class SaleCreate(BaseModel):
    item_name: str
    quantity: float
    unit_price: float
    payment_mode: str = "Cash"
    transaction_ref: Optional[str] = None

class SaleOut(BaseModel):
    id: int
    item_name: str
    quantity: float
    unit_price: float
    total_amount: float
    payment_mode: str
    transaction_ref: Optional[str]
    sale_date: datetime

    class Config:
        from_attributes = True

# ─── Chat Schemas ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    language: str = "English"

class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# ─── Dashboard Schemas ────────────────────────────────────────────────────────
class DashboardMetrics(BaseModel):
    today_sales: float
    today_sales_change: float
    weekly_profit: float
    low_stock_items: List[str]
    health_score: int
    ai_tip: str