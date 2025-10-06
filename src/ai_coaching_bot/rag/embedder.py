"""
Embedding service sử dụng OpenAI API.
"""
import hashlib
import pickle
from pathlib import Path
from typing import List
import numpy as np
from langchain_openai import OpenAIEmbeddings
from ..config import settings


class Embedder:
    """Service để tạo embeddings với caching."""
    
    def __init__(self):
        """Khởi tạo embedder với config từ settings."""
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url
        )
        self.cache_dir = settings.base_dir / "embedding_cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, text: str) -> str:
        """
        Tạo cache key từ text.
        
        Args:
            text: Text để hash
            
        Returns:
            Cache key (hex string)
        """
        return hashlib.md5(text.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def embed_text(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Embed single text.
        
        Args:
            text: Text để embed
            use_cache: Có sử dụng cache không
            
        Returns:
            Embedding vector (numpy array)
        """
        if use_cache:
            cache_key = self._get_cache_key(text)
            cache_path = self._get_cache_path(cache_key)
            
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
        
        # Tạo embedding mới
        embedding = self.embeddings.embed_query(text)
        embedding_array = np.array(embedding, dtype=np.float32)
        
        # Cache nếu cần
        if use_cache:
            cache_key = self._get_cache_key(text)
            cache_path = self._get_cache_path(cache_key)
            with open(cache_path, 'wb') as f:
                pickle.dump(embedding_array, f)
        
        return embedding_array
    
    def embed_texts(self, texts: List[str], use_cache: bool = True) -> np.ndarray:
        """
        Embed multiple texts.
        
        Args:
            texts: List of texts
            use_cache: Có sử dụng cache không
            
        Returns:
            Embeddings matrix (numpy array)
        """
        embeddings = []
        
        for text in texts:
            emb = self.embed_text(text, use_cache=use_cache)
            embeddings.append(emb)
        
        return np.array(embeddings, dtype=np.float32)
