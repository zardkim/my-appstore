import os
import re
from pathlib import Path
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
import logging
logger = logging.getLogger(__name__)


from app.models.product import Product
from app.models.version import Version
from app.models.filename_violation import FilenameViolation
from app.core.metadata_enricher import MetadataEnricher
from app.core.icon_cache import IconCache
from app.core.parser import FilenameParser
from app.core.filename_validator import FilenameValidator
from app.config import settings
import logging
logger = logging.getLogger(__name__)



class FileScanner:
    """
    File system scanner for detecting software and versions
    Supports AI-powered metadata generation
    """

    def __init__(self, db: Session, use_ai: bool = True, ai_provider: str = "openai"):
        """
        Initialize scanner

        Args:
            db: Database session
            use_ai: Enable AI metadata generation (requires API key)
            ai_provider: AI provider ('openai' or 'gemini')
        """
        self.db = db
        self.use_ai = use_ai
        self.enricher = MetadataEnricher(ai_provider=ai_provider, use_ai=use_ai) if use_ai else None
        self.icon_cache = IconCache()
        self.parser = FilenameParser()
        exclusions_data = self._load_scan_exclusions()
        self.scan_exclusions = exclusions_data.get("folders", [])
        self.scan_patterns = exclusions_data.get("patterns", [])
        self.scan_paths = exclusions_data.get("paths", [])

    def _load_scan_exclusions(self) -> dict:
        """파일에서 스캔 예외 목록 로드"""
        import json

        try:
            exclusions_file = Path(settings.SCAN_EXCLUSIONS_FILE)

            # 파일이 없으면 기본 예외 목록으로 생성
            if not exclusions_file.exists():
                default_data = {
                    "folders": ['.DAV', '.git', '.node_modules', '_MACOSX', '#recycle', '@eaDir'],
                    "patterns": ['*.txt', '*.log', 'thumbs.db', 'desktop.ini', '*.nfo', '*.sfv', '*.sha1', '*.md5', '*.md4'],
                    "paths": []
                }
                exclusions_file.parent.mkdir(parents=True, exist_ok=True)
                with open(exclusions_file, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
                return default_data

            # JSON 파일에서 읽기
            with open(exclusions_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {
                        "folders": ['.DAV', '.git', '.node_modules', '_MACOSX', '#recycle', '@eaDir'],
                        "patterns": ['*.txt', '*.log', 'thumbs.db', 'desktop.ini', '*.nfo', '*.sfv', '*.sha1', '*.md5', '*.md4'],
                        "paths": []
                    }

                try:
                    data = json.loads(content)
                    return {
                        "folders": data.get("folders", []),
                        "patterns": data.get("patterns", []),
                        "paths": data.get("paths", [])
                    }
                except json.JSONDecodeError:
                    # 구 형식(줄바꿈)인 경우 폴더 목록으로 간주
                    exclusions = [
                        line.strip()
                        for line in content.split('\n')
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    return {
                        "folders": exclusions,
                        "patterns": ['*.txt', '*.log', 'thumbs.db', 'desktop.ini', '*.nfo', '*.sfv', '*.sha1', '*.md5', '*.md4'],
                        "paths": []
                    }
        except Exception as e:
            logger.error(f"Failed to load scan exclusions: {e}")
            return {"folders": [], "patterns": [], "paths": []}

    def _is_excluded(self, folder_name: str) -> bool:
        """폴더가 스캔 예외 목록에 있는지 확인"""
        return folder_name.lower() in [ex.lower() for ex in self.scan_exclusions]

    def _is_excluded_file(self, file_name: str) -> bool:
        """파일이 스캔 예외 목록에 있는지 확인 (와일드카드 패턴 지원)"""
        import fnmatch

        file_name_lower = file_name.lower()

        # 정확한 파일명 매칭 (폴더 예외 목록에서)
        if file_name_lower in [ex.lower() for ex in self.scan_exclusions]:
            logger.info(f"File {file_name} excluded by exact match in folders list")
            return True

        # 와일드카드 패턴 매칭
        for pattern in self.scan_patterns:
            pattern_lower = pattern.lower()
            if fnmatch.fnmatch(file_name_lower, pattern_lower):
                logger.info(f"File {file_name} excluded by pattern match: {pattern}")
                return True

        # 디버그: 매칭 실패 시 로그
        if file_name_lower in ['.gitkeep', 'readme.md'] or file_name_lower.endswith('.md'):
            logger.warning(f"File {file_name} NOT excluded. Patterns: {self.scan_patterns}, Folders: {self.scan_exclusions}")

        return False

    def _validate_filename(self, filename: str, folder_path: str):
        """
        파일명이 표준 규칙을 따르는지 검증하고, 위반사항을 DB에 저장

        Args:
            filename: 검증할 파일명
            folder_path: 파일이 속한 폴더 경로
        """
        validator = FilenameValidator()
        result = validator.validate_filename(filename)

        if not result["is_valid"]:
            # 기존 위반사항 삭제 (같은 파일에 대해 중복 저장 방지)
            self.db.query(FilenameViolation).filter(
                FilenameViolation.folder_path == folder_path,
                FilenameViolation.file_name == filename
            ).delete()

            # 새로운 위반사항 저장
            for violation in result["violations"]:
                db_violation = FilenameViolation(
                    folder_path=folder_path,
                    file_name=filename,
                    violation_type=violation["type"],
                    violation_details=violation["details"],
                    suggestion=violation.get("suggestion", ""),
                    is_resolved=False
                )
                self.db.add(db_violation)

            self.db.flush()

    async def scan_directory_async(self, base_path: str) -> Dict:
        """
        Scan a directory for software files recursively (async version with AI)

        Args:
            base_path: Root path to scan

        Returns:
            Dictionary with scan results
        """
        base_path = Path(base_path)

        if not base_path.exists():
            raise ValueError(f"Path does not exist: {base_path}")

        results = {
            "new_products": 0,
            "new_versions": 0,
            "updated_products": 0,
            "deleted_versions": 0,
            "deleted_products": 0,
            "ai_generated": 0,
            "icons_cached": 0,
            "errors": []
        }

        # 스캔 경로 내의 기존 파일들 추적
        scanned_files = set()

        # 재귀적으로 모든 하위 폴더 스캔
        await self._scan_folder_recursive_async(base_path, results, scanned_files)

        # 삭제된 파일 정리
        self._cleanup_deleted_files(str(base_path.absolute()), scanned_files, results)

        self.db.commit()
        return results

    async def _scan_folder_recursive_async(self, folder: Path, results: Dict, scanned_files: set):
        """
        재귀적으로 폴더를 스캔 (하위 폴더 포함)

        Args:
            folder: 스캔할 폴더
            results: 결과 딕셔너리
            scanned_files: 스캔된 파일 경로 추적용 Set
        """
        # 스캔 예외 목록에 있는 폴더는 건너뛰기
        if self._is_excluded(folder.name):
            logger.debug(f"Skipping excluded folder: {folder.name}")
            return

        try:
            # 현재 폴더의 파일들 처리
            await self._process_folder_async(folder, results, scanned_files)

            # 하위 폴더 재귀 스캔
            for subfolder in folder.iterdir():
                if subfolder.is_dir():
                    await self._scan_folder_recursive_async(subfolder, results, scanned_files)

        except Exception as e:
            results["errors"].append(f"Error processing {folder.name}: {str(e)}")

    def scan_directory(self, base_path: str) -> Dict:
        """
        Scan a directory for software files recursively (sync version without AI)

        Args:
            base_path: Root path to scan

        Returns:
            Dictionary with scan results
        """
        base_path = Path(base_path)

        if not base_path.exists():
            raise ValueError(f"Path does not exist: {base_path}")

        results = {
            "new_products": 0,
            "new_versions": 0,
            "updated_products": 0,
            "deleted_versions": 0,
            "deleted_products": 0,
            "errors": []
        }

        # 스캔 경로 내의 기존 파일들 추적
        scanned_files = set()

        # 재귀적으로 모든 하위 폴더 스캔
        self._scan_folder_recursive(base_path, results, scanned_files)

        # 삭제된 파일 정리
        self._cleanup_deleted_files(str(base_path.absolute()), scanned_files, results)

        self.db.commit()
        return results

    def _scan_folder_recursive(self, folder: Path, results: Dict, scanned_files: set):
        """
        재귀적으로 폴더를 스캔 (하위 폴더 포함)

        Args:
            folder: 스캔할 폴더
            results: 결과 딕셔너리
            scanned_files: 스캔된 파일 경로 추적용 Set
        """
        # 스캔 예외 목록에 있는 폴더는 건너뛰기
        if self._is_excluded(folder.name):
            logger.debug(f"Skipping excluded folder: {folder.name}")
            return

        try:
            # 현재 폴더의 파일들 처리
            self._process_folder(folder, results, scanned_files)

            # 하위 폴더 재귀 스캔
            for subfolder in folder.iterdir():
                if subfolder.is_dir():
                    self._scan_folder_recursive(subfolder, results, scanned_files)

        except Exception as e:
            results["errors"].append(f"Error processing {folder.name}: {str(e)}")

    async def _process_folder_async(self, folder: Path, results: Dict, scanned_files: set):
        """
        Process a single folder - add all files to FilenameViolation as "scanned"
        (Product will be created later when user clicks AI matching)

        Args:
            folder: Path to the product folder
            results: Results dictionary to update
            scanned_files: Set to track scanned file paths
        """
        folder_path_str = str(folder.absolute())

        # Scan files in the folder and add them to FilenameViolation
        for file_path in folder.iterdir():
            if file_path.is_file():
                # 예외 파일 건너뛰기 (desktop.ini, .DS_Store 등)
                if self._is_excluded_file(file_path.name):
                    logger.debug(f"Skipping excluded file: {file_path.name}")
                    continue
                self._add_scanned_file(file_path, folder_path_str, results)
                # 스캔된 파일 추적
                scanned_files.add(str(file_path.absolute()))

    def _process_folder(self, folder: Path, results: Dict, scanned_files: set):
        """
        Process a single folder - add all files to FilenameViolation as "scanned"
        (Product will be created later when user clicks AI matching)

        Args:
            folder: Path to the product folder
            results: Results dictionary to update
            scanned_files: Set to track scanned file paths
        """
        folder_path_str = str(folder.absolute())

        # Scan files in the folder and add them to FilenameViolation
        for file_path in folder.iterdir():
            if file_path.is_file():
                # 예외 파일 건너뛰기 (desktop.ini, .DS_Store 등)
                if self._is_excluded_file(file_path.name):
                    logger.debug(f"Skipping excluded file: {file_path.name}")
                    continue
                self._add_scanned_file(file_path, folder_path_str, results)
                # 스캔된 파일 추적
                scanned_files.add(str(file_path.absolute()))

    def _process_file(self, file_path: Path, product: Product, results: Dict):
        """
        Process a single file (represents a version)

        Args:
            file_path: Path to the file
            product: Product this file belongs to
            results: Results dictionary to update
        """
        file_path_str = str(file_path.absolute())

        # 파일명 규칙 검증
        self._validate_filename(file_path.name, str(file_path.parent.absolute()))

        # Check if version already exists
        existing = self.db.query(Version).filter(
            Version.file_path == file_path_str
        ).first()

        if existing:
            return  # Skip already registered files

        # Extract version from filename using parser
        parsed = self.parser.parse(file_path.name, file_path.parent.name)
        version_name = parsed.get('version') or 'Unknown'
        is_portable = parsed.get('is_portable', False)

        # Create new version entry
        version = Version(
            product_id=product.id,
            file_name=file_path.name,
            file_path=file_path_str,
            file_size=file_path.stat().st_size,
            version_name=version_name,
            is_portable=is_portable
        )
        self.db.add(version)
        results["new_versions"] += 1

    def _add_scanned_file(self, file_path: Path, folder_path_str: str, results: Dict):
        """
        Add scanned file to FilenameViolation table as "scanned" type
        (Will be converted to Product later when user clicks AI matching)

        Args:
            file_path: Path to the file
            folder_path_str: Parent folder path
            results: Results dictionary to update
        """
        file_name = file_path.name
        file_path_str = str(file_path.absolute())

        # Check if already exists in FilenameViolation
        existing_violation = self.db.query(FilenameViolation).filter(
            FilenameViolation.folder_path == folder_path_str,
            FilenameViolation.file_name == file_name
        ).first()

        if existing_violation:
            return  # Skip already scanned files

        # Check if Version already exists (이미 매칭된 파일)
        existing_version = self.db.query(Version).filter(
            Version.file_path == file_path_str
        ).first()

        # Validate filename and determine violation type
        validator = FilenameValidator()
        validation_result = validator.validate_filename(file_name)

        if validation_result["is_valid"]:
            # Valid filename - add as "scanned" type
            violation_type = "scanned"
            violation_details = "스캔된 파일 (AI 매칭 대기중)"
            suggestion = file_name  # No change needed
        else:
            # Invalid filename - use actual violation type
            violation_type = validation_result["violations"][0]["type"]
            violation_details = validation_result["violations"][0]["details"]
            suggestion = validation_result["violations"][0].get("suggestion", "")

        # Create FilenameViolation
        violation = FilenameViolation(
            folder_path=folder_path_str,
            file_name=file_name,
            violation_type=violation_type,
            violation_details=violation_details,
            suggestion=suggestion if suggestion else file_name,
            is_resolved=False
        )

        # If Version exists, link it automatically and mark as resolved
        if existing_version:
            violation.product_id = existing_version.product_id
            violation.version_id = existing_version.id
            violation.is_resolved = True
            violation.violation_details = "이미 스토어에 등록된 파일"

        self.db.add(violation)
        results["new_products"] += 1  # Count scanned files as new products

    def _cleanup_deleted_files(self, base_path: str, scanned_files: set, results: Dict):
        """
        스캔 경로 내에서 삭제된 파일의 Version과 Product를 DB에서 제거

        Args:
            base_path: 스캔 경로
            scanned_files: 스캔된 파일 경로 Set
            results: 결과 딕셔너리
        """
        try:
            # 스캔 경로 내의 모든 Version 조회
            versions = self.db.query(Version).join(Product).filter(
                Product.folder_path.like(f"{base_path}%")
            ).all()

            deleted_version_ids = []
            product_ids_to_check = set()

            # 파일이 존재하지 않는 Version 찾기
            for version in versions:
                if version.file_path not in scanned_files:
                    logger.info(f"Deleted file detected: {version.file_path}")
                    deleted_version_ids.append(version.id)
                    product_ids_to_check.add(version.product_id)

            # Version 삭제
            if deleted_version_ids:
                self.db.query(Version).filter(Version.id.in_(deleted_version_ids)).delete(synchronize_session=False)
                results["deleted_versions"] = len(deleted_version_ids)
                logger.info(f"Deleted {len(deleted_version_ids)} versions")

            # Version이 없는 Product 삭제
            deleted_product_ids = []
            for product_id in product_ids_to_check:
                version_count = self.db.query(Version).filter(Version.product_id == product_id).count()
                if version_count == 0:
                    deleted_product_ids.append(product_id)

            if deleted_product_ids:
                self.db.query(Product).filter(Product.id.in_(deleted_product_ids)).delete(synchronize_session=False)
                results["deleted_products"] = len(deleted_product_ids)
                logger.info(f"Deleted {len(deleted_product_ids)} products with no versions")

        except Exception as e:
            logger.error(f"Error cleaning up deleted files: {e}")
            results["errors"].append(f"Cleanup error: {str(e)}")
