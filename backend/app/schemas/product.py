from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class VersionBase(BaseModel):
    version_name: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None


class VersionResponse(VersionBase):
    id: int
    product_id: int
    file_path: str
    release_date: datetime
    is_portable: bool = False

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    icon_url: Optional[str] = None
    category: Optional[str] = None


class ProductCreate(ProductBase):
    folder_path: str


class PatchLink(BaseModel):
    """패치/크랙 관련 링크"""
    title: str
    url: str


class ProductResponse(ProductBase):
    id: int
    folder_path: str
    is_portable: bool = False
    versions: List[VersionResponse] = []

    # 확장 메타데이터
    official_website: Optional[str] = None
    license_type: Optional[str] = None
    platform: Optional[str] = None
    detailed_description: Optional[str] = None
    features: Optional[List[str]] = None  # 기능 목록
    system_requirements: Optional[Dict[str, Any]] = None
    supported_formats: Optional[List[str]] = None  # 지원 포맷 목록
    release_notes: Optional[str] = None
    release_date: Optional[str] = None
    crawled_from: Optional[Dict[str, Any]] = None
    last_crawled_at: Optional[datetime] = None
    screenshots: Optional[List[str]] = None  # 문자열 배열로 변경 (URL 직접 저장)
    installation_guide: Optional[str] = None
    patch_links: Optional[List[PatchLink]] = None  # 패치/크랙 관련 링크 (최대 5개)

    @field_validator('screenshots', mode='before')
    @classmethod
    def convert_screenshots(cls, v):
        """DB에서 읽을 때 객체 배열을 문자열 배열로 변환"""
        if v is None:
            return None
        if isinstance(v, list):
            # 이미 문자열 배열이면 그대로 반환
            if all(isinstance(item, str) for item in v):
                return v
            # 객체 배열이면 URL만 추출
            return [item.get('url') if isinstance(item, dict) else item for item in v]
        return v

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    products: List[ProductResponse]


class ProductUpdateRequest(BaseModel):
    """제품 메타데이터 업데이트 요청"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    category: Optional[str] = None
    icon_url: Optional[str] = None
    is_portable: Optional[bool] = None

    # 확장 메타데이터
    official_website: Optional[str] = None
    license_type: Optional[str] = None
    platform: Optional[str] = None
    detailed_description: Optional[str] = None
    installation_guide: Optional[str] = None
    features: Optional[List[str]] = None  # 기능 목록
    system_requirements: Optional[Dict[str, Any]] = None
    supported_formats: Optional[List[str]] = None  # 지원 포맷 목록
    release_notes: Optional[str] = None
    release_date: Optional[str] = None
    screenshots: Optional[List[str]] = None  # 문자열 배열로 변경
    patch_links: Optional[List[PatchLink]] = None  # 패치/크랙 관련 링크 (최대 5개)


class VersionUpdateRequest(BaseModel):
    """버전 정보 업데이트 요청"""
    version_name: Optional[str] = None
    release_date: Optional[datetime] = None
    is_portable: Optional[bool] = None
