"""
Job Matcher Coordinator Service.
"""
from typing import Dict, Any, Tuple
from services.ai_service import AIService
from prompts.job_matching import JOB_MATCHING_SYSTEM_PROMPT, build_job_matching_prompt


class JobMatcher:
    """Service to coordinate AI job description matching."""

    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()

    def match(self, resume_text: str, job_description: str) -> Tuple[Dict[str, Any], bool]:
        """
        Executes job matching analysis between resume text and job description.
        Returns (result_dict, is_ai_generated).
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is missing. Please upload a resume first.")

        if not job_description or not job_description.strip():
            raise ValueError("Job description is missing. Please enter a job description.")

        system_prompt = JOB_MATCHING_SYSTEM_PROMPT
        user_prompt = build_job_matching_prompt(resume_text, job_description)

        match_result, is_ai = self.ai_service.match_job(system_prompt, user_prompt, resume_text, job_description)

        # Validate score bounds
        match_score = match_result.get("job_match_score", 75)
        try:
            match_score = int(match_score)
        except (ValueError, TypeError):
            match_score = 75
        match_result["job_match_score"] = min(max(match_score, 0), 100)

        return match_result, is_ai
