# CA Assistant - Minimal API Version

A lightweight, API-only Retrieval-Augmented Generation (RAG) service specifically designed for Indian Chartered Accountants. Optimized for low memory usage (<512MB) while maintaining core functionality for document search, AI response generation, and web search integration.

## 🎯 Minimal Features

- **📚 Lightweight Document Search**: Retrieves information from Qdrant vector database without heavy ML dependencies
- **🤖 AI-Powered Responses**: Uses OpenAI GPT-4o-mini with India-specific CA prompts
- **🌐 Optional Web Search**: Brave Search API integration for current affairs
- **⚖️ India-Specific Focus**: Tailored for Indian chartered accountants with GST, PAN, and tax law expertise
- **📊 Source Attribution**: Shows document and web sources in responses
- **🚀 Pure REST API**: Lightweight FastAPI server with comprehensive documentation
- **💾 Memory Optimized**: Runs under 512MB RAM on Render's starter plan
- **📄 Document Processing**: PDF, Word, Excel support without pandas/scikit-learn
- **⚡ Fast Response Times**: Optimized for quick processing without heavy ML libraries
- **🔧 Production Ready**: Gunicorn + uvicorn workers for reliable deployment

## Architecture

The system consists of several enhanced components:

1. **QdrantService** (`qdrant_service.py`): Handles connection to Qdrant vector database with multi-collection support
2. **DocumentRetriever** (`retrieval_system.py`): Retrieves relevant documents with smart relevance filtering
3. **ResponseGenerator** (`response_generator.py`): Enhanced response generation with AI refinement and web search integration
4. **OpenAIService** (`openai_service.py`): Professional legal assistant response refinement using GPT-4o-mini
5. **BraveSearchService** (`brave_search_service.py`): Web search integration for current affairs and recent updates
6. **Enhanced Chainlit App** (`app.py`): Modern chat interface with toggle controls and metadata display
7. **API Server** (`api_server.py`): FastAPI server providing REST API endpoints and web interface hosting

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

### Local Development

#### Running the Chainlit Web Interface

Start the Chainlit application:

```bash
chainlit run app.py
```

The chatbot will be available at `http://localhost:8000`

#### Running the API Server

Start the FastAPI server with both web interface and API endpoints:

```bash
python api_server.py
```

The server will be available at:
- API Documentation: `http://localhost:10000/docs`
- Web Interface: `http://localhost:10000/chainlit`
- Health Check: `http://localhost:10000/health`

### Production Deployment

#### Render Deployment

1. Connect your GitHub repository to Render
2. Set the following environment variables in Render dashboard:
   - `OPENAI_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `QDRANT_COLLECTION_NAME`
   - `QDRANT_TAX_RAG_COLLECTION`
   - `QDRANT_TAX_DOCUMENTS_COLLECTION`
   - `BRAVE_API_KEY`

3. Render will automatically use `render.yaml` for deployment configuration

#### API Usage

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API usage examples.

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
