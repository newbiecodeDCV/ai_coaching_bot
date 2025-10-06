"""
FastAPI dependencies - Database session, auth, etc.
"""
from typing import Generator
from sqlalchemy.orm import Session
from ..config import settings
from ..database.base import get_engine, get_session_maker

# Database dependencies
engine = get_engine(settings.database_url)
SessionLocal = get_session_maker(engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency để lấy database session.
    
    Yields:
        SQLAlchemy session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def validate_user_id(user_id: str) -> str:
    """
    Validate user_id format.
    
    Args:
        user_id: User ID cần validate
        
    Returns:
        Validated user_id
        
    Raises:
        ValueError: Nếu user_id không hợp lệ
    """
    if not user_id or len(user_id.strip()) == 0:
        raise ValueError("user_id không được rỗng")
    
    if len(user_id) > 50:
        raise ValueError("user_id quá dài (tối đa 50 ký tự)")
    
    # Basic alphanumeric + underscore validation
    if not user_id.replace("_", "").replace("-", "").isalnum():
        raise ValueError("user_id chỉ được chứa chữ, số, dấu _ và -")
    
    return user_id.strip()


def validate_message(message: str) -> str:
    """
    Validate và clean message từ user.
    
    Args:
        message: Message cần validate
        
    Returns:
        Cleaned message
        
    Raises:
        ValueError: Nếu message không hợp lệ
    """
    if not message or len(message.strip()) == 0:
        raise ValueError("Message không được rỗng")
    
    if len(message.strip()) > 2000:
        raise ValueError("Message quá dài (tối đa 2000 ký tự)")
    
    # Remove excessive whitespace
    cleaned = " ".join(message.split())
    
    return cleaned


# Rate limiting (future implementation)
# def rate_limit_dependency():
#     """Rate limiting dependency."""
#     pass

# Authentication (future implementation)  
# def get_current_user():
#     """Authentication dependency."""
#     pass