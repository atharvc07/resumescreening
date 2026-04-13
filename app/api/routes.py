from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from ..schemas import SubmitResumeResponse, EvaluationStatusEnum, GetEvaluationResponse, EvaluationResult
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

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "resume-screening"}
