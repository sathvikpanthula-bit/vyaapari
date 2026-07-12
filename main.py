from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db
import os
from datetime import datetime
from typing import Dict, Any

# 🤖 IBM watsonx.ai SDK Imports
from ibm_watsonx_ai.foundation_models import Model

app = FastAPI(
    title="VYAAPARI API",
    description="Multi-User Street Vendor Digitalization Agent — FastAPI Backend",
    version="2.1.0",
)

# CORS — allow React dev server and production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 📁 DYNAMIC MULTI-USER STORAGE MAPS ---
USER_PROFILES = {}      
USER_INVENTORY = {}     
USER_SALES = {}         

class ChatRequest(BaseModel):
    message: str

class ItemRequest(BaseModel):
    name: str
    category: str = "General"
    quantity: float
    price: float
    unit: str = "kg"

class SalesRequest(BaseModel):
    amount: float
    description: str = ""
    item_id: int = None

# 🧠 FIXED: Accepting a raw dynamic dictionary to safely match whatever field names LandingPage.tsx uses!
class PermissiveAuthRequest(BaseModel):
    phone: str = ""
    phone_number: str = ""
    vendor_name: str = ""
    name: str = ""
    business_name: str = ""
    area: str = "Gachibowli"
    city: str = "Hyderabad"

# --- 🛠️ MULTI-USER DATA UTILITIES ---
def get_user_from_token(authorization: str = Header(None)):
    if not authorization:
        return "default_vendor"
    parts = authorization.split(" ")
    if len(parts) == 2:
        return parts[1]
    return "default_vendor"

def initialize_user_space(phone: str, name="Vendor", biz="My Shop", area="Gachibowli", city="Hyderabad"):
    if phone not in USER_PROFILES:
        USER_PROFILES[phone] = {
            "vendor_name": name,
            "business_name": biz,
            "phone": phone,
            "area": area,
            "city": city
        }
    if phone not in USER_INVENTORY:
        USER_INVENTORY[phone] = [
            {"id": 1, "item_name": "Watermelon", "category": "Fruits", "stock_qty": 18, "unit": "piece", "price_per_unit": 40.0, "low_stock_threshold": 5, "updated_at": datetime.now().isoformat()},
            {"id": 2, "item_name": "Banana", "category": "Fruits", "stock_qty": 3, "unit": "dozen", "price_per_unit": 40.0, "low_stock_threshold": 5, "updated_at": datetime.now().isoformat()}
        ]
    if phone not in USER_SALES:
        USER_SALES[phone] = [
            {"id": 1, "item_name": "Watermelon", "quantity": 3, "unit_price": 40.0, "total_amount": 120.0, "amount": 120.0, "payment_mode": "UPI", "transaction_ref": "TXN824712", "sale_date": datetime.now().isoformat(), "timestamp": datetime.now().isoformat()}
        ]

# --- 🔐 FIXED ACCOUNT ROUTERS ---
@app.post("/auth/register", tags=["Auth"])
@app.post("/api/auth/register", tags=["Auth"])
def register_vendor(payload: PermissiveAuthRequest):
    # Extract phone from whichever key the frontend used
    phone_id = (payload.phone or payload.phone_number or "unknown_vendor").strip()
    vendor_name = (payload.vendor_name or payload.name or "Vendor").strip()
    
    initialize_user_space(
        phone=phone_id, 
        name=vendor_name, 
        biz=payload.business_name or "Market Stall",
        area=payload.area,
        city=payload.city
    )
    
    return {
        "status": "success",
        "message": "Vendor profile created successfully!",
        "token": phone_id,
        "user": USER_PROFILES[phone_id]
    }

@app.post("/auth/login", tags=["Auth"])
@app.post("/api/auth/login", tags=["Auth"])
def login_vendor(payload: PermissiveAuthRequest):
    phone_id = (payload.phone or payload.phone_number or "unknown_vendor").strip()
    
    if phone_id not in USER_PROFILES:
        initialize_user_space(phone=phone_id, name="Returning Vendor", biz="Market Stall")
        
    return {
        "status": "success",
        "message": "Logged in successfully!",
        "token": phone_id,
        "user": USER_PROFILES[phone_id]
    }

# --- 🧠 AI CHAT LAYER ---
@app.post("/api/ai/chat", tags=["AI"])
def ai_chat(payload: ChatRequest):
    watsonx_key = os.environ.get("WATSONX_APIKEY") or os.getenv("WATSONX_APIKEY", "")
    watsonx_project = os.environ.get("WATSONX_PROJECT_ID") or os.getenv("WATSONX_PROJECT_ID", "")

    if not watsonx_key or not watsonx_project:
        return {"response": "Authentication keys are currently missing from the system setup."}

    try:
        credentials = {"url": "https://au-syd.ml.cloud.ibm.com", "apikey": watsonx_key}
        model_id = "meta-llama/llama-3-3-70b-instruct"
        parameters = {"decoding_method": "greedy", "max_new_tokens": 300, "min_new_tokens": 1, "repetition_penalty": 1.0}
        
        model = Model(model_id=model_id, credentials=credentials, project_id=watsonx_project, params=parameters)
        system_prompt = (
            "You are an expert micro-business consultant assisting local street vendors and small shops. "
            "Provide highly actionable, concise, and practical advice on pricing, inventory layout, "
            "customer retention, and financial literacy (like PM SVANidhi loans or UPI setup).\n\n"
        )
        full_prompt = f"{system_prompt}User: {payload.message}\nAssistant:"
        generated_response = model.generate_text(prompt=full_prompt)
        return {"response": generated_response.strip()}
    except Exception as e:
        return {"response": f"Connected to backend, but watsonx execution encountered an error: {str(e)}"}

# --- 📦 USER-ISOLATED INVENTORY MANAGEMENT ---
@app.get("/inventory/", tags=["Inventory"])
@app.get("/api/inventory/", tags=["Inventory"])
def get_inventory(authorization: str = Header(None)):
    user_id = get_user_from_token(authorization)
    initialize_user_space(user_id)
    return USER_INVENTORY[user_id]

@app.post("/inventory/", tags=["Inventory"])
@app.post("/api/inventory/", tags=["Inventory"])
def add_inventory_item(item: ItemRequest, authorization: str = Header(None)):
    user_id = get_user_from_token(authorization)
    initialize_user_space(user_id)
    
    new_id = len(USER_INVENTORY[user_id]) + 1
    new_item = {
        "id": new_id,
        "item_name": item.name,
        "name": item.name,
        "category": item.category,
        "stock_qty": item.quantity,
        "quantity": item.quantity,
        "price_per_unit": item.price,
        "price": item.price,
        "unit": item.unit,
        "low_stock_threshold": 5,
        "updated_at": datetime.now().isoformat()
    }
    USER_INVENTORY[user_id].append(new_item)
    return {"status": "success", "message": "Item added!", "item": new_item}

# --- 💰 USER-ISOLATED SALES MANAGEMENT ---
@app.get("/sales/", tags=["Sales"])
@app.get("/api/sales/", tags=["Sales"])
def get_sales_data(authorization: str = Header(None)):
    user_id = get_user_from_token(authorization)
    initialize_user_space(user_id)
    return USER_SALES[user_id]

@app.post("/sales/", tags=["Sales"])
@app.post("/api/sales/", tags=["Sales"])
def record_revenue(sale: SalesRequest, authorization: str = Header(None)):
    user_id = get_user_from_token(authorization)
    initialize_user_space(user_id)
    
    new_id = len(USER_SALES[user_id]) + 1
    current_time = datetime.now().isoformat()
    display_name = sale.description.split(" (")[0] if " (" in sale.description else sale.description
    if not display_name:
        display_name = "General Sale"

    new_sale = {
        "id": new_id,
        "item_name": display_name,
        "description": sale.description,
        "quantity": 1,
        "unit_price": sale.amount,
        "total_amount": sale.amount,
        "amount": sale.amount,
        "payment_mode": "UPI" if "upi" in sale.description.lower() else "Cash",
        "transaction_ref": None,
        "sale_date": current_time,
        "timestamp": current_time,
        "createdAt": current_time
    }
    USER_SALES[user_id].append(new_sale)
    return {"status": "success", "message": "Revenue recorded!", "sale": new_sale}

# --- 📊 USER-ISOLATED DASHBOARD METRICS ---
@app.get("/dashboard/metrics", tags=["Dashboard"])
@app.get("/api/dashboard/metrics", tags=["Dashboard"])
def get_dashboard_metrics(authorization: str = Header(None)):
    user_id = get_user_from_token(authorization)
    initialize_user_space(user_id)
    
    user_sales = USER_SALES[user_id]
    user_inventory = USER_INVENTORY[user_id]
    
    calculated_total = sum(s["amount"] for s in user_sales)
    low_stock_alerts = [f"{i['item_name']} low stock" for i in user_inventory if i["stock_qty"] <= i["low_stock_threshold"]]
    
    activities = []
    for s in list(reversed(user_sales))[:2]:
        activities.append({
            "id": s["id"], "type": "sale", "title": f"Recorded Sale: {s['item_name']}",
            "amount": s["amount"], "total": s["amount"], "date": s["sale_date"]
        })

    return {
        "today_sales": calculated_total if calculated_total > 0 else 1500.0,
        "today_sales_change": 8.2,
        "weekly_profit": calculated_total * 0.45 if calculated_total > 0 else 5200.0,
        "low_stock_items": low_stock_alerts,
        "health_score": 85 if len(low_stock_alerts) == 0 else 72,
        "ai_tip": f"Welcome back! Digital payment adoption speeds up transactions by 35% in your area."
    }

# --- 🚀 SYSTEM STARTUP & HEALTH ---
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", tags=["Health"])
def root():
    return {"status": "VYAAPARI Multi-Tenant API running", "version": "2.1.0"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "vyaapari-backend"}
