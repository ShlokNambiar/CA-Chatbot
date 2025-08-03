from typing import List, Dict, Any, Optional
from qdrant_service import QdrantService
import re

class DocumentRetriever:
    """Document retrieval system for RAG pipeline"""
    
    def __init__(self):
        """Initialize the retrieval system"""
        self.qdrant_service = QdrantService()
        self.min_score_threshold = 0.01  # Minimum similarity score for relevance (lowered for better recall)
        
    def retrieve_relevant_documents(self, query: str, max_docs: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a given query
        
        Args:
            query: User query
            max_docs: Maximum number of documents to retrieve
            
        Returns:
            List of relevant documents with content and metadata
        """
        # Clean and preprocess the query
        cleaned_query = self._preprocess_query(query)
        
        # Search across all collections
        documents = self.qdrant_service.search_documents(
            query=cleaned_query,
            limit=max_docs * 2  # Get more results to filter by threshold
        )
        
        # Filter by relevance threshold and limit results
        relevant_docs = [
            doc for doc in documents 
            if doc['score'] >= self.min_score_threshold
        ][:max_docs]
        
        return relevant_docs
    
    def retrieve_from_specific_collection(self, query: str, collection_type: str, max_docs: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve documents from a specific collection
        
        Args:
            query: User query
            collection_type: Type of collection ('ca_knowledge_base', 'tax_rag', 'tax_documents')
            max_docs: Maximum number of documents to retrieve
            
        Returns:
            List of relevant documents from the specified collection
        """
        if collection_type not in self.qdrant_service.collections:
            return []
            
        collection_name = self.qdrant_service.collections[collection_type]
        cleaned_query = self._preprocess_query(query)
        
        documents = self.qdrant_service.search_documents(
            query=cleaned_query,
            collection_name=collection_name,
            limit=max_docs * 2
        )
        
        # Filter by relevance threshold
        relevant_docs = [
            doc for doc in documents 
            if doc['score'] >= self.min_score_threshold
        ][:max_docs]
        
        return relevant_docs
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess the user query for better retrieval
        
        Args:
            query: Raw user query
            
        Returns:
            Cleaned and preprocessed query
        """
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Convert to lowercase for consistency
        query = query.lower()
        
        return query
    
    def get_context_from_documents(self, documents: List[Dict[str, Any]]) -> str:
        """
        Extract and format context from retrieved documents
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', '').strip()
            source = doc.get('source', 'Unknown')
            title = doc.get('title', '')
            
            if content:
                doc_context = f"Document {i}"
                if title:
                    doc_context += f" - {title}"
                if source:
                    doc_context += f" (Source: {source})"
                doc_context += f":\n{content}\n"
                
                context_parts.append(doc_context)
        
        return "\n".join(context_parts)
    
    def determine_collection_type(self, query: str) -> Optional[str]:
        """
        Determine which collection might be most relevant based on query content
        
        Args:
            query: User query
            
        Returns:
            Suggested collection type or None for all collections
        """
        query_lower = query.lower()
        
        # Tax-related keywords
        tax_keywords = ['tax', 'taxes', 'taxation', 'deduction', 'irs', 'income', 'filing', 'return']
        if any(keyword in query_lower for keyword in tax_keywords):
            return 'tax_rag'
        
        # For now, return None to search all collections
        return None
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the retrieval system"""
        collection_info = self.qdrant_service.get_collection_info()
        return {
            'collections': collection_info,
            'min_score_threshold': self.min_score_threshold,
            'connection_status': self.qdrant_service.test_connection()
        }
