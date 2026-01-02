from pydantic import BaseModel
from typing import List, Optional


class GoogleImageSearchRequest(BaseModel):
    """Google 이미지 검색 요청"""
    query: str
    limit: int = 5
    offset: int = 0


class GoogleImageResult(BaseModel):
    """Google 이미지 검색 결과"""
    url: str
    title: str
    thumbnail: str
    context_link: str = ""


class GoogleImageSearchResponse(BaseModel):
    """Google 이미지 검색 응답"""
    success: bool
    images: List[GoogleImageResult]
    error: Optional[str] = None


class ImageUploadResponse(BaseModel):
    """이미지 업로드 응답"""
    success: bool
    url: Optional[str] = None
    urls: Optional[List[str]] = None
    error: Optional[str] = None


class ImageDeleteResponse(BaseModel):
    """이미지 삭제 응답"""
    success: bool
    deleted_count: int
    error: Optional[str] = None
