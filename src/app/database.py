from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from sqlalchemy import PickleType  # Add to imports

DATABASE_URL = "sqlite:///./knowledge.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class SolvedProblem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    method = Column(String(20), nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    embedding = Column(PickleType, nullable=True)  # ← Add this line
    cid       = Column(String, nullable=True)  # IPFS content ID
