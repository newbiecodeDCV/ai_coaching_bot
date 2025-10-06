"""
Chat router - Main chat endpoint sử dụng LangGraph workflow.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ...graph.workflow import execute_coaching_workflow
from ..schemas import ChatRequest, ChatResponse, ErrorResponse
from ..dependencies import get_db, validate_user_id, validate_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/execute", 
             response_model=ChatResponse,
             summary="Thực hiện chat với AI Coaching Bot",
             description="""
Endpoint chính để chat với AI Coaching Bot.

Bot sẽ tự động:
1. Phân loại intent (coaching/performance/docs-qa)
2. Thực hiện workflow tương ứng
3. Trả về câu trả lời với metadata

**Lưu ý**: Model được cố định ở server, client không thể chỉnh model.
""")
async def chat_execute(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Thực hiện chat với AI Coaching Bot.
    
    Args:
        request: Chat request với user_id và message
        db: Database session
        
    Returns:
        ChatResponse với answer và metadata
        
    Raises:
        HTTPException: Khi có lỗi validation hoặc processing
    """
    try:
        # Validate inputs
        user_id = validate_user_id(request.user_id)
        message = validate_message(request.message)
        
        # Execute LangGraph workflow
        result = execute_coaching_workflow(
            user_id=user_id,
            message=message,
            session_id=request.session_id
        )
        
        # Return response
        return ChatResponse(**result)
        
    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/route",
             response_model=dict,
             summary="Chỉ phân loại intent (không thực hiện workflow)",
             description="Endpoint để test intent classification mà không chạy full workflow.")
async def chat_route_only(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Chỉ phân loại intent mà không thực hiện workflow đầy đủ.
    
    Args:
        request: Chat request
        db: Database session
        
    Returns:
        Dict với mode và confidence
    """
    try:
        # Import router node
        from ...graph.nodes.router import router_node
        
        # Validate inputs
        user_id = validate_user_id(request.user_id)
        message = validate_message(request.message)
        
        # Run only router
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
            "error": None
        }
        
        result = router_node(initial_state)
        
        return {
            "user_id": user_id,
            "message": message,
            "mode": result.get("mode"),
            "error": result.get("error"),
            "route_only": True
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))