"""
FastAPI integration for serving bus schedule PDFs.
Add these endpoints to your main FastAPI application.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime
import os

router = APIRouter(prefix="/api/bus-schedules", tags=["Bus Schedules"])

# Path to bus schedules directory
SCHEDULES_DIR = Path(__file__).parent.parent / "data" / "bus_schedules"


def get_file_info(filepath: Path) -> dict:
    """Get file metadata."""
    if not filepath.exists():
        return None
    
    stat = filepath.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


def read_metadata() -> dict:
    """Read metadata file and parse it."""
    metadata_file = SCHEDULES_DIR / "metadata.txt"
    
    if not metadata_file.exists():
        return {
            "last_updated": None,
            "source_url": None,
            "files": {}
        }
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        metadata = {
            "last_updated": None,
            "source_url": None,
            "files": {}
        }
        
        for line in lines:
            if line.startswith("Last Updated:"):
                metadata["last_updated"] = line.split("Last Updated:")[1].strip()
            elif line.startswith("Source URL:"):
                metadata["source_url"] = line.split("Source URL:")[1].strip()
        
        return metadata
    except Exception as e:
        return {
            "last_updated": None,
            "source_url": None,
            "error": str(e)
        }


@router.get("/weekday")
async def get_weekday_schedule():
    """
    Download the weekday bus schedule PDF.
    
    Returns:
        PDF file of weekday bus schedules
    """
    filepath = SCHEDULES_DIR / "weekday_schedule.pdf"
    
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail="Weekday schedule not found. Please run the download script first."
        )
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="canakkale_weekday_bus_schedule.pdf"
    )


@router.get("/weekend")
async def get_weekend_schedule():
    """
    Download the weekend bus schedule PDF.
    
    Returns:
        PDF file of weekend bus schedules
    """
    filepath = SCHEDULES_DIR / "weekend_schedule.pdf"
    
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail="Weekend schedule not found. Please run the download script first."
        )
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="canakkale_weekend_bus_schedule.pdf"
    )


@router.get("/info")
async def get_schedules_info():
    """
    Get information about available bus schedules.
    
    Returns:
        JSON with metadata about the schedules
    """
    weekday_path = SCHEDULES_DIR / "weekday_schedule.pdf"
    weekend_path = SCHEDULES_DIR / "weekend_schedule.pdf"
    
    metadata = read_metadata()
    
    return {
        "weekday": get_file_info(weekday_path),
        "weekend": get_file_info(weekend_path),
        "metadata": metadata,
        "source_website": "https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/"
    }


@router.get("/status")
async def get_download_status():
    """
    Check if bus schedules are available and up to date.
    
    Returns:
        Status information about the schedules
    """
    weekday_exists = (SCHEDULES_DIR / "weekday_schedule.pdf").exists()
    weekend_exists = (SCHEDULES_DIR / "weekend_schedule.pdf").exists()
    metadata = read_metadata()
    
    status = "ok" if (weekday_exists and weekend_exists) else "incomplete"
    if not weekday_exists and not weekend_exists:
        status = "missing"
    
    return {
        "status": status,
        "weekday_available": weekday_exists,
        "weekend_available": weekend_exists,
        "last_updated": metadata.get("last_updated"),
        "message": (
            "All schedules available" if status == "ok"
            else "Some schedules missing" if status == "incomplete"
            else "No schedules available - run download script"
        )
    }


# Example usage in main.py:
"""
from app.routers.bus_schedules import router as bus_schedules_router

app = FastAPI()
app.include_router(bus_schedules_router)
"""
