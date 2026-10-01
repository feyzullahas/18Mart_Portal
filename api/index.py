import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.main import app as fastapi_app

# Vercel Python runtime requires an explicit top-level app/handler variable.
app = fastapi_app
