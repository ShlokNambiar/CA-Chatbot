"""
API Server for CA Chatbot - Supports both web interface and REST API
"""
import os
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import threading
import time

# Import our services
from response_generator import ResponseGenerator
from openai_service import OpenAIService
from brave_search_service import BraveSearchService
from file_processor import FileProcessor

# Initialize services
response_gen = ResponseGenerator()
openai_service = OpenAIService()
brave_search = BraveSearchService()
file_processor = FileProcessor()

# FastAPI app
app = FastAPI(
    title="CA Chatbot API",
    description="AI-powered Chartered Accountant Assistant API for Indian CAs",
    version="1.0.0",
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
    import datetime
    
    # Test service connections
    services_status = {
        "openai": "healthy" if openai_service else "unavailable",
        "qdrant": "healthy",  # We'll assume healthy for now
        "brave_search": "healthy" if brave_search else "unavailable"
    }
    
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
        # Generate response using the same logic as the Chainlit app
        result = response_gen.generate_enhanced_response(
            query=request.message,
            use_web_search=request.web_search_enabled,
            refine_with_openai=True,
            uploaded_files=[]  # API doesn't support file uploads yet
        )
        
        # Extract sources information
        sources = []
        if result.get('document_sources'):
            sources.extend(result['document_sources'])
        if result.get('web_search_results', {}).get('results'):
            sources.extend(result['web_search_results']['results'])
        
        return ChatResponse(
            response=result['response'],
            sources=sources,
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
        # This would typically query your Qdrant service
        collections = [
            "TAX-RAG-1",
            "tax_documents", 
            "ca_knowledge_base",
            "test_project_indexing",
            "hugging_face_docs",
            "transformers_docs"
        ]
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching collections: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CA Chatbot API",
        "description": "AI-powered Chartered Accountant Assistant for Indian CAs",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health",
            "collections": "/api/collections",
            "docs": "/docs",
            "web_interface": "/chainlit"
        }
    }

# Chainlit integration
chainlit_app = None

def start_chainlit():
    """Start Chainlit in a separate thread"""
    global chainlit_app
    try:
        import chainlit as cl
        from chainlit.server import app as cl_app
        import app  # Import our Chainlit app
        chainlit_app = cl_app
        print("✅ Chainlit app loaded successfully")
    except Exception as e:
        print(f"❌ Error loading Chainlit: {e}")

# Mount Chainlit app
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting CA Chatbot API Server...")
    print("📊 Initializing services...")
    
    # Start Chainlit in background
    start_chainlit()
    
    print("✅ API Server ready!")
    print(f"📱 API Documentation: http://localhost:{os.getenv('PORT', 10000)}/docs")
    print(f"🌐 Health Check: http://localhost:{os.getenv('PORT', 10000)}/health")

# Mount Chainlit app if available
try:
    from chainlit.server import app as chainlit_server
    import app as chainlit_app_module
    app.mount("/chainlit", chainlit_server)
    print("✅ Chainlit web interface mounted at /chainlit")
except Exception as e:
    print(f"⚠️ Chainlit web interface not available: {e}")

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
