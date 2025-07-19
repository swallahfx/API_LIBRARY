# ============================================================================
# tests/unit/test_document_service.py - Document Service Tests
# ============================================================================

import pytest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

from app.services.document_service import DocumentService
from app.models.document import DocumentMetadata

class TestDocumentService:
    
    @pytest.fixture
    def document_service(self):
        return DocumentService()
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("This is test content for document processing.")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_save_uploaded_file(self, document_service):
        """Test file saving functionality"""
        test_content = b"Test file content"
        filename = "test_file.txt"
        
        file_path = await document_service.save_uploaded_file(test_content, filename)
        
        assert Path(file_path).exists()
        assert filename in file_path
        
        # Read content to verify
        with open(file_path, 'rb') as f:
            saved_content = f.read()
        
        assert saved_content == test_content
        
        # Cleanup
        Path(file_path).unlink()
    
    @pytest.mark.asyncio
    async def test_process_document_text(self, document_service, temp_file, test_db):
        """Test processing text document"""
        metadata = DocumentMetadata(
            title="Test Document",
            author="Test Author",
            category="Testing"
        )
        
        with patch('app.core.database.get_database', return_value=test_db):
            result = await document_service.process_document(
                temp_file,
                "test.txt",
                "text/plain",
                metadata
            )
        
        assert result.filename == "test.txt"
        assert result.content_type == "text/plain"
        assert result.status.value == "processed"
        assert result.chunk_count > 0
        assert result.metadata.title == "Test Document"
    
    @pytest.mark.asyncio
    async def test_process_unsupported_file_type(self, document_service, temp_file):
        """Test handling of unsupported file types"""
        with pytest.raises(ValueError, match="Unsupported file type"):
            await document_service.process_document(
                temp_file,
                "test.xyz",
                "application/xyz",
                None
            )
    
    @pytest.mark.asyncio
    async def test_get_document(self, document_service, test_db):
        """Test getting document by ID"""
        # Insert test document
        doc_data = {
            "_id": "test_doc_123",
            "filename": "test.txt",
            "content_type": "text/plain",
            "upload_date": "2023-01-01T00:00:00",
            "status": "processed",
            "chunk_count": 1
        }
        
        await test_db.documents.insert_one(doc_data)
        
        with patch('app.core.database.get_database', return_value=test_db):
            result = await document_service.get_document("test_doc_123")
        
        assert result is not None
        assert result.id == "test_doc_123"
        assert result.filename == "test.txt"
    
    @pytest.mark.asyncio
    async def test_list_documents(self, document_service, test_db):
        """Test listing documents with pagination"""
        # Insert test documents
        docs = [
            {
                "_id": f"doc_{i}",
                "filename": f"test_{i}.txt",
                "content_type": "text/plain",
                "upload_date": "2023-01-01T00:00:00",
                "status": "processed",
                "chunk_count": 1
            }
            for i in range(5)
        ]
        
        await test_db.documents.insert_many(docs)
        
        with patch('app.core.database.get_database', return_value=test_db):
            result = await document_service.list_documents(page=1, limit=3)
        
        assert len(result["documents"]) == 3
        assert result["total"] == 5
        assert result["page"] == 1
        assert result["has_next"] is True
        assert result["has_prev"] is False