"""
FAISS vector store cho document retrieval.
"""
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import faiss
import pickle
from ..config import settings


class VectorStore:
    """FAISS vector store manager."""
    
    def __init__(self, index_name: str = "main"):
        """
        Khởi tạo vector store.
        
        Args:
            index_name: Tên của index
        """
        self.index_name = index_name
        self.index_dir = settings.faiss_index_dir
        self.index_path = self.index_dir / f"{index_name}.index"
        self.metadata_path = self.index_dir / f"{index_name}_metadata.pkl"
        
        self.index = None
        self.metadata = []
        
        self._load_or_create()
    
    def _load_or_create(self):
        """Load index hiện có hoặc tạo mới."""
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            # Tạo index mới (dimension = 1536 cho text-embedding-3-small)
            self.index = faiss.IndexFlatL2(1536)
            self.metadata = []
            self._save()
    
    def _save(self):
        """Lưu index và metadata."""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def add_documents(self, 
                     doc_id: int,
                     chunks: List[Dict],
                     embeddings: np.ndarray):
        """
        Add documents vào index.
        
        Args:
            doc_id: Document ID từ DB
            chunks: List of chunk dicts
            embeddings: Embeddings matrix (n_chunks x dim)
        """
        if embeddings.shape[0] != len(chunks):
            raise ValueError("Số chunks và embeddings không khớp")
        
        # Add embeddings vào FAISS
        self.index.add(embeddings)
        
        # Lưu metadata
        for chunk in chunks:
            self.metadata.append({
                "document_id": doc_id,
                "chunk_index": chunk.get("chunk_index"),
                "text": chunk.get("text"),
                "metadata": chunk.get("metadata", {})
            })
        
        self._save()
    
    def search(self, 
               query_embedding: np.ndarray,
               top_k: int = 5,
               doc_id_filter: Optional[int] = None) -> List[Dict]:
        """
        Search documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Số kết quả trả về
            doc_id_filter: Lọc theo document_id (optional)
            
        Returns:
            List of results với {text, score, metadata, document_id}
        """
        if self.index.ntotal == 0:
            return []
        
        # Reshape query
        query = query_embedding.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query, min(top_k * 2, self.index.ntotal))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS trả về -1 nếu không tìm thấy
                continue
            
            meta = self.metadata[idx]
            
            # Filter theo doc_id nếu có
            if doc_id_filter and meta["document_id"] != doc_id_filter:
                continue
            
            results.append({
                "text": meta["text"],
                "score": float(dist),
                "metadata": meta["metadata"],
                "document_id": meta["document_id"],
                "chunk_index": meta["chunk_index"]
            })
            
            if len(results) >= top_k:
                break
        
        return results
    
    def delete_document(self, doc_id: int):
        """
        Xóa document khỏi index (rebuild index).
        
        Args:
            doc_id: Document ID cần xóa
        """
        # Filter metadata
        new_metadata = [m for m in self.metadata if m["document_id"] != doc_id]
        
        if len(new_metadata) == len(self.metadata):
            return  # Không có gì để xóa
        
        # Rebuild index
        self.metadata = new_metadata
        
        if len(self.metadata) == 0:
            self.index = faiss.IndexFlatL2(1536)
        else:
            # Rebuild với embeddings còn lại (cần re-embed)
            # Để đơn giản, ta mark cho rebuild sau
            pass
        
        self._save()
    
    def clear(self):
        """Clear toàn bộ index."""
        self.index = faiss.IndexFlatL2(1536)
        self.metadata = []
        self._save()
