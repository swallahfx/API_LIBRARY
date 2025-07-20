import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# from langchain_openai import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
# from langchain.schema import Document
from langchain_core.documents import Document


from app.core.config import settings
from app.core.database import get_database
from app.services.vector_service import vector_service
from app.models.query import QueryRequest, QueryResponse, SourceDocument
import logging

logger = logging.getLogger(__name__)

class QAService:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.3,
            model_name=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    async def answer_question(self, query_request: QueryRequest) -> QueryResponse:
        """Answer question using RAG (Retrieval-Augmented Generation)"""
        start_time = datetime.utcnow()
        query_id = str(uuid.uuid4())
        
        try:
            # Search for relevant documents
            docs_with_scores = vector_service.search_similar_with_scores(
                query_request.question, 
                k=query_request.max_results
            )
            
            if not docs_with_scores:
                # No relevant documents found
                return QueryResponse(
                    answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
                    confidence=0.0,
                    sources=[],
                    query_id=query_id,
                    processing_time=(datetime.utcnow() - start_time).total_seconds(),
                    model_used=settings.OPENAI_MODEL,
                    timestamp=datetime.utcnow()
                )
            
            # Create retriever from vector store
            retriever = vector_service.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": query_request.max_results}
            )
            
            # Create QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            
            # Get answer
            result = qa_chain({"query": query_request.question})
            
            # Process sources
            sources = []
            if query_request.include_sources:
                for i, (doc, score) in enumerate(docs_with_scores):
                    source = SourceDocument(
                        content=doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                        metadata=doc.metadata,
                        relevance_score=float(1.0 - score),  # Convert distance to similarity
                        document_id=doc.metadata.get("document_id", "unknown"),
                        chunk_index=doc.metadata.get("chunk_index", i)
                    )
                    sources.append(source)
            
            # Calculate confidence based on relevance scores and answer length
            avg_relevance = sum(s.relevance_score for s in sources) / len(sources) if sources else 0.0
            answer_length_factor = min(1.0, len(result["result"]) / 200)
            confidence = (avg_relevance + answer_length_factor) / 2
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create response
            response = QueryResponse(
                answer=result["result"],
                confidence=min(0.95, confidence),
                sources=sources,
                query_id=query_id,
                processing_time=processing_time,
                model_used=settings.OPENAI_MODEL,
                timestamp=datetime.utcnow()
            )
            
            # Save query to database
            await self._save_query_to_database(query_request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            
            # Return error response
            return QueryResponse(
                answer=f"I encountered an error while processing your question: {str(e)}",
                confidence=0.0,
                sources=[],
                query_id=query_id,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                model_used=settings.OPENAI_MODEL,
                timestamp=datetime.utcnow()
            )
    
    async def _save_query_to_database(self, query_request: QueryRequest, response: QueryResponse):
        """Save query and response to database for analytics"""
        try:
            database = await get_database()
            
            query_record = {
                "_id": response.query_id,
                "question": query_request.question,
                "answer": response.answer,
                "confidence": response.confidence,
                "sources_count": len(response.sources),
                "processing_time": response.processing_time,
                "model_used": response.model_used,
                "timestamp": response.timestamp,
                "context_filter": query_request.context_filter,
                "max_results": query_request.max_results,
                "temperature": query_request.temperature
            }
            
            await database.queries.insert_one(query_record)
            
        except Exception as e:
            logger.warning(f"Failed to save query to database: {e}")

# Global QA service instance
qa_service = QAService()
