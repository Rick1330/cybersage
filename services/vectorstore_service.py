"""
Vector Store Service - Manages document embeddings and similarity search.

This service provides an abstraction layer over vector stores (FAISS/Pinecone)
for storing and querying document embeddings with support for metadata management,
batch processing, and caching.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
from datetime import datetime
import faiss
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.vectorstores.base import VectorStore

logger = logging.getLogger(__name__)

class VectorStoreError(Exception):
    """Base exception for vector store related errors."""
    pass

class VectorStoreService:
    def __init__(
        self,
        embedding_model: str = "text-embedding-ada-002",
        index_path: Optional[str] = None,
        distance_strategy: str = "cosine",  # or "l2" or "inner_product"
        cache_dir: Optional[str] = None
    ):
        """Initialize the vector store service.
        
        Args:
            embedding_model: Name of the embedding model to use
            index_path: Path to save/load the FAISS index
            distance_strategy: Distance metric for similarity search
            cache_dir: Directory for caching embeddings
        """
        try:
            self.embeddings = OpenAIEmbeddings(model=embedding_model)
            self.index_path = index_path
            self.distance_strategy = distance_strategy
            self.cache_dir = cache_dir
            self.vector_store: Optional[VectorStore] = None
            
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
                
        except Exception as e:
            logger.error(f"Failed to initialize vector store service: {str(e)}")
            raise VectorStoreError(f"Initialization failed: {str(e)}") from e

    async def initialize(self) -> None:
        """Initialize or load the vector store.
        
        Raises:
            VectorStoreError: If initialization fails
        """
        try:
            if self.index_path and os.path.exists(self.index_path):
                logger.info(f"Loading existing index from {self.index_path}")
                self.vector_store = FAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    normalize_L2=self.distance_strategy == "cosine"
                )
            else:
                logger.info("Creating new FAISS index")
                self.vector_store = FAISS(
                    embedding_function=self.embeddings,
                    index=None,
                    normalize_L2=self.distance_strategy == "cosine"
                )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise VectorStoreError(f"Vector store initialization failed: {str(e)}") from e

    async def _save_index(self) -> None:
        """Save the current index to disk if index_path is set."""
        if self.index_path:
            try:
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                self.vector_store.save_local(self.index_path)
                logger.info(f"Saved index to {self.index_path}")
            except Exception as e:
                logger.error(f"Failed to save index: {str(e)}")
                raise VectorStoreError(f"Index saving failed: {str(e)}") from e

    async def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Add texts to the vector store with batching support.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dicts
            batch_size: Size of batches for processing
            
        Returns:
            List of document IDs
            
        Raises:
            VectorStoreError: If adding texts fails
        """
        try:
            if not self.vector_store:
                await self.initialize()

            all_ids = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metadata = metadatas[i:i + batch_size] if metadatas else None
                
                # Add creation timestamp to metadata
                if batch_metadata:
                    for metadata in batch_metadata:
                        metadata["created_at"] = datetime.utcnow().isoformat()
                
                ids = await self.vector_store.aadd_texts(
                    texts=batch_texts,
                    metadatas=batch_metadata
                )
                all_ids.extend(ids)
                
                logger.info(f"Added batch of {len(batch_texts)} documents")
                
            await self._save_index()
            return all_ids
            
        except Exception as e:
            logger.error(f"Failed to add texts: {str(e)}")
            raise VectorStoreError(f"Adding texts failed: {str(e)}") from e

    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search with metadata filtering and scoring.
        
        Args:
            query: Search query string
            k: Number of results to return
            filter_metadata: Optional metadata filters
            score_threshold: Optional similarity score threshold
            
        Returns:
            List of (document, score) tuples
            
        Raises:
            VectorStoreError: If search fails
        """
        try:
            if not self.vector_store:
                await self.initialize()

            results = await self.vector_store.asimilarity_search_with_score(
                query=query,
                k=k
            )
            
            # Filter by metadata if specified
            if filter_metadata:
                results = [
                    (doc, score) for doc, score in results
                    if all(
                        doc.metadata.get(key) == value
                        for key, value in filter_metadata.items()
                    )
                ]
            
            # Filter by score threshold if specified
            if score_threshold is not None:
                results = [
                    (doc, score) for doc, score in results
                    if score >= score_threshold
                ]
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            raise VectorStoreError(f"Similarity search failed: {str(e)}") from e

    async def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Delete documents by IDs or metadata filter.
        
        Args:
            ids: Optional list of document IDs to delete
            filter_metadata: Optional metadata filters
            
        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            if not self.vector_store:
                await self.initialize()

            if ids:
                await self.vector_store.adelete(ids)
                logger.info(f"Deleted {len(ids)} documents by ID")
                
            if filter_metadata:
                # Get documents matching the filter
                matching_docs = []
                for doc in self.vector_store.docstore._dict.values():
                    if all(
                        doc.metadata.get(key) == value
                        for key, value in filter_metadata.items()
                    ):
                        matching_docs.append(doc.id)
                
                if matching_docs:
                    await self.vector_store.adelete(matching_docs)
                    logger.info(f"Deleted {len(matching_docs)} documents by metadata filter")
            
            await self._save_index()
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            raise VectorStoreError(f"Document deletion failed: {str(e)}") from e

    async def update_metadata(
        self,
        doc_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update metadata for a document.
        
        Args:
            doc_id: Document ID
            metadata: New metadata dictionary
            
        Raises:
            VectorStoreError: If update fails
        """
        try:
            if not self.vector_store:
                await self.initialize()

            if doc_id not in self.vector_store.docstore._dict:
                raise VectorStoreError(f"Document {doc_id} not found")
                
            doc = self.vector_store.docstore._dict[doc_id]
            doc.metadata.update(metadata)
            doc.metadata["updated_at"] = datetime.utcnow().isoformat()
            
            await self._save_index()
            logger.info(f"Updated metadata for document {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {str(e)}")
            raise VectorStoreError(f"Metadata update failed: {str(e)}") from e

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index.
        
        Returns:
            Dictionary containing index statistics
        """
        if not self.vector_store:
            return {"status": "not_initialized"}
            
        try:
            index = self.vector_store.index
            return {
                "status": "active",
                "total_vectors": index.ntotal,
                "dimension": index.d,
                "index_type": type(index).__name__,
                "distance_strategy": self.distance_strategy,
                "document_count": len(self.vector_store.docstore._dict)
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {"status": "error", "message": str(e)}
