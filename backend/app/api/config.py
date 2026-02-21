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

# 프로세스 내 Fernet 키 싱글톤 - 매 호출마다 다른 키가 생성되는 문제 방지
_fernet_instance: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    """Get or create a stable Fernet key.
    Uses a module-level singleton to ensure the SAME key is used throughout
    the process lifetime. Also persists the key to a file for cross-restart durability."""
    global _fernet_instance

    # 싱글톤: 이미 초기화된 키 재사용 (매 호출마다 다른 키 생성 방지)
    if _fernet_instance is not None:
        return _fernet_instance

    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # 파일에서 기존 키 로드
    if ENCRYPTION_KEY_FILE.exists():
        try:
            with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                key = f.read().strip()
            _fernet_instance = Fernet(key)
            logger.debug("Loaded encryption key from file")
            return _fernet_instance
        except Exception as e:
            logger.warning(f"Failed to load encryption key file, regenerating: {e}")

    # 새 키 생성
    key = Fernet.generate_key()
    try:
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        logger.info("Created new encryption key file")
    except Exception as e:
        logger.error(f"Failed to save encryption key file (key will reset on restart): {e}")

    _fernet_instance = Fernet(key)
    return _fernet_instance


def _get_fernet_legacy() -> Fernet:
    """Fallback: derive Fernet key from SECRET_KEY (for migrating old encrypted values)"""
    key_bytes = settings.SECRET_KEY.encode('utf-8')
    derived = hashlib.sha256(key_bytes).digest()
    fernet_key = base64.urlsafe_b64encode(derived)
    return Fernet(fernet_key)


def encrypt_value(value: str) -> str:
    """Store value as plaintext (no encryption - personal NAS use).
    Previously used Fernet encryption which caused key-mismatch issues on restart."""
    if not value:
        return value
    # If already plaintext (no ENC: prefix), return as-is
    if not value.startswith(ENCRYPTED_PREFIX):
        return value
    # If it's already an ENC: value (legacy), keep as-is until next save
    return value


def decrypt_value(value: str) -> str:
    """Return plaintext value. Handles legacy ENC:-prefixed encrypted values."""
    if not value:
        return value
    # Plaintext value - return as-is
    if not value.startswith(ENCRYPTED_PREFIX):
        return value
    # Legacy encrypted value - try to decrypt for migration
    encrypted_data = value[len(ENCRYPTED_PREFIX):]
    try:
        f = _get_fernet()
        plain = f.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
        logger.info("Decrypted legacy ENC: value - will be stored as plaintext on next save")
        return plain
    except Exception:
        pass
    try:
        f_legacy = _get_fernet_legacy()
        plain = f_legacy.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
        logger.info("Decrypted legacy SECRET_KEY value - will be stored as plaintext on next save")
        return plain
    except Exception:
        logger.warning("Failed to decrypt legacy ENC: value - please re-enter the API key in Settings")
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
            "openaiApiKey": "",
            "geminiApiKey": "",
            "googleApiKey": "",
            "googleSearchEngineId": "",
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


def _migrate_config(config: Dict[str, Any]) -> tuple:
    """Migrate legacy config fields. Returns (migrated_config, needs_save)."""
    needs_save = False
    # Migrate: metadata.apiKey → metadata.openaiApiKey (field rename)
    if 'metadata' in config and isinstance(config['metadata'], dict):
        meta = config['metadata']
        if 'apiKey' in meta and 'openaiApiKey' not in meta:
            meta['openaiApiKey'] = meta.pop('apiKey')
            logger.info("Migrated metadata.apiKey → metadata.openaiApiKey")
            needs_save = True
        elif 'apiKey' in meta and meta['apiKey']:
            # Both exist but old apiKey has value - copy if new is empty
            if not meta.get('openaiApiKey'):
                meta['openaiApiKey'] = meta.pop('apiKey')
                logger.info("Migrated non-empty metadata.apiKey → metadata.openaiApiKey")
            else:
                meta.pop('apiKey')
            needs_save = True
        elif 'apiKey' in meta:
            meta.pop('apiKey')
            needs_save = True
    return config, needs_save


def _has_encrypted_sensitive(data: Any) -> bool:
    """Check if data has any ENC:-prefixed sensitive fields that need migration to plaintext"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key in SENSITIVE_FIELDS and isinstance(value, str) and value.startswith(ENCRYPTED_PREFIX):
                return True
            if isinstance(value, (dict, list)) and _has_encrypted_sensitive(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if _has_encrypted_sensitive(item):
                return True
    return False


def load_config() -> Dict[str, Any]:
    """Load config from JSON file. Decrypts legacy ENC: values and migrates field names."""
    ensure_config_exists()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Decrypt any legacy ENC: values first
        if _has_encrypted_sensitive(config):
            logger.info("Decrypting legacy ENC: sensitive fields to plaintext")
            config = decrypt_sensitive_fields(config)
            needs_resave = True
        else:
            needs_resave = False

        # Migrate field names (e.g. apiKey → openaiApiKey)
        config, migrated = _migrate_config(config)
        needs_resave = needs_resave or migrated

        # Re-save as plaintext if any migrations happened
        if needs_resave:
            try:
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                logger.info("Config migrated and saved as plaintext")
            except Exception as e:
                logger.warning(f"Could not save migrated config: {e}")

        return config
    except Exception as e:
        logger.debug(f"Error loading config: {e}")
        return get_default_config()


def save_config(config: Dict[str, Any]):
    """Save config to JSON file as plaintext (no encryption)."""
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
