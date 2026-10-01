import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
	from app.main import app  # noqa
except Exception as exc:
	from fastapi import FastAPI

	initialization_error = f"{type(exc).__name__}: {exc}"
	app = FastAPI(title="18Mart Portal API - initialization error")

	@app.get("/{path:path}")
	async def initialization_failure(path: str):
		return {
			"status": "error",
			"message": "API initialization failed",
			"error": initialization_error,
		}
