from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FavoriteBase(BaseModel):
    product_id: int


class FavoriteCreate(FavoriteBase):
    pass


class Favorite(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteWithProduct(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: Optional[dict] = None

    class Config:
        from_attributes = True
