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
        self.scan_exclusions = self._load_scan_exclusions()

    def _load_scan_exclusions(self) -> List[str]:
        """파일에서 스캔 예외 목록 로드"""
        try:
            exclusions_file = Path(settings.SCAN_EXCLUSIONS_FILE)

            # 파일이 없으면 기본 예외 목록으로 생성
            if not exclusions_file.exists():
                default_exclusions = [
                    '.git',
                    'node_modules',
                    '__MACOSX',
                    '$RECYCLE.BIN',
                    '.Trash',
                    'System Volume Information',
                    '.DS_Store',
                    'Thumbs.db',
                    'desktop.ini',
                    '._.DS_Store',
                    'Icon\r',
                    '@eaDir'
                ]
                exclusions_file.parent.mkdir(parents=True, exist_ok=True)
                with open(exclusions_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(default_exclusions))
                return default_exclusions

            # 파일에서 읽기 (줄 단위로 읽고 빈 줄과 주석 제외)
            with open(exclusions_file, 'r', encoding='utf-8') as f:
                exclusions = [
                    line.strip()
                    for line in f.readlines()
                    if line.strip() and not line.strip().startswith('#')
                ]
                return exclusions
        except Exception as e:
            logger.error(f"Failed to load scan exclusions: {e}")
            return []

    def _is_excluded(self, folder_name: str) -> bool:
        """폴더가 스캔 예외 목록에 있는지 확인"""
        return folder_name.lower() in [ex.lower() for ex in self.scan_exclusions]

    def _is_excluded_file(self, file_name: str) -> bool:
        """파일이 스캔 예외 목록에 있는지 확인"""
        return file_name.lower() in [ex.lower() for ex in self.scan_exclusions]

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
            "ai_generated": 0,
            "icons_cached": 0,
            "errors": []
        }

        # 재귀적으로 모든 하위 폴더 스캔
        await self._scan_folder_recursive_async(base_path, results)

        self.db.commit()
        return results

    async def _scan_folder_recursive_async(self, folder: Path, results: Dict):
        """
        재귀적으로 폴더를 스캔 (하위 폴더 포함)

        Args:
            folder: 스캔할 폴더
            results: 결과 딕셔너리
        """
        # 스캔 예외 목록에 있는 폴더는 건너뛰기
        if self._is_excluded(folder.name):
            logger.debug(f"Skipping excluded folder: {folder.name}")
            return

        try:
            # 현재 폴더의 파일들 처리
            await self._process_folder_async(folder, results)

            # 하위 폴더 재귀 스캔
            for subfolder in folder.iterdir():
                if subfolder.is_dir():
                    await self._scan_folder_recursive_async(subfolder, results)

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
            "errors": []
        }

        # 재귀적으로 모든 하위 폴더 스캔
        self._scan_folder_recursive(base_path, results)

        self.db.commit()
        return results

    def _scan_folder_recursive(self, folder: Path, results: Dict):
        """
        재귀적으로 폴더를 스캔 (하위 폴더 포함)

        Args:
            folder: 스캔할 폴더
            results: 결과 딕셔너리
        """
        # 스캔 예외 목록에 있는 폴더는 건너뛰기
        if self._is_excluded(folder.name):
            logger.debug(f"Skipping excluded folder: {folder.name}")
            return

        try:
            # 현재 폴더의 파일들 처리
            self._process_folder(folder, results)

            # 하위 폴더 재귀 스캔
            for subfolder in folder.iterdir():
                if subfolder.is_dir():
                    self._scan_folder_recursive(subfolder, results)

        except Exception as e:
            results["errors"].append(f"Error processing {folder.name}: {str(e)}")

    async def _process_folder_async(self, folder: Path, results: Dict):
        """
        Process a single folder - add all files to FilenameViolation as "scanned"
        (Product will be created later when user clicks AI matching)

        Args:
            folder: Path to the product folder
            results: Results dictionary to update
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

    def _process_folder(self, folder: Path, results: Dict):
        """
        Process a single folder - add all files to FilenameViolation as "scanned"
        (Product will be created later when user clicks AI matching)

        Args:
            folder: Path to the product folder
            results: Results dictionary to update
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
