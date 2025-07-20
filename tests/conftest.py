# ============================================================================
# tests/conftest.py - Pytest Configuration
# ============================================================================

import pytest
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path

# Set test environment
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["DATABASE_NAME"] = "ai_library_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["OPENAI_API_KEY"] = "test-key"

from app.main import app
from app.core.database import get_database

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_db():
    """Create test database"""
    database = await get_database()
    yield database
    
    # Cleanup after test
    await database.drop_collection("documents")
    await database.drop_collection("queries")
    await database.drop_collection("knowledge_base")

@pytest.fixture
def sample_document():
    """Sample document for testing"""
    return {
        "filename": "test_document.txt",
        "content": "This is a test document for AI analysis.",
        "content_type": "text/plain"
    }

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content"""
    return b"%PDF-1.4 test content"