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
from app.models.attachment import Attachment
from app.models.favorite import Favorite
from app.core.metadata_enricher import MetadataEnricher
from app.core.icon_cache import IconCache
from app.core.parser import FilenameParser
from app.core.classifier import classify_file
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

    # 이미지 및 비소프트웨어 확장자 (항상 제외)
    EXCLUDED_EXTENSIONS = {
        # 이미지 파일
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
        '.svg', '.webp', '.ico', '.heic', '.heif', '.avif',
        # 레지스트리 파일
        '.reg',
    }

    def _is_excluded_file(self, file_name: str) -> bool:
        """파일이 스캔 예외 목록에 있는지 확인 (와일드카드 패턴 지원)"""
        import fnmatch

        file_name_lower = file_name.lower()

        # 이미지/레지스트리 등 비소프트웨어 확장자 제외
        ext = os.path.splitext(file_name_lower)[1]
        if ext in self.EXCLUDED_EXTENSIONS:
            logger.debug(f"File {file_name} excluded by extension: {ext}")
            return True

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

        return False

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
            "deleted_violations": 0,
            "renamed_files": 0,
            "ai_generated": 0,
            "icons_cached": 0,
            "scanned_folders": 0,
            "scanned_files": 0,
            "errors": []
        }

        # 스캔 경로 내의 기존 파일들 추적
        scanned_files = set()

        # 재귀적으로 모든 하위 폴더 스캔
        await self._scan_folder_recursive_async(base_path, results, scanned_files)

        # 파일명 변경 감지 및 업데이트 (삭제 전에 먼저 실행)
        try:
            self._detect_renamed_files(str(base_path.absolute()), scanned_files, results)
        except Exception as e:
            logger.error(f"Error detecting renamed files: {e}")
            results["errors"].append(f"Rename detection error: {str(e)}")
            try:
                self.db.rollback()
            except Exception:
                pass

        # 삭제된 파일 정리
        try:
            self._cleanup_deleted_files(str(base_path.absolute()), scanned_files, results)
        except Exception as e:
            logger.error(f"Error cleaning up deleted files: {e}")
            results["errors"].append(f"Cleanup error: {str(e)}")
            try:
                self.db.rollback()
            except Exception:
                pass

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing scan results: {e}")
            self.db.rollback()
            results["errors"].append(f"Commit error: {str(e)}")
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
            logger.info(f"Scanning folder: {folder}")
            results["scanned_folders"] += 1

            # 현재 폴더의 파일들 처리
            await self._process_folder_async(folder, results, scanned_files)

            # 하위 폴더 재귀 스캔
            for subfolder in folder.iterdir():
                if subfolder.is_dir():
                    await self._scan_folder_recursive_async(subfolder, results, scanned_files)

        except PermissionError as e:
            error_msg = f"Permission denied: {folder} - {str(e)}"
            logger.warning(error_msg)
            results["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Error processing {folder}: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

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
            "deleted_violations": 0,
            "renamed_files": 0,
            "scanned_folders": 0,
            "scanned_files": 0,
            "errors": []
        }

        # 스캔 경로 내의 기존 파일들 추적
        scanned_files = set()

        # 재귀적으로 모든 하위 폴더 스캔
        self._scan_folder_recursive(base_path, results, scanned_files)

        # 파일명 변경 감지 및 업데이트 (삭제 전에 먼저 실행)
        try:
            self._detect_renamed_files(str(base_path.absolute()), scanned_files, results)
        except Exception as e:
            logger.error(f"Error detecting renamed files: {e}")
            results["errors"].append(f"Rename detection error: {str(e)}")
            try:
                self.db.rollback()
            except Exception:
                pass

        # 삭제된 파일 정리
        try:
            self._cleanup_deleted_files(str(base_path.absolute()), scanned_files, results)
        except Exception as e:
            logger.error(f"Error cleaning up deleted files: {e}")
            results["errors"].append(f"Cleanup error: {str(e)}")
            try:
                self.db.rollback()
            except Exception:
                pass

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing scan results: {e}")
            self.db.rollback()
            results["errors"].append(f"Commit error: {str(e)}")
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
            logger.info(f"Scanning folder: {folder}")
            results["scanned_folders"] += 1

            # 현재 폴더의 파일들 처리
            self._process_folder(folder, results, scanned_files)

            # 하위 폴더 재귀 스캔
            for subfolder in folder.iterdir():
                if subfolder.is_dir():
                    self._scan_folder_recursive(subfolder, results, scanned_files)

        except PermissionError as e:
            error_msg = f"Permission denied: {folder} - {str(e)}"
            logger.warning(error_msg)
            results["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Error processing {folder}: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

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

        # 유효한 파일만 수집 (제외 대상 건너뛰기)
        valid_files = []
        for file_path in folder.iterdir():
            if file_path.is_file():
                if self._is_excluded_file(file_path.name):
                    logger.debug(f"Skipping excluded file: {file_path.name}")
                    continue
                valid_files.append(file_path)

        # 유효한 파일이 없으면 폴더 건너뛰기
        if not valid_files:
            logger.debug(f"Skipping empty folder (no valid files): {folder}")
            return

        for file_path in valid_files:
            logger.debug(f"Processing file: {file_path.name}")
            results["scanned_files"] += 1
            try:
                with self.db.begin_nested():
                    self._add_scanned_file(file_path, folder_path_str, results)
                scanned_files.add(str(file_path.absolute()))
            except Exception as e:
                logger.warning(f"Failed to scan file {file_path.name}: {e}")
                results["errors"].append(f"File error {file_path.name}: {str(e)}")

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

        # 유효한 파일만 수집 (제외 대상 건너뛰기)
        valid_files = []
        for file_path in folder.iterdir():
            if file_path.is_file():
                if self._is_excluded_file(file_path.name):
                    logger.debug(f"Skipping excluded file: {file_path.name}")
                    continue
                valid_files.append(file_path)

        # 유효한 파일이 없으면 폴더 건너뛰기
        if not valid_files:
            logger.debug(f"Skipping empty folder (no valid files): {folder}")
            return

        for file_path in valid_files:
            logger.debug(f"Processing file: {file_path.name}")
            results["scanned_files"] += 1
            try:
                with self.db.begin_nested():
                    self._add_scanned_file(file_path, folder_path_str, results)
                scanned_files.add(str(file_path.absolute()))
            except Exception as e:
                logger.warning(f"Failed to scan file {file_path.name}: {e}")
                results["errors"].append(f"File error {file_path.name}: {str(e)}")


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
            # 기존 violation이 resolved 상태이지만 연결된 product/version이 없으면 리셋
            # (product 삭제 시 CASCADE SET NULL로 product_id가 NULL이 되었지만 is_resolved가 True로 남은 경우)
            if existing_violation.is_resolved and existing_violation.product_id is None and existing_violation.version_id is None:
                existing_violation.is_resolved = False
                existing_violation.violation_details = "스캔된 파일 (AI 매칭 대기중)"
            return  # Skip creating a new violation record

        # Check if Version already exists (이미 매칭된 파일)
        existing_version = self.db.query(Version).filter(
            Version.file_path == file_path_str
        ).first()

        # 파일명 + 폴더명으로 자동 분류
        folder_name = Path(folder_path_str).name
        classification = classify_file(file_name, folder_name)

        # 파일명 규칙 검사 없이 모두 "scanned" 타입으로 추가 (스캔 예외 규칙만 적용됨)
        violation = FilenameViolation(
            folder_path=folder_path_str,
            file_name=file_name,
            violation_type="scanned",
            violation_details="스캔된 파일 (AI 매칭 대기중)",
            suggestion=file_name,
            is_resolved=False,
            classification=classification,
            classification_auto=True,
        )

        # If Version exists, link it automatically and mark as resolved
        if existing_version:
            violation.product_id = existing_version.product_id
            violation.version_id = existing_version.id
            violation.is_resolved = True
            violation.violation_details = "이미 스토어에 등록된 파일"

        self.db.add(violation)
        results["new_products"] += 1  # Count scanned files as new products

    def _detect_renamed_files(self, base_path: str, scanned_files: set, results: Dict):
        """
        파일명이 변경된 파일을 감지하고 업데이트

        같은 폴더 내에서 파일 크기와 수정 시간이 동일한 파일을 찾아서
        Version과 FilenameViolation 레코드를 업데이트

        Args:
            base_path: 스캔 경로
            scanned_files: 스캔된 파일 경로 Set (딕셔너리로 변경 필요)
            results: 결과 딕셔너리
        """
        try:
            # 스캔된 파일들의 메타데이터 수집 (경로, 크기, 수정 시간)
            scanned_file_info = {}
            for file_path in scanned_files:
                if os.path.isfile(file_path):
                    try:
                        stat = os.stat(file_path)
                        folder = str(Path(file_path).parent)
                        scanned_file_info[file_path] = {
                            'folder': folder,
                            'size': stat.st_size,
                            'mtime': int(stat.st_mtime),
                            'name': Path(file_path).name
                        }
                    except Exception as e:
                        logger.warning(f"Could not get file info for {file_path}: {e}")

            # DB에 있는 모든 Version 조회
            versions = self.db.query(Version).join(Product).filter(
                Product.folder_path.like(f"{base_path}%")
            ).all()

            renamed_count = 0

            for version in versions:
                if version.file_path not in scanned_files:
                    # 파일이 스캔 결과에 없음 - 삭제되었거나 이름이 변경됨
                    old_path = version.file_path

                    # 같은 폴더 내에서 크기가 같은 파일 찾기
                    old_folder = str(Path(old_path).parent)

                    if os.path.isfile(old_path):
                        # 파일이 여전히 존재 - 스캔 대상이 아님
                        continue

                    try:
                        # 기존 파일 정보가 있다면 사용
                        if version.file_size:
                            old_size = version.file_size
                        else:
                            continue

                        # 같은 폴더 내에서 같은 크기의 새 파일 찾기
                        matched_new_file = None
                        for new_path, info in scanned_file_info.items():
                            if (info['folder'] == old_folder and
                                info['size'] == old_size):
                                # DB에 이미 있는지 확인
                                existing = self.db.query(Version).filter(
                                    Version.file_path == new_path
                                ).first()

                                if not existing:
                                    matched_new_file = new_path
                                    break

                        if matched_new_file:
                            # 파일명 변경 감지됨 - Version 업데이트
                            old_filename = version.file_name
                            new_filename = Path(matched_new_file).name

                            logger.info(f"Renamed file detected: {old_filename} → {new_filename}")

                            version.file_name = new_filename
                            version.file_path = matched_new_file

                            # FilenameViolation도 업데이트
                            violations = self.db.query(FilenameViolation).filter(
                                FilenameViolation.folder_path == old_folder,
                                FilenameViolation.file_name == old_filename
                            ).all()

                            for violation in violations:
                                violation.file_name = new_filename
                                violation.suggestion = new_filename

                            renamed_count += 1

                            # scanned_files에서 제거하여 중복 처리 방지
                            scanned_files.discard(matched_new_file)

                    except Exception as e:
                        logger.warning(f"Error detecting rename for {old_path}: {e}")

            if renamed_count > 0:
                results["renamed_files"] = renamed_count
                logger.info(f"Updated {renamed_count} renamed files")

        except Exception as e:
            logger.error(f"Error detecting renamed files: {e}")
            results["errors"].append(f"Rename detection error: {str(e)}")

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
            # scanned_files 체크와 실제 파일 존재 여부 모두 확인
            for version in versions:
                # 1. scanned_files에 없거나
                # 2. 실제로 파일이 존재하지 않으면 삭제
                file_exists = os.path.exists(version.file_path)

                if version.file_path not in scanned_files or not file_exists:
                    logger.info(f"Deleted file detected: {version.file_path} (exists: {file_exists})")
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
                # FilenameViolation 리셋 (재스캔 가능하도록)
                self.db.query(FilenameViolation).filter(
                    FilenameViolation.product_id.in_(deleted_product_ids)
                ).update({
                    "is_resolved": False,
                    "product_id": None,
                    "version_id": None,
                    "violation_details": "스캔된 파일 (AI 매칭 대기중)"
                }, synchronize_session=False)
                # 외래키 제약 조건이 있는 관련 레코드 먼저 삭제
                self.db.query(Attachment).filter(Attachment.product_id.in_(deleted_product_ids)).delete(synchronize_session=False)
                self.db.query(Favorite).filter(Favorite.product_id.in_(deleted_product_ids)).delete(synchronize_session=False)
                # Product 삭제 (ProductVideo, ShareLink는 ondelete=CASCADE로 자동 처리)
                self.db.query(Product).filter(Product.id.in_(deleted_product_ids)).delete(synchronize_session=False)
                results["deleted_products"] = len(deleted_product_ids)
                logger.info(f"Deleted {len(deleted_product_ids)} products with no versions")

            # product_id가 NULL인 FilenameViolation 중 실제 파일이 없는 것 삭제
            # (AI 매칭 전 상태인 "scanned" 항목으로, 파일이 삭제된 경우)
            unmatched_violations = self.db.query(FilenameViolation).filter(
                FilenameViolation.product_id.is_(None),
                FilenameViolation.folder_path.like(f"{base_path}%")
            ).all()

            deleted_violation_ids = []
            for violation in unmatched_violations:
                full_path = os.path.join(violation.folder_path, violation.file_name)
                if not os.path.exists(full_path):
                    deleted_violation_ids.append(violation.id)
                    logger.info(f"Deleted unmatched violation (file gone): {full_path}")

            if deleted_violation_ids:
                self.db.query(FilenameViolation).filter(
                    FilenameViolation.id.in_(deleted_violation_ids)
                ).delete(synchronize_session=False)
                results["deleted_violations"] = len(deleted_violation_ids)
                logger.info(f"Deleted {len(deleted_violation_ids)} unmatched violations")

        except Exception as e:
            logger.error(f"Error cleaning up deleted files: {e}")
            results["errors"].append(f"Cleanup error: {str(e)}")
