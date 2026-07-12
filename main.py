from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db

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

# We will include routers here once their files are set up!

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
    # Provides initial dashboard state for tracking points and streaks!
    return {
        "total_sales": 0.0,
        "points": 100,
        "streak_days": 5,
        "recent_activity": []
    }
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

@app.post("/api/ai/chat", tags=["AI"])
def ai_chat(payload: ChatRequest):
    # This acts as a safe fallback response until your full Watsonx/Granite integration is wired up!
    user_msg = payload.message.lower()
    if "loan" in user_msg or "svanidhi" in user_msg:
        return {"response": "You can check your PM SVANidhi eligibility by visiting the official portal on the right side of your dashboard. First-time vendors can apply for a collateral-free loan up to ₹10,000."}
    elif "qr" in user_msg or "upi" in user_msg:
        return {"response": "To set up digital payments, click the BHIM UPI portal link on the right. You will need your bank account details and your business smartphone to download the merchant app."}
    else:
        return {"response": f"I received your message: '{payload.message}'. I am online and connected to your cloud profile!"}
    
