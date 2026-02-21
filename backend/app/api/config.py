"""
Config API for managing application settings
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Union
import json
import os
import base64
import hashlib
from pathlib import Path
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


from app.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.config import settings

# --- API Key Encryption ---
# Sensitive field names that should be encrypted in config.json
SENSITIVE_FIELDS = {"apiKey", "geminiApiKey", "openaiApiKey", "googleApiKey", "smtpPassword"}
ENCRYPTED_PREFIX = "ENC:"


def _get_fernet() -> Fernet:
    """Get or create a stable Fernet key stored in the data directory.
    This ensures API keys survive Docker rebuilds regardless of SECRET_KEY changes."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if ENCRYPTION_KEY_FILE.exists():
        try:
            with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                key = f.read().strip()
            return Fernet(key)
        except Exception as e:
            logger.warning(f"Failed to load encryption key file, regenerating: {e}")

    # Generate a new stable key and save it
    key = Fernet.generate_key()
    try:
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        logger.info("Created new encryption key file")
    except Exception as e:
        logger.error(f"Failed to save encryption key file: {e}")
    return Fernet(key)


def _get_fernet_legacy() -> Fernet:
    """Fallback: derive Fernet key from SECRET_KEY (for migrating old encrypted values)"""
    key_bytes = settings.SECRET_KEY.encode('utf-8')
    derived = hashlib.sha256(key_bytes).digest()
    fernet_key = base64.urlsafe_b64encode(derived)
    return Fernet(fernet_key)


def encrypt_value(value: str) -> str:
    """Encrypt a string value. Returns prefixed encrypted string."""
    if not value or value.startswith(ENCRYPTED_PREFIX):
        return value
    try:
        f = _get_fernet()
        encrypted = f.encrypt(value.encode('utf-8')).decode('utf-8')
        return f"{ENCRYPTED_PREFIX}{encrypted}"
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return value


def decrypt_value(value: str) -> str:
    """Decrypt an encrypted string value. Returns plain text."""
    if not value or not value.startswith(ENCRYPTED_PREFIX):
        return value
    encrypted_data = value[len(ENCRYPTED_PREFIX):]
    # Try file-based key first
    try:
        f = _get_fernet()
        return f.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        pass
    except Exception as e:
        logger.error(f"Decryption failed with file key: {e}")

    # Fallback: try SECRET_KEY-based key (migration from older versions)
    try:
        f_legacy = _get_fernet_legacy()
        plain = f_legacy.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
        logger.info("Decrypted with legacy SECRET_KEY - will re-encrypt with file key on next save")
        return plain
    except InvalidToken:
        logger.warning("Failed to decrypt value - key mismatch (re-enter API key)")
        return ""
    except Exception as e:
        logger.error(f"Decryption failed with legacy key: {e}")
        return ""


def encrypt_sensitive_fields(data: Any) -> Any:
    """Recursively encrypt sensitive fields in config data"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in SENSITIVE_FIELDS and isinstance(value, str):
                result[key] = encrypt_value(value)
            elif isinstance(value, (dict, list)):
                result[key] = encrypt_sensitive_fields(value)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [encrypt_sensitive_fields(item) for item in data]
    return data


def decrypt_sensitive_fields(data: Any) -> Any:
    """Recursively decrypt sensitive fields in config data"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in SENSITIVE_FIELDS and isinstance(value, str):
                result[key] = decrypt_value(value)
            elif isinstance(value, (dict, list)):
                result[key] = decrypt_sensitive_fields(value)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [decrypt_sensitive_fields(item) for item in data]
    return data


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

router = APIRouter()

# Config file path - 환경변수에서 가져오기
CONFIG_DIR = Path(settings.CONFIG_DATA_DIR)
CONFIG_FILE = CONFIG_DIR / "config.json"
ENCRYPTION_KEY_FILE = CONFIG_DIR / ".encryption_key"

def get_default_config() -> Dict[str, Any]:
    """
    Generate default config with environment-aware values.

    NOTE: This is only used when config.json doesn't exist (first run).
    config.json is the single source of truth for all settings.
    Changes should be made in config.json, not here.
    """
    # 환경별 기본 URL 설정
    environment = settings.ENVIRONMENT
    if environment == "production":
        # 프로덕션 환경: localhost 사용 (리버스 프록시로 접근)
        default_frontend_url = "http://localhost:5900"
        default_backend_url = "http://localhost:8110"
    else:
        # 개발 환경: localhost 사용
        default_frontend_url = "http://localhost:5900"
        default_backend_url = "http://localhost:8110"

    # 스캔 기본 폴더 경로 설정
    # 도커 환경에서는 /app/data/library를 기본으로 사용
    default_scan_folder = settings.SCAN_BASE_PATH
    if not default_scan_folder.startswith('/'):
        default_scan_folder = f"/{default_scan_folder}"

    # /library는 /app/data/library로 매핑
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


def _has_unencrypted_sensitive(data: Any) -> bool:
    """Check if data has any unencrypted sensitive fields that need migration"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key in SENSITIVE_FIELDS and isinstance(value, str) and value and not value.startswith(ENCRYPTED_PREFIX):
                return True
            if isinstance(value, (dict, list)) and _has_unencrypted_sensitive(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if _has_unencrypted_sensitive(item):
                return True
    return False


def load_config() -> Dict[str, Any]:
    """Load config from JSON file with decryption of sensitive fields"""
    ensure_config_exists()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Auto-migrate: encrypt any plaintext sensitive fields
        if _has_unencrypted_sensitive(config):
            logger.info("Migrating plaintext sensitive fields to encrypted format")
            encrypted_config = encrypt_sensitive_fields(config)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(encrypted_config, f, ensure_ascii=False, indent=2)

        return decrypt_sensitive_fields(config)
    except Exception as e:
        logger.debug(f"Error loading config: {e}")
        return get_default_config()


def save_config(config: Dict[str, Any]):
    """Save config to JSON file with encryption of sensitive fields"""
    ensure_config_exists()

    try:
        encrypted_config = encrypt_sensitive_fields(config)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(encrypted_config, f, ensure_ascii=False, indent=2)
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

    # Hide sensitive fields from non-admin users
    if current_user.role != "admin":
        config = mask_sensitive_fields(config)

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

    # Hide sensitive fields from non-admin users
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
    Update specific configuration section
    Requires admin authentication
    Data can be dict (most sections) or list (categories)
    """
    logger.info(f"Updating config section: {section}")
    logger.debug(f"Received data type: {type(data)}")

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

    # Update the section - deep merge for dict, full replace for list
    if isinstance(data, dict) and section in config and isinstance(config[section], dict):
        # Deep merge: preserve existing fields not in the update
        config[section].update(data)
    else:
        config[section] = data

    # Save to file
    try:
        save_config(config)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")

    logger.info(f"Config section '{section}' updated successfully")
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
