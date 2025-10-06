"""
Script seed dữ liệu mô phỏng cho database.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import (
    User, Skill, SkillPrerequisite, Course, CourseSkill,
    Assessment, Enrollment, Document
)


def seed_skills(session: Session):
    """Seed dữ liệu skills."""
    skills_data = [
        {"id": "sql", "name": "SQL", "synonyms": ["sql", "t-sql", "truy vấn dữ liệu"], "weight": 1.2},
        {"id": "python", "name": "Python", "synonyms": ["python", "py"], "weight": 1.3},
        {"id": "data_analysis", "name": "Data Analysis", "synonyms": ["phân tích dữ liệu", "data analysis"], "weight": 1.2},
        {"id": "visualization", "name": "Data Visualization", "synonyms": ["trực quan hóa", "visualization", "biểu đồ"], "weight": 1.0},
        {"id": "ml_basics", "name": "Machine Learning Basics", "synonyms": ["machine learning", "ml", "học máy"], "weight": 1.5},
        {"id": "communication", "name": "Communication", "synonyms": ["giao tiếp", "communication"], "weight": 1.1},
        {"id": "leadership", "name": "Leadership", "synonyms": ["lãnh đạo", "leadership", "quản lý"], "weight": 1.4},
        {"id": "excel", "name": "Excel", "synonyms": ["excel", "spreadsheet"], "weight": 0.9},
        {"id": "statistics", "name": "Statistics", "synonyms": ["thống kê", "statistics"], "weight": 1.2},
        {"id": "git", "name": "Git/Version Control", "synonyms": ["git", "version control", "source control"], "weight": 0.8},
    ]
    
    for data in skills_data:
        skill = Skill(**data)
        session.add(skill)
    
    # Prerequisites
    prereqs = [
        ("python", "git"),
        ("data_analysis", "sql"),
        ("data_analysis", "python"),
        ("ml_basics", "python"),
        ("ml_basics", "statistics"),
    ]
    
    for skill_id, prereq_id in prereqs:
        prereq = SkillPrerequisite(skill_id=skill_id, prereq_skill_id=prereq_id)
        session.add(prereq)
    
    session.commit()


def seed_courses(session: Session):
    """Seed dữ liệu courses."""
    courses_data = [
        {"id": "sql_basics", "title": "SQL Fundamentals", "provider": "Codecademy", "url": "https://example.com/sql", "duration_hours": 20, "cost": 0},
        {"id": "sql_advanced", "title": "Advanced SQL for Data Analysis", "provider": "Udemy", "url": "https://example.com/sql-adv", "duration_hours": 15, "cost": 19.99},
        {"id": "python_basics", "title": "Python for Beginners", "provider": "Coursera", "url": "https://example.com/py", "duration_hours": 25, "cost": 0},
        {"id": "python_data", "title": "Python for Data Science", "provider": "edX", "url": "https://example.com/py-data", "duration_hours": 30, "cost": 49.99},
        {"id": "data_viz", "title": "Data Visualization with Python", "provider": "DataCamp", "url": "https://example.com/viz", "duration_hours": 12, "cost": 29.99},
        {"id": "ml_intro", "title": "Introduction to Machine Learning", "provider": "Coursera", "url": "https://example.com/ml", "duration_hours": 40, "cost": 79.99},
        {"id": "excel_pro", "title": "Excel for Data Analysts", "provider": "LinkedIn Learning", "url": "https://example.com/excel", "duration_hours": 8, "cost": 0},
        {"id": "stats_basics", "title": "Statistics Fundamentals", "provider": "Khan Academy", "url": "https://example.com/stats", "duration_hours": 18, "cost": 0},
        {"id": "comm_skills", "title": "Effective Communication Skills", "provider": "Udemy", "url": "https://example.com/comm", "duration_hours": 6, "cost": 19.99},
        {"id": "git_basics", "title": "Git Essentials", "provider": "GitHub Learning Lab", "url": "https://example.com/git", "duration_hours": 4, "cost": 0},
    ]
    
    for data in courses_data:
        course = Course(**data)
        session.add(course)
    
    # Course-Skill mapping
    mappings = [
        ("sql_basics", "sql", 1),
        ("sql_advanced", "sql", 3),
        ("python_basics", "python", 1),
        ("python_data", "python", 2),
        ("python_data", "data_analysis", 2),
        ("data_viz", "visualization", 2),
        ("data_viz", "python", 2),
        ("ml_intro", "ml_basics", 2),
        ("ml_intro", "python", 3),
        ("excel_pro", "excel", 1),
        ("excel_pro", "data_analysis", 1),
        ("stats_basics", "statistics", 1),
        ("comm_skills", "communication", 1),
        ("git_basics", "git", 1),
    ]
    
    for course_id, skill_id, min_level in mappings:
        cs = CourseSkill(course_id=course_id, skill_id=skill_id, min_level=min_level)
        session.add(cs)
    
    session.commit()


def seed_users(session: Session):
    """Seed dữ liệu users."""
    users_data = [
        {"id": "user_001", "name": "Nguyễn Văn A", "email": "nva@example.com", "role": "Data Analyst", "level": 2, "time_budget_per_week": 5},
        {"id": "user_002", "name": "Trần Thị B", "email": "ttb@example.com", "role": "Junior Developer", "level": 1, "time_budget_per_week": 4},
        {"id": "user_003", "name": "Lê Văn C", "email": "lvc@example.com", "role": "Business Analyst", "level": 3, "time_budget_per_week": 3},
    ]
    
    for data in users_data:
        user = User(**data)
        session.add(user)
    
    session.commit()


def seed_assessments(session: Session):
    """Seed dữ liệu assessments."""
    assessments_data = [
        # user_001
        {"user_id": "user_001", "skill_id": "sql", "score": 75, "level": 3},
        {"user_id": "user_001", "skill_id": "python", "score": 60, "level": 2},
        {"user_id": "user_001", "skill_id": "data_analysis", "score": 70, "level": 3},
        {"user_id": "user_001", "skill_id": "excel", "score": 85, "level": 4},
        # user_002
        {"user_id": "user_002", "skill_id": "python", "score": 45, "level": 2},
        {"user_id": "user_002", "skill_id": "git", "score": 50, "level": 2},
        # user_003
        {"user_id": "user_003", "skill_id": "communication", "score": 80, "level": 4},
        {"user_id": "user_003", "skill_id": "data_analysis", "score": 65, "level": 3},
    ]
    
    for data in assessments_data:
        assessment = Assessment(**data, taken_at=datetime.utcnow() - timedelta(days=30))
        session.add(assessment)
    
    session.commit()


def seed_enrollments(session: Session):
    """Seed dữ liệu enrollments."""
    enrollments_data = [
        {"user_id": "user_001", "course_id": "sql_basics", "status": "completed", "progress_percent": 100, "started_at": datetime.utcnow() - timedelta(days=90), "completed_at": datetime.utcnow() - timedelta(days=60)},
        {"user_id": "user_001", "course_id": "python_data", "status": "in_progress", "progress_percent": 65, "started_at": datetime.utcnow() - timedelta(days=20)},
        {"user_id": "user_002", "course_id": "python_basics", "status": "in_progress", "progress_percent": 40, "started_at": datetime.utcnow() - timedelta(days=15)},
        {"user_id": "user_003", "course_id": "comm_skills", "status": "completed", "progress_percent": 100, "started_at": datetime.utcnow() - timedelta(days=45), "completed_at": datetime.utcnow() - timedelta(days=30)},
    ]
    
    for data in enrollments_data:
        enrollment = Enrollment(**data)
        session.add(enrollment)
    
    session.commit()


def seed_documents(session: Session):
    """Seed dữ liệu documents."""
    docs_data = [
        {"title": "Chính sách đào tạo nội bộ 2024", "source_path": "demo_docs/training_policy_2024.pdf", "mime": "application/pdf"},
        {"title": "Hướng dẫn phát triển kỹ năng Data Analysis", "source_path": "demo_docs/data_analysis_guide.md", "mime": "text/markdown", "skill_id": "data_analysis"},
        {"title": "SQL Best Practices", "source_path": "demo_docs/sql_best_practices.pdf", "mime": "application/pdf", "skill_id": "sql"},
    ]
    
    for data in docs_data:
        doc = Document(**data, created_at=datetime.utcnow())
        session.add(doc)
    
    session.commit()


def seed_all(session: Session):
    """
    Seed tất cả dữ liệu mô phỏng.
    
    Args:
        session: SQLAlchemy session
    """
    print("🌱 Bắt đầu seed dữ liệu...")
    
    seed_skills(session)
    print("✅ Skills seeded")
    
    seed_courses(session)
    print("✅ Courses seeded")
    
    seed_users(session)
    print("✅ Users seeded")
    
    seed_assessments(session)
    print("✅ Assessments seeded")
    
    seed_enrollments(session)
    print("✅ Enrollments seeded")
    
    seed_documents(session)
    print("✅ Documents seeded")
    
    print("🎉 Seed hoàn tất!")
