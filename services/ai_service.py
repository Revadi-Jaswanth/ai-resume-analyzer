"""
Modular AI Service supporting OpenAI API and fallback Heuristic NLP model engine.
"""
import json
import os
import re
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Optional sklearn for NLP TF-IDF fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Import OpenAI safely
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class AIService:
    """Modular AI service for Resume Analysis & Job Matching."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        if HAS_OPENAI and self.api_key and self.api_key != "your_api_key_here":
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def is_api_available(self) -> bool:
        """Returns True if OpenAI API is configured."""
        return self.client is not None

    def _clean_json_response(self, text: str) -> Dict[str, Any]:
        """Extracts and parses JSON from raw LLM output text."""
        cleaned = text.strip()
        # Remove markdown fenced code blocks if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()
        
        # Find first '{' and last '}'
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]

        return json.loads(cleaned)

    def analyze_resume(self, system_prompt: str, user_prompt: str, raw_text: str) -> Tuple[Dict[str, Any], bool]:
        """
        Analyzes a resume using OpenAI API if available, else falls back to NLP Rule-Based Engine.
        Returns (result_dict, is_ai_generated).
        """
        if self.is_api_available():
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                )
                raw_content = response.choices[0].message.content
                parsed_json = self._clean_json_response(raw_content)
                return parsed_json, True
            except Exception as e:
                # Log or note error, fall back to NLP rule engine
                pass

        # Fallback to Rule-Based NLP Analysis
        return self._rule_based_resume_analysis(raw_text), False

    def match_job(self, system_prompt: str, user_prompt: str, resume_text: str, jd_text: str) -> Tuple[Dict[str, Any], bool]:
        """
        Matches resume against Job Description using OpenAI API if available, else NLP TF-IDF matcher.
        Returns (result_dict, is_ai_generated).
        """
        if self.is_api_available():
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                )
                raw_content = response.choices[0].message.content
                parsed_json = self._clean_json_response(raw_content)
                return parsed_json, True
            except Exception:
                pass

        # Fallback to Rule-Based TF-IDF matching
        return self._rule_based_job_matching(resume_text, jd_text), False

    # ----------------------------------------------------------------------
    # NLP HEURISTIC FALLBACK ENGINES
    # ----------------------------------------------------------------------
    def _rule_based_resume_analysis(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive NLP heuristic resume analysis when OpenAI API is unavailable.
        Evaluates skills, metrics, ATS section structure, action verbs, and formatting.
        """
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)

        # Common Tech / Professional Skills library
        SKILLS_DB = [
            "python", "java", "javascript", "typescript", "c++", "c#", "sql", "html", "css", "react",
            "angular", "vue", "node.js", "express", "django", "flask", "fastapi", "spring boot",
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "nltk",
            "spacy", "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab",
            "ci/cd", "rest api", "graphql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
            "tableau", "power bi", "excel", "agile", "scrum", "jira", "linux", "bash", "communication",
            "leadership", "problem solving", "project management", "data analysis", "machine learning"
        ]

        ACTION_VERBS = [
            "achieved", "accelerated", "architected", "built", "created", "decreased", "delivered",
            "designed", "developed", "engineered", "established", "expanded", "generated", "implemented",
            "improved", "increased", "launched", "lead", "managed", "maximized", "optimized",
            "orchestrated", "reduced", "spearheaded", "transformed", "utilised", "utilized"
        ]

        # 1. Detect present skills
        detected_skills = [skill.title() for skill in SKILLS_DB if re.search(r'\b' + re.escape(skill) + r'\b', text_lower)]
        
        # 2. Section detection
        sections_found = {
            "summary": bool(re.search(r'\b(summary|profile|about me|objective)\b', text_lower)),
            "skills": bool(re.search(r'\b(skills|technical skills|competencies|expertise)\b', text_lower)),
            "experience": bool(re.search(r'\b(experience|work history|employment|professional background)\b', text_lower)),
            "projects": bool(re.search(r'\b(projects|key projects|portfolio)\b', text_lower)),
            "education": bool(re.search(r'\b(education|academic|qualifications|degrees)\b', text_lower)),
        }

        # 3. Quantifiable achievements (numbers, percentages, dollar signs)
        metric_matches = re.findall(r'\b\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?[kM]?|\b\d+\+\b|\b\d+x\b', text)
        metric_count = len(metric_matches)

        # 4. Action verbs count
        action_verb_count = sum(len(re.findall(r'\b' + re.escape(v) + r'\b', text_lower)) for v in ACTION_VERBS)

        # 5. Score components calculation. Section headings establish
        # structure, but content quality earns the points. This prevents a
        # resume from receiving full marks just by naming each section.
        contact_signals = sum(bool(re.search(pattern, text_lower)) for pattern in [
            r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b', r'\b(?:linkedin|github)\b',
            r'\b(?:phone|mobile|tel)\b'
        ])
        date_count = len(re.findall(
            r'\b(?:19|20)\d{2}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
            r'[a-z]*\s+(?:19|20)\d{2}\b', text_lower))
        bullet_count = len(re.findall(r'(?m)^\s*(?:[-•*▪]|[0-9]+[.)])\s+', text))
        project_metrics = metric_count if sections_found["projects"] else 0

        ats_score = min(20.0, (
            sum(sections_found.values()) * 2.5
            + min(contact_signals, 3) * 1.0
            + min(bullet_count, 6) * 0.35
        ))
        skills_score = min(20.0, len(detected_skills) * 1.0)
        exp_score = min(15.0, (
            (4.0 if sections_found["experience"] else 0.0)
            + min(action_verb_count, 8) * 0.55
            + min(metric_count, 5) * 0.55
            + min(date_count, 4) * 0.5
        ))
        proj_score = min(15.0, (
            (4.0 if sections_found["projects"] else 0.0)
            + min(project_metrics, 4) * 1.25
            + min(len(detected_skills), 7) * 0.5
        ))
        keywords_score = min(10.0, len(detected_skills) * 0.5)
        achieve_score = min(10.0, metric_count * 1.5)
        format_score = min(5.0, (
            (2.0 if 250 <= word_count <= 900 else 1.0 if word_count >= 150 else 0.0)
            + min(bullet_count, 6) * 0.35
            + (1.0 if date_count >= 1 else 0.0)
        ))
        clarity_score = min(5.0, (
            (2.0 if 250 <= word_count <= 900 else 1.0 if word_count >= 150 else 0.0)
            + min(action_verb_count, 6) * 0.35
            + (1.0 if sections_found["summary"] else 0.0)
        ))

        score_breakdown = {
            "ats_compatibility": round(ats_score, 1),
            "skills": round(skills_score, 1),
            "experience": round(exp_score, 1),
            "projects": round(proj_score, 1),
            "keywords": round(keywords_score, 1),
            "achievements": round(achieve_score, 1),
            "formatting": round(format_score, 1),
            "clarity": round(clarity_score, 1)
        }

        total_score = round(sum(score_breakdown.values()))
        final_ats_score = round((ats_score / 20.0) * 100)

        # Strengths & Weaknesses
        strengths = []
        weaknesses = []
        suggestions = []
        ats_issues = []

        if len(detected_skills) >= 6:
            strengths.append(f"Strong array of technical & professional skills ({len(detected_skills)} skills identified).")
        else:
            weaknesses.append("Skill list is concise; consider adding more specific domain technologies.")
            suggestions.append("Add relevant technical keywords like Docker, AWS, or specialized tools for your target role.")

        if metric_count >= 3:
            strengths.append(f"Includes quantifiable business metrics and results ({metric_count} metrics found).")
        else:
            weaknesses.append("Lacks quantifiable metrics to demonstrate measurable impact.")
            suggestions.append("Your experience bullets describe responsibilities but do not show measurable impact. Add metrics such as 'reduced processing time by 30%' or 'increased efficiency by 15%'.")

        if action_verb_count >= 4:
            strengths.append("Effective use of strong action verbs to describe accomplishments.")
        else:
            suggestions.append("Use stronger action verbs (e.g. 'Architected', 'Spearheaded', 'Optimized') at the start of bullet points.")

        if not sections_found["summary"]:
            ats_issues.append("Missing explicit Professional Summary section header.")
            suggestions.append("Include a 3-4 line Professional Summary at the top highlighting key experience and value proposition.")

        if not sections_found["projects"]:
            weaknesses.append("No dedicated Projects section found.")
            suggestions.append("Add a Projects section with 2-3 key technical projects highlighting technologies used and outcomes achieved.")

        if word_count < 250:
            ats_issues.append("Resume length is below standard 300+ word threshold.")

        missing_skills_sample = ["Docker", "AWS", "CI/CD", "System Design", "Microservices"]
        matching_keywords_sample = detected_skills[:5]
        missing_keywords_sample = [s for s in missing_skills_sample if s not in detected_skills]

        return {
            "overall_score": total_score,
            "ats_score": final_ats_score,
            "summary": f"Resume contains {word_count} words and demonstrates key capabilities in {', '.join(detected_skills[:4]) if detected_skills else 'your field'}.",
            "strengths": strengths or ["Clear layout and structure.", "Contains relevant education details."],
            "weaknesses": weaknesses or ["Could benefit from additional quantitative metrics.", "Consider adding more domain keywords."],
            "skills": detected_skills or ["Communication", "Problem Solving", "Project Management"],
            "missing_skills": missing_keywords_sample,
            "matching_keywords": matching_keywords_sample or ["Analysis", "Development"],
            "missing_keywords": missing_keywords_sample,
            "score_breakdown": score_breakdown,
            "sections": {
                "summary": {"score": 85 if sections_found["summary"] else 50, "feedback": "Summary header detected." if sections_found["summary"] else "Missing explicit summary header."},
                "skills": {"score": min(95, int(skills_score * 5)), "feedback": f"Detected {len(detected_skills)} relevant skills."},
                "experience": {"score": min(95, int(exp_score * 6.6)), "feedback": "Work history structure evaluated."},
                "projects": {"score": round((proj_score / 15.0) * 100), "feedback": "Projects section and evidence evaluated." if sections_found["projects"] else "Missing dedicated projects section."},
                "education": {"score": 90 if sections_found["education"] else 60, "feedback": "Education credentials detected."}
            },
            "improvement_suggestions": suggestions or [
                "Your experience bullets describe responsibilities but do not show measurable impact. Add metrics such as 'reduced processing time by 30%' or 'improved accuracy by 15%'.",
                "Ensure standard section headings like 'Work Experience' and 'Education' are used for maximum ATS readability."
            ],
            "ats_issues": ats_issues or ["Ensure font size and section headings follow standard clean layouts."],
            "recommended_changes": [
                "Reformat skills into distinct categories (Core Tech, Frameworks, Tools).",
                "Include quantifiable outcomes in every work experience bullet point."
            ]
        }

    def _rule_based_job_matching(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        NLP TF-IDF cosine similarity & term matching for fallback Job Description alignment.
        """
        text_res_lower = resume_text.lower()
        text_jd_lower = jd_text.lower()

        # Common tech keywords to compare
        TECH_WORDS = [
            "python", "java", "javascript", "typescript", "c++", "c#", "sql", "react", "angular", "vue",
            "node.js", "django", "flask", "fastapi", "aws", "docker", "kubernetes", "pandas", "numpy",
            "scikit-learn", "tensorflow", "pytorch", "rest api", "graphql", "git", "ci/cd", "agile",
            "scrum", "microservices", "postgresql", "mysql", "redis", "tableau", "linux", "cloud"
        ]

        matching_tech = [t.title() for t in TECH_WORDS if t in text_res_lower and t in text_jd_lower]
        missing_tech = [t.title() for t in TECH_WORDS if t in text_jd_lower and t not in text_res_lower]

        if not matching_tech:
            matching_tech = ["Problem Solving", "Communication", "Teamwork"]
        if not missing_tech:
            missing_tech = ["Cloud Infrastructure", "CI/CD Deployment"]

        tfidf_sim = 0.5
        if HAS_SKLEARN:
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
                tfidf_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            except Exception:
                tfidf_sim = 0.5

        # Combined Match Score: 50% TF-IDF similarity + 50% Skill Overlap Ratio
        overlap_denom = (len(matching_tech) + len(missing_tech))
        skill_ratio = (len(matching_tech) / overlap_denom) if overlap_denom > 0 else 0.5

        combined_score = (tfidf_sim * 50 * 1.8) + (skill_ratio * 50)
        match_score = int(min(max(combined_score, 45), 98))

        match_level = "Excellent Match" if match_score >= 85 else ("Strong Match" if match_score >= 70 else ("Moderate Match" if match_score >= 50 else "Needs Alignment"))

        return {
            "job_match_score": match_score,
            "match_level": match_level,
            "summary": f"Your resume achieves a {match_score}% semantic alignment with the target Job Description.",
            "matching_skills": matching_tech,
            "missing_skills": missing_tech,
            "matching_keywords": matching_tech[:5],
            "missing_keywords": missing_tech[:5],
            "experience_alignment": "Experience aligns well with core role requirements.",
            "education_alignment": "Educational qualifications satisfy basic JD criteria.",
            "tools_and_tech_match": matching_tech,
            "tools_and_tech_missing": missing_tech,
            "recommended_skills_to_learn": missing_tech[:3],
            "resume_changes_recommended": [
                f"Integrate missing target keywords such as '{', '.join(missing_tech[:3])}' into your experience bullet points." if missing_tech else "Add quantitative metrics to your bullet points.",
                "Tailor your Professional Summary to explicitly state the primary job title from the job posting."
            ]
        }
