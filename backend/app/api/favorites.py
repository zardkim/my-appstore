from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.favorite import Favorite
from ..models.product import Product
from ..schemas import favorite as favorite_schema
from ..dependencies import get_current_user

router = APIRouter(tags=["favorites"])


@router.get("/", response_model=List[favorite_schema.FavoriteWithProduct])
async def get_my_favorites(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """현재 사용자의 즐겨찾기 목록 조회"""
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).all()

    # 제품 정보와 함께 반환
    result = []
    for fav in favorites:
        product = db.query(Product).filter(Product.id == fav.product_id).first()
        result.append({
            "id": fav.id,
            "user_id": fav.user_id,
            "product_id": fav.product_id,
            "created_at": fav.created_at,
            "product": {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "vendor": product.vendor,
                "icon_url": product.icon_url,
                "category": product.category
            } if product else None
        })

    return result


@router.post("/{product_id}")
async def add_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """즐겨찾기 추가"""
    # 제품 존재 확인
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 이미 즐겨찾기에 있는지 확인
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == product_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    # 즐겨찾기 추가
    favorite = Favorite(
        user_id=current_user.id,
        product_id=product_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return {"message": "Added to favorites", "id": favorite.id}


@router.delete("/{product_id}")
async def remove_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """즐겨찾기 제거"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == product_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()

    return {"message": "Removed from favorites"}


@router.get("/check/{product_id}")
async def check_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """특정 제품이 즐겨찾기에 있는지 확인"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.product_id == product_id
    ).first()

    return {"is_favorite": favorite is not None}
