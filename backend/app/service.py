from datetime import datetime
from bson import ObjectId
import pymongo
from app.core.logger import get_logger
from app.core.security import get_password_hash

logger = get_logger(__name__)

class DatabaseService:

    def __init__(self, db):
        self.db = db
        self.products = db["products"]
        self.reviews = db["reviews"]
        self.users = db["users"]
        self.orders = db["orders"]
        
        # Ensure unique index for users
        self.users.create_index("email", unique=True)

    async def create_product(self, product_data: dict):
        try:
            result = await self.products.insert_one(product_data)
            product = await self.products.find_one({"_id": result.inserted_id})
            logger.info(f"Created product: {result.inserted_id}")
            return product
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    async def get_product(self, product_id: str):
        try:
            product = await self.products.find_one({"_id": ObjectId(product_id)})
            if not product:
                raise ValueError(f"Product {product_id} not found")
            return product
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise

    async def list_products(self, skip: int = 0, limit: int = 10):
        try:
            total = await self.products.count_documents({})
            products = await self.products.find({}).skip(skip).limit(limit).to_list(limit)
            logger.info(f"Listed {len(products)} products")
            return products, total
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise

    async def update_product(self, product_id: str, update_data: dict):
        try:
            await self.get_product(product_id)
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data})
            
            product = await self.products.find_one({"_id": ObjectId(product_id)})
            logger.info(f"Updated product: {product_id}")
            return product
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise

    async def delete_product(self, product_id: str):
        try:
            await self.get_product(product_id)
            await self.products.delete_one({"_id": ObjectId(product_id)})
            logger.info(f"Deleted product: {product_id}")
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise


    async def create_review(self, product_id: str, review_data: dict):
        try:
            # Verify product exists
            await self.get_product(product_id)
            
            # Check if review already exists for this (product, user) 
            # (Double check at application level before insert)
            user_id = review_data.get("user_id")
            existing = await self.reviews.find_one({
                "product_id": product_id,
                "user_id": user_id
            })
            
            if existing:
                raise ValueError(f"User {user_id} has already reviewed this product")
                
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

    # User Methods
    async def create_user(self, user_data: dict):
        try:
            user_data["password"] = get_password_hash(user_data["password"])
            user_data["created_at"] = datetime.utcnow()
            result = await self.users.insert_one(user_data)
            user = await self.users.find_one({"_id": result.inserted_id})
            logger.info(f"Created user: {user_data['email']}")
            return user
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f"User with email {user_data['email']} already exists")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def get_user_by_email(self, email: str):
        try:
            return await self.users.find_one({"email": email})
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise

    # Order Methods
    async def create_order(self, order_data: dict):
        try:
            # Check product exists
            product = await self.get_product(order_data["product_id"])
            order_data["total_price"] = product["price"] * order_data["quantity"]
            order_data["status"] = "pending"
            order_data["created_at"] = datetime.utcnow()
            
            result = await self.orders.insert_one(order_data)
            order = await self.orders.find_one({"_id": result.inserted_id})
            logger.info(f"Created order for user {order_data['user_id']}")
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise

async def get_service(db):
    return DatabaseService(db)
