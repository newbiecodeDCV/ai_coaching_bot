"""
Router node - Phân loại intent của user message.
"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from ...config import settings
from ..prompts import ROUTER_PROMPT
from ..state import GraphState


def router_node(state: GraphState) -> Dict[str, Any]:
    """
    Phân loại intent của user message.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với mode được set
    """
    try:
        message = state.get("message", "")
        
        if not message:
            return {
                **state,
                "mode": "docs_qa",
                "error": "Message trống"
            }
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=0.3  # Lower temp cho classification
        )
        
        # Format prompt
        prompt = ROUTER_PROMPT.format(message=message)
        
        # Call LLM
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Parse JSON (remove markdown if exists)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        result = json.loads(content)
        
        # Validate mode
        valid_modes = ["coach_general", "coach_skill", "performance", "docs_qa"]
        mode = result.get("mode", "docs_qa")
        
        if mode not in valid_modes:
            mode = "docs_qa"
        
        return {
            **state,
            "mode": mode
        }
        
    except Exception as e:
        # Fallback to docs_qa on error
        return {
            **state,
            "mode": "docs_qa",
            "error": f"Router error: {str(e)}"
        }
