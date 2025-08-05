#!/bin/bash

# Render deployment startup script for CA Chatbot

echo "🚀 Starting CA Chatbot on Render..."
echo "=========================================="

# Set environment variables
export PORT=${PORT:-10000}
export HOST=${HOST:-0.0.0.0}

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Warning: OPENAI_API_KEY not set"
fi

if [ -z "$QDRANT_URL" ]; then
    echo "⚠️ Warning: QDRANT_URL not set"
fi

# Start the API server
echo "🔧 Starting API server..."
echo "📱 API will be available at: https://your-app.onrender.com"
echo "📚 API Documentation: https://your-app.onrender.com/docs"
echo "🌐 Web Interface: https://your-app.onrender.com/chainlit"
echo "🛑 Health Check: https://your-app.onrender.com/health"
echo ""

python api_server.py
