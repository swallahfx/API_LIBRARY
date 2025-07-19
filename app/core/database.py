import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    logger.info("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]
    logger.info("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    logger.info("Closing connection to MongoDB...")
    db.client.close()
    logger.info("Disconnected from MongoDB")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.database

async def create_indexes():
    """Create database indexes for better performance"""
    database = await get_database()
    
    # Documents collection indexes
    await database.documents.create_index([("filename", 1)])
    await database.documents.create_index([("upload_date", -1)])
    await database.documents.create_index([("status", 1)])
    await database.documents.create_index([("content_type", 1)])
    
    # Queries collection indexes
    await database.queries.create_index([("timestamp", -1)])
    await database.queries.create_index([("question", "text")])
    
    # Knowledge base indexes
    await database.knowledge_base.create_index([("document_id", 1)])
    await database.knowledge_base.create_index([("content", "text")])
    
    logger.info("Database indexes created successfully")
