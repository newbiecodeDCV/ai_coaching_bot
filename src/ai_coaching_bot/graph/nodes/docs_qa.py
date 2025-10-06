"""
Docs QA node - Hỏi đáp trên tài liệu với RAG.
"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from ...config import settings
from ...database.base import get_engine, get_session_maker
from ...rag.service import RAGService
from ..prompts import DOCS_QA_PROMPT
from ..state import GraphState


def docs_qa_node(state: GraphState) -> Dict[str, Any]:
    """
    Trả lời câu hỏi dựa trên tài liệu (RAG).
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với answer và citations
    """
    try:
        message = state.get("message", "")
        
        # Setup DB
        engine = get_engine(settings.database_url)
        SessionLocal = get_session_maker(engine)
        session = SessionLocal()
        
        try:
            # RAG query
            rag_service = RAGService(session)
            results = rag_service.query_documents(message, top_k=5)
            
            if not results:
                return {
                    **state,
                    "docs_results": [],
                    "answer": "Xin lỗi, tôi không tìm thấy tài liệu liên quan đến câu hỏi của bạn. Bạn có thể:\n- Thử câu hỏi khác\n- Upload tài liệu mới\n- Hỏi về các chủ đề khác",
                    "citations": []
                }
            
            # Format context
            context_parts = []
            for i, r in enumerate(results, 1):
                context_parts.append(f"[{i}] {r['citation']}\n{r['text']}\n")
            context = "\n".join(context_parts)
            
            # LLM synthesis
            llm = ChatOpenAI(
                model=settings.model_name,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                temperature=settings.temperature
            )
            
            prompt = DOCS_QA_PROMPT.format(
                context=context,
                question=message
            )
            
            response = llm.invoke(prompt)
            content = response.content.strip()
            
            # Parse JSON
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            result = json.loads(content)
            
            return {
                **state,
                "docs_results": results,
                "answer": result.get("answer", "Không thể tạo câu trả lời"),
                "citations": result.get("citations", [])
            }
            
        finally:
            session.close()
            
    except Exception as e:
        return {
            **state,
            "docs_results": [],
            "answer": f"Xin lỗi, có lỗi khi tra cứu tài liệu: {str(e)}",
            "citations": [],
            "error": str(e)
        }
