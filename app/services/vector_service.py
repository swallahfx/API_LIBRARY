import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

from app.core.config import settings
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        self.vector_store: Optional[FAISS] = None
        self.vector_store_path = Path(settings.VECTOR_STORE_PATH)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
    
    async def initialize_vector_store(self):
        """Initialize or load existing vector store"""
        try:
            # Try to load existing vector store
            if (self.vector_store_path / "index.faiss").exists():
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path),
                    self.embeddings
                )
                logger.info("Loaded existing vector store")
            else:
                # Create new vector store from database
                await self.rebuild_vector_store()
                
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            # Create empty vector store as fallback
            self.vector_store = FAISS.from_texts(
                texts=[""],
                embedding=self.embeddings
            )
    
    async def rebuild_vector_store(self):
        """Rebuild vector store from database"""
        try:
            database = await get_database()
            
            # Get all chunks from knowledge base
            chunks_cursor = database.knowledge_base.find({})
            chunks = await chunks_cursor.to_list(length=None)
            
            if chunks:
                texts = [chunk["content"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]
                
                # Create FAISS vector store
                self.vector_store = FAISS.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas
                )
                
                # Save vector store
                self.vector_store.save_local(str(self.vector_store_path))
                
                logger.info(f"Vector store rebuilt with {len(chunks)} chunks")
            else:
                # Create empty vector store
                self.vector_store = FAISS.from_texts(
                    texts=[""],
                    embedding=self.embeddings
                )
                logger.info("Created empty vector store")
                
        except Exception as e:
            logger.error(f"Failed to rebuild vector store: {e}")
            raise
    
    async def add_document_chunks(self, document_id: str):
        """Add chunks from a specific document to vector store"""
        try:
            database = await get_database()
            
            # Get chunks for this document
            chunks_cursor = database.knowledge_base.find({"document_id": document_id})
            chunks = await chunks_cursor.to_list(length=None)
            
            if chunks and self.vector_store:
                texts = [chunk["content"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]
                
                # Add to existing vector store
                self.vector_store.add_texts(texts, metadatas)
                
                # Save updated vector store
                self.vector_store.save_local(str(self.vector_store_path))
                
                logger.info(f"Added {len(chunks)} chunks to vector store")
                
        except Exception as e:
            logger.error(f"Failed to add document chunks to vector store: {e}")
    
    async def remove_document_chunks(self, document_id: str):
        """Remove chunks from a specific document from vector store"""
        # For now, we'll rebuild the entire vector store
        # FAISS doesn't have built-in delete functionality
        await self.rebuild_vector_store()
        logger.info(f"Rebuilt vector store after removing document: {document_id}")
    
    def search_similar(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def search_similar_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """Search for similar documents with similarity scores"""
        if not self.vector_store:
            return []
        
        try:
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            return docs_with_scores
        except Exception as e:
            logger.error(f"Vector search with scores failed: {e}")
            return []

# Global vector service instance
vector_service = VectorService()
