import os
import openai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIService:
    """Service class for OpenAI API integration to refine RAG responses"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = "gpt-4o-mini"  # Using cost-effective model
        
    def refine_rag_response(self, query: str, rag_response: str, sources: list, confidence: float, document_context: bool = False) -> Dict[str, Any]:
        """
        Refine RAG response with legal assistant personality for chartered accountants
        
        Args:
            query: Original user query
            rag_response: Raw response from RAG system
            sources: List of source documents
            confidence: Confidence score of RAG response
            
        Returns:
            Dictionary with refined response and metadata
        """
        try:
            # Create the system prompt for legal assistant personality
            system_prompt = self._get_legal_assistant_prompt()
            
            # Create the user prompt with context
            user_prompt = self._create_refinement_prompt(query, rag_response, sources, confidence, document_context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent legal advice
                max_tokens=2500,  # Increased for more comprehensive responses
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            refined_response = response.choices[0].message.content
            
            return {
                "refined_response": refined_response,
                "original_response": rag_response,
                "tokens_used": response.usage.total_tokens,
                "model_used": self.model,
                "refinement_successful": True
            }
            
        except Exception as e:
            print(f"Error refining response with OpenAI: {e}")
            return {
                "refined_response": rag_response,  # Fallback to original
                "original_response": rag_response,
                "error": str(e),
                "refinement_successful": False
            }
    
    def _get_legal_assistant_prompt(self) -> str:
        """Get the system prompt for CA-focused assistant personality"""
        return """You are a professional AI assistant specifically designed for Indian chartered accountants and primarily serves users in India. You provide accurate, comprehensive, and practical advice tailored to Indian tax laws, GST regulations, PAN requirements, and other India-specific accounting and compliance matters.

PERSONALITY & TONE:
- Professional yet friendly and approachable
- Comprehensive but well-structured (provide detailed information when needed)
- Use clear, practical language that CAs can quickly understand
- Supportive and helpful tone
- Focus on actionable advice

RESPONSE STYLE:
- Provide COMPREHENSIVE and INFORMATIVE responses (5-10 sentences for complex queries)
- Start with the direct answer immediately
- Use proper formatting with bullet points, numbered lists, and sections
- Highlight key dates, amounts, or requirements in **bold**
- Include relevant examples when helpful
- End with practical tips or next steps

CONTENT GUIDELINES:
- Base responses ONLY on the provided context
- If context is insufficient, say "Based on available information..." and provide what you can
- Focus on practical implications for CA practice
- Mention compliance deadlines when relevant
- Keep legal jargon minimal - use plain business language
- Provide step-by-step processes when applicable

RESPONSE FORMAT:
- Direct answer first (2-3 sentences maximum)
- Key points organized with proper formatting:
  • Use bullet points for lists
  • Use numbered lists for processes
  • Use **bold** for important information
  • Use SHORT section headers (2-4 words maximum)
- Include practical tips or next steps
- Brief disclaimer only when necessary

FORMATTING REQUIREMENTS:
- Use clean markdown formatting WITHOUT hashtags (#)
- Keep all headings SHORT and concise (maximum 4 words)
- Structure information clearly with brief subheadings
- Make responses scannable with good visual hierarchy
- Include specific details like amounts, dates, percentages
- Provide context and background when relevant
- NEVER use hashtag symbols (#) in responses

AVOID:
- Overly brief responses that lack detail
- Poor formatting without structure
- Excessive legal disclaimers
- Academic-style responses without practical value"""

    def _create_refinement_prompt(self, query: str, rag_response: str, sources: list, confidence: float, document_context: bool = False) -> str:
        """Create the user prompt for response refinement"""
        
        # Format sources information
        sources_info = ""
        if sources:
            sources_info = "\n\nSOURCE DOCUMENTS:\n"
            for i, source in enumerate(sources[:5], 1):  # Show more sources for better context
                if source.get('type') == 'uploaded_document':
                    # Handle uploaded document sources
                    name = source.get('name', 'Untitled Document')
                    relevance = source.get('relevance', 0.0)
                    sources_info += f"{i}. {name} (Uploaded Document, Relevance: {relevance:.3f})\n"
                else:
                    # Handle knowledge base sources
                    title = source.get('title', 'Untitled')
                    collection = source.get('collection', 'Unknown')
                    relevance = source.get('relevance_score', 0.0)
                    sources_info += f"{i}. {title} (Knowledge Base: {collection}, Relevance: {relevance:.3f})\n"
        
        confidence_note = ""
        if document_context:
            confidence_note = "\n\nNOTE: This response is based on uploaded document(s). Ensure accuracy by cross-referencing with current regulations."
        elif confidence < 0.3:
            confidence_note = "\n\nNOTE: The confidence score for this response is relatively low, so please be cautious and recommend professional consultation where appropriate."
        elif confidence > 0.7:
            confidence_note = "\n\nNOTE: This response has high confidence based on the source documents."
        
        return f"""Refine this response for a chartered accountant. Make it comprehensive, well-formatted, and professional.

QUERY: {query}

RESPONSE TO REFINE:
{rag_response}
{sources_info}
{confidence_note}

INSTRUCTIONS:
1. Provide COMPREHENSIVE and DETAILED responses (5-10 sentences for complex queries)
2. Start with the direct answer immediately
3. Use proper markdown formatting with bullet points, numbered lists, and **bold** text
4. Structure information clearly with sections and headings when appropriate
5. Include specific details like amounts, dates, percentages, and processes
6. Provide step-by-step guidance when applicable
7. Add practical tips and next steps
8. Include relevant examples or scenarios when helpful
9. Use proper formatting to make the response scannable and professional
10. Keep disclaimers brief but include when necessary

FORMATTING REQUIREMENTS:
- Use **bold** for important information (amounts, dates, key terms)
- Use bullet points (•) for lists of items
- Use numbered lists (1., 2., 3.) for processes or steps
- Use sections with clear headings when covering multiple topics
- Include specific details and context
- Make the response visually appealing and easy to scan

Make this response comprehensive, well-structured, and immediately useful for a chartered accountant."""

    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"OpenAI connection test failed: {e}")
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics (placeholder for future implementation)"""
        return {
            "model": self.model,
            "connection_status": self.test_connection()
        }
