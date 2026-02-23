"""
Config API for managing application settings
"""
from fastapi import APIRouter, Depends, HTTPException, Body
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

# Sensitive field names - these are preserved (not overwritten) when incoming value is empty
SENSITIVE_FIELDS = {"apiKey", "geminiApiKey", "openaiApiKey", "googleApiKey", "bingApiKey", "smtpPassword"}

router = APIRouter()

# Config file path
CONFIG_DIR = Path(settings.CONFIG_DATA_DIR)
CONFIG_FILE = CONFIG_DIR / "config.json"


def mask_sensitive_fields(data: Any) -> Any:
    """Recursively mask sensitive fields for non-admin users"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in SENSITIVE_FIELDS and isinstance(value, str):
                result[key] = "***" if value else ""
            elif isinstance(value, (dict, list)):
                result[key] = mask_sensitive_fields(value)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [mask_sensitive_fields(item) for item in data]
    return data


def get_default_config() -> Dict[str, Any]:
    """
    Generate default config with environment-aware values.
    NOTE: Only used when config.json doesn't exist (first run).
    """
    environment = settings.ENVIRONMENT
    default_frontend_url = "http://localhost:5900"
    default_backend_url = "http://localhost:8110"

    default_scan_folder = settings.SCAN_BASE_PATH
    if not default_scan_folder.startswith('/'):
        default_scan_folder = f"/{default_scan_folder}"
    if default_scan_folder == "/library":
        default_scan_folder = "/app/data/library"

    return {
        "general": {
            "language": "ko",
            "frontendUrl": default_frontend_url,
            "backendUrl": default_backend_url
        },
        "folders": {
            "scanFolders": [default_scan_folder]
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
            "openaiApiKey": "",
            "geminiApiKey": "",
            "bingApiKey": "",
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


def ensure_config_exists():
    """Ensure config directory and file exist"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(get_default_config(), f, ensure_ascii=False, indent=2)


def _migrate_config(config: Dict[str, Any]) -> tuple:
    """Migrate legacy config fields. Returns (migrated_config, needs_save)."""
    needs_save = False
    if 'metadata' in config and isinstance(config['metadata'], dict):
        meta = config['metadata']

        # Remove any legacy ENC: encrypted values (from old encryption feature)
        # These can't be decrypted anymore - user will need to re-enter
        for field in list(SENSITIVE_FIELDS):
            if field in meta and isinstance(meta[field], str) and meta[field].startswith('ENC:'):
                logger.warning(f"Removing legacy encrypted value for {field} - please re-enter in Settings")
                meta[field] = ''
                needs_save = True

        # Migrate: metadata.apiKey → metadata.openaiApiKey
        if 'apiKey' in meta:
            if not meta.get('openaiApiKey') and meta['apiKey']:
                meta['openaiApiKey'] = meta['apiKey']
                logger.info("Migrated metadata.apiKey → metadata.openaiApiKey")
            del meta['apiKey']
            needs_save = True

    return config, needs_save


def load_config() -> Dict[str, Any]:
    """Load config from JSON file. Migrates legacy fields if needed."""
    ensure_config_exists()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Migrate legacy fields
        config, needs_save = _migrate_config(config)

        if needs_save:
            try:
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                logger.info("Config migrated and saved")
            except Exception as e:
                logger.warning(f"Could not save migrated config: {e}")

        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()


def save_config(config: Dict[str, Any]):
    """Save config to JSON file (plaintext, no encryption)."""
    ensure_config_exists()

    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save config")


@router.get("/")
async def get_config(current_user: User = Depends(get_current_user)):
    """Get all configuration. Requires authentication."""
    config = load_config()
    if current_user.role != "admin":
        config = mask_sensitive_fields(config)
    return config


@router.get("/{section}")
async def get_config_section(
    section: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific configuration section. Requires authentication."""
    config = load_config()

    if section not in config:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")

    data = config[section]
    if current_user.role != "admin":
        data = mask_sensitive_fields(data)

    return data


@router.put("/{section}")
async def update_config_section(
    section: str,
    data: Union[Dict[str, Any], List[Any]] = Body(...),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update specific configuration section. Requires admin authentication.
    NOTE: For sensitive fields (API keys), empty string means 'keep existing value'.
          To actually clear a key, it must not be present or send null explicitly.
    """
    logger.info(f"Updating config section: {section}")

    config = load_config()

    # 폴더 설정인 경우 경로 검증
    if section == "folders":
        if not isinstance(data, dict):
            raise HTTPException(status_code=422, detail="Folders config must be a dictionary")
        if "scanFolders" not in data:
            raise HTTPException(status_code=422, detail="scanFolders field is required")
        if not isinstance(data["scanFolders"], list):
            raise HTTPException(status_code=422, detail="scanFolders must be a list")

        invalid_paths = []
        for folder_path in data["scanFolders"]:
            if not isinstance(folder_path, str):
                raise HTTPException(status_code=422, detail=f"Folder path must be a string: {folder_path}")
            if not Path(folder_path).exists():
                invalid_paths.append(folder_path)
                logger.warning(f"Folder path does not exist: {folder_path}")

        if invalid_paths:
            raise HTTPException(
                status_code=422,
                detail=f"Following paths do not exist: {', '.join(invalid_paths)}"
            )

    # Update section
    if isinstance(data, dict) and section in config and isinstance(config[section], dict):
        existing = config[section]
        for key, value in data.items():
            # For sensitive fields: empty string = keep existing (don't overwrite saved key)
            if key in SENSITIVE_FIELDS and isinstance(value, str) and not value.strip():
                existing_val = existing.get(key, '')
                if existing_val:
                    logger.debug(f"Preserving existing value for sensitive field: {key}")
                    continue  # Skip - keep existing value
            config[section][key] = value
    else:
        config[section] = data

    try:
        save_config(config)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")

    logger.info(f"Config section '{section}' updated successfully")
    return {"message": f"Section '{section}' updated successfully", "data": data}


@router.post("/reset")
async def reset_config(current_user: User = Depends(get_current_admin_user)):
    """Reset configuration to defaults. Requires admin authentication."""
    default_config = get_default_config()
    save_config(default_config)
    return {"message": "Configuration reset to defaults", "data": default_config}
