"""
Minimal API Server for CA Chatbot - API-only lightweight version
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

# Import minimal services
from minimal_rag_service import MinimalRAGService

# Initialize minimal service
rag_service = MinimalRAGService()

# Minimal FastAPI app
app = FastAPI(
    title="CA Chatbot API - Minimal",
    description="Lightweight AI-powered Chartered Accountant Assistant API for Indian CAs",
    version="2.0.0-minimal",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    web_search_enabled: Optional[bool] = False
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict[str, Any]]] = None
    web_search_used: Optional[bool] = False
    documents_found: Optional[int] = 0
    session_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]

# API Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""

    # Test minimal service connections
    services_status = await rag_service.check_services()

    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.now().isoformat(),
        services=services_status
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for API access
    """
    try:
        # Generate response using minimal RAG service
        result = await rag_service.generate_response(
            query=request.message,
            use_web_search=request.web_search_enabled or False,
            session_id=request.session_id
        )

        return ChatResponse(
            response=result['response'],
            sources=result.get('sources', []),
            web_search_used=result.get('web_search_used', False),
            documents_found=result.get('documents_found', 0),
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/collections")
async def get_collections():
    """Get available document collections"""
    try:
        collections = await rag_service.get_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching collections: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CA Chatbot API - Minimal",
        "description": "Lightweight AI-powered Chartered Accountant Assistant for Indian CAs",
        "version": "2.0.0-minimal",
        "features": [
            "API-only service (no web interface)",
            "Lightweight memory footprint (<512MB)",
            "OpenAI GPT integration",
            "Qdrant vector database",
            "Document processing (PDF, Word, Excel)",
            "Brave Search integration",
            "India-specific CA guidance"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health",
            "collections": "/api/collections",
            "docs": "/docs"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize minimal services on startup"""
    print("🚀 Starting CA Chatbot API Server (Minimal Version)...")
    print("📊 Initializing lightweight services...")

    # Initialize RAG service
    await rag_service.initialize()

    print("✅ Minimal API Server ready!")
    print(f"📱 API Documentation: http://localhost:{os.getenv('PORT', 10000)}/docs")
    print(f"🌐 Health Check: http://localhost:{os.getenv('PORT', 10000)}/health")
    print("💡 This is a lightweight API-only version (no web interface)")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🚀 Starting CA Chatbot API Server on {host}:{port}")
    print(f"📱 Environment: {'Production' if not os.getenv('DEBUG', 'False').lower() == 'true' else 'Development'}")
    print(f"🌐 Web Interface will be available at: http://{host}:{port}/chainlit")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"❤️ Health Check: http://{host}:{port}/health")

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )
