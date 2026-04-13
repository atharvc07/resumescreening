# AI Resume Screening Service - Complete Implementation Guide

## Overview
This guide walks you through building a production-ready AI resume screening service with proper Git workflow and multiple commits.

---

## Phase 1: Project Setup & Git Initialization (Commits 1-3)

### Commit 1: "Initial project structure and README"

**What to do:**
```bash
mkdir ai-resume-screener
cd ai-resume-screener
git init
```

**Create basic structure:**
```
ai-resume-screener/
├── README.md
├── .gitignore
├── .env.example
└── requirements.txt (or package.json if using Node.js)
```

**README.md** (basic version):
```markdown
# AI Resume Screening Service

A production-ready backend service that uses LLMs to screen resumes against job descriptions.

## Tech Stack
(To be filled)

## Setup Instructions
(To be filled)

## Testing
(To be filled)
```

**.gitignore**:
```
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
node_modules/
*.log
.DS_Store
.vscode/
.idea/
*.db
*.sqlite3
```

**.env.example**:
```
# LLM API Configuration
OPENAI_API_KEY=your_api_key_here
# or
ANTHROPIC_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/resume_screening

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
REDIS_URL=redis://localhost:6379
```

```bash
git add .
git commit -m "Initial project structure and README"
```

---

### Commit 2: "Add Docker configuration"

**Create:**
- `Dockerfile`
- `docker-compose.yml`

**Dockerfile** (example for Python/FastAPI):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/resume_screening
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./prompts:/app/prompts
  
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=resume_screening
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  worker:
    build: .
    command: python -m app.worker
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/resume_screening
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./prompts:/app/prompts

volumes:
  postgres_data:
```

```bash
git add Dockerfile docker-compose.yml
git commit -m "Add Docker configuration for multi-service architecture"
```

---

### Commit 3: "Add external prompt templates"

**Create directory:**
```bash
mkdir prompts
```

**Create `prompts/resume_screening.md`**:
```markdown
# Resume Screening System Prompt

You are an expert technical recruiter analyzing resumes against job descriptions.

## Your Task
Evaluate how well a candidate's resume matches the provided job description.

## Output Format
You MUST respond with ONLY a valid JSON object in this exact format:
{
  "score": <integer between 0-100>,
  "verdict": "<STRONG_MATCH|GOOD_MATCH|PARTIAL_MATCH|WEAK_MATCH|NO_MATCH>",
  "missing_requirements": [
    "Requirement 1",
    "Requirement 2"
  ],
  "justification": "Detailed explanation of the evaluation"
}

## Scoring Guidelines
- 90-100: Exceptional match - exceeds most requirements
- 70-89: Strong match - meets most key requirements
- 50-69: Partial match - meets some requirements, missing key skills
- 30-49: Weak match - few matching qualifications
- 0-29: Poor match - minimal relevant experience

## Analysis Steps
1. Extract key requirements from the job description (technical skills, experience, education)
2. Identify matching qualifications in the resume
3. List missing critical requirements
4. Calculate overall match score
5. Provide detailed justification

## Important Rules
- Be objective and fair
- Focus on concrete skills and experience, not assumptions
- Consider both technical and soft skills
- Account for equivalent experience
- DO NOT add any text before or after the JSON object
```

**Create `prompts/resume_screening_examples.md`** (Few-shot examples):
```markdown
# Few-Shot Examples for Resume Screening

## Example 1: Strong Match

**Job Description:**
"Senior Python Developer with 5+ years experience in Django, PostgreSQL, and AWS deployment."

**Resume:**
"7 years Python development. Led Django projects at scale. Expert in PostgreSQL optimization. AWS certified."

**Expected Output:**
{
  "score": 92,
  "verdict": "STRONG_MATCH",
  "missing_requirements": [],
  "justification": "Candidate exceeds experience requirement (7 years vs 5 required) and demonstrates all key technical skills including Django, PostgreSQL, and AWS. The AWS certification adds additional credibility."
}

## Example 2: Partial Match

**Job Description:**
"Full-stack developer: React, Node.js, MongoDB, 3+ years experience."

**Resume:**
"2 years experience with React and Vue.js. Familiar with Express.js and MySQL."

**Expected Output:**
{
  "score": 58,
  "verdict": "PARTIAL_MATCH",
  "missing_requirements": [
    "3+ years experience (has only 2 years)",
    "Node.js experience (only Express.js mentioned)",
    "MongoDB experience (has MySQL instead)"
  ],
  "justification": "Candidate has strong React skills but falls short on experience timeline. While Express.js knowledge is relevant, explicit Node.js experience is not demonstrated. Database experience is with MySQL rather than required MongoDB."
}

## Example 3: No Match

**Job Description:**
"DevOps Engineer: Kubernetes, Terraform, CI/CD pipelines, 4+ years experience."

**Resume:**
"Junior Frontend Developer. 1 year experience with HTML, CSS, JavaScript. Intern projects with React."

**Expected Output:**
{
  "score": 15,
  "verdict": "NO_MATCH",
  "missing_requirements": [
    "Kubernetes experience",
    "Terraform experience",
    "CI/CD pipeline experience",
    "4+ years DevOps experience (candidate has 1 year in different field)"
  ],
  "justification": "Candidate's experience is entirely in frontend development with no demonstrated DevOps skills. The role requires infrastructure and automation expertise that is not present in the resume."
}
```

```bash
git add prompts/
git commit -m "Add external prompt templates with few-shot examples"
```

---

## Phase 2: Core Application Structure (Commits 4-6)

### Commit 4: "Add database models and schemas"

**Create app structure:**
```
app/
├── __init__.py
├── models.py
├── schemas.py
├── database.py
└── config.py
```

**app/models.py** (SQLAlchemy example):
```python
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
```

**app/schemas.py** (Pydantic):
```python
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
```

```bash
git add app/
git commit -m "Add database models and Pydantic schemas"
```

---

### Commit 5: "Implement PDF parsing utility"

**Create `app/utils/pdf_parser.py`**:
```python
import PyPDF2
from typing import Optional

class PDFParseError(Exception):
    pass

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text content from PDF bytes.
    
    Args:
        pdf_bytes: Raw PDF file content
        
    Returns:
        Extracted text as string
        
    Raises:
        PDFParseError: If PDF parsing fails
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        full_text = "\n".join(text_parts)
        
        if not full_text.strip():
            raise PDFParseError("No text content found in PDF")
        
        return full_text
        
    except Exception as e:
        raise PDFParseError(f"Failed to parse PDF: {str(e)}")
```

**Update requirements.txt**:
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
pydantic==2.5.0
python-multipart==0.0.6
PyPDF2==3.0.1
openai==1.3.0  # or anthropic
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.1
```

```bash
git add app/utils/ requirements.txt
git commit -m "Implement PDF text extraction utility"
```

---

### Commit 6: "Setup async task queue with Celery"

**Create `app/worker.py`**:
```python
from celery import Celery
from .config import settings

celery_app = Celery(
    "resume_screening",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,
)
```

**Create `app/tasks.py`**:
```python
from .worker import celery_app
from .services.llm_service import evaluate_resume
from .database import SessionLocal
from .models import ResumeEvaluation, EvaluationStatus
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_resume_evaluation(self, evaluation_id: str):
    """
    Async task to process resume evaluation using LLM.
    
    Implements retry logic for rate limits and temporary failures.
    """
    db = SessionLocal()
    
    try:
        # Get evaluation from database
        evaluation = db.query(ResumeEvaluation).filter(
            ResumeEvaluation.id == evaluation_id
        ).first()
        
        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        # Update status
        evaluation.status = EvaluationStatus.PROCESSING
        db.commit()
        
        # Call LLM service
        result = evaluate_resume(
            resume_text=evaluation.resume_content,
            job_description=evaluation.job_description
        )
        
        # Store results
        evaluation.score = result["score"]
        evaluation.verdict = result["verdict"]
        evaluation.missing_requirements = result["missing_requirements"]
        evaluation.justification = result["justification"]
        evaluation.status = EvaluationStatus.COMPLETED
        db.commit()
        
    except Exception as exc:
        logger.error(f"Task failed for {evaluation_id}: {exc}")
        evaluation.status = EvaluationStatus.FAILED
        evaluation.error_message = str(exc)
        db.commit()
        
        # Retry on rate limit or temporary errors
        if "rate_limit" in str(exc).lower() or "429" in str(exc):
            raise self.retry(exc=exc, countdown=60)  # Retry after 1 minute
        
        raise
        
    finally:
        db.close()
```

```bash
git add app/worker.py app/tasks.py
git commit -m "Setup async task queue with Celery and retry logic"
```

---

## Phase 3: LLM Integration (Commits 7-8)

### Commit 7: "Implement LLM service with external prompts"

**Create `app/services/llm_service.py`**:
```python
import os
import json
from openai import OpenAI
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = self._load_prompt("prompts/resume_screening.md")
        self.examples = self._load_prompt("prompts/resume_screening_examples.md")
    
    def _load_prompt(self, filepath: str) -> str:
        """Load prompt from external file."""
        with open(filepath, 'r') as f:
            return f.read()
    
    def evaluate_resume(self, resume_text: str, job_description: str) -> Dict:
        """
        Evaluate resume against job description using LLM.
        
        Returns:
            Dict with score, verdict, missing_requirements, justification
        """
        user_message = f"""
{self.examples}

---

Now evaluate this resume:

**Job Description:**
{job_description}

**Resume:**
{resume_text}

Remember: Respond with ONLY the JSON object, no additional text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            result = json.loads(result_text)
            
            # Validate required fields
            required_fields = ["score", "verdict", "missing_requirements", "justification"]
            if not all(field in result for field in required_fields):
                raise ValueError("LLM response missing required fields")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError("Invalid JSON response from LLM")
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise

# Singleton instance
llm_service = LLMService()

def evaluate_resume(resume_text: str, job_description: str) -> Dict:
    """Wrapper function for task compatibility."""
    return llm_service.evaluate_resume(resume_text, job_description)
```

```bash
git add app/services/
git commit -m "Implement LLM service with external prompt loading"
```

---

### Commit 8: "Add rate limit handling and exponential backoff"

**Update `app/services/llm_service.py`**:
```python
import time
from openai import RateLimitError

class LLMService:
    # ... previous code ...
    
    def evaluate_resume(self, resume_text: str, job_description: str, max_retries: int = 3) -> Dict:
        """
        Evaluate resume with retry logic for rate limits.
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                
                # ... rest of processing ...
                return result
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # Exponential backoff
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                logger.error(f"LLM API error: {e}")
                raise
```

```bash
git add app/services/llm_service.py
git commit -m "Add exponential backoff for rate limit handling"
```

---

## Phase 4: API Endpoints (Commits 9-10)

### Commit 9: "Implement submit resume endpoint"

**Create `app/api/routes.py`**:
```python
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from ..schemas import SubmitResumeResponse, EvaluationStatusEnum
from ..models import ResumeEvaluation, EvaluationStatus
from ..database import get_db
from ..tasks import process_resume_evaluation
from ..utils.pdf_parser import extract_text_from_pdf, PDFParseError
import uuid

router = APIRouter()

@router.post("/evaluations", response_model=SubmitResumeResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Submit a resume for evaluation (async processing).
    
    Returns immediately with 202 Accepted and evaluation_id.
    """
    # Validate PDF
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted"
        )
    
    # Read and parse PDF
    try:
        pdf_bytes = await resume.read()
        resume_text = extract_text_from_pdf(pdf_bytes)
    except PDFParseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create evaluation record
    evaluation_id = str(uuid.uuid4())
    db = next(get_db())
    
    evaluation = ResumeEvaluation(
        id=evaluation_id,
        resume_filename=resume.filename,
        resume_content=resume_text,
        job_description=job_description,
        status=EvaluationStatus.PENDING
    )
    
    db.add(evaluation)
    db.commit()
    
    # Queue async task
    process_resume_evaluation.delay(evaluation_id)
    
    return SubmitResumeResponse(
        evaluation_id=evaluation_id,
        status=EvaluationStatusEnum.PENDING,
        message="Resume submitted for evaluation"
    )
```

```bash
git add app/api/
git commit -m "Implement async resume submission endpoint"
```

---

### Commit 10: "Implement get evaluation result endpoint"

**Update `app/api/routes.py`**:
```python
@router.get("/evaluations/{evaluation_id}", response_model=GetEvaluationResponse)
async def get_evaluation(evaluation_id: str):
    """
    Get evaluation results by ID.
    
    Returns current status and results if completed.
    """
    db = next(get_db())
    
    evaluation = db.query(ResumeEvaluation).filter(
        ResumeEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    response = GetEvaluationResponse(
        evaluation_id=evaluation.id,
        status=evaluation.status.value,
        created_at=evaluation.created_at.isoformat()
    )
    
    if evaluation.status == EvaluationStatus.COMPLETED:
        response.result = EvaluationResult(
            score=evaluation.score,
            verdict=evaluation.verdict.value,
            missing_requirements=evaluation.missing_requirements,
            justification=evaluation.justification
        )
    elif evaluation.status == EvaluationStatus.FAILED:
        response.error_message = evaluation.error_message
    
    return response
```

```bash
git add app/api/routes.py
git commit -m "Implement get evaluation result endpoint"
```

---

## Phase 5: Testing (Commits 11-12)

### Commit 11: "Add integration test fixtures"

**Create `tests/__init__.py`, `tests/conftest.py`**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

```bash
git add tests/
git commit -m "Add integration test fixtures and setup"
```

---

### Commit 12: "Add end-to-end integration tests"

**Create `tests/test_integration.py`**:
```python
import pytest
import io
from PyPDF2 import PdfWriter
from time import sleep

def create_test_pdf(text: str) -> bytes:
    """Create a simple PDF for testing."""
    # Implementation to create PDF with text
    pass

def test_submit_and_retrieve_evaluation(client, db_session):
    """
    Test complete flow: submit resume -> check status -> get results.
    """
    # Create test PDF
    resume_pdf = create_test_pdf("Python developer with 5 years experience...")
    
    # Submit resume
    response = client.post(
        "/evaluations",
        files={"resume": ("test_resume.pdf", resume_pdf, "application/pdf")},
        data={"job_description": "Looking for Python developer with 3+ years"}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert "evaluation_id" in data
    assert data["status"] == "pending"
    
    evaluation_id = data["evaluation_id"]
    
    # Poll for results (in real test, might use mocking)
    max_attempts = 10
    for _ in range(max_attempts):
        response = client.get(f"/evaluations/{evaluation_id}")
        assert response.status_code == 200
        
        data = response.json()
        if data["status"] == "completed":
            assert data["result"]["score"] >= 0
            assert data["result"]["score"] <= 100
            assert data["result"]["verdict"] in ["STRONG_MATCH", "GOOD_MATCH", "PARTIAL_MATCH", "WEAK_MATCH", "NO_MATCH"]
            assert isinstance(data["result"]["missing_requirements"], list)
            assert len(data["result"]["justification"]) > 0
            break
        
        sleep(2)

def test_invalid_file_type(client):
    """Test rejection of non-PDF files."""
    response = client.post(
        "/evaluations",
        files={"resume": ("test.txt", b"not a pdf", "text/plain")},
        data={"job_description": "Any job"}
    )
    
    assert response.status_code == 400

def test_evaluation_not_found(client):
    """Test 404 for non-existent evaluation."""
    response = client.get("/evaluations/non-existent-id")
    assert response.status_code == 404
```

```bash
git add tests/test_integration.py
git commit -m "Add comprehensive integration tests for main flows"
```

---

## Phase 6: Documentation & Polish (Commits 13-14)

### Commit 13: "Update README with complete documentation"

**Update README.md** with full architecture, setup, and testing instructions.

```bash
git add README.md
git commit -m "Add comprehensive README with architecture and setup guide"
```

---

### Commit 14: "Add API documentation and health check endpoint"

**Add OpenAPI docs and health check:**
```python
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "resume-screening"}
```

```bash
git add app/api/routes.py
git commit -m "Add API documentation and health check endpoint"
```

---

## Git Push Strategy

After each commit, you can push to GitHub:

```bash
# First time setup
git remote add origin https://github.com/yourusername/ai-resume-screener.git
git branch -M main

# Push after each commit or in batches
git push -u origin main
```

**Recommended Push Points:**
1. After Phase 1 complete (commits 1-3)
2. After Phase 2 complete (commits 4-6)
3. After Phase 3 complete (commits 7-8)
4. After Phase 4 complete (commits 9-10)
5. After Phase 5 complete (commits 11-12)
6. After Phase 6 complete (commits 13-14)

---

## Final Checklist

Before submission, verify:

- [ ] `docker-compose up` starts all services
- [ ] Integration tests pass with `pytest tests/`
- [ ] README.md has complete instructions
- [ ] `.env.example` file present
- [ ] No API keys in git history
- [ ] At least 10+ meaningful commits
- [ ] Prompts are in external .txt/.md files
- [ ] Async architecture properly implemented
- [ ] Error handling for rate limits included

---

## Architecture Summary

Your final architecture will have:

1. **API Layer** (FastAPI): Handles HTTP requests, returns 202 immediately
2. **Task Queue** (Celery + Redis): Processes evaluations asynchronously
3. **Database** (PostgreSQL): Stores evaluations and results
4. **LLM Service**: Reads prompts from files, calls OpenAI/Claude
5. **Worker Process**: Executes background tasks with retry logic

All running in Docker containers with proper service dependencies.
