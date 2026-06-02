from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String)
    author = Column(String)
    author_id = Column(String)
    desc = Column(Text)
    cover_path = Column(String)

    summary = Column(Text)
    category = Column(String, index=True)
    tags = Column(JSON)
    key_points = Column(JSON)
    quality_score = Column(Integer)

    created_at = Column(DateTime)
    favorited_at = Column(DateTime)
    synced_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(String)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
