import uuid
import os
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader, CSVLoader

from app.core.config import settings
from app.core.database import get_database
from app.models.document import DocumentStatus, DocumentMetadata, DocumentResponse
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )
        
        self.loaders = {
            "application/pdf": PyPDFLoader,
            "text/plain": TextLoader,
            "text/csv": CSVLoader,
        }
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to disk"""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_id = str(uuid.uuid4())
        file_path = upload_dir / f"{file_id}_{filename}"
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        
        return str(file_path)
    
    async def process_document(
        self, 
        file_path: str, 
        filename: str, 
        content_type: str,
        metadata: Optional[DocumentMetadata] = None
    ) -> DocumentResponse:
        """Process uploaded document and extract chunks"""
        
        start_time = datetime.utcnow()
        doc_id = str(uuid.uuid4())
        
        try:
            # Validate file type
            if content_type not in self.loaders:
                raise ValueError(f"Unsupported file type: {content_type}")
            
            # Load document
            loader_class = self.loaders[content_type]
            loader = loader_class(file_path)
            documents = loader.load()
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create document record
            document_record = {
                "_id": doc_id,
                "filename": filename,
                "content_type": content_type,
                "upload_date": datetime.utcnow(),
                "status": DocumentStatus.PROCESSED.value,
                "chunk_count": len(chunks),
                "processing_time": (datetime.utcnow() - start_time).total_seconds(),
                "file_path": file_path,
                "file_size": file_size,
                "metadata": metadata.dict() if metadata else {}
            }
            
            # Save to database
            database = await get_database()
            await database.documents.insert_one(document_record)
            
            # Save chunks to knowledge base
            chunk_records = []
            for i, chunk in enumerate(chunks):
                chunk_record = {
                    "_id": f"{doc_id}_chunk_{i}",
                    "document_id": doc_id,
                    "content": chunk.page_content,
                    "metadata": {
                        **chunk.metadata,
                        "filename": filename,
                        "chunk_index": i,
                        "document_metadata": metadata.dict() if metadata else {}
                    }
                }
                chunk_records.append(chunk_record)
            
            if chunk_records:
                await database.knowledge_base.insert_many(chunk_records)
            
            logger.info(f"Successfully processed document: {filename}")
            
            return DocumentResponse(**document_record)
            
        except Exception as e:
            # Update status to failed
            database = await get_database()
            await database.documents.update_one(
                {"_id": doc_id},
                {"$set": {
                    "status": DocumentStatus.FAILED.value, 
                    "error": str(e),
                    "processing_time": (datetime.utcnow() - start_time).total_seconds()
                }}
            )
            logger.error(f"Document processing failed for {filename}: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """Get document by ID"""
        database = await get_database()
        document = await database.documents.find_one({"_id": document_id})
        
        if document:
            return DocumentResponse(**document)
        return None
    
    async def list_documents(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """List documents with pagination"""
        database = await get_database()
        
        # Count total documents
        total = await database.documents.count_documents({})
        
        # Calculate pagination
        skip = (page - 1) * limit
        has_next = skip + limit < total
        has_prev = page > 1
        
        # Get documents
        cursor = database.documents.find({}).skip(skip).limit(limit).sort("upload_date", -1)
        documents = []
        
        async for doc in cursor:
            documents.append(DocumentResponse(**doc))
        
        return {
            "documents": documents,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": has_next,
            "has_prev": has_prev
        }
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document and its chunks"""
        database = await get_database()
        
        # Delete document
        result = await database.documents.delete_one({"_id": document_id})
        if result.deleted_count == 0:
            return False
        
        # Delete associated chunks
        await database.knowledge_base.delete_many({"document_id": document_id})
        
        logger.info(f"Successfully deleted document: {document_id}")
        return True
