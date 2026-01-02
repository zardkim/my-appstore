from app.config import settings
from app.main import app
import os
from pathlib import Path # Added import

print("--- Backend Configuration Check ---")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"SECRET_KEY: {settings.SECRET_KEY}")
print(f"SCAN_BASE_PATH: {settings.SCAN_BASE_PATH}")
print(f"ICON_CACHE_DIR: {settings.ICON_CACHE_DIR}")

# To check CORS origins, we need to access the middleware stack.
# This is a bit more complex to do directly from settings,
# but we can infer it if the app starts with the correct config.
# For now, let's just confirm the path settings.

# Verify if the ICON_CACHE_DIR exists and is writable
try:
    test_dir = Path(settings.ICON_CACHE_DIR)
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"ICON_CACHE_DIR '{settings.ICON_CACHE_DIR}' is accessible and writable.")
    test_file = test_dir / "test_write.tmp"
    test_file.touch()
    test_file.unlink()
    print(f"Successfully wrote and deleted test file in '{settings.ICON_CACHE_DIR}'.")
except Exception as e:
    print(f"Error accessing/writing to ICON_CACHE_DIR '{settings.ICON_CACHE_DIR}': {e}")

print("--- End Configuration Check ---")
