from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class AnalyticsResponse(BaseModel):
    total_documents: int
    total_queries: int
    popular_topics: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    usage_statistics: Dict[str, Any]

class DocumentAnalytics(BaseModel):
    document_id: str
    filename: str
    view_count: int
    query_count: int
    last_accessed: datetime
    average_relevance: float

class QueryAnalytics(BaseModel):
    total_queries: int
    average_response_time: float
    success_rate: float
    popular_questions: List[Dict[str, Any]]
    query_trends: List[Dict[str, Any]]
