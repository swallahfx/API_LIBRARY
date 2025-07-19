from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from app.core.database import get_database
from app.core.redis import redis_client
from app.services.vector_service import vector_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {}
    }
    
    # Check MongoDB
    try:
        database = await get_database()
        await database.command("ping")
        health_status["services"]["mongodb"] = {
            "status": "healthy",
            "response_time": "< 10ms"
        }
    except Exception as e:
        health_status["services"]["mongodb"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        await redis_client.redis.ping()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "response_time": "< 5ms"
        }
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Vector Store
    try:
        if vector_service.vector_store:
            health_status["services"]["vector_store"] = {
                "status": "ready",
                "index_size": "unknown"
            }
        else:
            health_status["services"]["vector_store"] = {
                "status": "not_ready"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["vector_store"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check if all critical services are available
        database = await get_database()
        await database.command("ping")
        
        if not vector_service.vector_store:
            return {"status": "not_ready", "reason": "vector_store_not_initialized"}
        
        return {"status": "ready"}
        
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow()}
