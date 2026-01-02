"""
불일치 항목 스키마
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class UnmatchedItemBase(BaseModel):
    """불일치 항목 기본 스키마"""
    file_path: str
    file_name: str
    folder_path: str
    parsed_name: Optional[str] = None
    parsed_version: Optional[str] = None
    parsed_vendor: Optional[str] = None


class UnmatchedItemCreate(UnmatchedItemBase):
    """불일치 항목 생성"""
    suggested_metadata: Optional[Dict[str, Any]] = None
    confidence_score: float


class UnmatchedItemUpdate(BaseModel):
    """불일치 항목 업데이트"""
    status: Optional[str] = None
    manual_metadata: Optional[Dict[str, Any]] = None
    reviewed_by: Optional[int] = None


class UnmatchedItemResponse(UnmatchedItemBase):
    """불일치 항목 응답"""
    id: int
    suggested_metadata: Optional[Dict[str, Any]] = None
    confidence_score: float
    status: str
    manual_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None

    class Config:
        from_attributes = True


class UnmatchedListResponse(BaseModel):
    """불일치 목록 응답"""
    total: int
    items: List[UnmatchedItemResponse]


class ApproveRequest(BaseModel):
    """AI 제안 승인 요청"""
    pass  # 별도 파라미터 불필요


class ManualMetadataRequest(BaseModel):
    """수동 메타데이터 입력 요청"""
    title: str
    vendor: str
    category: str
    description: str
    official_website: Optional[str] = None
    icon_url: Optional[str] = None


class SearchRequest(BaseModel):
    """수동 검색 요청"""
    software_name: str
    collect_extended: bool = True
