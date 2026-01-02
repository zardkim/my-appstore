"""
Version API endpoints

Provides version information for the backend API.
"""

from fastapi import APIRouter
from app.version import get_version, get_version_info

router = APIRouter()

@router.get("/version")
async def get_api_version():
    """
    Get API version information

    Returns the current version of the backend API.
    """
    return {
        "version": get_version(),
        "api": "MyApp Store Backend"
    }

@router.get("/version/detailed")
async def get_detailed_version():
    """
    Get detailed version information

    Returns comprehensive version information including build details.
    """
    version_info = get_version_info()
    return {
        "api": "MyApp Store Backend",
        **version_info
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns API health status and version.
    """
    return {
        "status": "healthy",
        "version": get_version(),
        "api": "MyApp Store Backend"
    }
