"""
Simplified Database Service
Handles all product and review operations directly
"""
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncDatabase
from app.core.logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """Unified database service for products and reviews"""

    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.products = db["products"]
        self.reviews = db["reviews"]

    async def create_product(self, product_data: dict):
        """Create a new product"""
        try:
            result = await self.products.insert_one(product_data)
            product = await self.products.find_one({"_id": result.inserted_id})
            logger.info(f"Created product: {result.inserted_id}")
            return product
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    async def get_product(self, product_id: str):
        """Get product by ID"""
        try:
            product = await self.products.find_one({"_id": ObjectId(product_id)})
            if not product:
                raise ValueError(f"Product {product_id} not found")
            return product
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise

    async def list_products(self, skip: int = 0, limit: int = 10):
        """List all products with pagination"""
        try:
            total = await self.products.count_documents({})
            products = await self.products.find({}).skip(skip).limit(limit).to_list(limit)
            logger.info(f"Listed {len(products)} products")
            return products, total
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise

    async def update_product(self, product_id: str, update_data: dict):
        """Update a product"""
        try:
            await self.get_product(product_id)
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )
            
            product = await self.products.find_one({"_id": ObjectId(product_id)})
            logger.info(f"Updated product: {product_id}")
            return product
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise

    async def delete_product(self, product_id: str):
        """Delete a product"""
        try:
            await self.get_product(product_id)
            await self.products.delete_one({"_id": ObjectId(product_id)})
            logger.info(f"Deleted product: {product_id}")
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise


    async def create_review(self, product_id: str, review_data: dict):
        """Create a review for a product"""
        try:
            # Verify product exists
            await self.get_product(product_id)
            
            review_data["product_id"] = product_id
            review_data["created_at"] = datetime.utcnow()
            review_data["updated_at"] = datetime.utcnow()
            
            # Insert review
            result = await self.reviews.insert_one(review_data)
            logger.info(f"Created review: {result.inserted_id}")
            
            # Recalculate and update product rating
            await self._update_product_rating(product_id)
            
            review = await self.reviews.find_one({"_id": result.inserted_id})
            return review
            
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}")
            raise

    async def get_product_reviews(self, product_id: str, skip: int = 0, limit: int = 10):
        """Get all reviews for a product"""
        try:
            # Verify product exists
            await self.get_product(product_id)
            
            total = await self.reviews.count_documents({"product_id": product_id})
            reviews = await self.reviews.find(
                {"product_id": product_id}
            ).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
            
            logger.info(f"Retrieved {len(reviews)} reviews for product {product_id}")
            return reviews, total
            
        except Exception as e:
            logger.error(f"Error getting product reviews: {str(e)}")
            raise

    async def delete_review(self, review_id: str, user_id: str):
        """Delete a review (only by author)"""
        try:
            review = await self.reviews.find_one({"_id": ObjectId(review_id)})
            if not review:
                raise ValueError(f"Review {review_id} not found")
            
            if review["user_id"] != user_id:
                raise ValueError("Only review author can delete")
            
            product_id = review["product_id"]
            await self.reviews.delete_one({"_id": ObjectId(review_id)})
            
            # Recalculate and update product rating
            await self._update_product_rating(product_id)
            
            logger.info(f"Deleted review: {review_id}")
            
        except Exception as e:
            logger.error(f"Error deleting review: {str(e)}")
            raise

    async def _update_product_rating(self, product_id: str):
        """Recalculate and update product average rating"""
        try:
            reviews = await self.reviews.find(
                {"product_id": product_id}
            ).to_list(None)
            
            if reviews:
                avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
                total_reviews = len(reviews)
            else:
                avg_rating = 0.0
                total_reviews = 0
            
            await self.products.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$set": {
                        "avg_rating": round(avg_rating, 2),
                        "total_reviews": total_reviews,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Updated rating for {product_id}: {avg_rating:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating rating: {str(e)}")
            raise


async def get_service(db: AsyncDatabase) -> DatabaseService:
    """Dependency for getting database service"""
    return DatabaseService(db)
