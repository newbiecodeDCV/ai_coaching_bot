"""
Document parser cho PDF và Markdown files.
"""
from pathlib import Path
from typing import List, Dict
import pdfplumber


class DocumentParser:
    """Parser cho các loại tài liệu."""
    
    @staticmethod
    def parse_pdf(file_path: str) -> List[Dict]:
        """
        Parse PDF file thành text và metadata.
        
        Args:
            file_path: Đường dẫn đến PDF file
            
        Returns:
            List of dicts với {text, page, metadata}
        """
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({
                        "text": text.strip(),
                        "page": i,
                        "metadata": {
                            "source": Path(file_path).name,
                            "page_count": len(pdf.pages)
                        }
                    })
        return pages
    
    @staticmethod
    def parse_markdown(file_path: str) -> Dict:
        """
        Parse Markdown file.
        
        Args:
            file_path: Đường dẫn đến MD file
            
        Returns:
            Dict với {text, metadata}
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return {
            "text": text.strip(),
            "page": None,
            "metadata": {
                "source": Path(file_path).name
            }
        }
    
    @staticmethod
    def parse(file_path: str) -> List[Dict]:
        """
        Parse file dựa vào extension.
        
        Args:
            file_path: Đường dẫn file
            
        Returns:
            List of page dicts
        """
        path = Path(file_path)
        
        if path.suffix.lower() == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        elif path.suffix.lower() in ['.md', '.markdown']:
            return [DocumentParser.parse_markdown(file_path)]
        elif path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return [{
                "text": text.strip(),
                "page": None,
                "metadata": {"source": path.name}
            }]
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
