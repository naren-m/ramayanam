#!/usr/bin/env python3
"""
FastAPI server for Ramayanam RAG System
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import asyncio
from contextlib import asynccontextmanager

from ramayanam_rag_system import RamayanamRAGSystem, RamayanamSloka

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG system instance
rag_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global rag_system
    
    # Startup: Initialize RAG system
    logger.info("🚀 Initializing Ramayanam RAG System...")
    
    data_path = os.getenv("DATA_PATH", "./data/slokas/Slokas")
    db_path = os.getenv("DB_PATH", "./ramayanam_chroma_db")
    ollama_url = os.getenv("OLLAMA_URL", "http://192.168.68.73:11434")
    
    try:
        rag_system = RamayanamRAGSystem(
            data_path=data_path,
            db_path=db_path,
            ollama_url=ollama_url
        )
        
        # Load and index corpus
        logger.info("📚 Loading corpus...")
        rag_system.load_corpus()
        
        logger.info("🔍 Indexing corpus...")
        rag_system.index_corpus()
        
        logger.info("✅ RAG system ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG system: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Ramayanam RAG API",
    description="API for querying the Ramayanam using Retrieval-Augmented Generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests/responses
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int

class GenerateRequest(BaseModel):
    query: str
    model: Optional[str] = None
    top_k: int = 5

class GenerateResponse(BaseModel):
    query: str
    response: str
    context_used: str
    model_used: str

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model_used: str

class HealthResponse(BaseModel):
    status: str
    message: str
    ollama_available: bool
    corpus_loaded: bool

class SlokaReferenceRequest(BaseModel):
    reference: str  # e.g., "BalaKanda.1.5"

class SlokaResponse(BaseModel):
    sloka: Optional[Dict[str, Any]]
    found: bool

# API Routes

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    ollama_available = rag_system.ollama.is_available()
    corpus_loaded = len(rag_system.slokas) > 0
    
    status = "healthy" if ollama_available and corpus_loaded else "degraded"
    
    return HealthResponse(
        status=status,
        message="Ramayanam RAG API is running",
        ollama_available=ollama_available,
        corpus_loaded=corpus_loaded
    )

@app.post("/search", response_model=SearchResponse)
async def search_slokas(request: SearchRequest):
    """Search for relevant slokas"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        results = rag_system.search(request.query, request.top_k)
        
        # Convert results to dictionaries
        results_dict = [sloka.to_dict() for sloka in results]
        
        return SearchResponse(
            results=results_dict,
            total_results=len(results_dict)
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """Generate response using RAG"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Get context for transparency
        context = rag_system.get_context(request.query, request.top_k)
        
        # Generate response
        response = rag_system.generate_response(
            request.query, 
            model=request.model, 
            top_k=request.top_k
        )
        
        # Determine which model was used
        model_used = request.model or rag_system.default_model
        available_models = rag_system.ollama.list_models()
        if available_models and model_used not in available_models:
            model_used = available_models[0]
        
        return GenerateResponse(
            query=request.query,
            response=response,
            context_used=context,
            model_used=model_used
        )
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with context from Ramayanam"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        response = rag_system.chat(request.messages, request.model)
        
        # Determine which model was used
        model_used = request.model or rag_system.default_model
        available_models = rag_system.ollama.list_models()
        if available_models and model_used not in available_models:
            model_used = available_models[0]
        
        return ChatResponse(
            response=response,
            model_used=model_used
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List available Ollama models"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        models = rag_system.ollama.list_models()
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Models list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    # Count slokas by kanda
    kanda_counts = {}
    for sloka in rag_system.slokas:
        kanda = sloka.kanda
        kanda_counts[kanda] = kanda_counts.get(kanda, 0) + 1
    
    return {
        "total_slokas": len(rag_system.slokas),
        "kandas": kanda_counts,
        "embedding_dimension": rag_system.embedding_model.get_dimension(),
        "ollama_available": rag_system.ollama.is_available(),
        "database_path": rag_system.collection._client._settings.persist_directory if rag_system.collection else "N/A"
    }

@app.post("/sloka", response_model=SlokaResponse)
async def get_sloka_by_reference(request: SlokaReferenceRequest):
    """Get a specific sloka by its reference (e.g., 'BalaKanda.1.5')"""
    global rag_system
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        sloka = rag_system.get_sloka_by_reference(request.reference)
        
        if sloka:
            return SlokaResponse(
                sloka=sloka.to_dict(),
                found=True
            )
        else:
            return SlokaResponse(
                sloka=None,
                found=False
            )
            
    except Exception as e:
        logger.error(f"Sloka reference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve a simple HTML interface
@app.get("/")
async def read_root():
    """Simple HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ramayanam RAG API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🕉️ Ramayanam RAG API</h1>
            <p>Retrieval-Augmented Generation system for the Ramayanam Sanskrit epic.</p>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <h3>GET /health</h3>
                <p>Check system health and status</p>
            </div>
            
            <div class="endpoint">
                <h3>POST /search</h3>
                <p>Search for relevant slokas</p>
                <pre>{"query": "Who is Rama?", "top_k": 5}</pre>
            </div>
            
            <div class="endpoint">
                <h3>POST /generate</h3>
                <p>Generate response using RAG</p>
                <pre>{"query": "Tell me about Rama's qualities", "top_k": 5}</pre>
            </div>
            
            <div class="endpoint">
                <h3>POST /chat</h3>
                <p>Chat with context from Ramayanam</p>
                <pre>{"messages": [{"role": "user", "content": "Who is Hanuman?"}]}</pre>
            </div>
            
            <div class="endpoint">
                <h3>GET /models</h3>
                <p>List available Ollama models</p>
            </div>
            
            <div class="endpoint">
                <h3>GET /stats</h3>
                <p>Get system statistics</p>
            </div>
            
            <div class="endpoint">
                <h3>POST /sloka</h3>
                <p>Get a specific sloka by reference</p>
                <pre>{"reference": "BalaKanda.1.5"}</pre>
            </div>
            
            <h2>Documentation:</h2>
            <p><a href="/docs">Interactive API Documentation (Swagger)</a></p>
            <p><a href="/redoc">Alternative Documentation (ReDoc)</a></p>
            
            <h2>Chat Interface:</h2>
            <p>For a full chat interface, use Open WebUI at <a href="http://localhost:3000">http://localhost:3000</a></p>
        </div>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Run the server
    uvicorn.run(
        "fastapi_server:app",
        host=host,
        port=port,
        log_level="info",
        reload=False  # Set to True for development
    )