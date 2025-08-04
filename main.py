"""
Vercel deployment entry point for CA Chatbot
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables for Chainlit
os.environ.setdefault("CHAINLIT_HOST", "0.0.0.0")
os.environ.setdefault("CHAINLIT_PORT", "8000")

# Import the Chainlit app
try:
    import chainlit as cl

    # Import our app to register the handlers
    import app

    # Get the Chainlit ASGI application
    # This is the correct way to get the ASGI app from Chainlit
    from chainlit.server import app as chainlit_app

    # Export the app for Vercel
    app = chainlit_app

except ImportError as e:
    print(f"Import error: {e}")
    # Create a simple ASGI app for error reporting
    async def app(scope, receive, send):
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [
                    [b'content-type', b'text/html'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': f'''
                <html>
                <head><title>CA Chatbot - Error</title></head>
                <body>
                    <h1>CA Chatbot Deployment Error</h1>
                    <p>Import Error: {str(e)}</p>
                    <p>Please check your environment variables and dependencies.</p>
                </body>
                </html>
                '''.encode(),
            })

except Exception as e:
    print(f"General error: {e}")
    # Create a simple ASGI app for error reporting
    async def app(scope, receive, send):
        if scope['type'] == 'http':
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [
                    [b'content-type', b'text/html'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': f'''
                <html>
                <head><title>CA Chatbot - Error</title></head>
                <body>
                    <h1>CA Chatbot Deployment Error</h1>
                    <p>Error: {str(e)}</p>
                    <p>Please check your configuration.</p>
                </body>
                </html>
                '''.encode(),
            })

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
