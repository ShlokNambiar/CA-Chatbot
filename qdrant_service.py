import os
import json
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QdrantService:
    """Service class for interacting with Qdrant vector database"""
    
    def __init__(self):
        """Initialize Qdrant client and embedding model"""
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        # Initialize sentence transformer for embeddings
        # Using a model that can be transformed to 1536 dimensions
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # 768 dimensions
        
        # Available collections (updated based on actual collections)
        self.collections = {
            'tax_rag': os.getenv("QDRANT_TAX_RAG_COLLECTION", "TAX-RAG-1"),
            'tax_documents': os.getenv("QDRANT_TAX_DOCUMENTS_COLLECTION", "tax_documents"),
            'test_project': "test_project_indexing",
            'hugging_face_docs': "hugging_face_docs",
            'transformers_docs': "transformers_docs"
        }
        
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text and transform to 1536 dimensions"""
        try:
            embedding = self.embedding_model.encode(text)

            # Transform to 1536 dimensions to match collection requirements
            # Pad with zeros if needed (768 -> 1536)
            if len(embedding) < 1536:
                padding = np.zeros(1536 - len(embedding))
                embedding = np.concatenate([embedding, padding])
            elif len(embedding) > 1536:
                # Truncate if too long
                embedding = embedding[:1536]

            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def search_documents(self, query: str, collection_name: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in Qdrant collections

        Args:
            query: Search query text
            collection_name: Specific collection to search (if None, searches all)
            limit: Maximum number of results to return

        Returns:
            List of relevant documents with metadata
        """
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []

        results = []
        collections_to_search = [collection_name] if collection_name else list(self.collections.values())

        for collection in collections_to_search:
            try:
                # Check if collection exists first
                try:
                    collection_info = self.client.get_collection(collection)
                except Exception as e:
                    print(f"Collection {collection} not found: {e}")
                    continue

                # Handle different collection configurations
                search_params = {
                    'collection_name': collection,
                    'limit': limit,
                    'with_payload': True,
                    'with_vectors': False
                }

                # Handle named vectors for TAX-RAG-1 collection
                if collection == "TAX-RAG-1":
                    # Use text-dense vector for this collection
                    search_params['query_vector'] = ("text-dense", query_embedding)
                else:
                    # All other collections use standard vectors with 1536 dimensions
                    search_params['query_vector'] = query_embedding

                search_result = self.client.search(**search_params)

                for point in search_result:
                    # Handle different payload structures
                    payload = point.payload

                    # Extract content from different payload structures
                    content = ""
                    if 'content' in payload:
                        content = payload['content']
                    elif 'page_content' in payload:
                        content = payload['page_content']
                    elif '_node_content' in payload:
                        content = payload['_node_content']

                    # Handle JSON content (for some collections)
                    if isinstance(content, str) and content.startswith('{'):
                        try:
                            json_content = json.loads(content)
                            # Extract text from JSON structure
                            if 'text' in json_content:
                                content = json_content['text']
                            elif 'content' in json_content:
                                content = json_content['content']
                            elif isinstance(json_content, dict):
                                # Look for text-like fields
                                for key in ['text', 'content', 'body', 'description']:
                                    if key in json_content:
                                        content = json_content[key]
                                        break
                        except json.JSONDecodeError:
                            # If it's not valid JSON, keep as is
                            pass

                    # Extract source information
                    source = payload.get('source', payload.get('file_path', payload.get('file_name', 'Unknown')))

                    # Extract title
                    title = payload.get('title', payload.get('file_name', ''))

                    doc = {
                        'id': point.id,
                        'score': point.score,
                        'collection': collection,
                        'content': content,
                        'metadata': payload.get('metadata', payload),
                        'source': source,
                        'title': title
                    }
                    results.append(doc)

            except Exception as e:
                print(f"Error searching collection {collection}: {e}")
                continue

        # Sort by relevance score (higher is better)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about available collections"""
        info = {}
        for name, collection in self.collections.items():
            try:
                collection_info = self.client.get_collection(collection)
                info[name] = {
                    'name': collection,
                    'vectors_count': collection_info.vectors_count,
                    'status': collection_info.status,
                    'available': True
                }
            except Exception as e:
                info[name] = {
                    'name': collection,
                    'error': str(e),
                    'available': False
                }
        return info
    
    def test_connection(self) -> bool:
        """Test connection to Qdrant"""
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
