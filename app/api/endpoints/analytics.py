from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta

from app.models.analytics import AnalyticsResponse, DocumentAnalytics, QueryAnalytics
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics():
    """Get comprehensive system analytics"""
    
    try:
        database = await get_database()
        
        # Count documents and queries
        doc_count = await database.documents.count_documents({})
        query_count = await database.queries.count_documents({})
        
        # Get popular topics (based on document categories)
        popular_topics = await _get_popular_topics(database)
        
        # Get recent activity
        recent_activity = await _get_recent_activity(database)
        
        # Get performance metrics
        performance_metrics = await _get_performance_metrics(database)
        
        # Get usage statistics
        usage_statistics = await _get_usage_statistics(database)
        
        return AnalyticsResponse(
            total_documents=doc_count,
            total_queries=query_count,
            popular_topics=popular_topics,
            recent_activity=recent_activity,
            performance_metrics=performance_metrics,
            usage_statistics=usage_statistics
        )
        
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/documents", response_model=Dict[str, Any])
async def get_document_analytics():
    """Get document-specific analytics"""
    
    try:
        database = await get_database()
        
        # Get document analytics
        pipeline = [
            {
                "$group": {
                    "_id": "$content_type",
                    "count": {"$sum": 1},
                    "avg_chunk_count": {"$avg": "$chunk_count"},
                    "total_size": {"$sum": "$file_size"}
                }
            }
        ]
        
        doc_stats = []
        async for stat in database.documents.aggregate(pipeline):
            doc_stats.append(stat)
        
        return {
            "document_types": doc_stats,
            "total_documents": await database.documents.count_documents({}),
            "processing_status": await _get_processing_status(database)
        }
        
    except Exception as e:
        logger.error(f"Failed to get document analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document analytics")

@router.get("/queries", response_model=QueryAnalytics)
async def get_query_analytics():
    """Get query-specific analytics"""
    
    try:
        database = await get_database()
        
        # Calculate query analytics
        total_queries = await database.queries.count_documents({})
        
        # Average response time
        pipeline = [
            {"$group": {"_id": None, "avg_response_time": {"$avg": "$processing_time"}}}
        ]
        avg_time_result = await database.queries.aggregate(pipeline).to_list(1)
        avg_response_time = avg_time_result[0]["avg_response_time"] if avg_time_result else 0.0
        
        # Success rate (confidence > 0.5)
        high_confidence_queries = await database.queries.count_documents({"confidence": {"$gt": 0.5}})
        success_rate = (high_confidence_queries / total_queries * 100) if total_queries > 0 else 0.0
        
        # Popular questions
        popular_questions = await _get_popular_questions(database)
        
        # Query trends
        query_trends = await _get_query_trends(database)
        
        return QueryAnalytics(
            total_queries=total_queries,
            average_response_time=avg_response_time,
            success_rate=success_rate,
            popular_questions=popular_questions,
            query_trends=query_trends
        )
        
    except Exception as e:
        logger.error(f"Failed to get query analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get query analytics")

# Helper functions
async def _get_popular_topics(database) -> list:
    """Get popular topics based on document categories"""
    pipeline = [
        {"$unwind": "$metadata.tags"},
        {"$group": {"_id": "$metadata.tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    topics = []
    async for topic in database.documents.aggregate(pipeline):
        topics.append({"topic": topic["_id"], "count": topic["count"]})
    
    return topics

async def _get_recent_activity(database) -> list:
    """Get recent activity (queries and uploads)"""
    recent_queries = database.queries.find({}).sort("timestamp", -1).limit(5)
    recent_docs = database.documents.find({}).sort("upload_date", -1).limit(5)
    
    activity = []
    
    async for query in recent_queries:
        activity.append({
            "type": "query",
            "description": query["question"][:50] + "...",
            "timestamp": query["timestamp"]
        })
    
    async for doc in recent_docs:
        activity.append({
            "type": "upload",
            "description": f"Uploaded {doc['filename']}",
            "timestamp": doc["upload_date"]
        })
    
    # Sort by timestamp
    activity.sort(key=lambda x: x["timestamp"], reverse=True)
    return activity[:10]

async def _get_performance_metrics(database) -> dict:
    """Get system performance metrics"""
    # Average processing time for documents
    doc_pipeline = [
        {"$group": {"_id": None, "avg_processing_time": {"$avg": "$processing_time"}}}
    ]
    doc_result = await database.documents.aggregate(doc_pipeline).to_list(1)
    avg_doc_processing = doc_result[0]["avg_processing_time"] if doc_result else 0.0
    
    # Average query response time
    query_pipeline = [
        {"$group": {"_id": None, "avg_response_time": {"$avg": "$processing_time"}}}
    ]
    query_result = await database.queries.aggregate(query_pipeline).to_list(1)
    avg_query_response = query_result[0]["avg_response_time"] if query_result else 0.0
    
    return {
        "avg_document_processing_time": avg_doc_processing,
        "avg_query_response_time": avg_query_response,
        "system_uptime": "99.9%"  # Placeholder
    }

async def _get_usage_statistics(database) -> dict:
    """Get usage statistics"""
    now = datetime.utcnow()
    
    # Queries in last 24 hours
    queries_24h = await database.queries.count_documents({
        "timestamp": {"$gte": now - timedelta(hours=24)}
    })
    
    # Documents uploaded in last 24 hours
    docs_24h = await database.documents.count_documents({
        "upload_date": {"$gte": now - timedelta(hours=24)}
    })
    
    return {
        "queries_last_24h": queries_24h,
        "documents_last_24h": docs_24h,
        "peak_usage_hour": "14:00"  # Placeholder
    }

async def _get_processing_status(database) -> dict:
    """Get document processing status distribution"""
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    
    status_dist = {}
    async for status in database.documents.aggregate(pipeline):
        status_dist[status["_id"]] = status["count"]
    
    return status_dist

async def _get_popular_questions(database) -> list:
    """Get popular question patterns"""
    # This is a simplified version - in production you'd use NLP to group similar questions
    recent_queries = database.queries.find({}).sort("timestamp", -1).limit(50)
    
    questions = []
    async for query in recent_queries:
        questions.append({
            "question": query["question"][:100] + "...",
            "confidence": query["confidence"],
            "timestamp": query["timestamp"]
        })
    
    return questions[:10]

async def _get_query_trends(database) -> list:
    """Get query trends over time"""
    # Group queries by day for the last 7 days
    now = datetime.utcnow()
    
    trends = []
    for i in range(7):
        date = now - timedelta(days=i)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        count = await database.queries.count_documents({
            "timestamp": {"$gte": start_of_day, "$lt": end_of_day}
        })
        
        trends.append({
            "date": start_of_day.isoformat(),
            "query_count": count
        })
    
    return trends
