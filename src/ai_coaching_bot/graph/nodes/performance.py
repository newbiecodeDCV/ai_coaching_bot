"""
Performance analysis node - Phân tích hiệu suất học tập của user.
"""
import json
from typing import Dict, Any
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from ...config import settings
from ...database.base import get_engine, get_session_maker
from ...database.models import User, Assessment, Enrollment, Course, Skill
from ..prompts import PERFORMANCE_ANALYSIS_PROMPT, format_assessments_for_prompt
from ..state import GraphState


def performance_analysis_node(state: GraphState) -> Dict[str, Any]:
    """
    Phân tích performance của user dựa trên user_id.
    
    Args:
        state: GraphState hiện tại
        
    Returns:
        Updated state với performance analysis
    """
    try:
        user_id = state.get("user_id")
        user_profile = state.get("user_profile", {})
        
        if not user_id:
            return {
                **state,
                "answer": "Không thể phân tích hiệu suất: thiếu user_id",
                "error": "Missing user_id for performance analysis"
            }
        
        # Setup DB
        engine = get_engine(settings.database_url)
        SessionLocal = get_session_maker(engine)
        session = SessionLocal()
        
        try:
            # Fetch comprehensive data
            # 1. User info (nếu chưa có từ fetch_user_data_node)
            if not user_profile:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return {
                        **state,
                        "answer": f"User {user_id} không tồn tại",
                        "error": f"User {user_id} not found"
                    }
                
                user_profile = {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role,
                    "level": user.level,
                    "time_budget_per_week": user.time_budget_per_week
                }
            
            # 2. All assessments (không chỉ 30 ngày) để xem trend
            all_assessments_query = session.query(Assessment, Skill).join(
                Skill, Assessment.skill_id == Skill.id
            ).filter(
                Assessment.user_id == user_id
            ).order_by(Assessment.taken_at.desc())
            
            all_assessments = []
            for assessment, skill in all_assessments_query.all():
                all_assessments.append({
                    "skill_id": skill.id,
                    "skill_name": skill.name,
                    "score": assessment.score,
                    "level": assessment.level,
                    "taken_at": assessment.taken_at.isoformat()
                })
            
            # 3. Recent assessments (30 ngày) để highlight
            recent_date = datetime.utcnow() - timedelta(days=30)
            recent_assessments = [
                a for a in all_assessments 
                if datetime.fromisoformat(a["taken_at"]) >= recent_date
            ]
            
            # 4. All enrollments để xem progress
            all_enrollments_query = session.query(Enrollment, Course).join(
                Course, Enrollment.course_id == Course.id
            ).filter(
                Enrollment.user_id == user_id
            ).order_by(Enrollment.started_at.desc())
            
            all_enrollments = []
            completed_this_month = 0
            total_study_hours = 0
            
            for enrollment, course in all_enrollments_query.all():
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
                
                all_enrollments.append(enrollment_data)
                
                # Calculate metrics
                if enrollment.completed_at and enrollment.completed_at >= recent_date:
                    completed_this_month += 1
                
                if enrollment.status in ["completed", "in_progress"]:
                    progress_hours = (enrollment.progress_percent / 100) * course.duration_hours
                    total_study_hours += progress_hours
            
            # 5. Skill breakdown với latest scores
            skill_breakdown = {}
            role_expectations = {
                "Data Analyst": {"sql": 4, "python": 3, "data_analysis": 4, "excel": 3, "statistics": 3},
                "Junior Developer": {"python": 3, "git": 3, "sql": 2, "communication": 3},
                "Business Analyst": {"data_analysis": 3, "excel": 4, "communication": 4, "sql": 2}
            }
            
            expected_levels = role_expectations.get(user_profile.get("role", ""), {})
            
            # Group assessments by skill (lấy latest)
            for assessment in all_assessments:
                skill_id = assessment["skill_id"]
                if skill_id not in skill_breakdown:
                    skill_breakdown[skill_id] = {
                        "skill": assessment["skill_name"],
                        "current_level": assessment["level"],
                        "score": assessment["score"],
                        "expected_level": expected_levels.get(skill_id, 3),
                        "status": "good" if assessment["level"] >= expected_levels.get(skill_id, 3) else "needs_improvement",
                        "trend": "stable"  # Default, có thể analyze trend sau
                    }
            
            # 6. Identify strengths và improvements
            strengths = []
            improvements_needed = []
            
            for skill_data in skill_breakdown.values():
                if skill_data["status"] == "good":
                    strengths.append(f"{skill_data['skill']} - Level {skill_data['current_level']} (Score: {skill_data['score']})")
                else:
                    improvements_needed.append({
                        "skill": skill_data["skill"],
                        "current_level": skill_data["current_level"],
                        "target_level": skill_data["expected_level"],
                        "gap": skill_data["expected_level"] - skill_data["current_level"],
                        "suggestion": f"Focus on {skill_data['skill']} improvement",
                        "priority": "high" if skill_data["expected_level"] - skill_data["current_level"] >= 2 else "medium"
                    })
            
            # 7. Format data cho LLM
            user_data_text = json.dumps({
                "name": user_profile.get("name"),
                "role": user_profile.get("role"),
                "level": user_profile.get("level"),
                "time_budget_per_week": user_profile.get("time_budget_per_week")
            }, ensure_ascii=False, indent=2)
            
            assessments_text = format_assessments_for_prompt(recent_assessments or all_assessments[:5])
            
            enrollments_text = "\n".join([
                f"- {e['course_title']}: {e['status']} ({e['progress_percent']}%)"
                for e in all_enrollments[:5]
            ])
            
            # 8. LLM Analysis
            llm = ChatOpenAI(
                model=settings.model_name,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                temperature=settings.temperature
            )
            
            prompt = PERFORMANCE_ANALYSIS_PROMPT.format(
                user_data=user_data_text,
                assessments=assessments_text,
                enrollments=enrollments_text
            )
            
            response = llm.invoke(prompt)
            content = response.content.strip()
            
            # Parse JSON
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            result = json.loads(content)
            
            # 9. Enhance với calculated metrics
            enhanced_result = {
                **result,
                "calculated_metrics": {
                    "total_skills_assessed": len(skill_breakdown),
                    "courses_completed_this_month": completed_this_month,
                    "total_study_hours": round(total_study_hours, 1),
                    "active_courses": len([e for e in all_enrollments if e["status"] == "in_progress"]),
                    "average_score": round(sum(a["score"] for a in all_assessments) / len(all_assessments), 1) if all_assessments else 0
                },
                "skill_breakdown": list(skill_breakdown.values())
            }
            
            return {
                **state,
                "assessments": all_assessments,
                "enrollments": all_enrollments,
                "answer": _format_performance_answer(enhanced_result)
            }
            
        finally:
            session.close()
            
    except Exception as e:
        # Fallback analysis
        user_profile = state.get("user_profile", {})
        assessments = state.get("assessments", [])
        enrollments = state.get("enrollments", [])
        
        if assessments or enrollments:
            fallback_answer = f"""## 📊 Phân tích hiệu suất - {user_profile.get('name', 'User')}

### 🎯 Tóm tắt
Hiện tại bạn có {len(assessments)} kỹ năng được đánh giá và {len(enrollments)} khóa học đang/đã học.

### 📈 Kỹ năng hiện tại
"""
            for assessment in assessments[:3]:
                fallback_answer += f"- **{assessment['skill_name']}**: Level {assessment['level']} (Score: {assessment['score']})\n"
            
            fallback_answer += f"""
### 📚 Khóa học
"""
            for enrollment in enrollments[:3]:
                fallback_answer += f"- **{enrollment['course_title']}**: {enrollment['status']} ({enrollment['progress_percent']}%)\n"
            
            fallback_answer += """
### ✅ Bước tiếp theo
1. Tiếp tục hoàn thành các khóa đang học
2. Lấy thêm assessment cho các kỹ năng mới
3. Xem xét kế hoạch học tiếp theo

💡 **Gợi ý**: Hãy hỏi tôi về kỹ năng cụ thể nào đó để được tư vấn chi tiết hơn!"""
        else:
            fallback_answer = """## 📊 Chưa có dữ liệu đánh giá

Hiện tại chưa có thông tin về kỹ năng và khóa học của bạn.

### ✅ Bước tiếp theo
1. Thực hiện đánh giá kỹ năng đầu tiên
2. Đăng ký khóa học phù hợp
3. Bắt đầu hành trình học tập

💡 **Gợi ý**: Hãy nói "Tôi muốn học [tên kỹ năng]" để bắt đầu!"""
        
        return {
            **state,
            "answer": fallback_answer,
            "error": f"Performance analysis error: {str(e)}"
        }


def _format_performance_answer(analysis_result: Dict[str, Any]) -> str:
    """
    Format kết quả analysis thành markdown response.
    
    Args:
        analysis_result: Kết quả từ LLM + calculated metrics
        
    Returns:
        Formatted markdown string
    """
    try:
        summary = analysis_result.get("summary", "Phân tích hiệu suất tổng quan")
        strengths = analysis_result.get("strengths", [])
        improvements = analysis_result.get("improvements_needed", [])
        progress = analysis_result.get("progress_this_month", "Chưa có dữ liệu")
        next_actions = analysis_result.get("next_actions", [])
        motivation = analysis_result.get("motivation_note", "")
        metrics = analysis_result.get("calculated_metrics", {})
        
        answer = f"""## 📊 Phân tích hiệu suất

### 🎯 Tóm tắt
{summary}

### 📈 Thành tích nổi bật
"""
        
        for strength in strengths[:3]:
            answer += f"- ✅ {strength}\n"
        
        if not strengths:
            answer += "- Chưa có điểm mạnh được xác định\n"
        
        answer += "\n### 🎯 Kỹ năng cần cải thiện\n"
        
        for improvement in improvements[:3]:
            skill = improvement.get("skill", "Unknown")
            current = improvement.get("current_level", 0)
            target = improvement.get("target_level", 3)
            suggestion = improvement.get("suggestion", "Cần cải thiện")
            priority = improvement.get("priority", "medium")
            
            priority_emoji = "🔥" if priority == "high" else "📈"
            answer += f"- {priority_emoji} **{skill}**: Level {current} → {target} - {suggestion}\n"
        
        if not improvements:
            answer += "- 🎉 Tất cả kỹ năng đã đạt mức mong đợi!\n"
        
        answer += f"\n### 📚 Tiến độ học tập\n{progress}\n"
        
        if metrics:
            answer += f"""
### 📊 Thống kê
- **Tổng kỹ năng**: {metrics.get('total_skills_assessed', 0)}
- **Điểm trung bình**: {metrics.get('average_score', 0)}/100
- **Khóa hoàn thành tháng này**: {metrics.get('courses_completed_this_month', 0)}
- **Tổng giờ học**: {metrics.get('total_study_hours', 0)} giờ
- **Khóa đang học**: {metrics.get('active_courses', 0)}
"""
        
        answer += "\n### ✅ Bước tiếp theo\n"
        
        for i, action in enumerate(next_actions[:3], 1):
            answer += f"{i}. {action}\n"
        
        if not next_actions:
            answer += "1. Tiếp tục duy trì tiến độ học tập hiện tại\n"
            answer += "2. Xem xét thêm kỹ năng mới\n"
            answer += "3. Thực hiện đánh giá định kỳ\n"
        
        if motivation:
            answer += f"\n---\n💪 **{motivation}**"
        
        return answer
        
    except Exception as e:
        return f"Đã phân tích hiệu suất của bạn, nhưng có lỗi khi format kết quả: {str(e)}"