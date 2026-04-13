import PyPDF2
from typing import Optional
import io

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
