import os
import json
import time
import google.generativeai as genai
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Using gemini-pro for the widest possible compatibility
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')
        
        self.system_prompt = self._load_prompt("prompts/resume_screening.md")
        self.examples = self._load_prompt("prompts/resume_screening_examples.md")
    
    def _load_prompt(self, filepath: str) -> str:
        """Load prompt from external file."""
        with open(filepath, 'r') as f:
            return f.read()
    
    def evaluate_resume(self, resume_text: str, job_description: str, max_retries: int = 3) -> Dict:
        """
        Evaluate resume using Google Gemini with retry logic.
        """
        prompt = f"""
{self.system_prompt}

---
EXAMPLES:
{self.examples}

---
Now evaluate this resume:

**Job Description:**
{job_description}

**Resume:**
{resume_text}

Remember: Respond with ONLY a valid JSON object.
"""
        
        for attempt in range(max_retries):
            try:
                # Call Gemini Pro
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                    )
                )
                
                result_text = response.text.strip()
                
                # Manual clean up of result_text if Gemini adds markdown markers
                if result_text.startswith("```json"):
                    result_text = result_text[7:-3].strip()
                elif result_text.startswith("```"):
                    result_text = result_text[3:-3].strip()
                
                # Parse JSON response
                result = json.loads(result_text)
                
                # Validate required fields
                required_fields = ["score", "verdict", "missing_requirements", "justification"]
                if not all(field in result for field in required_fields):
                    raise ValueError("Gemini response missing required fields")
                
                return result
                
            except Exception as e:
                logger.error(f"Gemini API error (Attempt {attempt + 1}): {e}")
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    time.sleep(wait_time)
                    continue
                raise
            
# Singleton instance
llm_service = LLMService()

def evaluate_resume(resume_text: str, job_description: str) -> Dict:
    """Wrapper function for task compatibility."""
    return llm_service.evaluate_resume(resume_text, job_description)
