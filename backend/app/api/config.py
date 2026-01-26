"""
Config API for managing application settings
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Union
import json
import os
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


from app.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.config import settings

router = APIRouter()

# Config file path - 환경변수에서 가져오기
CONFIG_DIR = Path(settings.CONFIG_DATA_DIR)
CONFIG_FILE = CONFIG_DIR / "config.json"

def get_default_config() -> Dict[str, Any]:
    """
    Generate default config with environment-aware values.

    NOTE: This is only used when config.json doesn't exist (first run).
    config.json is the single source of truth for all settings.
    Changes should be made in config.json, not here.
    """
    # VITE_APP_URL 환경변수가 있으면 사용, 없으면 기본값
    default_access_url = os.getenv("VITE_APP_URL", "http://localhost:5900")

    return {
        "general": {
            "language": "ko",
            "accessUrl": default_access_url
        },
        "folders": {
            "scanFolders": [settings.SCAN_BASE_PATH]
        },
        "categories": [
        {"name": "Graphics", "label": "그래픽", "icon": "🎨"},
        {"name": "Office", "label": "오피스", "icon": "📊"},
        {"name": "Development", "label": "개발", "icon": "💻"},
        {"name": "Utility", "label": "유틸리티", "icon": "🛠️"},
        {"name": "Media", "label": "미디어", "icon": "🎬"},
        {"name": "OS", "label": "운영체제", "icon": "💿"},
        {"name": "Security", "label": "보안", "icon": "🔒"},
        {"name": "Network", "label": "네트워크", "icon": "🌐"},
        {"name": "Mac", "label": "맥", "icon": "🍎"},
        {"name": "Mobile", "label": "모바일", "icon": "📱"},
        {"name": "Patch", "label": "패치", "icon": "🔧"},
        {"name": "Driver", "label": "드라이버", "icon": "⚙️"},
        {"name": "Source", "label": "소스코드", "icon": "📦"},
        {"name": "Backup", "label": "백업&복구", "icon": "💾"},
        {"name": "Portable", "label": "포터블", "icon": "🎒"},
        {"name": "Business", "label": "업무용", "icon": "💼"},
        {"name": "Engineering", "label": "공학용", "icon": "📐"},
        {"name": "Theme", "label": "테마&스킨", "icon": "🎭"},
        {"name": "Hardware", "label": "하드웨어", "icon": "🔌"},
        {"name": "Font", "label": "글꼴", "icon": "🔤"},
        {"name": "Uncategorized", "label": "미분류", "icon": "📂"}
    ],
        "metadata": {
            "scanMethod": "ai",
            "aiProvider": "openai",
            "aiModel": "gpt-4o-mini",
            "apiKey": "",
            "autoDescription": True,
            "autoIcon": True
        },
        "board": {
            "categories": [
                {"value": "tip", "label": "팁", "color": "green"},
                {"value": "tech", "label": "기술", "color": "blue"},
                {"value": "tutorial", "label": "튜토리얼", "color": "purple"},
                {"value": "qna", "label": "Q&A", "color": "yellow"},
                {"value": "news", "label": "뉴스", "color": "red"}
            ],
            "postsPerPage": "20",
            "allowComments": True,
            "allowAttachments": True,
            "allowAnonymousComments": False
        }
    }


class ConfigUpdateRequest(BaseModel):
    section: str
    data: Dict[str, Any]


def ensure_config_exists():
    """Ensure config directory and file exist"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        # Create default config
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(get_default_config(), f, ensure_ascii=False, indent=2)


def load_config() -> Dict[str, Any]:
    """Load config from JSON file"""
    ensure_config_exists()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.debug(f"Error loading config: {e}")
        return get_default_config()


def save_config(config: Dict[str, Any]):
    """Save config to JSON file"""
    ensure_config_exists()

    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.debug(f"Error saving config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save config")


@router.get("/")
async def get_config(current_user: User = Depends(get_current_user)):
    """
    Get all configuration
    Requires authentication
    """
    config = load_config()

    # Hide API key from non-admin users
    if current_user.role != "admin":
        if "metadata" in config and "apiKey" in config["metadata"]:
            config["metadata"]["apiKey"] = "***" if config["metadata"]["apiKey"] else ""

    return config


@router.get("/{section}")
async def get_config_section(
    section: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get specific configuration section
    Requires authentication
    """
    config = load_config()

    if section not in config:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")

    data = config[section]

    # Hide API key from non-admin users
    if section == "metadata" and current_user.role != "admin":
        if "apiKey" in data:
            data["apiKey"] = "***" if data["apiKey"] else ""

    return data


@router.put("/{section}")
async def update_config_section(
    section: str,
    data: Any,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update specific configuration section
    Requires admin authentication
    Data can be dict (most sections) or list (categories)
    """
    config = load_config()

    # 폴더 설정인 경우 경로 검증
    if section == "folders":
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=422,
                detail="Folders config must be a dictionary"
            )
        if "scanFolders" not in data:
            raise HTTPException(
                status_code=422,
                detail="scanFolders field is required"
            )
        if not isinstance(data["scanFolders"], list):
            raise HTTPException(
                status_code=422,
                detail="scanFolders must be a list"
            )

        # 경로 존재 여부 확인 (경고만 하고 저장은 허용)
        invalid_paths = []
        for folder_path in data["scanFolders"]:
            if not isinstance(folder_path, str):
                raise HTTPException(
                    status_code=422,
                    detail=f"Folder path must be a string: {folder_path}"
                )
            path_obj = Path(folder_path)
            if not path_obj.exists():
                invalid_paths.append(folder_path)
                logger.warning(f"Folder path does not exist: {folder_path}")

        # 존재하지 않는 경로가 있으면 에러 반환
        if invalid_paths:
            raise HTTPException(
                status_code=422,
                detail=f"Following paths do not exist: {', '.join(invalid_paths)}"
            )

    # Update the section
    config[section] = data

    # Save to file
    save_config(config)

    return {"message": f"Section '{section}' updated successfully", "data": data}


@router.post("/reset")
async def reset_config(current_user: User = Depends(get_current_admin_user)):
    """
    Reset configuration to defaults
    Requires admin authentication
    """
    default_config = get_default_config()
    save_config(default_config)

    return {"message": "Configuration reset to defaults", "data": default_config}
