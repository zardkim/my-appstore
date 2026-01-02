import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import SessionLocal
from app.core.scanner import FileScanner
from app.models.setting import Setting

logger = logging.getLogger(__name__)


class ScanScheduler:
    """
    자동 스캔 스케줄러
    APScheduler를 사용하여 주기적으로 파일 스캔 실행
    """

    def __init__(self):
        jobstores = {
            'default': MemoryJobStore()
        }
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        self.scan_paths: List[str] = []
        self.cron_schedule: str = "0 2 * * *"  # 기본: 매일 새벽 2시
        self.use_ai: bool = True
        self.is_running: bool = False
        self.last_scan_time: Optional[datetime] = None
        self.last_scan_result: Optional[dict] = None

    def start(self, cron_expression: Optional[str] = None, scan_paths: Optional[List[str]] = None, use_ai: bool = True):
        """
        스케줄러 시작

        Args:
            cron_expression: Cron 표현식 (예: "0 2 * * *" = 매일 새벽 2시)
            scan_paths: 스캔할 경로 목록
            use_ai: AI 메타데이터 생성 활성화
        """
        if cron_expression:
            self.cron_schedule = cron_expression

        if scan_paths:
            self.scan_paths = scan_paths

        self.use_ai = use_ai

        # 기존 작업 제거
        if self.scheduler.get_job('auto_scan'):
            self.scheduler.remove_job('auto_scan')

        # 새 작업 추가
        self.scheduler.add_job(
            self._run_scheduled_scan,
            CronTrigger.from_crontab(self.cron_schedule),
            id='auto_scan',
            name='Automatic File Scan',
            replace_existing=True
        )

        if not self.scheduler.running:
            self.scheduler.start()
            self.is_running = True

        logger.info(f"✓ Scheduler started with cron: {self.cron_schedule}")
        logger.info(f"✓ Scan paths: {self.scan_paths}")
        logger.info(f"✓ AI enabled: {self.use_ai}")

    def stop(self):
        """스케줄러 중지"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("✓ Scheduler stopped")

    async def _run_scheduled_scan(self):
        """
        스케줄된 스캔 실행
        """
        logger.info(f"Starting scheduled scan at {datetime.now()}")

        db = SessionLocal()
        all_results = {
            "new_products": 0,
            "new_versions": 0,
            "updated_products": 0,
            "ai_generated": 0,
            "icons_cached": 0,
            "errors": [],
            "scanned_paths": []
        }

        try:
            # 모든 경로 스캔
            for path in self.scan_paths:
                try:
                    scanner = FileScanner(db, use_ai=self.use_ai)

                    if self.use_ai:
                        results = await scanner.scan_directory_async(path)
                    else:
                        results = scanner.scan_directory(path)

                    # 결과 집계
                    all_results["new_products"] += results.get("new_products", 0)
                    all_results["new_versions"] += results.get("new_versions", 0)
                    all_results["updated_products"] += results.get("updated_products", 0)
                    all_results["ai_generated"] += results.get("ai_generated", 0)
                    all_results["icons_cached"] += results.get("icons_cached", 0)
                    all_results["errors"].extend(results.get("errors", []))
                    all_results["scanned_paths"].append(path)

                    logger.info(f"  ✓ Scanned: {path}")

                except Exception as e:
                    error_msg = f"Failed to scan {path}: {str(e)}"
                    all_results["errors"].append(error_msg)
                    logger.error(f"  ✗ {error_msg}", exc_info=True)

            self.last_scan_time = datetime.now()
            self.last_scan_result = all_results

            logger.info(f"Scheduled scan completed at {datetime.now()}:")
            logger.info(f"  - New products: {all_results['new_products']}")
            logger.info(f"  - New versions: {all_results['new_versions']}")
            logger.info(f"  - AI generated: {all_results['ai_generated']}")
            logger.info(f"  - Icons cached: {all_results['icons_cached']}")
            if all_results['errors']:
                logger.warning(f"  - Errors: {len(all_results['errors'])}")

        finally:
            db.close()

    def get_status(self) -> dict:
        """
        스케줄러 상태 조회

        Returns:
            스케줄러 상태 정보
        """
        next_run = None
        if self.scheduler.running:
            job = self.scheduler.get_job('auto_scan')
            if job:
                next_run = job.next_run_time

        return {
            "is_running": self.is_running,
            "cron_schedule": self.cron_schedule,
            "scan_paths": self.scan_paths,
            "use_ai": self.use_ai,
            "next_run_time": next_run.isoformat() if next_run else None,
            "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "last_scan_result": self.last_scan_result
        }

    async def run_manual_scan(self) -> dict:
        """
        수동으로 즉시 스캔 실행

        Returns:
            스캔 결과
        """
        logger.info("Starting manual scheduled scan...")
        await self._run_scheduled_scan()
        return self.last_scan_result or {}

    def load_settings_from_db(self):
        """
        데이터베이스에서 스케줄러 설정 로드
        """
        db = SessionLocal()
        try:
            # 스캔 경로 로드
            scan_paths_setting = db.query(Setting).filter(Setting.key == "scan_paths").first()
            if scan_paths_setting and scan_paths_setting.value:
                import json
                self.scan_paths = json.loads(scan_paths_setting.value)

            # Cron 스케줄 로드
            cron_setting = db.query(Setting).filter(Setting.key == "cron_schedule").first()
            if cron_setting and cron_setting.value:
                self.cron_schedule = cron_setting.value

            # AI 활성화 여부 로드
            ai_setting = db.query(Setting).filter(Setting.key == "use_ai").first()
            if ai_setting and ai_setting.value:
                self.use_ai = ai_setting.value.lower() == "true"

            logger.info("✓ Scheduler settings loaded from database")

        finally:
            db.close()


# 전역 스케줄러 인스턴스
scan_scheduler = ScanScheduler()
