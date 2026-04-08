from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from app.db.database import get_database
from app.models import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ReviewCreate, ReviewResponse, ReviewListResponse,
    UserRegister, UserLogin, Token, UserResponse,
    OrderCreate, OrderResponse
)
from app.service import DatabaseService
from app.core.logger import get_logger
from app.core.security import create_access_token, verify_password

logger = get_logger(__name__)
router = APIRouter()

async def get_service(db = Depends(get_database)) -> DatabaseService:
    return DatabaseService(db)

security = HTTPBearer()

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security),
    service: DatabaseService = Depends(get_service)
) -> UserResponse:
    from app.core.security import decode_access_token
    email = decode_access_token(auth.credentials)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Convert ObjectId to string for Pydantic model
    user["_id"] = str(user["_id"])
    return UserResponse(**user)

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
        # Convert MongoDB ObjectId to string
        result["_id"] = str(result["_id"])
        return result
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products", tags=["products"])
async def list_products(skip: int = 0, limit: int = 10, service: DatabaseService = Depends(get_service)):
    try:
        products, total = await service.list_products(skip, limit)
        # Convert ObjectId to string for all products
        for product in products:
            product["_id"] = str(product["_id"])
        return {"products": products, "total": total}
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}", response_model=ProductResponse, tags=["products"])
async def get_product(product_id: str, service: DatabaseService = Depends(get_service)):
    """Get a product by ID"""
    try:
        product = await service.get_product(product_id)
        product["_id"] = str(product["_id"])
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
        result["_id"] = str(result["_id"])
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
        result["_id"] = str(result["_id"])
        return result
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND
        if "already reviewed" in str(e).lower():
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=str(e))
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
        # Convert ObjectId to string for all reviews
        for review in reviews:
            review["_id"] = str(review["_id"])
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
    current_user: UserResponse = Depends(get_current_user),
    service: DatabaseService = Depends(get_service)):
    
    try:
        await service.delete_review(review_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "Product Review API"}

# Auth Routes
@router.post("/auth/register", response_model=UserResponse, status_code=201, tags=["auth"])
async def register(user: UserRegister, service: DatabaseService = Depends(get_service)):
    try:
        result = await service.create_user(user.dict())
        result["_id"] = str(result["_id"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/auth/login", response_model=Token, tags=["auth"])
async def login(user_data: UserLogin, service: DatabaseService = Depends(get_service)):
    user = await service.get_user_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    user["_id"] = str(user["_id"])
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user
    }

# Order Routes
@router.post("/orders", response_model=OrderResponse, status_code=201, tags=["orders"])
async def create_order(
    order: OrderCreate, 
    user_id: str = Query(...), 
    service: DatabaseService = Depends(get_service)):
    try:
        data = order.dict()
        data["user_id"] = user_id
        result = await service.create_order(data)
        result["_id"] = str(result["_id"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
