from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import get_logger
from app.db.database import Database
from app.routes import router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logger.info("Starting up application...")
    await Database.connect_db()
    yield
    
    logger.info("Shutting down application...")
    await Database.close_db()

# Create application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Product Review API - FastAPI with MongoDB",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Product Review API",
        "version": settings.APP_VERSION,
        "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
