from fastapi import APIRouter, HTTPException
from typing import List

from app.models.query import QueryRequest, QueryResponse, QueryHistory
from app.services.qa_service import qa_service
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(query: QueryRequest):
    """Ask a question and get an AI-powered answer"""
    
    try:
        response = await qa_service.answer_question(query)
        return response
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail="Query processing failed")

@router.get("/history", response_model=QueryHistory)
async def get_query_history(page: int = 1, limit: int = 20):
    """Get query history with pagination"""
    
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20
    
    try:
        database = await get_database()
        
        # Count total queries
        total = await database.queries.count_documents({})
        
        # Get paginated queries
        skip = (page - 1) * limit
        cursor = database.queries.find({}).skip(skip).limit(limit).sort("timestamp", -1)
        
        queries = []
        async for query in cursor:
            queries.append(QueryResponse(**query))
        
        return QueryHistory(
            queries=queries,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get query history")

@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(query_id: str):
    """Get specific query by ID"""
    
    try:
        database = await get_database()
        query = await database.queries.find_one({"_id": query_id})
        
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        
        return QueryResponse(**query)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get query: {e}")
        raise HTTPException(status_code=500, detail="Failed to get query")
