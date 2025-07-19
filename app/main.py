from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, create_indexes
from app.core.redis import redis_client
from app.services.vector_service import vector_service
from app.api.endpoints import documents, queries, analytics, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AI Knowledge Library...")
    
    # Connect to databases
    await connect_to_mongo()
    await create_indexes()
    await redis_client.connect()
    
    # Initialize vector store
    await vector_service.initialize_vector_store()
    
    logger.info("AI Knowledge Library started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Knowledge Library...")
    await close_mongo_connection()
    await redis_client.disconnect()
    logger.info("AI Knowledge Library shut down successfully")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Intelligent document search and Q&A system built with FastAPI, MongoDB, and LangChain",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(queries.router, prefix=f"{settings.API_V1_STR}/queries", tags=["queries"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(health.router, prefix="/health", tags=["health"])

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
