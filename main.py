from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db
import os

# 🤖 IBM watsonx.ai SDK Imports
from ibm_watsonx_ai.foundation_models import Model

app = FastAPI(
    title="VYAAPARI API",
    description="Street Vendor Digitalization Agent — FastAPI Backend",
    version="1.0.0",
)

# CORS — allow React dev server and production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/ai/chat", tags=["AI"])
def ai_chat(payload: ChatRequest):
    # 🔐 Read live system properties direct from shell environment mapping
    watsonx_key = os.environ.get("WATSONX_APIKEY") or os.getenv("WATSONX_APIKEY", "")
    watsonx_project = os.environ.get("WATSONX_PROJECT_ID") or os.getenv("WATSONX_PROJECT_ID", "")
    watsonx_url = os.environ.get("WATSONX_URL") or os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    # If keys are completely empty, return diagnostic text to help fix it instantly
    if not watsonx_key or not watsonx_project:
        return {
            "response": (
                f"⚠️ Cloud Binding Error: The server process cannot see your environment configuration values.\n\n"
                f"Diagnostic Check:\n"
                f"• APIKEY detected: {'✅ YES' if watsonx_key else '❌ NO (Empty)'}\n"
                f"• PROJECT_ID detected: {'✅ YES' if watsonx_project else '❌ NO (Empty)'}\n\n"
                f"Quick Fix: Go to your Render Environment settings tab, look closely to ensure there are no trailing whitespaces inside the input rows, save them, and trigger a 'Clear Build Cache & Deploy'."
            )
        }

    try:
        credentials = {
            "url": watsonx_url,
            "apikey": watsonx_key
        }
        
        # Core Granite foundation client initialization parameters
        model_id = "ibm/granite-13b-instruct-v2"
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
        return {
            "response": f"Connected to backend, but watsonx execution encountered an error: {str(e)}"
        }

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", tags=["Health"])
def root():
    return {"status": "VYAAPARI API running", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "vyaapari-backend"}

@app.get("/api/dashboard/metrics", tags=["Dashboard"])
def get_dashboard_metrics():
    return {
        "total_sales": 0.0,
        "points": 100,
        "streak_days": 5,
        "recent_activity": []
    }
