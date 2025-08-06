"""
WSGI entry point for CA Chatbot
This file provides WSGI compatibility for deployment platforms that expect it.
"""

from api_server import app

# WSGI application
application = app

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 10000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)
