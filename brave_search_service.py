import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class BraveSearchService:
    """Service class for Brave Search API integration"""
    
    def __init__(self):
        """Initialize Brave Search client"""
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
    def search_web(self, query: str, count: int = 5, focus_on_recent: bool = True) -> Dict[str, Any]:
        """
        Search the web using Brave Search API
        
        Args:
            query: Search query
            count: Number of results to return (max 20)
            focus_on_recent: Whether to focus on recent results
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Enhance query for tax/legal context
            enhanced_query = self._enhance_query_for_legal_context(query)
            
            params = {
                "q": enhanced_query,
                "count": min(count, 10),  # Limit to 10 for API efficiency
                "search_lang": "en",
                "country": "IN",  # Focus on India for CA-related content
                "safesearch": "strict",
                "text_decorations": False,
                "spellcheck": True
            }
            
            # Add freshness parameter for recent results
            if focus_on_recent:
                params["freshness"] = "py"  # Past year
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_search_results(data, query)
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status_code}",
                    "results": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _enhance_query_for_legal_context(self, query: str) -> str:
        """Enhance query with legal/tax context for better results"""
        # Add context keywords for better legal/tax results
        legal_keywords = ["tax law", "chartered accountant", "CA", "legal", "regulation", "compliance"]
        
        # Check if query already contains legal context
        query_lower = query.lower()
        has_legal_context = any(keyword in query_lower for keyword in ["tax", "legal", "law", "regulation", "compliance", "ca", "chartered"])
        
        if not has_legal_context:
            # Add relevant context based on common CA topics
            if any(term in query_lower for term in ["investment", "deduction", "income", "return", "filing"]):
                query += " tax law India"
            elif any(term in query_lower for term in ["company", "business", "corporate"]):
                query += " corporate law India"
            else:
                query += " chartered accountant India"
        
        return query
    
    def _process_search_results(self, data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Process and format search results"""
        results = []
        
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "published": item.get("age", ""),
                    "domain": self._extract_domain(item.get("url", "")),
                    "relevance_score": self._calculate_relevance_score(item, original_query)
                }
                results.append(result)
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "success": True,
            "query": original_query,
            "results": results,
            "total_results": len(results),
            "search_metadata": {
                "query_enhanced": data.get("query", {}).get("original", original_query),
                "search_time": data.get("query", {}).get("search_time", 0)
            }
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def _calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        query_words = set(query.lower().split())
        
        # Score based on title relevance
        title = item.get("title", "").lower()
        title_words = set(title.split())
        title_overlap = len(query_words.intersection(title_words))
        score += title_overlap * 0.4
        
        # Score based on description relevance
        description = item.get("description", "").lower()
        desc_words = set(description.split())
        desc_overlap = len(query_words.intersection(desc_words))
        score += desc_overlap * 0.3
        
        # Bonus for authoritative domains
        domain = self._extract_domain(item.get("url", ""))
        authoritative_domains = [
            "incometaxindia.gov.in", "mca.gov.in", "icai.org", 
            "cleartax.in", "taxguru.in", "caclubindia.com",
            "moneycontrol.com", "economictimes.indiatimes.com"
        ]
        
        if any(auth_domain in domain for auth_domain in authoritative_domains):
            score += 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    def search_for_current_affairs(self, query: str) -> Dict[str, Any]:
        """Search specifically for current affairs and recent updates"""
        # Enhance query for current affairs
        current_affairs_query = f"{query} latest news updates 2024 2025"
        
        return self.search_web(
            query=current_affairs_query,
            count=5,
            focus_on_recent=True
        )
    
    def get_contextual_web_info(self, rag_query: str, rag_confidence: float) -> Optional[Dict[str, Any]]:
        """
        Get contextual web information to supplement RAG response
        
        Args:
            rag_query: Original RAG query
            rag_confidence: Confidence score of RAG response
            
        Returns:
            Web search results if needed, None otherwise
        """
        # Only search web if RAG confidence is low or query seems to need current info
        current_keywords = ["latest", "recent", "current", "new", "update", "2024", "2025"]
        needs_current_info = any(keyword in rag_query.lower() for keyword in current_keywords)
        
        if rag_confidence < 0.4 or needs_current_info:
            return self.search_web(rag_query, count=3, focus_on_recent=True)
        
        return None
    
    def test_connection(self) -> bool:
        """Test Brave Search API connection"""
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={"q": "test", "count": 1},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Brave Search connection test failed: {e}")
            return False
    
    def format_web_results_for_display(self, search_results: Dict[str, Any]) -> str:
        """Format web search results for display in chat"""
        if not search_results.get("success") or not search_results.get("results"):
            return "No relevant web results found."
        
        formatted = "🌐 **Web Search Results:**\n\n"
        
        for i, result in enumerate(search_results["results"][:3], 1):
            formatted += f"**{i}. {result['title']}**\n"
            formatted += f"   📄 {result['description'][:150]}...\n"
            formatted += f"   🔗 [{result['domain']}]({result['url']})\n"
            if result.get('published'):
                formatted += f"   📅 {result['published']}\n"
            formatted += "\n"
        
        return formatted
