from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional, List
import os

from app.models.document import DocumentResponse, DocumentList, DocumentMetadata
from app.services.document_service import DocumentService
from app.services.vector_service import vector_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
document_service = DocumentService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Upload and process a document"""
    
    # Validate file size
    if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Create metadata
    metadata = DocumentMetadata(
        title=title,
        author=author,
        category=category,
        tags=tags.split(",") if tags else []
    )
    
    try:
        # Save uploaded file
        file_content = await file.read()
        file_path = await document_service.save_uploaded_file(file_content, file.filename)
        
        # Process document in background
        background_tasks.add_task(
            process_document_background,
            file_path,
            file.filename,
            file.content_type,
            metadata
        )
        
        return DocumentResponse(
            id="processing",
            filename=file.filename,
            content_type=file.content_type,
            status="processing",
            upload_date=datetime.utcnow(),
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_document_background(
    file_path: str, 
    filename: str, 
    content_type: str, 
    metadata: DocumentMetadata
):
    """Background task for document processing"""
    try:
        # Process document
        document = await document_service.process_document(
            file_path, filename, content_type, metadata
        )
        
        # Add to vector store
        await vector_service.add_document_chunks(document.id)
        
        logger.info(f"Successfully processed document: {filename}")
        
    except Exception as e:
        logger.error(f"Background processing failed for {filename}: {e}")

@router.get("/", response_model=DocumentList)
async def list_documents(page: int = 1, limit: int = 20):
    """List documents with pagination"""
    
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    
    try:
        result = await document_service.list_documents(page, limit)
        return DocumentList(**result)
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document by ID"""
    
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its chunks"""
    
    success = await document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove from vector store
    await vector_service.remove_document_chunks(document_id)
    
    return {"message": "Document deleted successfully"}
