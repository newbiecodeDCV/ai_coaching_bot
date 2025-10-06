"""
Common nodes - Shared utilities.
"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from ...config import settings
from ..prompts import SUMMARIZER_PROMPT
from ..state import GraphState


def summarizer_node(state: GraphState) -> Dict[str, Any]:
    """
    Tổng hợp và format response cuối cùng.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với answer được format
    """
    try:
        # Nếu đã có answer (từ docs_qa), chỉ cần format lại
        if state.get("answer") and state.get("mode") == "docs_qa":
            return state
        
        # Collect data để summarize
        data = {
            "mode": state.get("mode"),
            "user_profile": state.get("user_profile"),
            "gaps": state.get("gaps", []),
            "recommendations": state.get("recommendations", []),
            "plan": state.get("plan"),
            "assessments": state.get("assessments", []),
            "enrollments": state.get("enrollments", [])
        }
        
        # LLM summarize
        llm = ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=settings.temperature
        )
        
        prompt = SUMMARIZER_PROMPT.format(data=json.dumps(data, ensure_ascii=False, indent=2))
        
        response = llm.invoke(prompt)
        answer = response.content.strip()
        
        # Remove markdown code blocks if present
        if answer.startswith("```"):
            lines = answer.split("\n")
            answer = "\n".join(lines[1:-1])
        
        return {
            **state,
            "answer": answer
        }
        
    except Exception as e:
        # Fallback: simple text response
        return {
            **state,
            "answer": f"Đã xử lý yêu cầu của bạn. Chi tiết: {state.get('mode')}",
            "error": f"Summarizer error: {str(e)}"
        }
