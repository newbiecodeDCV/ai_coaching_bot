"""
Plans router - Learning plan management endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database.models import LearningPlan, User
from ..schemas import ErrorResponse
from ..dependencies import get_db, validate_user_id
from datetime import datetime
import uuid

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/user/{user_id}",
           response_model=List[dict],
           summary="Lấy learning plans của user",
           description="Endpoint để lấy tất cả learning plans của user.")
async def get_user_plans(
    user_id: str = Path(..., description="ID của user"),
    status: Optional[str] = Query(None, description="Filter theo status (active, completed, paused)"),
    limit: int = Query(50, ge=1, le=100, description="Giới hạn số kết quả"),
    offset: int = Query(0, ge=0, description="Offset cho pagination"),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Lấy learning plans của user.
    
    Args:
        user_id: ID của user
        status: Filter theo status
        limit: Giới hạn số kết quả
        offset: Offset cho pagination
        db: Database session
        
    Returns:
        List learning plans
    """
    try:
        # Validate user_id
        user_id = validate_user_id(user_id)
        
        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} không tồn tại")
        
        # Build query
        query = db.query(LearningPlan).filter(LearningPlan.user_id == user_id)
        
        if status:
            query = query.filter(LearningPlan.status == status)
        
        query = query.offset(offset).limit(limit).order_by(LearningPlan.created_at.desc())
        
        plans = query.all()
        
        result = []
        for plan in plans:
            plan_data = {
                "id": plan.id,
                "title": plan.title,
                "description": plan.description,
                "status": plan.status,
                "plan_data": plan.plan_data,
                "total_hours": plan.total_hours,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat()
            }
            result.append(plan_data)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}",
           response_model=dict,
           summary="Lấy chi tiết learning plan",
           description="Endpoint để lấy thông tin chi tiết của learning plan.")
async def get_plan_detail(
    plan_id: str = Path(..., description="ID của plan"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Lấy chi tiết learning plan.
    
    Args:
        plan_id: ID của plan
        db: Database session
        
    Returns:
        Dict với thông tin chi tiết
        
    Raises:
        HTTPException: 404 nếu plan không tồn tại
    """
    try:
        plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Learning plan {plan_id} không tồn tại"
            )
        
        # Get user info
        user = db.query(User).filter(User.id == plan.user_id).first()
        
        return {
            "id": plan.id,
            "title": plan.title,
            "description": plan.description,
            "status": plan.status,
            "plan_data": plan.plan_data,
            "total_hours": plan.total_hours,
            "user": {
                "id": user.id,
                "name": user.name,
                "role": user.role
            } if user else None,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/{user_id}",
            response_model=dict,
            summary="Tạo learning plan mới",
            description="Endpoint để tạo learning plan mới cho user.")
async def create_plan(
    user_id: str = Path(..., description="ID của user"),
    plan_request: dict = ...,
    db: Session = Depends(get_db)
) -> dict:
    """
    Tạo learning plan mới.
    
    Args:
        user_id: ID của user
        plan_request: Dict chứa title, description, plan_data
        db: Database session
        
    Returns:
        Dict với thông tin plan mới
        
    Raises:
        HTTPException: 400 cho dữ liệu không hợp lệ, 404 nếu user không tồn tại
    """
    try:
        # Validate user_id
        user_id = validate_user_id(user_id)
        
        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} không tồn tại")
        
        # Validate required fields
        if not plan_request.get("title"):
            raise HTTPException(status_code=400, detail="Title là bắt buộc")
        
        if not plan_request.get("plan_data"):
            raise HTTPException(status_code=400, detail="Plan data là bắt buộc")
        
        # Calculate total hours from plan_data
        total_hours = 0
        plan_data = plan_request.get("plan_data", {})
        
        if isinstance(plan_data, dict) and "courses" in plan_data:
            for course in plan_data["courses"]:
                if isinstance(course, dict) and "duration_hours" in course:
                    total_hours += course["duration_hours"]
        
        # Create new plan
        new_plan = LearningPlan(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=plan_request["title"],
            description=plan_request.get("description", ""),
            status="active",
            plan_data=plan_data,
            total_hours=total_hours,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        
        return {
            "id": new_plan.id,
            "title": new_plan.title,
            "description": new_plan.description,
            "status": new_plan.status,
            "plan_data": new_plan.plan_data,
            "total_hours": new_plan.total_hours,
            "created_at": new_plan.created_at.isoformat(),
            "updated_at": new_plan.updated_at.isoformat(),
            "success": True,
            "message": "Learning plan được tạo thành công"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{plan_id}/status",
           response_model=dict,
           summary="Cập nhật status của plan",
           description="Endpoint để cập nhật status của learning plan.")
async def update_plan_status(
    plan_id: str = Path(..., description="ID của plan"),
    status_request: dict = ...,
    db: Session = Depends(get_db)
) -> dict:
    """
    Cập nhật status của learning plan.
    
    Args:
        plan_id: ID của plan
        status_request: Dict chứa new_status
        db: Database session
        
    Returns:
        Dict với kết quả update
        
    Raises:
        HTTPException: 400 cho status không hợp lệ, 404 nếu plan không tồn tại
    """
    try:
        # Find plan
        plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Learning plan {plan_id} không tồn tại"
            )
        
        # Validate status
        new_status = status_request.get("new_status")
        valid_statuses = ["active", "completed", "paused"]
        
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Status không hợp lệ. Chỉ chấp nhận: {', '.join(valid_statuses)}"
            )
        
        # Update status
        old_status = plan.status
        plan.status = new_status
        plan.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "plan_id": plan_id,
            "old_status": old_status,
            "new_status": new_status,
            "updated_at": plan.updated_at.isoformat(),
            "success": True,
            "message": f"Status của plan được cập nhật từ {old_status} thành {new_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{plan_id}",
              response_model=dict,
              summary="Xóa learning plan",
              description="Endpoint để xóa learning plan.")
async def delete_plan(
    plan_id: str = Path(..., description="ID của plan cần xóa"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Xóa learning plan.
    
    Args:
        plan_id: ID của plan cần xóa
        db: Database session
        
    Returns:
        Dict với thông báo thành công
        
    Raises:
        HTTPException: 404 nếu plan không tồn tại
    """
    try:
        # Find plan
        plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
        
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Learning plan {plan_id} không tồn tại"
            )
        
        # Delete plan
        db.delete(plan)
        db.commit()
        
        return {
            "plan_id": plan_id,
            "success": True,
            "message": f"Learning plan {plan_id} đã được xóa thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/",
           response_model=List[dict],
           summary="Lấy tất cả learning plans",
           description="Endpoint để lấy tất cả learning plans trong hệ thống (admin).")
async def list_all_plans(
    status: Optional[str] = Query(None, description="Filter theo status"),
    limit: int = Query(50, ge=1, le=100, description="Giới hạn số kết quả"),
    offset: int = Query(0, ge=0, description="Offset cho pagination"),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Lấy tất cả learning plans (admin endpoint).
    
    Args:
        status: Filter theo status
        limit: Giới hạn số kết quả
        offset: Offset cho pagination
        db: Database session
        
    Returns:
        List tất cả learning plans
    """
    try:
        # Build query
        query = db.query(LearningPlan, User).join(User, LearningPlan.user_id == User.id)
        
        if status:
            query = query.filter(LearningPlan.status == status)
        
        query = query.offset(offset).limit(limit).order_by(LearningPlan.created_at.desc())
        
        results = query.all()
        
        plans = []
        for plan, user in results:
            plan_data = {
                "id": plan.id,
                "title": plan.title,
                "description": plan.description,
                "status": plan.status,
                "total_hours": plan.total_hours,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role
                },
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat()
            }
            plans.append(plan_data)
        
        return plans
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))