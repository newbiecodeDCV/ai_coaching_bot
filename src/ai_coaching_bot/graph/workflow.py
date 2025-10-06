"""
LangGraph workflow builder - Kết nối tất cả nodes thành workflow hoàn chỉnh.
"""
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import (
    router_node,
    fetch_user_data_node,
    skill_resolver_node,
    gap_analysis_node,
    course_selector_node,
    plan_builder_node,
    performance_analysis_node,
    docs_qa_node,
    summarizer_node,
)


def should_analyze_skill(state: GraphState) -> str:
    """
    Conditional edge: Có cần analyze skill cụ thể không?
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Next node name
    """
    mode = state.get("mode", "")
    
    if mode == "coach_skill":
        return "skill_resolver"
    elif mode in ["coach_general", "performance"]:
        return "gap_analysis"
    else:
        return "summarizer"


def should_build_plan(state: GraphState) -> str:
    """
    Conditional edge: Có cần build plan không?
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Next node name
    """
    mode = state.get("mode", "")
    gaps = state.get("gaps", [])
    
    if mode in ["coach_general", "coach_skill"] and gaps:
        return "course_selector"
    else:
        return "summarizer"


def should_continue_coaching(state: GraphState) -> str:
    """
    Conditional edge: Tiếp tục coaching workflow không?
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Next node name
    """
    recommendations = state.get("recommendations", [])
    
    if recommendations:
        return "plan_builder"
    else:
        return "summarizer"


def route_after_fetch(state: GraphState) -> str:
    """
    Conditional edge sau khi fetch user data.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Next node name
    """
    mode = state.get("mode", "")
    
    if mode == "performance":
        return "performance_analysis"
    elif mode == "coach_skill":
        return "skill_resolver"
    elif mode == "coach_general":
        return "gap_analysis"
    else:
        return "summarizer"


def build_coaching_workflow() -> StateGraph:
    """
    Xây dựng LangGraph workflow cho AI Coaching Bot.
    
    Returns:
        Compiled StateGraph workflow
    """
    # Tạo workflow
    workflow = StateGraph(GraphState)
    
    # Add tất cả nodes
    workflow.add_node("router", router_node)
    workflow.add_node("fetch_user_data", fetch_user_data_node)
    workflow.add_node("skill_resolver", skill_resolver_node)
    workflow.add_node("gap_analysis", gap_analysis_node)
    workflow.add_node("course_selector", course_selector_node)
    workflow.add_node("plan_builder", plan_builder_node)
    workflow.add_node("performance_analysis", performance_analysis_node)
    workflow.add_node("docs_qa", docs_qa_node)
    workflow.add_node("summarizer", summarizer_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Main routing sau router
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("mode", "docs_qa"),
        {
            "coach_general": "fetch_user_data",
            "coach_skill": "fetch_user_data", 
            "performance": "fetch_user_data",
            "docs_qa": "docs_qa"
        }
    )
    
    # Routing sau fetch_user_data
    workflow.add_conditional_edges(
        "fetch_user_data",
        route_after_fetch,
        {
            "performance_analysis": "performance_analysis",
            "skill_resolver": "skill_resolver",
            "gap_analysis": "gap_analysis",
            "summarizer": "summarizer"
        }
    )
    
    # Skill resolver (chỉ cho coach_skill)
    workflow.add_edge("skill_resolver", "gap_analysis")
    
    # Gap analysis → course selection
    workflow.add_conditional_edges(
        "gap_analysis",
        should_build_plan,
        {
            "course_selector": "course_selector",
            "summarizer": "summarizer"
        }
    )
    
    # Course selector → plan builder
    workflow.add_conditional_edges(
        "course_selector", 
        should_continue_coaching,
        {
            "plan_builder": "plan_builder",
            "summarizer": "summarizer"
        }
    )
    
    # All terminal nodes → summarizer
    workflow.add_edge("plan_builder", "summarizer")
    workflow.add_edge("performance_analysis", "summarizer") 
    workflow.add_edge("docs_qa", "summarizer")
    
    # Summarizer → END
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()


def execute_coaching_workflow(
    user_id: str,
    message: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute workflow với input parameters.
    
    Args:
        user_id: ID của user
        message: Message từ user
        **kwargs: Additional parameters
        
    Returns:
        Final state sau khi execute workflow
    """
    # Build workflow
    workflow = build_coaching_workflow()
    
    # Initial state
    initial_state = {
        "user_id": user_id,
        "message": message,
        "mode": "",
        "user_profile": None,
        "assessments": [],
        "enrollments": [],
        "skill_query": None,
        "target_level": None,
        "time_budget": None,
        "gaps": [],
        "recommendations": [],
        "plan": None,
        "docs_results": [],
        "answer": "",
        "citations": [],
        "error": None,
        **kwargs
    }
    
    try:
        # Execute workflow
        result = workflow.invoke(initial_state)
        
        # Extract key outputs
        return {
            "success": True,
            "mode": result.get("mode"),
            "answer": result.get("answer", "Không có phản hồi"),
            "citations": result.get("citations", []),
            "plan": result.get("plan"),
            "error": result.get("error"),
            "metadata": {
                "user_id": user_id,
                "has_user_profile": bool(result.get("user_profile")),
                "assessments_count": len(result.get("assessments", [])),
                "enrollments_count": len(result.get("enrollments", [])),
                "gaps_count": len(result.get("gaps", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "docs_results_count": len(result.get("docs_results", []))
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "mode": "error",
            "answer": f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn: {str(e)}",
            "citations": [],
            "plan": None,
            "error": str(e),
            "metadata": {
                "user_id": user_id,
                "has_user_profile": False,
                "assessments_count": 0,
                "enrollments_count": 0,
                "gaps_count": 0,
                "recommendations_count": 0,
                "docs_results_count": 0
            }
        }


# Quick test function
def test_workflow_simple():
    """
    Test function đơn giản để verify workflow.
    """
    try:
        # Test routing
        result = execute_coaching_workflow(
            user_id="user_001",
            message="Điểm SQL của tôi thế nào?"
        )
        
        print("✅ Workflow test passed")
        print(f"Mode: {result['mode']}")
        print(f"Success: {result['success']}")
        print(f"Answer length: {len(result['answer'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run quick test
    test_workflow_simple()