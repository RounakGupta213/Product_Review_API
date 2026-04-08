import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    
    APP_NAME: str = "Product Review API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL", "mongodb://localhost:27017" )
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "product_review_db")
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    API_V1_PREFIX: str = "/api/v1"
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Validation set for reviews 
    MAX_REVIEW_LENGTH: int = 5000
    MIN_REVIEW_LENGTH: int = 10
    MIN_RATING: int = 1
    MAX_RATING: int = 5

settings = Settings()