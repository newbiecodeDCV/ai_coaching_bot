"""
Script setup database và seed dữ liệu mô phỏng.
"""
from src.ai_coaching_bot.config import settings
from src.ai_coaching_bot.database.base import Base, get_engine, get_session_maker
from src.ai_coaching_bot.database.models import *
from src.ai_coaching_bot.database.seed import seed_all


def setup_database():
    """
    Tạo tables và seed dữ liệu.
    """
    print(f"📦 Setup database tại: {settings.database_url}")
    
    # Create engine
    engine = get_engine(settings.database_url)
    
    # Create all tables
    print("🔨 Đang tạo tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables đã được tạo")
    
    # Seed data
    SessionLocal = get_session_maker(engine)
    session = SessionLocal()
    
    try:
        seed_all(session)
    except Exception as e:
        print(f"❌ Lỗi khi seed: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    setup_database()
