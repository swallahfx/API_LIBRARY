# ============================================================================
# scripts/load_sample_data.py - Load Sample Documents
# ============================================================================

#!/usr/bin/env python3
"""
Load sample documents into the AI Library for testing and demonstration.
"""

import asyncio
import aiofiles
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.document_service import DocumentService
from app.models.document import DocumentMetadata
from app.core.database import connect_to_mongo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_sample_files():
    """Create sample files for testing"""
    sample_dir = Path("tests/fixtures/sample_documents")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # AI Guide content
    ai_guide_content = """
# Artificial Intelligence Implementation Guide

## Introduction
Artificial Intelligence (AI) is transforming businesses across industries. This guide provides a comprehensive approach to implementing AI solutions.

## Key Components
1. Data Collection and Preparation
2. Model Selection and Training
3. Deployment and Monitoring
4. Continuous Improvement

## Best Practices
- Ensure high-quality training data
- Choose appropriate algorithms
- Implement robust testing procedures
- Monitor model performance continuously

## Common Challenges
- Data quality issues
- Model bias and fairness
- Scalability concerns
- Integration with existing systems
"""
    
    # FastAPI Guide content
    fastapi_guide_content = """
# FastAPI Best Practices

## Overview
FastAPI is a modern, fast web framework for building APIs with Python 3.6+ based on standard Python type hints.

## Key Features
- Fast performance
- Easy to use and learn
- Automatic API documentation
- Built-in data validation

## Best Practices
1. Use Pydantic models for request/response validation
2. Implement proper error handling
3. Use dependency injection
4. Add comprehensive documentation
5. Implement security measures

## Performance Tips
- Use async/await for I/O operations
- Implement caching strategies
- Optimize database queries
- Use connection pooling
"""
    
    # MongoDB Guide content
    mongodb_guide_content = """
# MongoDB Optimization Guide

## Introduction
MongoDB is a popular NoSQL database. This guide covers optimization techniques.

## Indexing Strategies
- Create indexes on frequently queried fields
- Use compound indexes for multi-field queries
- Monitor index usage with explain()

## Query Optimization
- Use projection to limit returned fields
- Implement pagination for large result sets
- Use aggregation pipeline efficiently

## Performance Monitoring
- Monitor query execution times
- Track connection pool usage
- Set up alerts for slow queries

## Best Practices
- Design schemas for your query patterns
- Use appropriate read/write concerns
- Implement proper sharding strategies
"""
    
    sample_files = [
        ("ai_implementation_guide.md", ai_guide_content, {
            "title": "AI Implementation Guide",
            "author": "Tech Team",
            "category": "Documentation",
            "tags": ["AI", "Machine Learning", "Implementation"]
        }),
        ("fastapi_best_practices.md", fastapi_guide_content, {
            "title": "FastAPI Best Practices",
            "author": "Development Team", 
            "category": "Development",
            "tags": ["FastAPI", "Python", "API"]
        }),
        ("mongodb_optimization.md", mongodb_guide_content, {
            "title": "MongoDB Optimization Guide",
            "author": "Database Team",
            "category": "Database", 
            "tags": ["MongoDB", "Database", "Performance"]
        })
    ]
    
    created_files = []
    
    for filename, content, metadata in sample_files:
        file_path = sample_dir / filename
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(content)
        
        created_files.append((str(file_path), filename, metadata))
        logger.info(f"✅ Created sample file: {filename}")
    
    return created_files

async def load_sample_documents():
    """Load sample documents into the system"""
    document_service = DocumentService()
    
    # Create sample files
    sample_files = await create_sample_files()
    
    for file_path, filename, metadata_dict in sample_files:
        try:
            metadata = DocumentMetadata(**metadata_dict)
            
            # Process document
            result = await document_service.process_document(
                file_path=file_path,
                filename=filename,
                content_type="text/plain",
                metadata=metadata
            )
            
            logger.info(f"✅ Processed document: {result.filename}")
            logger.info(f"   - ID: {result.id}")
            logger.info(f"   - Chunks: {result.chunk_count}")
            logger.info(f"   - Status: {result.status}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {filename}: {e}")

async def main():
    """Main function"""
    logger.info("📚 Loading sample documents into AI Library...")
    
    try:
        # Connect to database
        await connect_to_mongo()
        logger.info("✅ Connected to database")
        
        # Load sample documents
        await load_sample_documents()
        
        logger.info("🎉 Sample documents loaded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to load sample documents: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())