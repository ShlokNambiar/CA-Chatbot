# CA Chatbot API Documentation

## Overview

The CA Chatbot API provides both a web interface and REST API endpoints for interacting with the AI-powered Chartered Accountant Assistant designed for Indian CAs.

## Base URL

```
https://your-app-name.onrender.com
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Endpoints

### 1. Health Check

**GET** `/health`

Check the health status of the API and its services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "services": {
    "openai": "healthy",
    "qdrant": "healthy",
    "brave_search": "healthy"
  }
}
```

### 2. Chat Endpoint

**POST** `/api/chat`

Send a message to the CA Assistant and receive an AI-generated response.

**Request Body:**
```json
{
  "message": "What are the GST rates for software services in India?",
  "web_search_enabled": false,
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "For software services in India, the GST rate is 18%...",
  "sources": [
    {
      "title": "GST Rates Document",
      "content": "Relevant excerpt...",
      "score": 0.85
    }
  ],
  "web_search_used": false,
  "documents_found": 3,
  "session_id": "optional-session-id"
}
```

### 3. Available Collections

**GET** `/api/collections`

Get a list of available document collections in the knowledge base.

**Response:**
```json
{
  "collections": [
    "TAX-RAG-1",
    "tax_documents",
    "ca_knowledge_base",
    "test_project_indexing",
    "hugging_face_docs",
    "transformers_docs"
  ]
}
```

### 4. Root Information

**GET** `/`

Get basic API information and available endpoints.

**Response:**
```json
{
  "message": "CA Chatbot API",
  "description": "AI-powered Chartered Accountant Assistant for Indian CAs",
  "endpoints": {
    "chat": "/api/chat",
    "health": "/health",
    "collections": "/api/collections",
    "docs": "/docs",
    "web_interface": "/chainlit"
  }
}
```

## Web Interface

### Chainlit Web Interface

**URL:** `/chainlit`

Access the full web-based chat interface with file upload capabilities and interactive features.

### API Documentation

**URL:** `/docs`

Interactive API documentation powered by FastAPI's automatic OpenAPI documentation.

## Example Usage

### Python Example

```python
import requests

# Base URL of your deployed app
BASE_URL = "https://your-app-name.onrender.com"

# Send a chat message
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "message": "What are the compliance requirements for GST registration?",
        "web_search_enabled": True
    }
)

if response.status_code == 200:
    data = response.json()
    print("Response:", data["response"])
    print("Sources found:", len(data.get("sources", [])))
else:
    print("Error:", response.status_code, response.text)
```

### cURL Example

```bash
curl -X POST "https://your-app-name.onrender.com/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the tax implications of digital services in India",
    "web_search_enabled": false
  }'
```

### JavaScript Example

```javascript
const BASE_URL = "https://your-app-name.onrender.com";

async function askChatbot(message) {
  try {
    const response = await fetch(`${BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        web_search_enabled: true
      })
    });
    
    const data = await response.json();
    console.log('Response:', data.response);
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
askChatbot("What are the latest changes in Indian tax law?");
```

## Error Handling

The API returns standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **500**: Internal Server Error

Error responses include a detail message:

```json
{
  "detail": "Error processing request: [specific error message]"
}
```

## Features

- **India-specific CA guidance**: Focused on Indian tax laws, GST, and PAN requirements
- **Document retrieval**: Access to comprehensive knowledge base
- **Web search integration**: Optional current affairs and recent updates
- **AI-powered responses**: Enhanced with OpenAI GPT-4o-mini
- **Multiple interfaces**: Both REST API and web interface
- **Real-time processing**: Fast response times with vector database

## Rate Limits

Currently, there are no rate limits implemented. However, please use the API responsibly.

## Support

For issues or questions, please refer to the project repository or contact the development team.
