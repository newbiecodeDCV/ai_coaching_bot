"""
SQLAlchemy models cho hệ thống AI Coaching Bot.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    """Model cho người dùng."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    role = Column(String)  # Data Analyst, HRBP, etc.
    level = Column(Integer, default=1)  # 1-5
    time_budget_per_week = Column(Integer, default=4)  # giờ/tuần
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    learning_plans = relationship("LearningPlan", back_populates="user", cascade="all, delete-orphan")


class Skill(Base):
    """Model cho kỹ năng."""
    __tablename__ = "skills"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    synonyms = Column(JSON, default=list)  # danh sách từ đồng nghĩa
    parent_skill_id = Column(String, ForeignKey("skills.id"), nullable=True)
    description = Column(Text)
    weight = Column(Float, default=1.0)  # trọng số ưu tiên
    
    # Relationships
    courses = relationship("CourseSkill", back_populates="skill")
    assessments = relationship("Assessment", back_populates="skill")
    prerequisites = relationship(
        "SkillPrerequisite",
        foreign_keys="SkillPrerequisite.skill_id",
        back_populates="skill"
    )


class SkillPrerequisite(Base):
    """Model cho prerequisite giữa các skills."""
    __tablename__ = "skill_prerequisites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    prereq_skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    note = Column(String)
    
    # Relationships
    skill = relationship("Skill", foreign_keys=[skill_id], back_populates="prerequisites")


class Course(Base):
    """Model cho khóa học."""
    __tablename__ = "courses"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    provider = Column(String)
    url = Column(String)
    duration_hours = Column(Float)
    cost = Column(Float, default=0.0)
    tags = Column(JSON, default=list)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = relationship("CourseSkill", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")


class CourseSkill(Base):
    """Many-to-many relationship giữa Course và Skill."""
    __tablename__ = "courses_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    min_level = Column(Integer, default=1)  # level tối thiểu để học course này
    
    # Relationships
    course = relationship("Course", back_populates="skills")
    skill = relationship("Skill", back_populates="courses")


class Assessment(Base):
    """Model cho đánh giá kỹ năng của user."""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    score = Column(Float)  # điểm raw
    level = Column(Integer)  # 1-5
    taken_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    skill = relationship("Skill", back_populates="assessments")


class Enrollment(Base):
    """Model cho việc user đăng ký/học khóa."""
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    status = Column(String, default="enrolled")  # enrolled, in_progress, completed
    progress_percent = Column(Float, default=0.0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class LearningPlan(Base):
    """Model cho kế hoạch học."""
    __tablename__ = "learning_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    status = Column(String, default="active")  # active, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_plans")
    items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")


class PlanItem(Base):
    """Model cho item trong learning plan."""
    __tablename__ = "plan_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("learning_plans.id"), nullable=False)
    week_no = Column(Integer)
    target = Column(String)
    course_id = Column(String, ForeignKey("courses.id"), nullable=True)
    kpi = Column(String)
    notes = Column(Text)
    
    # Relationships
    plan = relationship("LearningPlan", back_populates="items")


class Document(Base):
    """Model cho tài liệu upload."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    source_path = Column(String)
    mime = Column(String)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=True)
    ingested_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunks = relationship("DocChunk", back_populates="document", cascade="all, delete-orphan")


class DocChunk(Base):
    """Model cho chunk của document (metadata, vector trong FAISS)."""
    __tablename__ = "doc_chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer)
    text = Column(Text)
    page = Column(Integer, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
