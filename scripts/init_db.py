# ============================================================================
# scripts/init_db.py - Database Initialization Script
# ============================================================================

#!/usr/bin/env python3
"""
Initialize the AI Library database with collections, indexes, and sample data.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import connect_to_mongo, create_indexes, get_database
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_sample_data():
    """Create sample documents and queries for testing"""
    database = await get_database()
    
    # Sample documents
    sample_docs = [
        {
            "_id": "sample_ai_guide",
            "filename": "ai_implementation_guide.pdf",
            "content_type": "application/pdf",
            "upload_date": "2023-12-01T10:00:00",
            "status": "processed",
            "chunk_count": 8,
            "file_size": 2048000,
            "metadata": {
                "title": "AI Implementation Guide",
                "author": "Tech Team",
                "category": "Documentation",
                "tags": ["AI", "Machine Learning", "Implementation", "Guide"]
            }
        },
        {
            "_id": "sample_fastapi_docs",
            "filename": "fastapi_best_practices.md",
            "content_type": "text/plain",
            "upload_date": "2023-12-02T14:30:00",
            "status": "processed",
            "chunk_count": 5,
            "file_size": 1024000,
            "metadata": {
                "title": "FastAPI Best Practices",
                "author": "Development Team",
                "category": "Development",
                "tags": ["FastAPI", "Python", "API", "Best Practices"]
            }
        },
        {
            "_id": "sample_mongodb_guide",
            "filename": "mongodb_optimization.txt",
            "content_type": "text/plain",
            "upload_date": "2023-12-03T09:15:00",
            "status": "processed",
            "chunk_count": 6,
            "file_size": 1536000,
            "metadata": {
                "title": "MongoDB Optimization Guide",
                "author": "Database Team",
                "category": "Database",
                "tags": ["MongoDB", "Database", "Optimization", "Performance"]
            }
        }
    ]
    
    # Sample knowledge base chunks
    sample_chunks = [
        {
            "_id": "sample_ai_guide_chunk_0",
            "document_id": "sample_ai_guide",
            "content": "Artificial Intelligence (AI) is revolutionizing how businesses operate. This guide provides comprehensive instructions for implementing AI solutions in enterprise environments. Key considerations include data quality, model selection, and deployment strategies.",
            "metadata": {
                "filename": "ai_implementation_guide.pdf",
                "chunk_index": 0,
                "page": 1
            }
        },
        {
            "_id": "sample_ai_guide_chunk_1",
            "document_id": "sample_ai_guide",
            "content": "Machine Learning models require careful training and validation processes. Data preprocessing is crucial for model performance. Common techniques include normalization, feature engineering, and cross-validation.",
            "metadata": {
                "filename": "ai_implementation_guide.pdf",
                "chunk_index": 1,
                "page": 2
            }
        },
        {
            "_id": "sample_fastapi_docs_chunk_0",
            "document_id": "sample_fastapi_docs",
            "content": "FastAPI is a modern, fast web framework for building APIs with Python. It provides automatic API documentation, data validation, and async support. Best practices include proper error handling, dependency injection, and security measures.",
            "metadata": {
                "filename": "fastapi_best_practices.md",
                "chunk_index": 0
            }
        },
        {
            "_id": "sample_mongodb_guide_chunk_0",
            "document_id": "sample_mongodb_guide",
            "content": "MongoDB performance optimization involves proper indexing strategies, query optimization, and connection pooling. Key metrics to monitor include query execution time, index usage, and connection counts.",
            "metadata": {
                "filename": "mongodb_optimization.txt",
                "chunk_index": 0
            }
        }
    ]
    
    # Sample queries
    sample_queries = [
        {
            "_id": "sample_query_1",
            "question": "How do I implement AI in my business?",
            "answer": "To implement AI in your business, start by identifying use cases, ensuring data quality, selecting appropriate models, and developing a deployment strategy. Consider factors like data preprocessing, model training, and performance monitoring.",
            "confidence": 0.85,
            "sources_count": 2,
            "processing_time": 1.2,
            "model_used": "gpt-3.5-turbo",
            "timestamp": "2023-12-04T10:30:00"
        },
        {
            "_id": "sample_query_2",
            "question": "What are FastAPI best practices?",
            "answer": "FastAPI best practices include implementing proper error handling, using dependency injection, securing endpoints with authentication, leveraging async capabilities, and maintaining comprehensive API documentation.",
            "confidence": 0.92,
            "sources_count": 1,
            "processing_time": 0.8,
            "model_used": "gpt-3.5-turbo",
            "timestamp": "2023-12-04T11:15:00"
        }
    ]
    
    try:
        # Insert sample data
        await database.documents.insert_many(sample_docs)
        await database.knowledge_base.insert_many(sample_chunks)
        await database.queries.insert_many(sample_queries)
        
        logger.info("✅ Sample data created successfully")
        logger.info(f"📄 {len(sample_docs)} documents")
        logger.info(f"📝 {len(sample_chunks)} knowledge chunks")
        logger.info(f"❓ {len(sample_queries)} sample queries")
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")

async def main():
    """Main initialization function"""
    logger.info("🚀 Starting AI Library database initialization...")
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("✅ Connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        logger.info("✅ Database indexes created")
        
        # Create sample data
        await create_sample_data()
        
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())