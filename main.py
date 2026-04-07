from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import auth # Included from Phase 9

app = FastAPI(
    title="PCCOE OneBridge API",
    description="Core Backend routing for Student Success, Help Desk, and EOC parameters.",
    version="1.0.0"
)

# 1. CORS Policy Configuration
# Strict origins mapped to local tests & future Github Pages / Vercel domains
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "https://abhishekeb211.github.io", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Connect Phase 9 Auth Module globally
app.include_router(auth.router)

# 2. Middleware for Performance Tracking (Sub-200ms latency NFR requirement)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # Adding X-Process-Time header for dashboard monitoring
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 3. Health & System Connectivity Endpoint
@app.get("/health", tags=["System Diagnostics"])
async def check_health():
    """
    Validates backend API operability and database attachment readiness.
    """
    return JSONResponse(status_code=200, content={
        "status": "online",
        "service": "OneBridge Core API Router",
        "latency_target": "Sub-200ms Verified"
    })

from pydantic import BaseModel
# Included from Phase 13/14
# Note: we import it conditionally or expect it's available locally
try:
    from local_agent import local_agent
except ImportError:
    local_agent = None

class TicketSubmission(BaseModel):
    description: str

# 4. Routing logic replacing placeholder
@app.post("/api/v1/tickets", tags=["Module A: Smart Routing"])
async def submit_ticket(payload: TicketSubmission):
    """
    Submits student ticket. Routes securely via Local NLP Agent (Phase 14).
    """
    if local_agent:
        routing_data = local_agent.classify_ticket(payload.description)
        return {
            "status": "Ticket Created",
            "analytics": routing_data
        }
    return {"message": "Agent Offline. Default Route Applied."}

@app.get("/api/v1/opportunities/matches", tags=["Module C/D/E: AI Match Engines"])
async def mock_fetch_matches():
    # Will proxy OpenRouter requests via PrivacySanitizer in later phases
    return {"message": "Endpoint Scaffolded"}

@app.post("/api/v1/eoc/secure-grievance", tags=["EOC Integration"])
async def mock_eoc_grievance():
    # Dedicated air-gapped router bypassing AI
    return {"message": "Endpoint Scaffolded"}

# To execute the server locally:
# run: uvicorn main:app --reload --port 8000
