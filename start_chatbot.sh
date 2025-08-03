#!/bin/bash

# CA Knowledge Base RAG Chatbot Startup Script

echo "Starting CA Knowledge Base RAG Chatbot..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your Qdrant configuration."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "import chainlit, qdrant_client, sentence_transformers" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Required packages not installed. Installing now..."
    pip install -r requirements.txt
fi

# Test Qdrant connection
echo "🔗 Testing Qdrant connection..."
python -c "
from qdrant_service import QdrantService
qs = QdrantService()
if qs.test_connection():
    print('✅ Qdrant connection successful')
else:
    print('❌ Qdrant connection failed')
    exit(1)
" || exit 1

# Start the Chainlit application
echo "🚀 Starting Chainlit application..."
echo "📱 The chatbot will be available at: http://localhost:8000"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

chainlit run app.py --host 0.0.0.0 --port 8000
