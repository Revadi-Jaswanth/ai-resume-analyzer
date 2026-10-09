"""
Resume Analyzer Coordinator Service.
"""
from typing import Dict, Any, Tuple
from services.ai_service import AIService
from prompts.resume_analysis import RESUME_ANALYSIS_SYSTEM_PROMPT, build_resume_analysis_prompt
from utils.scoring import calculate_overall_score, normalize_breakdown, get_score_label


class ResumeAnalyzer:
    """Service to coordinate full AI resume analysis."""

    def __init__(self, ai_service: AIService = None):
        self.ai_service = ai_service or AIService()

    def analyze(self, resume_text: str) -> Tuple[Dict[str, Any], bool]:
        """
        Executes complete analysis on parsed resume text.
        Returns (result_dict, is_ai_generated).
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty. Cannot perform analysis.")

        system_prompt = RESUME_ANALYSIS_SYSTEM_PROMPT
        user_prompt = build_resume_analysis_prompt(resume_text)

        raw_result, is_ai = self.ai_service.analyze_resume(system_prompt, user_prompt, resume_text)

        # Normalize score breakdown
        breakdown = normalize_breakdown(raw_result.get("score_breakdown", {}))
        
        # Dynamically calculate total overall score
        computed_overall_score = calculate_overall_score(breakdown)
        
        # Override or set score dynamically
        raw_result["overall_score"] = computed_overall_score
        raw_result["score_breakdown"] = breakdown
        
        # Attach score label meta
        score_label_info = get_score_label(computed_overall_score)
        raw_result["score_label"] = score_label_info["label"]
        raw_result["score_message"] = score_label_info["message"]
        raw_result["score_color"] = score_label_info["color"]
        raw_result["score_css_class"] = score_label_info["css_class"]

        # Ensure ATS score exists
        if "ats_score" not in raw_result or not isinstance(raw_result["ats_score"], (int, float)):
            raw_result["ats_score"] = round((breakdown.get("ats_compatibility", 15) / 20.0) * 100)

        return raw_result, is_ai
