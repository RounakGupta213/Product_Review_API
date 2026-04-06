from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import datetime
from app.db.database import get_database
from app.models import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ReviewCreate, ReviewResponse, ReviewListResponse)
from app.service import DatabaseService
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

async def get_service(db = Depends(get_database)) -> DatabaseService:
    return DatabaseService(db)

@router.post("/products", response_model=ProductResponse, status_code=201, tags=["products"])
async def create_product(product: ProductCreate, service: DatabaseService = Depends(get_service)):
    try:
        data = {
            **product.dict(),
            "avg_rating": 0.0,
            "total_reviews": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await service.create_product(data)
        return result
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products", tags=["products"])
async def list_products(skip: int = 0, limit: int = 10, service: DatabaseService = Depends(get_service)):
    try:
        products, total = await service.list_products(skip, limit)
        return {"products": products, "total": total}
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}", response_model=ProductResponse, tags=["products"])
async def get_product(product_id: str, service: DatabaseService = Depends(get_service)):
    """Get a product by ID"""
    try:
        product = await service.get_product(product_id)
        return product
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}", response_model=ProductResponse, tags=["products"])
async def update_product(product_id: str, product: ProductUpdate, service: DatabaseService = Depends(get_service)):
    """Update a product"""
    try:
        update_data = product.dict(exclude_unset=True)
        result = await service.update_product(product_id, update_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}", status_code=204, tags=["products"])
async def delete_product(product_id: str, service: DatabaseService = Depends(get_service)):
    """Delete a product"""
    try:
        await service.delete_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{product_id}/reviews", response_model=ReviewResponse, status_code=201, tags=["reviews"])
async def create_review(
    product_id: str, 
    review: ReviewCreate, 
    service: DatabaseService = Depends(get_service)):

    try:
        data = review.dict()
        result = await service.create_review(product_id, data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}/reviews", response_model=ReviewListResponse, tags=["reviews"])
async def get_product_reviews(
    product_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: DatabaseService = Depends(get_service)):

    try:
        reviews, total = await service.get_product_reviews(product_id, skip, limit)
        return {
            "reviews": reviews,
            "total": total
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reviews/{review_id}", status_code=204, tags=["reviews"])
async def delete_review(
    review_id: str,
    user_id: str = Query(...),
    service: DatabaseService = Depends(get_service)):
    
    try:
        await service.delete_review(review_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "Product Review API"}
