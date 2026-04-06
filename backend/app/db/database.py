from motor.motor_asyncio import AsyncClient, AsyncDatabase
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class Database:
    client: AsyncClient = None
    db: AsyncDatabase = None
    
    @classmethod
    async def connect_db(cls):
        try:
            cls.client = AsyncClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.DATABASE_NAME]
            
            await cls.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")
    
    @classmethod
    def get_db(cls) -> AsyncDatabase:
        """Get database instance"""
        return cls.db

async def get_database():
    return Database.get_db()
