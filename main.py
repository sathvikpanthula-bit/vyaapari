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

# 🔐 Extract Environment Variables from Render Config Panel
WATSONX_APIKEY = os.getenv("WATSONX_APIKEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

credentials = {
    "url": WATSONX_URL,
    "apikey": WATSONX_APIKEY
}

@app.post("/api/ai/chat", tags=["AI"])
def ai_chat(payload: ChatRequest):
    # Safe check if variables aren't entered in Render settings yet
    if not WATSONX_APIKEY or not WATSONX_PROJECT_ID:
        return {
            "response": "Granite engine is waiting for access keys. Please add WATSONX_APIKEY and WATSONX_PROJECT_ID inside your Render Environment settings tab!"
        }

    try:
        # Configuration parameters for business insight delivery
        model_id = "ibm/granite-13b-instruct-v2"
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 300,
            "min_new_tokens": 1,
            "repetition_penalty": 1.0
        }
        
        # Initialize the core model client instance
        model = Model(
            model_id=model_id,
            credentials=credentials,
            project_id=WATSONX_PROJECT_ID,
            params=parameters
        )
        
        # Construct context tailoring responses for local merchants
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
            "response": f"Successfully connected to backend, but watsonx execution encountered an issue: {str(e)}"
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
