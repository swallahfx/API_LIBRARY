# ============================================================================
# tests/integration/test_api_endpoints.py - API Integration Tests
# ============================================================================

import pytest
from httpx import AsyncClient
import tempfile
from pathlib import Path

class TestDocumentEndpoints:
    
    @pytest.mark.asyncio
    async def test_upload_document_success(self, client: AsyncClient):
        """Test successful document upload"""
        # Create test file
        test_content = "This is a test document for upload testing."
        
        files = {
            "file": ("test_document.txt", test_content, "text/plain")
        }
        
        data = {
            "title": "Test Document",
            "author": "Test Author",
            "category": "Testing"
        }
        
        response = await client.post("/api/v1/documents/upload", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["filename"] == "test_document.txt"
        assert result["status"] in ["processing", "processed"]
    
    @pytest.mark.asyncio
    async def test_upload_large_file(self, client: AsyncClient):
        """Test upload of file exceeding size limit"""
        # Create large file content (>10MB)
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        
        files = {
            "file": ("large_file.txt", large_content, "text/plain")
        }
        
        response = await client.post("/api/v1/documents/upload", files=files)
        
        assert response.status_code == 413  # File too large
    
    @pytest.mark.asyncio
    async def test_upload_unsupported_file_type(self, client: AsyncClient):
        """Test upload of unsupported file type"""
        files = {
            "file": ("test.xyz", "content", "application/xyz")
        }
        
        response = await client.post("/api/v1/documents/upload", files=files)
        
        assert response.status_code == 400
        result = response.json()
        assert "Unsupported file type" in result["detail"]
    
    @pytest.mark.asyncio
    async def test_list_documents(self, client: AsyncClient):
        """Test listing documents"""
        response = await client.get("/api/v1/documents/")
        
        assert response.status_code == 200
        result = response.json()
        assert "documents" in result
        assert "total" in result
        assert "page" in result
        assert "limit" in result

class TestQueryEndpoints:
    
    @pytest.mark.asyncio
    async def test_ask_question_no_documents(self, client: AsyncClient):
        """Test asking question when no documents are available"""
        query_data = {
            "question": "What is artificial intelligence?",
            "max_results": 5
        }
        
        response = await client.post("/api/v1/queries/ask", json=query_data)
        
        assert response.status_code == 200
        result = response.json()
        assert "answer" in result
        assert result["confidence"] == 0.0  # No documents available
    
    @pytest.mark.asyncio
    async def test_ask_empty_question(self, client: AsyncClient):
        """Test asking empty question"""
        query_data = {
            "question": "",
            "max_results": 5
        }
        
        response = await client.post("/api/v1/queries/ask", json=query_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_query_history(self, client: AsyncClient):
        """Test getting query history"""
        response = await client.get("/api/v1/queries/history")
        
        assert response.status_code == 200
        result = response.json()
        assert "queries" in result
        assert "total" in result

class TestAnalyticsEndpoints:
    
    @pytest.mark.asyncio
    async def test_get_analytics(self, client: AsyncClient):
        """Test getting system analytics"""
        response = await client.get("/api/v1/analytics/")
        
        assert response.status_code == 200
        result = response.json()
        assert "total_documents" in result
        assert "total_queries" in result
        assert "popular_topics" in result
        assert "recent_activity" in result
    
    @pytest.mark.asyncio
    async def test_get_document_analytics(self, client: AsyncClient):
        """Test getting document analytics"""
        response = await client.get("/api/v1/analytics/documents")
        
        assert response.status_code == 200
        result = response.json()
        assert "document_types" in result
        assert "total_documents" in result

class TestHealthEndpoints:
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health/")
        
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert "timestamp" in result
        assert "services" in result
    
    @pytest.mark.asyncio
    async def test_readiness_check(self, client: AsyncClient):
        """Test readiness check endpoint"""
        response = await client.get("/health/ready")
        
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_liveness_check(self, client: AsyncClient):
        """Test liveness check endpoint"""
        response = await client.get("/health/live")
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "alive"
