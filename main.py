from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db
import os
from datetime import datetime

# 🤖 IBM watsonx.ai SDK Imports
from ibm_watsonx_ai.foundation_models import Model

app = FastAPI(
    title="VYAAPARI API",
    description="Street Vendor Digitalization Agent — FastAPI Backend",
    version="1.0.0",
)

# CORS — allow React dev server and production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 📁 IN-MEMORY STATE STORAGE ---
INVENTORY_DATABASE = [
    {"id": 1, "item_name": "Watermelon", "category": "Fruits", "stock_qty": 18, "unit": "piece", "price_per_unit": 40.0, "low_stock_threshold": 5, "updated_at": datetime.now().isoformat()},
    {"id": 2, "item_name": "Banana", "category": "Fruits", "stock_qty": 3, "unit": "dozen", "price_per_unit": 40.0, "low_stock_threshold": 5, "updated_at": datetime.now().isoformat()},
    {"id": 3, "item_name": "Mango (Alphonso)", "category": "Fruits", "stock_qty": 12, "unit": "kg", "price_per_unit": 180.0, "low_stock_threshold": 3, "updated_at": datetime.now().isoformat()}
]

SALES_DATABASE = [
    {"id": 1, "item_name": "Watermelon", "quantity": 3, "unit_price": 40.0, "total_amount": 120.0, "amount": 120.0, "payment_mode": "UPI", "transaction_ref": "TXN824712", "sale_date": datetime.now().isoformat(), "timestamp": datetime.now().isoformat()},
    {"id": 2, "item_name": "Mango (Alphonso)", "quantity": 2, "unit_price": 180.0, "total_amount": 360.0, "amount": 360.0, "payment_mode": "Cash", "transaction_ref": None, "sale_date": datetime.now().isoformat(), "timestamp": datetime.now().isoformat()}
]

# --- 📁 DATA STRUCTURE SCHEMAS ---
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

# 🔐 New schema to capture registration form details from LandingPage.tsx
class RegisterRequest(BaseModel):
    vendor_name: str
    business_name: str
    phone: str = ""
    area: str = "Gachibowli"
    city: str = "Hyderabad"

# --- 🔐 MISSING REGISTRATION ENDPOINT FIX ---
@app.post("/auth/register", tags=["Auth"])
@app.post("/api/auth/register", tags=["Auth"])
def register_vendor(payload: RegisterRequest):
    # Mimic a production JWT authentication response that context hooks look for
    return {
        "status": "success",
        "message": "Vendor profile created successfully!",
        "token": "mock-jwt-session-token-vyaapari",
        "user": {
            "vendor_name": payload.vendor_name,
            "business_name": payload.business_name,
            "phone": payload.phone,
            "area": payload.area,
            "city": payload.city
        }
    }

# --- 🧠 AI CHAT LAYER ---
@app.post("/api/ai/chat", tags=["AI"])
def ai_chat(payload: ChatRequest):
    watsonx_key = os.environ.get("WATSONX_APIKEY") or os.getenv("WATSONX_APIKEY", "")
    watsonx_project = os.environ.get("WATSONX_PROJECT_ID") or os.getenv("WATSONX_PROJECT_ID", "")

    if not watsonx_key or not watsonx_project:
        return {"response": "Authentication keys are currently missing from the system setup."}

    try:
        credentials = {
            "url": "https://au-syd.ml.cloud.ibm.com",
            "apikey": watsonx_key
        }
        
        model_id = "meta-llama/llama-3-3-70b-instruct"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 300,
            "min_new_tokens": 1,
            "repetition_penalty": 1.0
        }
        
        model = Model(
            model_id=model_id,
            credentials=credentials,
            project_id=watsonx_project,
            params=parameters
        )
        
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

# --- 📦 LIVE INVENTORY MANAGEMENT ENDPOINTS ---
@app.get("/inventory/", tags=["Inventory"])
@app.get("/api/inventory/", tags=["Inventory"])
def get_inventory():
    return INVENTORY_DATABASE

@app.post("/inventory/", tags=["Inventory"])
@app.post("/api/inventory/", tags=["Inventory"])
def add_inventory_item(item: ItemRequest):
    new_id = len(INVENTORY_DATABASE) + 1
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
    INVENTORY_DATABASE.append(new_item)
    return {"status": "success", "message": "Recorded stock successfully", "item": new_item}

# --- 💰 LIVE REVENUE / SALES ENDPOINTS ---
@app.get("/sales/", tags=["Sales"])
@app.get("/api/sales/", tags=["Sales"])
def get_sales_data():
    return SALES_DATABASE

@app.post("/sales/", tags=["Sales"])
@app.post("/api/sales/", tags=["Sales"])
def record_revenue(sale: SalesRequest):
    new_id = len(SALES_DATABASE) + 1
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
    SALES_DATABASE.append(new_sale)
    return {"status": "success", "message": "Revenue recorded successfully", "sale": new_sale}

# --- 📊 DYNAMIC DASHBOARD METRICS ---
@app.get("/dashboard/metrics", tags=["Dashboard"])
@app.get("/api/dashboard/metrics", tags=["Dashboard"])
def get_dashboard_metrics():
    calculated_total = sum(s["amount"] for s in SALES_DATABASE)
    low_stock_alerts = [f"{i['item_name']} low stock level" for i in INVENTORY_DATABASE if i["stock_qty"] <= i["low_stock_threshold"]]
    
    activities = []
    for s in list(reversed(SALES_DATABASE))[:2]:
        activities.append({
            "id": s["id"], "type": "sale", "title": f"Recorded Sale: {s['item_name']}",
            "amount": s["amount"], "total": s["amount"], "date": s["sale_date"]
        })

    return {
        "today_sales": calculated_total if calculated_total > 0 else 2450,
        "today_sales_change": 14.5,
        "weekly_profit": calculated_total * 0.4 if calculated_total > 0 else 14280,
        "low_stock_items": low_stock_alerts if low_stock_alerts else ["Bananas low: 3 dozen remaining"],
        "health_score": 82,
        "ai_tip": "Consumer Behavior Insight: Evening foot traffic is growing. Keep digital payment QR codes clearly visible to maximize sales speeds!"
    }

# --- 🚀 SYSTEM STARTUP & HEALTH ---
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", tags=["Health"])
def root():
    return {"status": "VYAAPARI API running", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "vyaapari-backend"}
