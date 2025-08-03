# Enhanced CA Legal Assistant RAG Chatbot

A sophisticated Retrieval-Augmented Generation (RAG) chatbot with AI refinement and web search capabilities, designed specifically as a legal assistant for chartered accountants.

## 🎯 Enhanced Features

- **📚 Knowledge Base Search**: Retrieves information from indexed documents in Qdrant vector database
- **🤖 AI-Powered Response Refinement**: Uses OpenAI GPT-4o-mini to refine responses with professional legal assistant personality
- **🌐 Toggleable Web Search**: Brave Search API integration for current affairs and recent updates
- **⚖️ Legal Assistant Personality**: Professional, authoritative responses tailored for chartered accountants
- **📊 Comprehensive Source Attribution**: Shows document sources, confidence scores, and metadata
- **🔧 Interactive Controls**: Toggle web search and AI refinement on/off
- **📱 Modern Chainlit Interface**: Clean, professional chat interface with side panels

## Architecture

The system consists of several enhanced components:

1. **QdrantService** (`qdrant_service.py`): Handles connection to Qdrant vector database with multi-collection support
2. **DocumentRetriever** (`retrieval_system.py`): Retrieves relevant documents with smart relevance filtering
3. **ResponseGenerator** (`response_generator.py`): Enhanced response generation with AI refinement and web search integration
4. **OpenAIService** (`openai_service.py`): Professional legal assistant response refinement using GPT-4o-mini
5. **BraveSearchService** (`brave_search_service.py`): Web search integration for current affairs and recent updates
6. **Enhanced Chainlit App** (`app.py`): Modern chat interface with toggle controls and metadata display

## Setup

### Prerequisites

- Python 3.8+
- Access to Qdrant vector database with indexed documents
- Required Python packages (see requirements.txt)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
# OpenAI Configuration (for AI response refinement)
OPENAI_API_KEY="your-openai-api-key"

# Qdrant Configuration
QDRANT_URL="your-qdrant-url"
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_COLLECTION_NAME=ca_knowledge_base
QDRANT_TAX_RAG_COLLECTION=TAX-RAG-1
QDRANT_TAX_DOCUMENTS_COLLECTION=tax_documents

# Brave Search Configuration (for web search)
BRAVE_API_KEY="your-brave-search-api-key"

# Application Configuration
APP_HOST=localhost
APP_PORT=8000
DEBUG=True
```

### Available Collections

The system searches across multiple collections:

- **TAX-RAG-1**: Tax-related RAG documents (with named vectors)
- **tax_documents**: Tax document collection
- **test_project_indexing**: Project documentation
- **hugging_face_docs**: Hugging Face documentation
- **transformers_docs**: Transformers documentation

## Usage

### Running the Chatbot

Start the Chainlit application:

```bash
chainlit run app.py
```

The chatbot will be available at `http://localhost:8000`

### Testing the System

Run the test script to validate all components:

```bash
python test_rag_system.py
```

This will test:
- Qdrant connection
- Embedding generation
- Document retrieval
- Response generation
- Interactive testing session

### Using the Chat Interface

1. Open the chatbot in your browser
2. Ask questions about topics covered in your indexed documents
3. The system will:
   - Search for relevant documents
   - Generate responses based only on found documents
   - Show confidence scores and source information
   - Indicate if no relevant documents are found

## How It Works

1. **Query Processing**: User query is preprocessed and converted to embeddings
2. **Document Retrieval**: System searches Qdrant collections for similar documents
3. **Relevance Filtering**: Only documents above a minimum relevance threshold are used
4. **Response Generation**: System synthesizes information from retrieved documents
5. **Source Attribution**: Response includes source documents and confidence scores

## Configuration

### Relevance Threshold

The system uses a minimum relevance threshold (default: 0.3) to filter documents. You can adjust this in `retrieval_system.py`:

```python
self.min_score_threshold = 0.3  # Adjust as needed
```

### Collection Priority

The system can automatically determine which collection to search based on query content, or search all collections simultaneously.

## Limitations

- **Document-Only**: Only provides information from indexed documents
- **No External Data**: Cannot access web or external APIs
- **Collection Dependent**: Quality depends on the indexed document quality
- **Embedding Model**: Uses sentence-transformers for embeddings (all-MiniLM-L6-v2)

## Troubleshooting

### Connection Issues

1. Verify Qdrant URL and API key in `.env`
2. Check if collections exist and contain documents
3. Run the test script to diagnose issues

### No Results Found

1. Check if documents are properly indexed
2. Try different query phrasings
3. Lower the relevance threshold if needed
4. Verify collection names match your Qdrant setup

### Performance Issues

1. Limit the number of documents retrieved
2. Optimize embedding model if needed
3. Check Qdrant server performance

## Development

### Adding New Collections

1. Add collection name to `.env`
2. Update `collections` dictionary in `QdrantService`
3. Optionally add collection-specific logic in `DocumentRetriever`

### Customizing Response Generation

Modify `ResponseGenerator` class to:
- Change response formatting
- Adjust information synthesis logic
- Add domain-specific processing

## Files Structure

```
├── app.py                 # Main Chainlit application
├── qdrant_service.py      # Qdrant database service
├── retrieval_system.py    # Document retrieval system
├── response_generator.py  # Response generation system
├── test_rag_system.py     # Test script
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── README.md             # This file
```
