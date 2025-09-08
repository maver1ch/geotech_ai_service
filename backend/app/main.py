"""
Geotechnical AI Service - FastAPI Application
Main entry point for the API with observability integration
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Import configuration and logging
from app.core.config.settings import get_settings
from app.core.config.logging_config import setup_logging

# Import API schemas
from app.api.schema.request import AskRequest
from app.api.schema.response import AskResponse, HealthResponse, MetricsResponse

# Import core services
from app.core.agent import GeotechAgent
from app.services.observability import get_metrics_collector

# Setup logging
setup_logging()
logger = logging.getLogger("app.main")

# Global agent instance
agent: GeotechAgent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global agent
    
    # Startup
    logger.info("Starting Geotechnical AI Service...")
    try:
        agent = GeotechAgent()
        logger.info("GeotechAgent initialized successfully")
        
        # Initialize metrics collector
        metrics = get_metrics_collector()
        logger.info("Metrics collector initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
        
    yield
    
    # Shutdown
    logger.info("Shutting down Geotechnical AI Service...")
    # Cleanup can be added here if needed

# Create FastAPI application
app = FastAPI(
    title="Geotechnical AI Service",
    description="AI-powered geotechnical engineering assistant with retrieval and calculation capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Optional: Keep minimal request logging for monitoring
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     duration = time.time() - start_time
#     logger.info(f"{request.method} {request.url} - {response.status_code} ({duration:.2f}s)")
#     return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service status
    """
    print("=== HEALTH ENDPOINT CALLED ===", flush=True)
    return HealthResponse(status="ok")

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get service metrics
    Returns operational metrics including request counts, timing, and success rates
    """
    try:
        metrics_collector = get_metrics_collector()
        metrics_data = metrics_collector.get_metrics()
        
        # Convert to response model
        return MetricsResponse(**metrics_data)
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Main endpoint for asking geotechnical engineering questions
    Processes questions through Plan → Execute → Synthesize workflow
    """
    global agent
    
    if not agent:
        logger.error("GeotechAgent not initialized")
        raise HTTPException(status_code=500, detail="Service not properly initialized")
    
    try:
        # Write to file to ensure we capture this
        with open("api_debug.log", "a") as f:
            f.write(f"\n=== API ENDPOINT DEBUG ===\n")
            f.write(f"Received question: '{request.question}'\n")
            f.write(f"Agent type: {type(agent)}\n")
            f.write(f"Agent initialized: {agent is not None}\n")
            f.write(f"About to call agent.run()...\n")
            f.write(f"=== END API ENDPOINT DEBUG ===\n")
            f.flush()
        
        print(f"\n=== API ENDPOINT DEBUG ===", flush=True)
        print(f"Received question: '{request.question}'", flush=True)
        print(f"Agent type: {type(agent)}", flush=True)
        print(f"Agent initialized: {agent is not None}", flush=True)
        print(f"About to call agent.run()...", flush=True)
        print(f"=== END API ENDPOINT DEBUG ===\n", flush=True)
        
        logger.info(f"[API DEBUG] Received question: '{request.question}'")
        logger.info(f"[API DEBUG] Agent type: {type(agent)}")
        logger.info(f"[API DEBUG] Agent initialized: {agent is not None}")
        
        # Process the question through the agent
        response = await agent.run(
            question=request.question,
            trace_id=getattr(request, 'trace_id', None)
        )
        
        print(f"\n=== API RESPONSE DEBUG ===", flush=True)
        print(f"Got response from agent.run()", flush=True)
        print(f"Answer length: {len(response.answer)} chars", flush=True)
        print(f"Citations: {len(response.citations)}", flush=True)
        print(f"Trace ID: {response.trace_id}", flush=True)
        print(f"=== END API RESPONSE DEBUG ===\n", flush=True)
        
        logger.info(f"[API DEBUG] Response received:")
        logger.info(f"    Answer length: {len(response.answer)} chars")
        logger.info(f"    Citations: {len(response.citations)}")
        logger.info(f"    Trace ID: {response.trace_id}")
        logger.info(f"Successfully processed question (trace_id={response.trace_id})")
        return response
        
    except Exception as e:
        print(f"\n=== API EXCEPTION DEBUG ===", flush=True)
        print(f"Exception in API endpoint: {e}", flush=True)
        print(f"=== END API EXCEPTION DEBUG ===\n", flush=True)
        
        logger.error(f"Failed to process question: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,  # Disable auto-reload to prevent RAG issues
        log_level=settings.LOG_LEVEL.lower()
    )