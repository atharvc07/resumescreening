import os
import json
import time
from openai import OpenAI, RateLimitError
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
    
    def evaluate_resume(self, resume_text: str, job_description: str, max_retries: int = 3) -> Dict:
        """
        Evaluate resume with retry logic for rate limits.
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
                
                result_text = response.choices[0].message.content.strip()
                
                # Parse JSON response
                result = json.loads(result_text)
                
                # Validate required fields
                required_fields = ["score", "verdict", "missing_requirements", "justification"]
                if not all(field in result for field in required_fields):
                    raise ValueError("LLM response missing required fields")
                
                return result
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # Exponential backoff
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
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
