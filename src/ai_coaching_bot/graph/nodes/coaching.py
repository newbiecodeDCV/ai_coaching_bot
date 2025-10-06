"""
Coaching nodes - Các node cho coaching workflow (general + skill-specific).
"""
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from ...config import settings
from ...database.base import get_engine, get_session_maker
from ...database.models import (
    User, Skill, Assessment, Enrollment, Course, CourseSkill
)
from ..prompts import (
    SKILL_RESOLVER_PROMPT, GAP_ANALYSIS_PROMPT, PLAN_BUILDER_PROMPT,
    format_skills_for_prompt, format_assessments_for_prompt, format_courses_for_prompt
)
from ..state import GraphState


def fetch_user_data_node(state: GraphState) -> Dict[str, Any]:
    """
    Fetch user data từ database.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với user_profile, assessments, enrollments
    """
    try:
        user_id = state.get("user_id")
        
        if not user_id:
            return {
                **state,
                "user_profile": None,
                "assessments": [],
                "enrollments": [],
                "error": "user_id không được cung cấp"
            }
        
        # Setup DB
        engine = get_engine(settings.database_url)
        SessionLocal = get_session_maker(engine)
        session = SessionLocal()
        
        try:
            # Fetch user profile
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    **state,
                    "user_profile": None,
                    "assessments": [],
                    "enrollments": [],
                    "error": f"User {user_id} không tồn tại"
                }
            
            user_profile = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "level": user.level,
                "time_budget_per_week": user.time_budget_per_week,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            
            # Fetch recent assessments (30 ngày gần nhất)
            recent_date = datetime.utcnow() - timedelta(days=30)
            assessments_query = session.query(Assessment, Skill).join(
                Skill, Assessment.skill_id == Skill.id
            ).filter(
                Assessment.user_id == user_id,
                Assessment.taken_at >= recent_date
            ).order_by(Assessment.taken_at.desc())
            
            assessments = []
            for assessment, skill in assessments_query.all():
                assessments.append({
                    "skill_id": skill.id,
                    "skill_name": skill.name,
                    "score": assessment.score,
                    "level": assessment.level,
                    "taken_at": assessment.taken_at.isoformat()
                })
            
            # Fetch current enrollments
            enrollments_query = session.query(Enrollment, Course).join(
                Course, Enrollment.course_id == Course.id
            ).filter(
                Enrollment.user_id == user_id,
                Enrollment.status.in_(["enrolled", "in_progress"])
            ).order_by(Enrollment.started_at.desc())
            
            enrollments = []
            for enrollment, course in enrollments_query.all():
                enrollments.append({
                    "course_id": course.id,
                    "course_title": course.title,
                    "course_provider": course.provider,
                    "status": enrollment.status,
                    "progress_percent": enrollment.progress_percent,
                    "started_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
                    "duration_hours": course.duration_hours
                })
            
            return {
                **state,
                "user_profile": user_profile,
                "assessments": assessments,
                "enrollments": enrollments
            }
            
        finally:
            session.close()
            
    except Exception as e:
        return {
            **state,
            "user_profile": None,
            "assessments": [],
            "enrollments": [],
            "error": f"Fetch user data error: {str(e)}"
        }


def skill_resolver_node(state: GraphState) -> Dict[str, Any]:
    """
    Parse skill từ user message (chỉ cho coach_skill mode).
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với skill_query, target_level, time_budget
    """
    try:
        mode = state.get("mode")
        
        # Chỉ chạy cho coach_skill
        if mode != "coach_skill":
            return state
        
        message = state.get("message", "")
        
        # Setup DB để lấy skills list
        engine = get_engine(settings.database_url)
        SessionLocal = get_session_maker(engine)
        session = SessionLocal()
        
        try:
            # Get all skills
            skills = session.query(Skill).all()
            skills_list = format_skills_for_prompt(skills)
            
            # LLM call
            llm = ChatOpenAI(
                model=settings.model_name,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                temperature=0.3
            )
            
            prompt = SKILL_RESOLVER_PROMPT.format(
                skills_list=skills_list,
                message=message
            )
            
            response = llm.invoke(prompt)
            content = response.content.strip()
            
            # Parse JSON
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            result = json.loads(content)
            
            # Extract và validate
            skill_id = result.get("skill_id")
            target_level = result.get("target_level")
            time_budget = result.get("time_budget")
            
            # Fallback time_budget từ user profile
            if not time_budget:
                user_profile = state.get("user_profile", {})
                time_budget = user_profile.get("time_budget_per_week", 4)
            
            return {
                **state,
                "skill_query": skill_id,
                "target_level": target_level,
                "time_budget": time_budget
            }
            
        finally:
            session.close()
            
    except Exception as e:
        # Fallback: extract skill từ message bằng keyword matching
        message = state.get("message", "").lower()
        skill_keywords = {
            "sql": "sql",
            "python": "python", 
            "data analysis": "data_analysis",
            "machine learning": "ml_basics",
            "excel": "excel",
            "communication": "communication",
            "leadership": "leadership"
        }
        
        skill_found = None
        for keyword, skill_id in skill_keywords.items():
            if keyword in message:
                skill_found = skill_id
                break
        
        user_profile = state.get("user_profile", {})
        time_budget = user_profile.get("time_budget_per_week", 4)
        
        return {
            **state,
            "skill_query": skill_found,
            "target_level": None,
            "time_budget": time_budget,
            "error": f"Skill resolver error: {str(e)}"
        }


def gap_analysis_node(state: GraphState) -> Dict[str, Any]:
    """
    Phân tích gaps giữa current và expected levels.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với gaps analysis
    """
    try:
        user_profile = state.get("user_profile", {})
        assessments = state.get("assessments", [])
        role = user_profile.get("role", "Unknown")
        level = user_profile.get("level", 1)
        time_budget = state.get("time_budget", 4)
        
        # Expected levels dựa theo role (hardcoded for MVP)
        role_expectations = {
            "Data Analyst": {
                "sql": 4,
                "python": 3,
                "data_analysis": 4,
                "excel": 3,
                "statistics": 3,
                "visualization": 3
            },
            "Junior Developer": {
                "python": 3,
                "git": 3,
                "sql": 2,
                "communication": 3
            },
            "Business Analyst": {
                "data_analysis": 3,
                "excel": 4,
                "communication": 4,
                "sql": 2
            }
        }
        
        expected_levels = role_expectations.get(role, {})
        
        # Format data cho LLM
        assessments_text = format_assessments_for_prompt(assessments)
        expected_text = "\n".join([f"- {skill}: Level {level}" for skill, level in expected_levels.items()])
        
        # LLM analysis
        llm = ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=settings.temperature
        )
        
        prompt = GAP_ANALYSIS_PROMPT.format(
            role=role,
            level=level,
            assessments=assessments_text,
            expected_levels=expected_text,
            time_budget=time_budget
        )
        
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Parse JSON
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        result = json.loads(content)
        gaps = result.get("gaps", [])
        
        return {
            **state,
            "gaps": gaps
        }
        
    except Exception as e:
        # Fallback: simple gap analysis
        user_profile = state.get("user_profile", {})
        assessments = state.get("assessments", [])
        
        # Create basic gaps
        fallback_gaps = []
        
        if not assessments:
            # Nếu chưa có assessment, đề xuất basic skills
            fallback_gaps = [
                {
                    "skill_id": "sql",
                    "skill_name": "SQL",
                    "current_level": 0,
                    "expected_level": 3,
                    "gap": 3,
                    "priority": "high",
                    "reasoning": "Kỹ năng cơ bản cần thiết"
                }
            ]
        
        return {
            **state,
            "gaps": fallback_gaps,
            "error": f"Gap analysis error: {str(e)}"
        }


def course_selector_node(state: GraphState) -> Dict[str, Any]:
    """
    Chọn courses phù hợp với gaps.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với recommendations
    """
    try:
        gaps = state.get("gaps", [])
        time_budget = state.get("time_budget", 4)
        
        if not gaps:
            return {
                **state,
                "recommendations": []
            }
        
        # Setup DB
        engine = get_engine(settings.database_url)
        SessionLocal = get_session_maker(engine)
        session = SessionLocal()
        
        try:
            recommendations = []
            total_hours = 0
            max_hours_per_week = time_budget * 4  # 4 tuần buffer
            
            # Lặp qua gaps theo priority
            for gap in gaps[:3]:  # Limit 3 gaps để focused
                skill_id = gap.get("skill_id")
                current_level = gap.get("current_level", 1)
                
                # Query courses cho skill này
                courses_query = session.query(Course, CourseSkill).join(
                    CourseSkill, Course.id == CourseSkill.course_id
                ).filter(
                    CourseSkill.skill_id == skill_id,
                    CourseSkill.min_level <= current_level + 1,
                    Course.duration_hours <= max_hours_per_week - total_hours
                ).order_by(
                    Course.cost,  # Free courses first
                    Course.duration_hours
                )
                
                course_added = False
                for course, course_skill in courses_query.limit(2):  # Max 2 courses per skill
                    if total_hours + course.duration_hours <= max_hours_per_week:
                        recommendations.append({
                            "course_id": course.id,
                            "course_title": course.title,
                            "provider": course.provider,
                            "url": course.url,
                            "duration_hours": course.duration_hours,
                            "cost": course.cost,
                            "skill_id": skill_id,
                            "skill_name": gap.get("skill_name"),
                            "priority": gap.get("priority", "medium")
                        })
                        
                        total_hours += course.duration_hours
                        course_added = True
                
                if not course_added:
                    # Nếu không tìm được course, đề xuất self-study
                    recommendations.append({
                        "course_id": None,
                        "course_title": f"Self-study {gap.get('skill_name')}",
                        "provider": "Various",
                        "url": "#",
                        "duration_hours": 8,
                        "cost": 0,
                        "skill_id": skill_id,
                        "skill_name": gap.get("skill_name"),
                        "priority": gap.get("priority", "medium")
                    })
            
            return {
                **state,
                "recommendations": recommendations
            }
            
        finally:
            session.close()
            
    except Exception as e:
        return {
            **state,
            "recommendations": [],
            "error": f"Course selector error: {str(e)}"
        }


def plan_builder_node(state: GraphState) -> Dict[str, Any]:
    """
    Tạo learning plan từ recommendations.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với plan
    """
    try:
        gaps = state.get("gaps", [])
        recommendations = state.get("recommendations", [])
        time_budget = state.get("time_budget", 4)
        user_profile = state.get("user_profile", {})
        
        if not recommendations:
            return {
                **state,
                "plan": None,
                "answer": "Không tìm được khóa học phù hợp. Hãy thử với skill khác hoặc điều chỉnh yêu cầu."
            }
        
        # Format data cho LLM
        gaps_text = json.dumps(gaps, ensure_ascii=False, indent=2)
        courses_text = format_courses_for_prompt([
            {
                "id": r["course_id"],
                "title": r["course_title"],
                "duration_hours": r["duration_hours"],
                "cost": r["cost"],
                "provider": r["provider"]
            }
            for r in recommendations
        ])
        
        # Estimate duration (8-12 tuần cho basic plan)
        total_hours = sum(r["duration_hours"] for r in recommendations)
        estimated_weeks = max(8, int(total_hours / time_budget))
        
        # LLM planning
        llm = ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=settings.temperature
        )
        
        prompt = PLAN_BUILDER_PROMPT.format(
            time_budget=time_budget,
            duration=estimated_weeks,
            target=f"Improve {len(gaps)} skills for {user_profile.get('role', 'current role')}",
            gaps=gaps_text,
            courses=courses_text
        )
        
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Parse JSON
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        result = json.loads(content)
        
        # Add metadata
        plan = {
            **result,
            "created_at": datetime.utcnow().isoformat(),
            "user_id": user_profile.get("id"),
            "status": "draft"
        }
        
        return {
            **state,
            "plan": plan
        }
        
    except Exception as e:
        # Fallback: simple plan
        recommendations = state.get("recommendations", [])
        time_budget = state.get("time_budget", 4)
        
        if recommendations:
            simple_plan = {
                "title": f"Kế hoạch học {len(recommendations)} khóa học",
                "weekly_plan": [
                    {
                        "week": 1,
                        "focus_skill": recommendations[0]["skill_name"],
                        "courses": [recommendations[0]["course_title"]],
                        "total_hours": min(time_budget, recommendations[0]["duration_hours"]),
                        "objectives": [f"Bắt đầu {recommendations[0]['skill_name']}"],
                        "kpi": "Hoàn thành 25% khóa học"
                    }
                ],
                "summary": f"Kế hoạch cơ bản với {len(recommendations)} khóa học",
                "total_hours": sum(r["duration_hours"] for r in recommendations),
                "created_at": datetime.utcnow().isoformat(),
                "status": "draft"
            }
        else:
            simple_plan = None
        
        return {
            **state,
            "plan": simple_plan,
            "error": f"Plan builder error: {str(e)}"
        }