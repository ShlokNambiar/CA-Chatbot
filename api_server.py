"""
Minimal API Server for CA Chatbot - API-only lightweight version
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime
import tempfile
import shutil

# Import minimal services
from minimal_rag_service import MinimalRAGService
from file_processor import FileProcessor

# Initialize minimal services
rag_service = MinimalRAGService()
file_processor = FileProcessor()

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

class FileUploadResponse(BaseModel):
    success: bool
    file_name: str
    file_type: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None

class FileAnalysisRequest(BaseModel):
    message: str
    file_content: str
    file_name: str
    file_type: str
    web_search_enabled: Optional[bool] = False
    session_id: Optional[str] = None

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

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a file (PDF, Word, Excel, CSV)
    """
    try:
        # Check file size (limit to 10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

        # Check file type
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in file_processor.get_supported_types():
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported types: {file_processor.get_supported_types()}"
            )

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        try:
            # Process the file
            result = file_processor.process_file(temp_path, file.filename)

            if result['success']:
                return FileUploadResponse(
                    success=True,
                    file_name=result['file_name'],
                    file_type=result['file_type'],
                    content=result['content'],
                    metadata=result['metadata'],
                    summary=result['summary']
                )
            else:
                return FileUploadResponse(
                    success=False,
                    file_name=file.filename,
                    file_type=file_ext,
                    error=result['error']
                )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/analyze-file", response_model=ChatResponse)
async def analyze_file_with_chat(request: FileAnalysisRequest):
    """
    Analyze uploaded file content with chat context
    """
    try:
        # Create enhanced query with file context
        enhanced_query = f"""
        DOCUMENT ANALYSIS REQUEST:

        User Question: {request.message}

        File Name: {request.file_name}
        File Type: {request.file_type}

        DOCUMENT CONTENT:
        {request.file_content}

        Please analyze this document and answer the user's question with specific reference to the document content.
        Focus on CA-specific insights, compliance issues, tax implications, and regulatory requirements.
        """

        # Generate response using RAG service with document context
        result = await rag_service.generate_response(
            query=enhanced_query,
            use_web_search=request.web_search_enabled or False,
            session_id=request.session_id,
            document_context=request.file_content
        )

        # Add document source to sources
        document_source = {
            "type": "document",
            "source": request.file_name,
            "title": f"Uploaded {request.file_type.upper()} Document",
            "content_preview": request.file_content[:200] + "..." if len(request.file_content) > 200 else request.file_content
        }

        sources = result.get('sources', [])
        sources.insert(0, document_source)  # Put document source first

        return ChatResponse(
            response=result['response'],
            sources=sources,
            web_search_used=result.get('web_search_used', False),
            documents_found=result.get('documents_found', 0) + 1,  # +1 for uploaded document
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")

@app.get("/api/collections")
async def get_collections():
    """Get available document collections"""
    try:
        collections = await rag_service.get_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching collections: {str(e)}")

@app.get("/api/supported-file-types")
async def get_supported_file_types():
    """Get list of supported file types for upload"""
    return {
        "supported_types": file_processor.get_supported_types(),
        "max_file_size": "10MB",
        "description": "Upload PDF, Word, Excel, or CSV files for analysis"
    }

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
