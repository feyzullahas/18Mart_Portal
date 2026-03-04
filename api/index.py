"""
Vercel entry point.

Vercel Python 3.12 runtime ASGI native support.
app (FastAPI instance) must be exposed directly — Mangum handler instance
causes 'issubclass() arg 1 must be a class' TypeError in newer Vercel runtime.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.main import app  # noqa – ASGI app, Vercel runtime handles it natively
