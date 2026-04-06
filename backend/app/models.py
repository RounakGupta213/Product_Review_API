from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)

class ProductResponse(ProductBase):
    id: str = Field(..., alias="_id")
    avg_rating: float = Field(default=0.0)
    total_reviews: int = Field(default=0)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class ReviewCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=5000)

    @validator('comment')
    def comment_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Comment cannot be empty or only whitespace')
        return v.strip()

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, min_length=10, max_length=5000)

    @validator('comment')
    def comment_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Comment cannot be empty or only whitespace')
        return v.strip() if v else v

class ReviewResponse(BaseModel):
    id: str = Field(..., alias="_id")
    product_id: str
    user_id: str
    rating: int
    comment: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class ReviewListResponse(BaseModel):
    reviews: list[ReviewResponse]
    total: int
