from typing import List, Dict, Any, Optional
from retrieval_system import DocumentRetriever
from openai_service import OpenAIService
from brave_search_service import BraveSearchService
import re

class ResponseGenerator:
    """Response generation system that creates answers based solely on retrieved documents"""
    
    def __init__(self):
        """Initialize the response generator"""
        self.retriever = DocumentRetriever()
        self.openai_service = OpenAIService()
        self.brave_search = BraveSearchService()
        
    def generate_response(self, query: str) -> Dict[str, Any]:
        """
        Generate a response based on retrieved documents
        
        Args:
            query: User query
            
        Returns:
            Dictionary containing response, sources, and metadata
        """
        # Retrieve relevant documents
        documents = self.retriever.retrieve_relevant_documents(query, max_docs=5)
        
        if not documents:
            return {
                'response': "I apologize, but I couldn't find any relevant information in the knowledge base to answer your question. Please try rephrasing your question or ask about topics covered in the available documents.",
                'sources': [],
                'confidence': 0.0,
                'documents_found': 0
            }
        
        # Generate response based on documents
        response = self._create_response_from_documents(query, documents)
        
        # Extract source information
        sources = self._extract_sources(documents)
        
        # Calculate confidence based on document scores
        confidence = self._calculate_confidence(documents)
        
        return {
            'response': response,
            'sources': sources,
            'confidence': confidence,
            'documents_found': len(documents)
        }

    def generate_enhanced_response(self, query: str, use_web_search: bool = False, refine_with_openai: bool = True, uploaded_files: list = None) -> Dict[str, Any]:
        """
        Generate enhanced response with document context, OpenAI refinement and optional web search

        Args:
            query: User query
            use_web_search: Whether to include web search results
            refine_with_openai: Whether to refine response with OpenAI
            uploaded_files: List of uploaded file information for document-based queries

        Returns:
            Dictionary containing enhanced response with all metadata
        """
        # PRIORITY 1: Check uploaded documents first
        document_response = None
        document_context_used = False
        document_sources = []

        if uploaded_files:
            document_response = self._process_document_query(query, uploaded_files)
            if document_response['relevant']:
                document_context_used = True
                document_sources = document_response['sources']


        # PRIORITY 2: Get RAG response (only as supplementary if documents found, primary if no documents)
        rag_result = self.generate_response(query)

        # Determine primary response source
        primary_response = document_response['response'] if document_context_used else rag_result['response']
        primary_confidence = 0.9 if document_context_used else rag_result['confidence']  # Higher confidence for document matches

        # Initialize enhanced result with prioritized data
        enhanced_result = {
            'rag_response': rag_result['response'],
            'sources': rag_result['sources'],
            'confidence': primary_confidence,
            'documents_found': rag_result['documents_found'],
            'web_search_results': None,
            'web_search_used': False,
            'refined_response': None,
            'openai_refinement_used': False,
            'document_context_used': document_context_used,
            'document_sources': document_sources,
            'final_response': primary_response
        }

        # Add web search if requested or if confidence is low
        web_results = None
        if use_web_search or rag_result['confidence'] < 0.3:
            try:
                web_results = self.brave_search.get_contextual_web_info(
                    query, rag_result['confidence']
                )
                if web_results and web_results.get('success'):
                    enhanced_result['web_search_results'] = web_results
                    enhanced_result['web_search_used'] = True
            except Exception as e:
                print(f"Web search error: {e}")

        # Refine response with OpenAI
        if refine_with_openai:
            try:
                # Prepare context for OpenAI including document context, RAG, and web results
                if document_context_used:
                    # Use document response as primary, supplement with RAG if needed
                    context_for_refinement = enhanced_result['final_response']
                    if rag_result['confidence'] > 0.3:  # Add RAG context if it's relevant
                        context_for_refinement += f"\n\nSUPPLEMENTARY KNOWLEDGE BASE INFO:\n{rag_result['response']}"
                else:
                    # Use RAG response as primary
                    context_for_refinement = rag_result['response']

                # Add web context if available
                if web_results and web_results.get('success'):
                    web_context = self._format_web_context_for_refinement(web_results)
                    context_for_refinement += f"\n\nADDITIONAL WEB CONTEXT:\n{web_context}"

                # Combine all sources for refinement
                all_sources = rag_result['sources'] + document_sources

                refinement_result = self.openai_service.refine_rag_response(
                    query=query,
                    rag_response=context_for_refinement,
                    sources=all_sources,
                    confidence=max(rag_result['confidence'], 0.8 if document_context_used else 0.0),
                    document_context=document_context_used
                )

                if refinement_result.get('refinement_successful'):
                    enhanced_result['refined_response'] = refinement_result['refined_response']
                    enhanced_result['openai_refinement_used'] = True
                    enhanced_result['final_response'] = refinement_result['refined_response']
                    enhanced_result['openai_tokens_used'] = refinement_result.get('tokens_used', 0)

            except Exception as e:
                print(f"OpenAI refinement error: {e}")

        return enhanced_result

    def _format_web_context_for_refinement(self, web_results: Dict[str, Any]) -> str:
        """Format web search results for OpenAI refinement context"""
        if not web_results.get('success') or not web_results.get('results'):
            return ""

        context = "Recent web search findings:\n"
        for i, result in enumerate(web_results['results'][:3], 1):
            context += f"{i}. {result['title']}\n"
            context += f"   {result['description'][:200]}...\n"
            context += f"   Source: {result['domain']}\n\n"

        return context
    
    def _create_response_from_documents(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """
        Create a response by synthesizing information from retrieved documents
        
        Args:
            query: Original user query
            documents: Retrieved relevant documents
            
        Returns:
            Generated response text
        """
        if not documents:
            return "No relevant information found."
        
        # Extract key information from documents
        relevant_info = []
        for doc in documents:
            content = doc.get('content', '').strip()
            if content:
                # Extract the most relevant sentences
                sentences = self._extract_relevant_sentences(content, query)
                relevant_info.extend(sentences)
        
        if not relevant_info:
            return "I found some documents but couldn't extract specific information relevant to your query."
        
        # Create a coherent response
        response = self._synthesize_information(query, relevant_info, documents)
        
        return response
    
    def _extract_relevant_sentences(self, content: str, query: str, max_sentences: int = 3) -> List[str]:
        """
        Extract the most relevant sentences from document content
        
        Args:
            content: Document content
            query: User query
            max_sentences: Maximum number of sentences to extract
            
        Returns:
            List of relevant sentences
        """
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Simple relevance scoring based on keyword overlap
        query_words = set(query.lower().split())
        scored_sentences = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(query_words.intersection(sentence_words))
            if overlap > 0:
                scored_sentences.append((sentence, overlap))
        
        # Sort by relevance and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored_sentences[:max_sentences]]
    
    def _synthesize_information(self, query: str, relevant_info: List[str], documents: List[Dict[str, Any]]) -> str:
        """
        Synthesize information from multiple sources into a coherent response
        
        Args:
            query: Original user query
            relevant_info: List of relevant information pieces
            documents: Source documents
            
        Returns:
            Synthesized response
        """
        if not relevant_info:
            return "No specific information found to answer your query."
        
        # Start with a direct answer approach
        response_parts = []
        
        # Add an introductory statement
        response_parts.append("Based on the available documents, here's what I found:")
        
        # Add the most relevant information
        for i, info in enumerate(relevant_info[:5], 1):  # Limit to top 5 pieces of info
            if info.strip():
                response_parts.append(f"\n{i}. {info.strip()}")
        
        # Add source attribution
        if len(documents) > 1:
            response_parts.append(f"\n\nThis information is compiled from {len(documents)} relevant documents in the knowledge base.")
        else:
            response_parts.append(f"\n\nThis information is from 1 document in the knowledge base.")
        
        return "".join(response_parts)
    
    def _extract_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract source information from documents
        
        Args:
            documents: Retrieved documents
            
        Returns:
            List of source information
        """
        sources = []
        for doc in documents:
            source_info = {
                'title': doc.get('title', 'Untitled'),
                'source': doc.get('source', 'Unknown'),
                'collection': doc.get('collection', 'Unknown'),
                'relevance_score': round(doc.get('score', 0.0), 3)
            }
            sources.append(source_info)
        
        return sources
    
    def _calculate_confidence(self, documents: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score based on document relevance scores
        
        Args:
            documents: Retrieved documents
            
        Returns:
            Confidence score between 0 and 1
        """
        if not documents:
            return 0.0
        
        # Average the top document scores
        scores = [doc.get('score', 0.0) for doc in documents]
        avg_score = sum(scores) / len(scores)
        
        # Normalize to 0-1 range (assuming max score is around 1.0)
        confidence = min(avg_score, 1.0)
        
        return round(confidence, 3)
    
    def generate_response_with_collection(self, query: str, collection_type: str) -> Dict[str, Any]:
        """
        Generate response using a specific collection
        
        Args:
            query: User query
            collection_type: Specific collection to search
            
        Returns:
            Response dictionary
        """
        documents = self.retriever.retrieve_from_specific_collection(query, collection_type, max_docs=5)
        
        if not documents:
            return {
                'response': f"I couldn't find relevant information in the {collection_type} collection. Please try a different query or check other collections.",
                'sources': [],
                'confidence': 0.0,
                'documents_found': 0,
                'collection_used': collection_type
            }
        
        response = self._create_response_from_documents(query, documents)
        sources = self._extract_sources(documents)
        confidence = self._calculate_confidence(documents)
        
        return {
            'response': response,
            'sources': sources,
            'confidence': confidence,
            'documents_found': len(documents),
            'collection_used': collection_type
        }

    def _process_document_query(self, query: str, uploaded_files: list) -> Dict[str, Any]:
        """
        Process query against uploaded documents using semantic search and keyword matching

        Args:
            query: User query
            uploaded_files: List of uploaded file information

        Returns:
            Dictionary with document-based response and relevance info
        """
        if not uploaded_files:
            return {'relevant': False, 'response': '', 'sources': []}

        # Find the most relevant document(s) for the query
        relevant_docs = []
        query_lower = query.lower()

        for file_info in uploaded_files:
            relevance_score = self._calculate_document_relevance(query_lower, file_info)

            # Lower threshold to catch more documents
            if relevance_score > 0.05:  # Lowered threshold
                relevant_docs.append({
                    'file_info': file_info,
                    'relevance': relevance_score
                })

        if not relevant_docs:
            # If no documents meet threshold, still try to use the first document for general queries
            if uploaded_files and any(term in query_lower for term in ['summarize', 'summary', 'what', 'contain', 'document', 'this']):
                relevant_docs.append({
                    'file_info': uploaded_files[0],
                    'relevance': 0.5  # Assign moderate relevance for general queries
                })
            else:
                return {'relevant': False, 'response': '', 'sources': []}

        # Sort by relevance
        relevant_docs.sort(key=lambda x: x['relevance'], reverse=True)

        # Generate response from most relevant documents
        response = self._generate_document_based_response(query, relevant_docs)
        sources = [{'name': doc['file_info']['name'], 'type': 'uploaded_document',
                   'relevance': doc['relevance']} for doc in relevant_docs]

        max_relevance = max(doc['relevance'] for doc in relevant_docs)

        return {
            'relevant': True,
            'response': response,
            'sources': sources,
            'max_relevance': max_relevance
        }

    def _calculate_document_relevance(self, query_lower: str, file_info: dict) -> float:
        """Calculate relevance score between query and document using semantic similarity"""
        content = file_info.get('content', '')
        name = file_info.get('name', '').lower()
        summary = file_info.get('summary', '').lower()

        if not content.strip():
            return 0.0

        try:
            # Use semantic similarity for better matching
            # Access the model through the qdrant service
            model = self.retriever.qdrant_service.embedding_model
            if not model:
                return self._calculate_keyword_relevance(query_lower, file_info)

            query_embedding = model.encode([query_lower])

            # Split content into chunks for better analysis
            content_chunks = self._split_content_into_chunks(content, max_chunk_size=500)

            max_similarity = 0.0
            if content_chunks:
                chunk_embeddings = model.encode(content_chunks)

                # Calculate cosine similarity between query and each chunk
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]
                max_similarity = float(max(similarities))

            # Also check summary and filename for additional context
            summary_similarity = 0.0
            if summary.strip():
                summary_embedding = model.encode([summary])
                summary_similarity = float(cosine_similarity(query_embedding, summary_embedding)[0][0])

            # Combine semantic similarity with keyword matching for robustness
            keyword_relevance = self._calculate_keyword_relevance(query_lower, file_info)

            # Weighted combination: prioritize semantic similarity but include keyword matching
            final_relevance = (max_similarity * 0.7) + (summary_similarity * 0.2) + (keyword_relevance * 0.1)

            # Boost score if query contains file-specific terms
            if any(term in query_lower for term in ['file', 'document', 'upload', 'data', 'table', 'sheet', 'summarize', 'summary']):
                final_relevance += 0.2

            # Boost score if query contains filename (without extension)
            filename_base = file_info.get('name', '').split('.')[0].lower()
            if filename_base and filename_base in query_lower:
                final_relevance += 0.2

            return min(final_relevance, 1.0)  # Cap at 1.0

        except Exception as e:
            # Fallback to keyword matching
            return self._calculate_keyword_relevance(query_lower, file_info)

    def _generate_document_based_response(self, query: str, relevant_docs: list) -> str:
        """Generate comprehensive response based on uploaded document content using semantic search"""
        if not relevant_docs:
            return "I couldn't find relevant information in the uploaded documents."

        # Use the most relevant document as primary source
        primary_doc = relevant_docs[0]['file_info']
        content = primary_doc.get('content', '')

        if not content.strip():
            return f"The document **{primary_doc['name']}** appears to be empty or couldn't be processed properly."

        response_parts = []
        response_parts.append(f"## Document Analysis: {primary_doc['name']}\n")

        try:
            # Use semantic search to find the most relevant content sections
            relevant_sections = self._extract_relevant_sections(query, content)

            if relevant_sections:
                response_parts.append("### Key Information Found:\n")
                for i, section in enumerate(relevant_sections[:8], 1):  # Show top 8 sections for more comprehensive response
                    if section.strip():
                        # Clean up the section text but keep more content
                        cleaned_section = ' '.join(section.split())
                        if len(cleaned_section) > 400:  # Increased length for more detail
                            cleaned_section = cleaned_section[:400] + "..."
                        response_parts.append(f"**{i}.** {cleaned_section}\n")

                # Add comprehensive analysis note
                response_parts.append(f"### Analysis Summary")
                response_parts.append(f"• **Document processed:** {primary_doc['name']}")
                response_parts.append(f"• **Relevant sections found:** {len(relevant_sections)}")
                response_parts.append(f"• **Document relevance score:** {relevant_docs[0]['relevance']:.3f}")

                # Add document metadata if available
                if primary_doc.get('summary'):
                    response_parts.append(f"• **Document summary:** {primary_doc['summary'][:200]}...")

                response_parts.append(f"\n*This analysis is based on the content of your uploaded document. Please verify information against current regulations and consult with relevant authorities for official guidance.*")

            else:
                # Fallback to keyword-based extraction
                keyword_sections = self._extract_keyword_sections(query, content)
                if keyword_sections:
                    response_parts.append("**Related information found:**")
                    for section in keyword_sections[:3]:
                        cleaned_section = ' '.join(section.split())
                        if len(cleaned_section) > 150:
                            cleaned_section = cleaned_section[:150] + "..."
                        response_parts.append(f"• {cleaned_section}")
                else:
                    # Last resort - provide document summary
                    response_parts.append(f"**Document Summary:** {primary_doc.get('summary', 'No summary available')}")
                    response_parts.append("\n*The document doesn't contain specific information matching your query. Try asking about general topics covered in the document.*")

        except Exception as e:
            print(f"Error in document response generation: {e}")
            # Fallback to simple approach
            response_parts.append(f"**Document Summary:** {primary_doc.get('summary', 'No summary available')}")
            response_parts.append("\n*Note: There was an issue analyzing the document content. Please try rephrasing your question.*")

        # Add information about additional relevant documents
        if len(relevant_docs) > 1:
            other_docs = [doc['file_info']['name'] for doc in relevant_docs[1:3]]
            response_parts.append(f"\n*Also found relevant information in: {', '.join(other_docs)}*")

        return '\n'.join(response_parts)

    def _split_content_into_chunks(self, content: str, max_chunk_size: int = 500) -> list:
        """Split content into smaller chunks for better semantic analysis"""
        if not content.strip():
            return []

        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += (" " + paragraph if current_chunk else paragraph)

        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # If no paragraphs, split by sentences
        if not chunks and content.strip():
            sentences = [s.strip() + '.' for s in content.split('.') if s.strip()]
            current_chunk = ""

            for sentence in sentences:
                if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += (" " + sentence if current_chunk else sentence)

            if current_chunk.strip():
                chunks.append(current_chunk.strip())

        return chunks if chunks else [content[:max_chunk_size]]

    def _calculate_keyword_relevance(self, query_lower: str, file_info: dict) -> float:
        """Calculate relevance using keyword matching as fallback"""
        content = file_info.get('content', '').lower()
        name = file_info.get('name', '').lower()
        summary = file_info.get('summary', '').lower()

        # Expand query with related terms for better matching
        expanded_query = self._expand_query_terms(query_lower)

        # Check for keyword matches in expanded query
        query_words = set(expanded_query.split())
        content_words = set(content.split())
        name_words = set(name.split())
        summary_words = set(summary.split())

        # Calculate overlap scores
        content_overlap = len(query_words.intersection(content_words)) / max(len(query_words), 1)
        name_overlap = len(query_words.intersection(name_words)) / max(len(query_words), 1)
        summary_overlap = len(query_words.intersection(summary_words)) / max(len(query_words), 1)

        # Weighted relevance score
        relevance = (content_overlap * 0.7) + (summary_overlap * 0.2) + (name_overlap * 0.1)

        return min(relevance, 1.0)

    def _expand_query_terms(self, query: str) -> str:
        """Expand query with related terms for better matching"""
        # Define related terms for common concepts
        term_expansions = {
            'salary': 'salary compensation pay wage earning income remuneration stipend',
            'pay': 'pay salary compensation wage earning income remuneration',
            'income': 'income salary pay wage earning compensation revenue',
            'wage': 'wage salary pay compensation earning income',
            'earning': 'earning income salary pay wage compensation revenue',
            'compensation': 'compensation salary pay wage earning income remuneration',
            'cost': 'cost expense price fee charge rate',
            'price': 'price cost fee rate charge amount',
            'fee': 'fee cost price charge rate amount',
            'tax': 'tax taxation levy duty assessment',
            'rate': 'rate percentage ratio proportion',
            'benefit': 'benefit advantage perk allowance',
            'allowance': 'allowance benefit perk bonus',
            'bonus': 'bonus incentive reward benefit',
            'experience': 'experience expertise skill qualification background',
            'qualification': 'qualification certification degree credential',
            'requirement': 'requirement criteria condition prerequisite',
            'job': 'job position role career employment work',
            'career': 'career job profession occupation work',
            'work': 'work job employment career profession'
        }

        expanded_terms = []
        query_words = query.split()

        for word in query_words:
            expanded_terms.append(word)
            if word in term_expansions:
                expanded_terms.extend(term_expansions[word].split())

        return ' '.join(expanded_terms)

    def _extract_relevant_sections(self, query: str, content: str) -> list:
        """Extract the most relevant sections from document content using semantic similarity"""
        try:
            # Split content into meaningful sections
            sections = self._split_content_into_sections(content)

            if not sections:
                return []

            # Get embeddings for query and sections
            model = self.retriever.qdrant_service.embedding_model
            query_embedding = model.encode([query.lower()])
            section_embeddings = model.encode(sections)

            # Calculate similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_embedding, section_embeddings)[0]

            # Get sections with similarity above threshold, sorted by relevance
            relevant_sections = []
            for i, similarity in enumerate(similarities):
                if similarity > 0.2:  # Threshold for relevance
                    relevant_sections.append((sections[i], similarity))

            # Sort by similarity score (descending)
            relevant_sections.sort(key=lambda x: x[1], reverse=True)

            # Return just the text content
            return [section[0] for section in relevant_sections]

        except Exception as e:
            print(f"Error in semantic section extraction: {e}")
            return []

    def _split_content_into_sections(self, content: str) -> list:
        """Split content into meaningful sections for analysis"""
        if not content.strip():
            return []

        sections = []

        # First try to split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        if len(paragraphs) > 1:
            sections.extend(paragraphs)
        else:
            # If no clear paragraphs, split by single newlines
            lines = [line.strip() for line in content.split('\n') if line.strip()]

            # Group lines into sections of 2-3 lines each
            current_section = []
            for line in lines:
                current_section.append(line)
                if len(current_section) >= 3 or len(' '.join(current_section)) > 300:
                    sections.append(' '.join(current_section))
                    current_section = []

            # Add remaining lines
            if current_section:
                sections.append(' '.join(current_section))

        # Filter out very short sections
        sections = [s for s in sections if len(s.split()) >= 5]

        return sections

    def _extract_keyword_sections(self, query: str, content: str) -> list:
        """Fallback method to extract sections using keyword matching"""
        expanded_query = self._expand_query_terms(query.lower())
        query_words = set(expanded_query.split())

        sections = self._split_content_into_sections(content)
        relevant_sections = []

        for section in sections:
            section_words = set(section.lower().split())
            overlap = len(query_words.intersection(section_words))

            if overlap > 0:
                # Calculate relevance score
                relevance = overlap / len(query_words)
                relevant_sections.append((section, relevance))

        # Sort by relevance
        relevant_sections.sort(key=lambda x: x[1], reverse=True)

        return [section[0] for section in relevant_sections]
