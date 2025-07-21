from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None

class DocumentCreate(BaseModel):
    filename: str
    content_type: str
    metadata: Optional[DocumentMetadata] = None

class DocumentResponse(BaseModel):
    # id: str
    id: str = Field(alias="_id")
    filename: str
    content_type: str
    status: DocumentStatus
    upload_date: datetime
    processing_time: Optional[float] = None
    chunk_count: Optional[int] = None
    file_size: Optional[int] = None
    metadata: Optional[DocumentMetadata] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None

class DocumentList(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool
