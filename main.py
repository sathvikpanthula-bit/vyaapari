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
