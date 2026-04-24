"""
WSGI/ASGI entry point for Render deployment.
Gunicorn uses uvicorn workers to serve the FastAPI (ASGI) app.

Usage (Render start command):
    gunicorn wsgi:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
"""

from main import app  # noqa: F401
