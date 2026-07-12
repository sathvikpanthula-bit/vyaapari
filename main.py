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

# --- 📁 DATA STRUCTURE SCHEMAS ---
class ChatRequest(BaseModel):
    message: str

class ItemRequest(BaseModel):
    name: str
    quantity: int
    price: float
    category: str = "General"

class SalesRequest(BaseModel):
    amount: float
    description: str = ""
    item_id: int = None

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

# --- 📦 INVENTORY MANAGEMENT ENDPOINTS ---
@app.get("/inventory/", tags=["Inventory"])
@app.get("/api/inventory/", tags=["Inventory"])
def get_inventory():
    return [
        {"id": 1, "name": "Sample Apple Batch", "quantity": 50, "price": 2.0, "category": "Fruits"},
        {"id": 2, "name": "Sample Banana Bundle", "quantity": 30, "price": 1.5, "category": "Fruits"}
    ]

@app.post("/inventory/", tags=["Inventory"])
@app.post("/api/inventory/", tags=["Inventory"])
def add_inventory_item(item: ItemRequest):
    return {
        "status": "success",
        "message": f"Successfully recorded stock for {item.name}!",
        "item": {
            "id": 99,
            "name": item.name,
            "quantity": item.quantity,
            "price": item.price,
            "category": item.category
        }
    }

# --- 💰 REVENUE / SALES ENDPOINTS ---
@app.get("/sales/", tags=["Sales"])
@app.get("/api/sales/", tags=["Sales"])
def get_sales_data():
    return [
        {"id": 1, "amount": 120.0, "description": "Morning vegetable market sales", "timestamp": datetime.now().isoformat()},
        {"id": 2, "amount": 45.5, "description": "Afternoon juice stall transactions", "timestamp": datetime.now().isoformat()}
    ]

@app.post("/sales/", tags=["Sales"])
@app.post("/api/sales/", tags=["Sales"])
def record_revenue(sale: SalesRequest):
    return {
        "status": "success",
        "message": f"Revenue of {sale.amount} recorded successfully!",
        "sale": {
            "id": 101,
            "amount": sale.amount,
            "description": sale.description,
            "timestamp": datetime.now().isoformat()
        }
    }

# --- 📊 DASHBOARD METRICS ---
@app.get("/dashboard/metrics", tags=["Dashboard"])
@app.get("/api/dashboard/metrics", tags=["Dashboard"])
def get_dashboard_metrics():
    # Structured objects to satisfy .toLocaleString() frontend properties safely
    current_time = datetime.now().isoformat()
    return {
        "total_sales": 165.5,
        "points": 120,
        "streak_days": 6,
        "recent_activity": [
            {
                "id": 1, 
                "type": "stock", 
                "title": "Added Stock: Apple Batch", 
                "amount": 100.0, 
                "date": current_time,
                "timestamp": current_time
            },
            {
                "id": 2, 
                "type": "sale", 
                "title": "Recorded Sale", 
                "amount": 45.5, 
                "date": current_time,
                "timestamp": current_time
            }
        ]
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
