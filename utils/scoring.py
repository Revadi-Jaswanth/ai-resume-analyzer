"""
Scoring methodology and dynamic calculation helpers.
"""
from typing import Dict, Any

CATEGORY_WEIGHTS = {
    "ats_compatibility": 20,
    "skills": 20,
    "experience": 15,
    "projects": 15,
    "keywords": 10,
    "achievements": 10,
    "formatting": 5,
    "clarity": 5
}

MAX_TOTAL_SCORE = sum(CATEGORY_WEIGHTS.values())  # 100


def calculate_overall_score(breakdown: Dict[str, float]) -> int:
    """
    Calculates the total score from individual weighted categories.
    Each category score should be out of its maximum weight.
    """
    total = 0.0
    for cat, max_weight in CATEGORY_WEIGHTS.items():
        score = breakdown.get(cat, 0.0)
        # Cap category score at max weight
        total += min(max(float(score), 0.0), float(max_weight))
    
    return min(100, max(0, round(total)))


def get_score_label(score: int) -> Dict[str, str]:
    """
    Returns text label and CSS class for a given 0-100 score.
    """
    if score >= 85:
        return {"label": "Excellent", "color": "#00E676", "css_class": "score-label-excellent", "message": "Outstanding resume! Highly optimized for ATS & recruiters."}
    elif score >= 70:
        return {"label": "Great Job!", "color": "#00E5FF", "css_class": "score-label-good", "message": "Strong resume with solid foundation. Minor polish recommended."}
    elif score >= 50:
        return {"label": "Needs Work", "color": "#FFD600", "css_class": "score-label-average", "message": "Fair resume, but missing key quantifiable impact & ATS keywords."}
    else:
        return {"label": "Requires Overhaul", "color": "#FF1744", "css_class": "score-label-poor", "message": "Needs significant improvements in formatting, keywords, and content."}


def normalize_breakdown(breakdown: Dict[str, Any]) -> Dict[str, float]:
    """
    Ensures all expected breakdown fields are present and clamped within valid weights.
    """
    normalized = {}
    for cat, max_wt in CATEGORY_WEIGHTS.items():
        # Missing evidence must not be rewarded. Callers can still provide an
        # explicit score when a model has evaluated the category.
        val = breakdown.get(cat, 0.0)
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            val_float = 0.0
        normalized[cat] = round(min(max(val_float, 0.0), float(max_wt)), 1)
    return normalized
