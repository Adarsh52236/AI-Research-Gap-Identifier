import json
from sqlalchemy import select, and_, exists
from backend.app.db.session import SessionLocal
from backend.app.db.models import PaperSectionVector
from backend.app.core.embeddings.vector_store import VectorStore
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class PgVectorStore(VectorStore):
    def upsert_texts(self, items: list[dict]):
        if not items:
            return
            
        # Optional: could use PostgreSQL INSERT ON CONFLICT DO UPDATE for true upsert,
        # but for simplicity, we can query existing IDs and update, or delete then insert.
        db = SessionLocal()
        try:
            for item in items:
                row = db.query(PaperSectionVector).filter(PaperSectionVector.id == item["id"]).first()
                if not row:
                    row = PaperSectionVector(id=item["id"])
                    db.add(row)
                    
                row.text = item.get("text", "")
                row.embedding = item["embedding"]
                row.metadata_json = json.dumps(item["metadata"])
                
            db.commit()
        except Exception as e:
            logger.error(f"Error upserting into PgVectorStore: {e}")
            db.rollback()
        finally:
            db.close()

    def query(self, query_embedding: list[float], top_k: int, where: dict | None = None) -> dict:
        """
        Executes an L2 or Cosine distance search using pgvector.
        We emulate the Chroma dictionary response format.
        """
        db = SessionLocal()
        try:
            stmt = select(PaperSectionVector)
            
            # If where clause exists, parse it. In Chroma, 'where' is usually simple eq checks like {"paper_id": "xyz"}
            # We must apply this via JSON casting in SQLAlchemy, or string matching.
            if where:
                for k, v in where.items():
                    if k == "paper_id":
                        # The simple hacky way: check if paper_id string is in metadata_json
                        # A better way would be using JSON operators, but SQLite compatibility for tests might break.
                        # Since pgvector implies Postgres, we could use Postgres JSON operators.
                        # But to keep it simple and robust, we can just do a LIKE.
                        stmt = stmt.where(PaperSectionVector.metadata_json.like(f'%"{k}": "{v}"%'))
                    else:
                        stmt = stmt.where(PaperSectionVector.metadata_json.like(f'%"{k}": "{v}"%'))

            # Format to match Chroma
            ids = []
            distances = []
            documents = []
            metadatas = []
                
            # Query with distance:
            stmt = select(
                PaperSectionVector,
                PaperSectionVector.embedding.cosine_distance(query_embedding).label("distance")
            )
            if where:
                for k, v in where.items():
                    stmt = stmt.where(PaperSectionVector.metadata_json.like(f'%"{k}": "{v}"%'))
                    
            stmt = stmt.order_by(PaperSectionVector.embedding.cosine_distance(query_embedding)).limit(top_k)
            
            rows = db.execute(stmt).all()
            
            for row, dist in rows:
                ids.append(row.id)
                distances.append(float(dist))
                documents.append(row.text)
                try:
                    metadatas.append(json.loads(row.metadata_json))
                except:
                    metadatas.append({})
            
            return {
                "ids": [ids],
                "distances": [distances],
                "documents": [documents],
                "metadatas": [metadatas]
            }
        except Exception as e:
            logger.error(f"Error querying PgVectorStore: {e}")
            return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}
        finally:
            db.close()

    def exists(self, ids: list[str]) -> list[bool]:
        if not ids:
            return []
            
        db = SessionLocal()
        try:
            stmt = select(PaperSectionVector.id).where(PaperSectionVector.id.in_(ids))
            existing_ids = set(db.execute(stmt).scalars().all())
            return [i in existing_ids for i in ids]
        except Exception as e:
            logger.error(f"Error checking exists in PgVectorStore: {e}")
            return [False] * len(ids)
        finally:
            db.close()
