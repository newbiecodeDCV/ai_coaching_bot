"""
Text chunking cho RAG.
"""
from typing import List, Dict


class TextChunker:
    """Chunker để chia text thành chunks nhỏ hơn."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 150):
        """
        Khởi tạo chunker.
        
        Args:
            chunk_size: Kích thước mỗi chunk (ký tự)
            overlap: Độ trùng lặp giữa chunks (ký tự)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chia text thành chunks với overlap.
        
        Args:
            text: Text cần chia
            metadata: Metadata để gắn vào mỗi chunk
            
        Returns:
            List of chunk dicts {text, metadata, chunk_index}
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Tìm vị trí ngắt câu tự nhiên (dấu câu + space)
            if end < len(text):
                # Tìm điểm ngắt tốt nhất trong 100 ký tự cuối
                search_start = max(end - 100, start)
                for sep in ['. ', '.\n', '! ', '?\n', '\n\n']:
                    pos = text.rfind(sep, search_start, end)
                    if pos != -1:
                        end = pos + len(sep)
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_meta = metadata.copy() if metadata else {}
                chunk_meta['chunk_index'] = chunk_index
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_meta,
                    "chunk_index": chunk_index
                })
                chunk_index += 1
            
            start = end - self.overlap if end < len(text) else len(text)
        
        return chunks
    
    def chunk_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        Chunk multiple pages, giữ page metadata.
        
        Args:
            pages: List of page dicts từ parser
            
        Returns:
            List of chunk dicts
        """
        all_chunks = []
        global_chunk_index = 0
        
        for page_data in pages:
            text = page_data.get("text", "")
            page_num = page_data.get("page")
            metadata = page_data.get("metadata", {})
            
            if page_num:
                metadata["page"] = page_num
            
            chunks = self.chunk_text(text, metadata)
            
            # Update global chunk index
            for chunk in chunks:
                chunk["chunk_index"] = global_chunk_index
                global_chunk_index += 1
            
            all_chunks.extend(chunks)
        
        return all_chunks
