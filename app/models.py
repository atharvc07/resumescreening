from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class EvaluationStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Verdict(enum.Enum):
    STRONG_MATCH = "STRONG_MATCH"
    GOOD_MATCH = "GOOD_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    WEAK_MATCH = "WEAK_MATCH"
    NO_MATCH = "NO_MATCH"

class ResumeEvaluation(Base):
    __tablename__ = "resume_evaluations"

    id = Column(String, primary_key=True, index=True)
    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.PENDING)
    
    # Input data
    resume_filename = Column(String, nullable=False)
    resume_content = Column(String, nullable=False)  # Extracted text
    job_description = Column(String, nullable=False)
    
    # Results
    score = Column(Integer, nullable=True)
    verdict = Column(Enum(Verdict), nullable=True)
    missing_requirements = Column(JSON, nullable=True)
    justification = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(String, nullable=True)
