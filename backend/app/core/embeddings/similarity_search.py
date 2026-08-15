"""Similarity Search Service."""
from backend.app.db.schemas import SimilaritySearchResponse, SimilarityMatch
from backend.app.core.embeddings.embedding_generator import get_embedding_generator
from backend.app.core.embeddings.vector_store import get_vector_store

class SimilaritySearchService:
    def __init__(self):
        self.generator = get_embedding_generator()
        self.store = get_vector_store()
        
    def search(self, query_text: str, top_k: int, filter_source: str | None, 
               filter_year_from: int | None, filter_year_to: int | None, 
               filter_section: str | None) -> SimilaritySearchResponse:
               
        embeddings = self.generator.embed_texts([query_text])
        if not embeddings:
            return SimilaritySearchResponse(status="error", count=0, results=[])
            
        query_emb = embeddings[0]
        
        # Build Where filter
        conditions = []
        if filter_source:
            conditions.append({"source": filter_source})
        if filter_section:
            conditions.append({"section": filter_section})
        if filter_year_from is not None:
            conditions.append({"year": {"$gte": filter_year_from}})
        if filter_year_to is not None:
            conditions.append({"year": {"$lte": filter_year_to}})
            
        where = None
        if len(conditions) == 1:
            where = conditions[0]
        elif len(conditions) > 1:
            where = {"$and": conditions}
            
        raw = self.store.query(query_embedding=query_emb, top_k=top_k, where=where)
        
        # Chroma returns lists of lists since it supports batch queries. We passed 1 query.
        matches = []
        if raw and raw.get("ids") and raw["ids"][0]:
            ids = raw["ids"][0]
            distances = raw["distances"][0]
            metadatas = raw["metadatas"][0]
            documents = raw["documents"][0]
            
            for i in range(len(ids)):
                dist = float(distances[i])
                score = max(0.0, min(1.0, 1.0 - dist))
                
                meta = metadatas[i] or {}
                doc = documents[i] or ""
                preview = doc[:240] + "..." if len(doc) > 240 else doc
                
                match = SimilarityMatch(
                    id=ids[i],
                    paper_id=meta.get("paper_id", "unknown"),
                    section=meta.get("section", "unknown"),
                    score=round(score, 4),
                    distance=round(dist, 4),
                    preview=preview,
                    metadata=meta
                )
                matches.append(match)
                
        return SimilaritySearchResponse(
            status="ok",
            count=len(matches),
            results=matches
        )
