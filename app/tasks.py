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
