"""
AI RESUME ANALYZER - Main Streamlit Application
Tagline: "Better Resume. Brighter Future."
"""
import os
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

from services.resume_parser import parse_resume_file
from services.resume_analyzer import ResumeAnalyzer
from services.job_matcher import JobMatcher
from services.ai_service import AIService
from utils.validators import validate_uploaded_file, validate_job_description
from utils.scoring import CATEGORY_WEIGHTS
from utils.helpers import (
    format_file_size,
    render_badges,
    render_score_circle,
    render_category_progress,
    render_list_items
)

load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer | Better Resume. Brighter Future.",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Session State ────────────────────────────────────────────────────────────
for key in ["resume_data", "analysis_result", "job_match_result"]:
    if key not in st.session_state:
        st.session_state[key] = None
for key in ["is_ai_analysis", "is_ai_job_match"]:
    if key not in st.session_state:
        st.session_state[key] = True

# ── Services ─────────────────────────────────────────────────────────────────
ai_service = AIService()
analyzer_service = ResumeAnalyzer(ai_service=ai_service)
matcher_service = JobMatcher(ai_service=ai_service)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: wrap content in a styled card (single st.markdown call = safe)
# ─────────────────────────────────────────────────────────────────────────────
def card(title_icon: str, title_text: str, body_html: str, extra_style: str = ""):
    """Render a complete glass-card in one st.markdown call."""
    st.markdown(f"""
    <div class="glass-card" style="{extra_style}">
        <div class="card-title"><span>{title_icon}</span> {title_text}</div>
        {body_html}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────────────────────
def render_header():
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("""
        <div class="app-title-badge">
            <span style="font-size:2rem;">⚡</span>
            <div>
                <h1>AI RESUME ANALYZER</h1>
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        status = "🟢 OpenAI Connected" if ai_service.is_api_available() else "🟡 Local NLP Engine"
        st.markdown(f"""
        <div style="text-align:right;padding-top:10px;">
            <span style="background:rgba(18,20,28,0.8);border:1px solid rgba(255,23,68,0.3);
            padding:6px 14px;border-radius:20px;font-size:0.82rem;color:#D1D5DB;font-weight:600;">
            {status}</span>
        </div>""", unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">AI RESUME <span>ANALYZER</span></div>
        <div class="app-tagline" style="font-size:1.1rem;margin-bottom:0.8rem;">
            "Better Resume. Brighter Future."
        </div>
        <div class="hero-subtitle">
            Optimize your resume for ATS algorithms, unlock personalized AI career
            recommendations, and match your skillset against your dream job roles instantly.
        </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  RADAR CHART
# ─────────────────────────────────────────────────────────────────────────────
def render_score_radar_chart(breakdown: dict):
    cats = ["ATS Compat.", "Skills", "Experience", "Projects",
            "Keywords", "Achievements", "Formatting", "Clarity"]
    keys = ["ats_compatibility", "skills", "experience", "projects",
            "keywords", "achievements", "formatting", "clarity"]
    scores = []
    for k in keys:
        val = breakdown.get(k, 0)
        mx = CATEGORY_WEIGHTS.get(k, 20)
        scores.append(round((val / mx) * 100, 1) if mx else 0)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores, theta=cats, fill='toself',
        fillcolor='rgba(255,23,68,0.25)',
        line=dict(color='#FF1744', width=2),
        marker=dict(size=6, color='#FF1744'),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False,
                            gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(tickfont=dict(size=11, color='#D1D5DB'),
                             gridcolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(18,20,28,0.6)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=20), height=320, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  UPLOAD & ANALYZE PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_analyze_page():
    st.markdown('<h2 style="color:#FFF;font-weight:800;font-size:1.6rem;margin-bottom:1.2rem;">'
                'Upload &amp; Analyze Resume</h2>', unsafe_allow_html=True)

    up_col, info_col = st.columns([1.6, 1])

    with up_col:
        with st.container(border=True):
            st.markdown("#### 📥 Select Resume File")
            st.caption("Upload your resume in PDF, DOCX, DOC, or TXT format (Max 5 MB).")

            uploaded_file = st.file_uploader(
                "Choose a resume file",
                type=["pdf", "docx", "doc", "txt"],
                label_visibility="collapsed"
            )

            if uploaded_file is not None:
                is_valid, err_msg = validate_uploaded_file(uploaded_file)
                if not is_valid:
                    st.error(f"❌ {err_msg}")
                else:
                    st.success(
                        f"📄 **{uploaded_file.name}** — "
                        f"{uploaded_file.name.split('.')[-1].upper()} — "
                        f"{format_file_size(uploaded_file.size)}"
                    )
                    if st.button("🚀 Analyze Resume", key="btn_analyze"):
                        with st.spinner("🔍 Extracting text & running AI analysis…"):
                            parsed = parse_resume_file(uploaded_file)
                            st.session_state.resume_data = parsed
                            if not parsed["success"]:
                                st.error(f"❌ {parsed['error_message']}")
                            else:
                                try:
                                    result, is_ai = analyzer_service.analyze(parsed["text"])
                                    st.session_state.analysis_result = result
                                    st.session_state.is_ai_analysis = is_ai
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Analysis error: {e}")

    with info_col:
        card("🛡️", "Security & Privacy",
             render_list_items([
                 "Files parsed in-memory — never stored.",
                 "API keys isolated via environment variables.",
                 "No personal data shared or logged.",
                 "Modern data-protection compliant."
             ], icon_type="check"))
        card("🎯", "Why Analyze?",
             '<p style="font-size:0.9rem;color:#B0B3C6;line-height:1.6;margin:0;">'
             'Over 75% of resumes are filtered by ATS before human review. '
             'Our AI audits layout, keyword density, section headers, and measurable impact.</p>')

    # Extracted text expander
    if st.session_state.resume_data and st.session_state.resume_data.get("text"):
        with st.expander("🔍 View Extracted Resume Text"):
            st.text_area("Extracted Text", st.session_state.resume_data["text"],
                         height=250, disabled=True, label_visibility="collapsed")

    if st.session_state.analysis_result:
        st.divider()
        render_dashboard(st.session_state.analysis_result)


# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def render_dashboard(data: dict):
    st.markdown('<h2 style="color:#FFF;font-weight:800;font-size:1.8rem;margin-bottom:1rem;">'
                '📊 RESUME ANALYSIS DASHBOARD</h2>', unsafe_allow_html=True)

    if not st.session_state.is_ai_analysis:
        st.warning("⚠️ OpenAI API unavailable — results from local NLP heuristic engine.")

    overall = data.get("overall_score", 0)
    ats = data.get("ats_score", 0)
    label = data.get("score_label", "Evaluated")
    msg = data.get("score_message", "")
    bd = data.get("score_breakdown", {})

    # ── Top row ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.2, 1.4, 1.4])
    with c1:
        st.markdown(render_score_circle(overall, label, "OVERALL SCORE"), unsafe_allow_html=True)
    with c2:
        mini_grid = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:15px;">
          <div style="background:rgba(255,255,255,0.04);padding:10px;border-radius:8px;border:1px solid rgba(255,23,68,0.2);">
            <div style="font-size:0.75rem;color:#8E92A8;">ATS FRIENDLINESS</div>
            <div style="font-size:1.4rem;font-weight:800;color:#FF1744;">{ats}/100</div>
          </div>
          <div style="background:rgba(255,255,255,0.04);padding:10px;border-radius:8px;border:1px solid rgba(255,23,68,0.2);">
            <div style="font-size:0.75rem;color:#8E92A8;">SKILLS DETECTED</div>
            <div style="font-size:1.4rem;font-weight:800;color:#00E5FF;">{len(data.get('skills', []))}</div>
          </div>
        </div>"""
        card("📈", "Score Summary",
             f'<p style="color:#D1D5DB;font-size:0.95rem;line-height:1.5;">{msg}</p>{mini_grid}',
             extra_style="height:100%;")
    with c3:
        with st.container(border=True):
            st.markdown("**🕸️ Profile Radar**")
            render_score_radar_chart(bd)

    # ── Tabs ─────────────────────────────────────────────────────────────
    tabs = st.tabs(["Overview", "ATS Analysis", "Skills & Keywords",
                     "Sections", "Experience", "Job Match", "Suggestions"])

    # TAB 0: Overview
    with tabs[0]:
        oc1, oc2 = st.columns(2)
        with oc1:
            card("✓", "What's Good (Strengths)",
                 render_list_items(data.get("strengths", []), "check"))
        with oc2:
            card("⚠️", "Areas for Improvement",
                 render_list_items(data.get("weaknesses", []), "alert"))

        # Score breakdown bars
        progress_html = ""
        for cat, mx in CATEGORY_WEIGHTS.items():
            s = bd.get(cat, 0)
            progress_html += render_category_progress(cat.replace("_", " ").title(), s, mx)
        card("📊", "Weighted Score Breakdown (100 Points)", progress_html)

    # TAB 1: ATS
    with tabs[1]:
        ac1, ac2 = st.columns([1, 2])
        with ac1:
            st.markdown(render_score_circle(ats, "ATS FRIENDLINESS", "ATS SCORE"),
                        unsafe_allow_html=True)
        with ac2:
            ats_compat = bd.get("ats_compatibility", 0)
            fmt = bd.get("formatting", 0)
            kw = bd.get("keywords", 0)
            st.markdown("#### ATS Compatibility Checklist")
            st.markdown(
                f"- **Standard Section Headings**: {'✅ Detected' if ats_compat >= 14 else '⚠️ Missing'}\n"
                f"- **Font & Format**: {'✅ Clean' if fmt >= 3.5 else '⚠️ Issues possible'}\n"
                f"- **Keyword Density**: {'✅ Good' if kw >= 7 else '⚠️ Low'}"
            )
        card("🚨", "Detected ATS Issues",
             render_list_items(data.get("ats_issues", []), "alert"))

    # TAB 2: Skills & Keywords
    with tabs[2]:
        card("🛠️", "Detected Skills",
             render_badges(data.get("skills", []), "success"))
        sc1, sc2 = st.columns(2)
        with sc1:
            card("🎯", "Matching Keywords",
                 render_badges(data.get("matching_keywords", []), "success"))
        with sc2:
            card("❌", "Missing Keywords",
                 render_badges(data.get("missing_keywords", []), "danger"))

    # TAB 3: Section Breakdown
    with tabs[3]:
        st.markdown("#### Individual Section Analysis")
        for sec_key, sec_data in data.get("sections", {}).items():
            name = sec_key.replace("_", " ").title()
            sc = sec_data.get("score", 70) if isinstance(sec_data, dict) else 70
            fb = sec_data.get("feedback", "Evaluated.") if isinstance(sec_data, dict) else str(sec_data)
            color = "#00E676" if sc >= 80 else ("#FFD600" if sc >= 60 else "#FF1744")
            card("📋", f"{name} Section",
                 f'<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
                 f'<span style="color:#D1D5DB;">{name}</span>'
                 f'<span style="font-weight:800;color:{color};">{sc}/100</span></div>'
                 f'<p style="color:#D1D5DB;font-size:0.95rem;margin:0;line-height:1.6;">{fb}</p>')

    # TAB 4: Experience & Projects
    with tabs[4]:
        ec1, ec2 = st.columns(2)
        with ec1:
            exp_s = bd.get("experience", 10)
            ach_s = bd.get("achievements", 7)
            card("💼", "Experience Impact",
                 f"<p style='color:#D1D5DB;'>Experience Score: <b>{exp_s}/15</b> &nbsp;|&nbsp; "
                 f"Achievements: <b>{ach_s}/10</b></p>"
                 "<ul class='feature-list'>"
                 "<li><span class='icon-bullet'>•</span> Include quantifiable numbers in every bullet.</li>"
                 "<li><span class='icon-bullet'>•</span> Lead with action verbs (Spearheaded, Engineered…).</li>"
                 "</ul>")
        with ec2:
            proj_s = bd.get("projects", 10)
            card("🚀", "Projects & Portfolio",
                 f"<p style='color:#D1D5DB;'>Projects Score: <b>{proj_s}/15</b></p>"
                 "<ul class='feature-list'>"
                 "<li><span class='icon-bullet'>•</span> Highlight architecture, tools, and outcomes.</li>"
                 "<li><span class='icon-bullet'>•</span> Link to GitHub repos or live demos.</li>"
                 "</ul>")

    # TAB 5: Job Match
    with tabs[5]:
        render_job_match_section()

    # TAB 6: Suggestions
    with tabs[6]:
        card("💡", "Actionable Improvement Suggestions",
             render_list_items(data.get("improvement_suggestions", []), "bullet"))
        card("📝", "Recommended Structural Changes",
             render_list_items(data.get("recommended_changes", []), "check"))


# ─────────────────────────────────────────────────────────────────────────────
#  JOB MATCH
# ─────────────────────────────────────────────────────────────────────────────
def render_job_match_section():
    st.markdown("### 🎯 Match With Target Job Role")

    if not st.session_state.resume_data or not st.session_state.resume_data.get("text"):
        st.info("💡 Upload and analyze your resume from the upload section on the Home page.")
        return

    with st.container(border=True):
        st.markdown("**📋 Paste Target Job Description**")
        jd_text = st.text_area(
            "Job Description",
            height=180,
            placeholder="Paste the full job description here…",
            label_visibility="collapsed"
        )
        match_btn = st.button("🎯 Analyze Job Match", key="btn_jd_match")

    if match_btn:
        ok, err = validate_job_description(jd_text)
        if not ok:
            st.error(f"❌ {err}")
        else:
            with st.spinner("⚡ Running AI Job Matcher…"):
                try:
                    res, is_ai = matcher_service.match(
                        st.session_state.resume_data["text"], jd_text)
                    st.session_state.job_match_result = res
                    st.session_state.is_ai_job_match = is_ai
                    st.success("✅ Job Match Complete!")
                except Exception as e:
                    st.error(f"❌ {e}")

    res = st.session_state.job_match_result
    if res:
        score = res.get("job_match_score", 0)
        lvl = res.get("match_level", "Evaluated")

        mc1, mc2 = st.columns([1, 2])
        with mc1:
            st.markdown(render_score_circle(score, lvl, "JOB MATCH SCORE"),
                        unsafe_allow_html=True)
        with mc2:
            card("📌", "Alignment Summary",
                 f'<p style="color:#D1D5DB;">{res.get("summary", "")}</p>'
                 f'<p style="color:#D1D5DB;"><b>Experience:</b> {res.get("experience_alignment", "—")}</p>'
                 f'<p style="color:#D1D5DB;"><b>Education:</b> {res.get("education_alignment", "—")}</p>')

        kc1, kc2 = st.columns(2)
        with kc1:
            card("✅", "Matching Skills",
                 render_badges(res.get("matching_skills", []), "success"))
            card("✅", "Matching Keywords",
                 render_badges(res.get("matching_keywords", []), "success"))
        with kc2:
            card("❌", "Missing Skills",
                 render_badges(res.get("missing_skills", []), "danger"))
            card("❌", "Missing Keywords",
                 render_badges(res.get("missing_keywords", []), "danger"))

        card("💡", "Recommended Resume Changes",
             render_list_items(res.get("resume_changes_recommended", []), "check"))


# ─────────────────────────────────────────────────────────────────────────────
#  TIPS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_tips_page():
    st.markdown("## 💡 Expert Resume Optimization Tips")
    st.caption("Follow these proven industry standards to maximize ATS scores.")

    t1, t2 = st.columns(2)
    with t1:
        card("🎯", "Action-Oriented Bullet Points",
             '<p style="font-size:0.9rem;color:#D1D5DB;line-height:1.6;">'
             'Use the <b>X-Y-Z formula</b>: <em>"Accomplished [X] measured by [Y], by doing [Z]."</em></p>'
             '<div style="background:rgba(0,230,118,0.08);border-left:3px solid #00E676;'
             'padding:10px;margin-top:10px;font-size:0.85rem;">'
             '<b>Example:</b> "Reduced API latency by 35% across 20+ microservices by '
             'refactoring SQL queries and adding Redis caching."</div>')
        card("📄", "ATS Readability Rules",
             render_list_items([
                 "Use standard fonts: Arial, Calibri, or Helvetica.",
                 "Avoid tables, images, or text boxes.",
                 "Save as PDF or standard DOCX."
             ], "check"))
    with t2:
        card("🔥", "Action Verbs Power List",
             render_badges(["Spearheaded", "Architected", "Accelerated", "Engineered",
                            "Optimized", "Transformed", "Decreased", "Maximized",
                            "Orchestrated", "Delivered"], "neutral"))
        card("🚫", "Top Mistakes to Avoid",
             render_list_items([
                 "Soft-skills only without technical proof.",
                 "Missing quantifiable impact numbers.",
                 'Non-standard headers like "My Journey".',
                 "Spelling and grammatical oversights."
             ], "alert"))


# ─────────────────────────────────────────────────────────────────────────────
#  ABOUT PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_about_page():
    st.markdown("## ℹ️ About AI Resume Analyzer")
    card("⚡", "Project Overview",
         '<p style="color:#D1D5DB;line-height:1.6;">'
         '<b>AI RESUME ANALYZER</b> is an enterprise-grade AI career tool. '
         'It uses LLMs (OpenAI) and NLP to parse resumes, audit ATS compatibility, '
         'evaluate skill coverage, and compute semantic job-role matching.</p>')

    a1, a2 = st.columns(2)
    with a1:
        card("💻", "Tech Stack",
             render_list_items([
                 "Frontend: Streamlit + custom CSS & Plotly",
                 "AI Engine: OpenAI API (GPT-4o-mini / GPT-4o)",
                 "Fallback NLP: Scikit-Learn TF-IDF + Regex engine",
                 "Document Parsing: PyPDF, PdfPlumber, Python-DOCX"
             ], "check"))
    with a2:
        card("⚖️", "Scoring Formula",
             "<p style='font-size:0.9rem;color:#D1D5DB;'>8 weighted categories, 100 points total:</p>"
             + render_list_items([
                 "ATS Compatibility: 20 pts", "Skills Coverage: 20 pts",
                 "Work Experience: 15 pts", "Projects Portfolio: 15 pts",
                 "Keyword Density: 10 pts", "Achievements: 10 pts",
                 "Formatting: 5 pts", "Clarity: 5 pts"
             ], "bullet"))


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    render_header()

    selected = st.radio("Navigation",
                        ["Home", "Job Match", "Tips", "About"],
                        horizontal=True, label_visibility="collapsed")

    st.markdown("")  # spacer

    if selected == "Home":
        render_hero()
        render_analyze_page()
    elif selected == "Job Match":
        render_job_match_section()
    elif selected == "Tips":
        render_tips_page()
    elif selected == "About":
        render_about_page()

    st.markdown("""
    <div class="app-footer">
        <p>© 2026 AI RESUME ANALYZER | "Better Resume. Brighter Future."</p>
        <p>Powered by OpenAI & Advanced NLP</p>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
