from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    context_filter: Optional[str] = None
    max_results: int = Field(default=5, ge=1, le=20)
    include_sources: bool = True
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)

class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
    document_id: str
    chunk_index: int

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[SourceDocument]
    query_id: str
    processing_time: float
    model_used: str
    timestamp: datetime

class QueryHistory(BaseModel):
    queries: List[QueryResponse]
    total: int
    page: int
    limit: int

class SuggestedQuestion(BaseModel):
    question: str
    category: str
    confidence: float
