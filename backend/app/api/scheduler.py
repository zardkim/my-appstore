from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.core.scheduler import scan_scheduler
from app.models.setting import Setting
from app.dependencies import get_current_admin_user
import json

router = APIRouter()


class SchedulerConfig(BaseModel):
    cron_schedule: str
    scan_paths: List[str]
    use_ai: bool = True


class SchedulerStatusResponse(BaseModel):
    is_running: bool
    cron_schedule: str
    scan_paths: List[str]
    use_ai: bool
    next_run_time: Optional[str]
    last_scan_time: Optional[str]
    last_scan_result: Optional[dict]


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    current_user = Depends(get_current_admin_user)
):
    """
    스케줄러 상태 조회
    """
    status = scan_scheduler.get_status()
    return status


@router.post("/start")
async def start_scheduler(
    config: SchedulerConfig,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    스케줄러 시작

    Args:
        cron_schedule: Cron 표현식 (예: "0 2 * * *")
        scan_paths: 스캔할 경로 목록
        use_ai: AI 메타데이터 생성 활성화
    """
    try:
        # 설정 저장
        _save_scheduler_settings(db, config)

        # 스케줄러 시작
        scan_scheduler.start(
            cron_expression=config.cron_schedule,
            scan_paths=config.scan_paths,
            use_ai=config.use_ai
        )

        return {
            "success": True,
            "message": "Scheduler started successfully",
            "status": scan_scheduler.get_status()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/stop")
async def stop_scheduler(
    current_user = Depends(get_current_admin_user)
):
    """
    스케줄러 중지
    """
    try:
        scan_scheduler.stop()
        return {
            "success": True,
            "message": "Scheduler stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")


@router.post("/run-now")
async def run_scheduler_now(
    current_user = Depends(get_current_admin_user)
):
    """
    즉시 스캔 실행 (스케줄 무시)
    """
    try:
        result = await scan_scheduler.run_manual_scan()
        return {
            "success": True,
            "message": "Manual scan completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run manual scan: {str(e)}")


@router.get("/config")
async def get_scheduler_config(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    저장된 스케줄러 설정 조회
    """
    config = _load_scheduler_settings(db)
    return config


def _save_scheduler_settings(db: Session, config: SchedulerConfig):
    """
    스케줄러 설정을 데이터베이스에 저장
    """
    # 스캔 경로
    scan_paths_setting = db.query(Setting).filter(Setting.key == "scan_paths").first()
    if scan_paths_setting:
        scan_paths_setting.value = json.dumps(config.scan_paths)
    else:
        scan_paths_setting = Setting(
            key="scan_paths",
            value=json.dumps(config.scan_paths),
            description="Scheduled scan paths"
        )
        db.add(scan_paths_setting)

    # Cron 스케줄
    cron_setting = db.query(Setting).filter(Setting.key == "cron_schedule").first()
    if cron_setting:
        cron_setting.value = config.cron_schedule
    else:
        cron_setting = Setting(
            key="cron_schedule",
            value=config.cron_schedule,
            description="Cron expression for scheduled scans"
        )
        db.add(cron_setting)

    # AI 활성화
    ai_setting = db.query(Setting).filter(Setting.key == "use_ai").first()
    if ai_setting:
        ai_setting.value = str(config.use_ai)
    else:
        ai_setting = Setting(
            key="use_ai",
            value=str(config.use_ai),
            description="Enable AI metadata generation"
        )
        db.add(ai_setting)

    db.commit()


def _load_scheduler_settings(db: Session) -> dict:
    """
    데이터베이스에서 스케줄러 설정 로드
    """
    scan_paths = []
    cron_schedule = "0 2 * * *"
    use_ai = True

    # 스캔 경로
    scan_paths_setting = db.query(Setting).filter(Setting.key == "scan_paths").first()
    if scan_paths_setting and scan_paths_setting.value:
        scan_paths = json.loads(scan_paths_setting.value)

    # Cron 스케줄
    cron_setting = db.query(Setting).filter(Setting.key == "cron_schedule").first()
    if cron_setting and cron_setting.value:
        cron_schedule = cron_setting.value

    # AI 활성화
    ai_setting = db.query(Setting).filter(Setting.key == "use_ai").first()
    if ai_setting and ai_setting.value:
        use_ai = ai_setting.value.lower() == "true"

    return {
        "cron_schedule": cron_schedule,
        "scan_paths": scan_paths,
        "use_ai": use_ai
    }
