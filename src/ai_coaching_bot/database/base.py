"""
Base configuration cho SQLAlchemy ORM.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def get_engine(database_url: str):
    """
    Tạo SQLAlchemy engine.
    
    Args:
        database_url: Connection string cho database
        
    Returns:
        SQLAlchemy engine instance
    """
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )

def get_session_maker(engine):
    """
    Tạo session maker.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        SessionLocal class
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
