"""
Users router - User profile và overview endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from ...database.models import User, Assessment, Enrollment, Skill, Course, LearningPlan
from ..schemas import UserProfile, UserOverview, ErrorResponse
from ..dependencies import get_db, validate_user_id

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}",
           response_model=UserProfile,
           summary="Lấy thông tin profile của user",
           description="Endpoint để lấy thông tin cơ bản của user theo user_id.")
async def get_user_profile(
    user_id: str = Path(..., description="ID của user"),
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    Lấy thông tin profile của user.
    
    Args:
        user_id: ID của user
        db: Database session
        
    Returns:
        UserProfile với thông tin cơ bản
        
    Raises:
        HTTPException: 404 nếu user không tồn tại
    """
    try:
        # Validate user_id
        user_id = validate_user_id(user_id)
        
        # Query user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} không tồn tại"
            )
        
        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            level=user.level,
            time_budget_per_week=user.time_budget_per_week,
            created_at=user.created_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/overview",
           response_model=UserOverview,
           summary="Lấy tổng quan chi tiết về user",
           description="Endpoint để lấy thông tin tổng quan về user bao gồm assessments, enrollments, gaps.")
async def get_user_overview(
    user_id: str = Path(..., description="ID của user"),
    db: Session = Depends(get_db)
) -> UserOverview:
    """
    Lấy thông tin tổng quan chi tiết về user.
    
    Args:
        user_id: ID của user
        db: Database session
        
    Returns:
        UserOverview với tất cả thông tin chi tiết
        
    Raises:
        HTTPException: 404 nếu user không tồn tại
    """
    try:
        # Validate user_id
        user_id = validate_user_id(user_id)
        
        # Query user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} không tồn tại"
            )
        
        # Get assessments với skill names
        assessments_query = db.query(Assessment, Skill).join(
            Skill, Assessment.skill_id == Skill.id
        ).filter(Assessment.user_id == user_id)
        
        assessments = []
        for assessment, skill in assessments_query.all():
            assessments.append({
                "skill_id": skill.id,
                "skill_name": skill.name,
                "score": assessment.score,
                "level": assessment.level,
                "taken_at": assessment.taken_at.isoformat()
            })
        
        # Get enrollments với course info
        enrollments_query = db.query(Enrollment, Course).join(
            Course, Enrollment.course_id == Course.id
        ).filter(Enrollment.user_id == user_id)
        
        enrollments = []
        total_study_hours = 0
        active_courses = 0
        completed_courses = 0
        
        for enrollment, course in enrollments_query.all():
            enrollment_data = {
                "course_id": course.id,
                "course_title": course.title,
                "course_provider": course.provider,
                "status": enrollment.status,
                "progress_percent": enrollment.progress_percent,
                "started_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
                "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                "duration_hours": course.duration_hours
            }
            
            enrollments.append(enrollment_data)
            
            # Calculate stats
            if enrollment.status == "in_progress":
                active_courses += 1
            elif enrollment.status == "completed":
                completed_courses += 1
            
            if enrollment.status in ["completed", "in_progress"]:
                study_hours = (enrollment.progress_percent / 100) * course.duration_hours
                total_study_hours += study_hours
        
        # Calculate gaps (simplified for API)
        role_expectations = {
            "Data Analyst": {"sql": 4, "python": 3, "data_analysis": 4, "excel": 3},
            "Junior Developer": {"python": 3, "git": 3, "sql": 2},
            "Business Analyst": {"data_analysis": 3, "excel": 4, "communication": 4}
        }
        
        expected_levels = role_expectations.get(user.role, {})
        current_levels = {a["skill_id"]: a["level"] for a in assessments}
        
        gaps = []
        for skill_id, expected_level in expected_levels.items():
            current_level = current_levels.get(skill_id, 0)
            if current_level < expected_level:
                gap = {
                    "skill_id": skill_id,
                    "expected_level": expected_level,
                    "current_level": current_level,
                    "gap": expected_level - current_level
                }
                gaps.append(gap)
        
        # Get active learning plan
        active_plan = db.query(LearningPlan).filter(
            LearningPlan.user_id == user_id,
            LearningPlan.status == "active"
        ).first()
        
        active_plan_data = None
        if active_plan:
            active_plan_data = {
                "id": active_plan.id,
                "title": active_plan.title,
                "created_at": active_plan.created_at.isoformat(),
                "updated_at": active_plan.updated_at.isoformat()
            }
        
        # Create profile
        profile = UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            level=user.level,
            time_budget_per_week=user.time_budget_per_week,
            created_at=user.created_at
        )
        
        # Stats
        stats = {
            "total_assessments": len(assessments),
            "average_score": round(sum(a["score"] for a in assessments) / len(assessments), 1) if assessments else 0,
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            "total_study_hours": round(total_study_hours, 1),
            "total_gaps": len(gaps)
        }
        
        return UserOverview(
            profile=profile,
            assessments=assessments,
            enrollments=enrollments,
            gaps=gaps,
            active_plan=active_plan_data,
            stats=stats
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/assessments",
           response_model=List[dict],
           summary="Lấy danh sách assessments của user",
           description="Endpoint để lấy tất cả assessments của user.")
async def get_user_assessments(
    user_id: str = Path(..., description="ID của user"),
    recent_days: int = 90,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Lấy danh sách assessments của user.
    
    Args:
        user_id: ID của user
        recent_days: Lấy assessments trong N ngày gần nhất (default: 90)
        db: Database session
        
    Returns:
        List assessments với skill info
    """
    try:
        # Validate user_id
        user_id = validate_user_id(user_id)
        
        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} không tồn tại")
        
        # Get recent assessments
        since_date = datetime.utcnow() - timedelta(days=recent_days)
        assessments_query = db.query(Assessment, Skill).join(
            Skill, Assessment.skill_id == Skill.id
        ).filter(
            Assessment.user_id == user_id,
            Assessment.taken_at >= since_date
        ).order_by(Assessment.taken_at.desc())
        
        assessments = []
        for assessment, skill in assessments_query.all():
            assessments.append({
                "id": assessment.id,
                "skill_id": skill.id,
                "skill_name": skill.name,
                "score": assessment.score,
                "level": assessment.level,
                "taken_at": assessment.taken_at.isoformat()
            })
        
        return assessments
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/enrollments",
           response_model=List[dict],
           summary="Lấy danh sách enrollments của user",
           description="Endpoint để lấy tất cả enrollments của user.")
async def get_user_enrollments(
    user_id: str = Path(..., description="ID của user"),
    status: str = None,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Lấy danh sách enrollments của user.
    
    Args:
        user_id: ID của user
        status: Filter theo status (enrolled, in_progress, completed)
        db: Database session
        
    Returns:
        List enrollments với course info
    """
    try:
        # Validate user_id
        user_id = validate_user_id(user_id)
        
        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} không tồn tại")
        
        # Build query
        query = db.query(Enrollment, Course).join(
            Course, Enrollment.course_id == Course.id
        ).filter(Enrollment.user_id == user_id)
        
        if status:
            query = query.filter(Enrollment.status == status)
        
        query = query.order_by(Enrollment.started_at.desc())
        
        enrollments = []
        for enrollment, course in query.all():
            enrollments.append({
                "id": enrollment.id,
                "course_id": course.id,
                "course_title": course.title,
                "course_provider": course.provider,
                "course_url": course.url,
                "status": enrollment.status,
                "progress_percent": enrollment.progress_percent,
                "started_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
                "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                "duration_hours": course.duration_hours
            })
        
        return enrollments
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))