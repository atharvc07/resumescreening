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
