"""
RAG service orchestration.
"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .parser import DocumentParser
from .chunker import TextChunker
from .embedder import Embedder
from .vector_store import VectorStore
from ..database.models import Document, DocChunk


class RAGService:
    """Service tổng hợp cho RAG pipeline."""
    
    def __init__(self, db_session: Session):
        """
        Khởi tạo RAG service.
        
        Args:
            db_session: SQLAlchemy session
        """
        self.db = db_session
        self.parser = DocumentParser()
        self.chunker = TextChunker(chunk_size=1000, overlap=150)
        self.embedder = Embedder()
        self.vector_store = VectorStore()
    
    def upload_document(self, 
                       file_path: str, 
                       title: str,
                       skill_id: Optional[str] = None) -> Document:
        """
        Upload document vào DB (chưa ingest).
        
        Args:
            file_path: Đường dẫn file
            title: Tên tài liệu
            skill_id: Skill liên quan (optional)
            
        Returns:
            Document model
        """
        path = Path(file_path)
        
        # Xác định mime type
        mime_map = {
            '.pdf': 'application/pdf',
            '.md': 'text/markdown',
            '.txt': 'text/plain'
        }
        mime = mime_map.get(path.suffix.lower(), 'application/octet-stream')
        
        # Tạo document trong DB
        doc = Document(
            title=title,
            source_path=str(path),
            mime=mime,
            skill_id=skill_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        
        return doc
    
    def ingest_document(self, doc_id: int) -> int:
        """
        Ingest document: parse -> chunk -> embed -> index.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Số chunks đã tạo
        """
        # Lấy document từ DB
        doc = self.db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise ValueError(f"Document {doc_id} không tồn tại")
        
        if not Path(doc.source_path).exists():
            raise FileNotFoundError(f"File không tồn tại: {doc.source_path}")
        
        # 1. Parse
        pages = self.parser.parse(doc.source_path)
        
        # 2. Chunk
        chunks = self.chunker.chunk_pages(pages)
        
        if not chunks:
            raise ValueError("Không có chunks nào được tạo")
        
        # 3. Embed
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed_texts(texts, use_cache=True)
        
        # 4. Lưu chunks vào DB
        for chunk in chunks:
            doc_chunk = DocChunk(
                document_id=doc_id,
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                page=chunk["metadata"].get("page")
            )
            self.db.add(doc_chunk)
        
        self.db.commit()
        
        # 5. Index vào FAISS
        self.vector_store.add_documents(doc_id, chunks, embeddings)
        
        # 6. Update document
        doc.ingested_at = datetime.utcnow()
        self.db.commit()
        
        return len(chunks)
    
    def query_documents(self,
                       query: str,
                       top_k: int = 5,
                       skill_id: Optional[str] = None) -> List[Dict]:
        """
        Query documents với RAG.
        
        Args:
            query: Query string
            top_k: Số kết quả
            skill_id: Lọc theo skill (optional)
            
        Returns:
            List of results với citations
        """
        # Embed query
        query_embedding = self.embedder.embed_text(query, use_cache=False)
        
        # Search
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Enrich với DB info
        enriched_results = []
        for result in results:
            doc = self.db.query(Document).filter(
                Document.id == result["document_id"]
            ).first()
            
            if not doc:
                continue
            
            # Filter theo skill nếu có
            if skill_id and doc.skill_id != skill_id:
                continue
            
            enriched_results.append({
                "text": result["text"],
                "score": result["score"],
                "document_title": doc.title,
                "document_id": doc.id,
                "page": result["metadata"].get("page"),
                "source": result["metadata"].get("source"),
                "citation": self._format_citation(doc.title, result["metadata"].get("page"))
            })
        
        return enriched_results
    
    @staticmethod
    def _format_citation(title: str, page: Optional[int]) -> str:
        """
        Format citation string.
        
        Args:
            title: Document title
            page: Page number
            
        Returns:
            Citation string như [doc:title#page]
        """
        if page:
            return f"[doc:{title}#page{page}]"
        return f"[doc:{title}]"
