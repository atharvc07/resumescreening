from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class VerdictEnum(str, Enum):
    STRONG_MATCH = "STRONG_MATCH"
    GOOD_MATCH = "GOOD_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    WEAK_MATCH = "WEAK_MATCH"
    NO_MATCH = "NO_MATCH"

class EvaluationStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SubmitResumeRequest(BaseModel):
    job_description: str = Field(..., min_length=10)

class SubmitResumeResponse(BaseModel):
    evaluation_id: str
    status: EvaluationStatusEnum
    message: str

class EvaluationResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    verdict: VerdictEnum
    missing_requirements: List[str]
    justification: str

class GetEvaluationResponse(BaseModel):
    evaluation_id: str
    status: EvaluationStatusEnum
    result: Optional[EvaluationResult] = None
    error_message: Optional[str] = None
    created_at: str
