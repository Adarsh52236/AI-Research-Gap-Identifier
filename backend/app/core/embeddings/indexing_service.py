"""Embedding Indexing Service."""
import json
import re
from pathlib import Path
from fastapi import HTTPException
from backend.app.config import settings
from backend.app.db.schemas import IndexEmbeddingsResponse
from backend.app.core.embeddings.embedding_generator import get_embedding_generator
from backend.app.core.embeddings.vector_store import get_vector_store
from backend.app.utils.file_utils import safe_resolve_under
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingIndexingService:
    def __init__(self):
        self.generator = get_embedding_generator()
        self.store = get_vector_store()
        
    def _is_high_quality(self, text: str) -> bool:
        if len(text) < 200:
            return False
            
        t_lower = text.strip().lower()
        if t_lower.startswith("table ") or t_lower.startswith("figure "):
            return False
            
        alphas = sum(c.isalpha() for c in text)
        if len(text) > 0 and (alphas / len(text)) < 0.5:
            return False
            
        return True

    def index_from_sections_json(self, sections_path: Path, paper_id: str, 
                                 source: str | None, year: int | None, title: str | None,
                                 sections_to_index: list[str], force_reindex: bool, save_text: bool) -> tuple[int, int]:
                                 
        if not sections_path.exists():
            return 0, 0
            
        with open(sections_path, "r", encoding="utf-8") as f:
            sections = json.load(f)
            
        items_to_embed = []
        skipped = 0
        
        for sec in sections_to_index:
            content = sections.get(sec) or sections.get(sec.upper())
            if not content:
                continue
                
            content = content[:settings.EMBEDDING_MAX_CHARS]
            
            if not self._is_high_quality(content):
                skipped += 1
                continue
                
            doc_id = f"{paper_id}:{sec.upper()}"
            items_to_embed.append({
                "id": doc_id,
                "text": content,
                "section": sec.upper()
            })
            
        if not items_to_embed:
            return 0, skipped
            
        if not force_reindex:
            # check exists
            ids_to_check = [item["id"] for item in items_to_embed]
            exists_flags = self.store.exists(ids_to_check)
            filtered = []
            for item, ex in zip(items_to_embed, exists_flags):
                if ex:
                    skipped += 1
                else:
                    filtered.append(item)
            items_to_embed = filtered
            
        if not items_to_embed:
            return 0, skipped
            
        texts = [item["text"] for item in items_to_embed]
        embeddings = self.generator.embed_texts(texts)
        
        upsert_items = []
        for item, emb in zip(items_to_embed, embeddings):
            upsert_items.append({
                "id": item["id"],
                "text": item["text"] if save_text else "",
                "embedding": emb,
                "metadata": {
                    "paper_id": paper_id,
                    "section": item["section"],
                    "source": source,
                    "year": year,
                    "title": title
                }
            })
            
        self.store.upsert_texts(upsert_items)
        return len(upsert_items), skipped

    def index_paper_ids(self, paper_ids: list[str] | None, processed_sections_paths: list[str] | None,
                        sections_to_index: list[str], force_reindex: bool, save_text: bool) -> IndexEmbeddingsResponse:
                        
        base_dir = Path(settings.STORAGE_DIR)
        tasks = []
        
        if paper_ids:
            for pid in paper_ids:
                try:
                    p = safe_resolve_under(base_dir, f"processed/{pid}/sections.json")
                    tasks.append((pid, p))
                except ValueError:
                    continue
                    
        if processed_sections_paths:
            for r_path in processed_sections_paths:
                try:
                    p = safe_resolve_under(base_dir, r_path)
                    pid = p.parent.name
                    tasks.append((pid, p))
                except ValueError:
                    continue
                    
        if not tasks:
            raise HTTPException(status_code=400, detail="No valid paths provided.")
            
        total_indexed = 0
        total_skipped = 0
        
        for pid, p in tasks:
            idx, skp = self.index_from_sections_json(
                sections_path=p,
                paper_id=pid,
                source=None,
                year=None,
                title=None,
                sections_to_index=sections_to_index,
                force_reindex=force_reindex,
                save_text=save_text
            )
            total_indexed += idx
            total_skipped += skp
            
        return IndexEmbeddingsResponse(
            status="indexed",
            indexed_count=total_indexed,
            skipped_count=total_skipped,
            collection=settings.CHROMA_COLLECTION_NAME
        )
