"""
Minimal RAG Service for CA Chatbot - Lightweight version without heavy ML dependencies
"""
import os
import asyncio
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
import openai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MinimalRAGService:
    """Lightweight RAG service without sentence transformers"""
    
    def __init__(self):
        self.qdrant_client = None
        self.openai_client = None
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        
        # Configuration
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Collections to search
        self.collections = [
            os.getenv("QDRANT_TAX_RAG_COLLECTION", "TAX-RAG-1"),
            os.getenv("QDRANT_TAX_DOCUMENTS_COLLECTION", "tax_documents"),
            os.getenv("QDRANT_COLLECTION_NAME", "ca_knowledge_base")
        ]
    
    async def initialize(self):
        """Initialize connections"""
        try:
            # Initialize Qdrant client
            if self.qdrant_url and self.qdrant_api_key:
                self.qdrant_client = QdrantClient(
                    url=self.qdrant_url,
                    api_key=self.qdrant_api_key
                )
                print("✅ Qdrant client initialized")
            
            # Initialize OpenAI client
            if self.openai_api_key:
                openai.api_key = self.openai_api_key
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                print("✅ OpenAI client initialized")
            
        except Exception as e:
            print(f"⚠️ Error initializing services: {e}")
    
    async def check_services(self) -> Dict[str, str]:
        """Check service health"""
        services = {}
        
        # Check OpenAI
        try:
            if self.openai_client:
                # Simple test call
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                services["openai"] = "healthy"
            else:
                services["openai"] = "not_configured"
        except Exception:
            services["openai"] = "error"
        
        # Check Qdrant
        try:
            if self.qdrant_client:
                collections = await asyncio.to_thread(self.qdrant_client.get_collections)
                services["qdrant"] = "healthy"
            else:
                services["qdrant"] = "not_configured"
        except Exception:
            services["qdrant"] = "error"
        
        # Check Brave Search
        services["brave_search"] = "healthy" if self.brave_api_key else "not_configured"
        
        return services
    
    async def get_collections(self) -> List[str]:
        """Get available collections"""
        try:
            if self.qdrant_client:
                collections_info = await asyncio.to_thread(self.qdrant_client.get_collections)
                return [col.name for col in collections_info.collections]
            else:
                return self.collections
        except Exception as e:
            print(f"Error getting collections: {e}")
            return self.collections
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search documents using simple text matching (no embeddings)"""
        results = []
        
        if not self.qdrant_client:
            return results
        
        try:
            # Use Qdrant's built-in text search if available
            for collection_name in self.collections:
                try:
                    # Simple scroll through documents and filter by text
                    search_results = await asyncio.to_thread(
                        self.qdrant_client.scroll,
                        collection_name=collection_name,
                        limit=limit,
                        with_payload=True
                    )
                    
                    # Filter results based on query keywords
                    query_words = query.lower().split()
                    for point in search_results[0]:
                        if point.payload:
                            text_content = str(point.payload.get('text', '')).lower()
                            # Simple keyword matching
                            if any(word in text_content for word in query_words):
                                results.append({
                                    'text': point.payload.get('text', ''),
                                    'source': point.payload.get('source', collection_name),
                                    'score': 0.8  # Fixed score since we're not using embeddings
                                })
                                
                except Exception as e:
                    print(f"Error searching collection {collection_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in document search: {e}")
        
        return results[:limit]
    
    async def web_search(self, query: str) -> Dict[str, Any]:
        """Perform web search using Brave API"""
        if not self.brave_api_key:
            return {"results": [], "used": False}
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.brave_api_key
            }
            
            params = {
                "q": f"{query} India chartered accountant tax GST",
                "count": 3,
                "search_lang": "en",
                "country": "IN"
            }
            
            response = await asyncio.to_thread(
                requests.get,
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for result in data.get("web", {}).get("results", [])[:3]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("description", "")
                    })
                
                return {"results": results, "used": True}
            
        except Exception as e:
            print(f"Web search error: {e}")
        
        return {"results": [], "used": False}
    
    async def generate_response(self, query: str, use_web_search: bool = False, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate response using minimal RAG approach"""
        
        # Search documents
        document_results = await self.search_documents(query)
        
        # Web search if enabled
        web_results = {"results": [], "used": False}
        if use_web_search:
            web_results = await self.web_search(query)
        
        # Prepare context
        context_parts = []
        
        # Add document context
        for doc in document_results:
            context_parts.append(f"Document: {doc['text'][:500]}...")
        
        # Add web context
        for web_result in web_results["results"]:
            context_parts.append(f"Web: {web_result['title']} - {web_result['description']}")
        
        context = "\n\n".join(context_parts)
        
        # Generate response with OpenAI
        response_text = await self.generate_openai_response(query, context)
        
        # Prepare sources
        sources = []
        sources.extend([{"type": "document", "content": doc["text"][:200], "source": doc["source"]} for doc in document_results])
        sources.extend([{"type": "web", "title": web["title"], "url": web["url"]} for web in web_results["results"]])
        
        return {
            "response": response_text,
            "sources": sources,
            "documents_found": len(document_results),
            "web_search_used": web_results["used"]
        }
    
    async def generate_openai_response(self, query: str, context: str) -> str:
        """Generate response using OpenAI"""
        if not self.openai_client:
            return f"I understand you're asking about: {query}. However, OpenAI service is not configured."
        
        try:
            system_prompt = """You are a professional AI assistant specifically designed for Indian chartered accountants and primarily serves users in India. You provide accurate, comprehensive, and practical advice tailored to Indian tax laws, GST regulations, PAN requirements, and other India-specific accounting and compliance matters.

Your responses should be:
- Professional and authoritative
- Specific to Indian regulations and practices
- Comprehensive yet practical
- Well-structured with clear explanations
- Include relevant examples when helpful

Focus on Indian tax laws, GST compliance, PAN procedures, accounting standards, and professional CA guidance."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context information:\n{context}\n\nQuestion: {query}"}
            ]
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return f"I understand your question about {query}, but I'm currently unable to provide a detailed response due to a service issue. Please try again later."
