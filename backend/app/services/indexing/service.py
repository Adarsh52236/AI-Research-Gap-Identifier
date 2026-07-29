import hashlib
import time
from typing import List

from app.core.logging import logger
from app.services.ingestion.models import Paper
from app.services.preprocessing.pipeline import PaperPreprocessingPipeline
from app.services.embeddings.service import EmbeddingService
from app.services.vectorstore.service import VectorStoreService
from .models import IndexingResult
from .exceptions import IndexingError
from .metadata_mapper import PaperMetadataMapper

class IndexingService:
    """Orchestrates the preprocessing, embedding, and storage of papers."""
    
    def __init__(
        self,
        preprocessing_pipeline: PaperPreprocessingPipeline,
        embedding_service: EmbeddingService,
        vector_store_service: VectorStoreService
    ):
        """
        Initializes the IndexingService with its dependencies via dependency injection.
        """
        self.preprocessing_pipeline = preprocessing_pipeline
        self.embedding_service = embedding_service
        self.vector_store_service = vector_store_service

    def _generate_paper_id(self, paper: Paper) -> str:
        """
        Generates a deterministic ID for a paper based on its title and source.
        """
        unique_string = f"{paper.source}_{paper.title}".encode('utf-8')
        return hashlib.sha256(unique_string).hexdigest()

    def _store_embeddings(self, ids: List[str], embeddings: List[List[float]], metadatas: List[dict]) -> None:
        """
        Encapsulates the vector storage calls to prepare for future retry policies.
        """
        self.vector_store_service.add_embeddings(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def index_paper(self, paper: Paper) -> IndexingResult:
        """
        Indexes a single paper.
        """
        return self.index_papers([paper])

    def index_papers(self, papers: List[Paper]) -> IndexingResult:
        """
        Processes and indexes a batch of papers.
        Leverages batch embedding but falls back to ensure processing continues 
        for remaining papers if errors occur at individual boundaries.
        """
        total_start = time.perf_counter()
        logger.info(f"Indexing started for {len(papers)} papers.")
        
        indexed_ids = []
        failed_ids = []
        
        # 1. Preprocessing Stage
        preproc_start = time.perf_counter()
        valid_papers = []
        
        for paper in papers:
            paper_id = self._generate_paper_id(paper)
            try:
                processed_paper = self.preprocessing_pipeline.process(paper)
                valid_papers.append((paper_id, processed_paper))
            except Exception as e:
                logger.error(f"Preprocessing failed for paper '{paper.title}' (ID: {paper_id}): {e}")
                failed_ids.append(paper_id)
                
        preproc_duration = time.perf_counter() - preproc_start
        logger.info(f"Preprocessing duration: {preproc_duration:.4f}s")
        
        if not valid_papers:
            total_duration = time.perf_counter() - total_start
            logger.info(f"Total indexing duration: {total_duration:.4f}s")
            return IndexingResult(len(papers), len(indexed_ids), len(failed_ids), indexed_ids, failed_ids)

        # 2. Embedding Stage
        embed_start = time.perf_counter()
        embeddings_map = {}
        processed_only = [vp[1] for vp in valid_papers]
        
        try:
            # Batch embedding
            embedding_results = self.embedding_service.embed_papers(processed_only)
            for (paper_id, _), emb_result in zip(valid_papers, embedding_results):
                embeddings_map[paper_id] = emb_result
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            # If batch fails, fail all valid papers at this step
            for paper_id, _ in valid_papers:
                failed_ids.append(paper_id)
            valid_papers = []
            
        embed_duration = time.perf_counter() - embed_start
        logger.info(f"Embedding duration: {embed_duration:.4f}s")

        # 3. Storage Stage
        storage_start = time.perf_counter()
        
        for paper_id, processed_paper in valid_papers:
            try:
                metadata = PaperMetadataMapper.map_to_metadata(processed_paper)
                emb_vector = embeddings_map[paper_id].vector
                
                # Use encapsulated helper for storage
                self._store_embeddings(ids=[paper_id], embeddings=[emb_vector], metadatas=[metadata])
                
                indexed_ids.append(paper_id)
                logger.info(f"Paper indexed successfully. ID: {paper_id}, Title: '{processed_paper.title}'")
            except Exception as e:
                logger.error(f"Storage failed for paper ID: {paper_id}: {e}")
                failed_ids.append(paper_id)
                
        storage_duration = time.perf_counter() - storage_start
        logger.info(f"Storage duration: {storage_duration:.4f}s")

        # Total completion
        total_duration = time.perf_counter() - total_start
        logger.info(f"Total indexing duration: {total_duration:.4f}s")
        logger.info(f"Indexing completed. Indexed: {len(indexed_ids)}, Failed: {len(failed_ids)}")
        
        return IndexingResult(
            total_papers=len(papers),
            indexed_papers=len(indexed_ids),
            failed_papers=len(failed_ids),
            indexed_ids=indexed_ids,
            failed_ids=failed_ids
        )
