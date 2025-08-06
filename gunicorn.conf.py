# Gunicorn configuration file for CA Chatbot - Minimal Version
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 10000)}"
backlog = 512

# Worker processes (minimal memory footprint)
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 50
timeout = 30
keepalive = 2

# Aggressive memory management
max_requests = 50
max_requests_jitter = 25

# Memory optimization for <512MB
preload_app = False
worker_tmp_dir = "/dev/shm"
max_worker_memory = 400  # MB

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ca-chatbot"

# Server mechanics
preload_app = True
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (not needed for Render)
keyfile = None
certfile = None
