# AI RESUME ANALYZER 📄⚡
> **Tagline:** "Better Resume. Brighter Future."

An enterprise-grade, AI-powered Resume Analyzer and Job Description Matching web application built with **Streamlit**, **Python**, **OpenAI API**, and **NLP Models**.

Designed with a modern dark/crimson cyberpunk UI aesthetic, this application helps job seekers optimize their resumes for Applicant Tracking Systems (ATS), detect weak bullet points, extract domain keywords, and perform deep semantic matching against specific target Job Descriptions.

---

## 🌟 Key Features

- 📥 **Multi-Format Resume Upload**: Supports PDF, DOCX, DOC, and TXT files up to 5 MB with robust text extraction.
- ⚡ **Structured AI Analysis**: Evaluates 15 core dimensions of a resume and produces actionable JSON-backed feedback.
- 📊 **Dynamic Weighted Scoring**: Computes a dynamic 0–100 overall score based on 8 weighted categories.
- 🤖 **ATS Friendliness Audit**: Checks section headers, font cleanliness, layout structure, and ATS keyword coverage.
- 🎯 **Job Description Semantic Matching**: Compares resume text against target job descriptions using TF-IDF and LLM semantic embeddings to calculate a Job Match Score (XX%).
- 🛠️ **Skill & Keyword Detection**: Highlights matching and missing technical skills, tools, and industry keywords.
- 💡 **Specific Improvement Suggestions**: Provides actionable advice (e.g., adding metrics like *"reduced latency by 30%"*) instead of vague suggestions.
- 🛡️ **Modular AI Service & Heuristic Fallback**: Includes a fallback NLP rule engine when an OpenAI API key is not provided, ensuring 100% uptime without application crashes.

---

## 🏗️ Tech Stack

- **Frontend & Dashboard**: [Streamlit](https://streamlit.io/), HTML5, Custom CSS3, [Plotly](https://plotly.com/)
- **Backend & Logic**: Python 3.11+
- **AI & NLP Services**: [OpenAI API](https://openai.com/) (`gpt-4o-mini` / `gpt-4o`), [Scikit-Learn](https://scikit-learn.org/) (TF-IDF & Cosine Similarity)
- **Document Extractors**: `pdfplumber`, `pypdf`, `python-docx`
- **Data Processing**: Pandas, Regular Expressions (Regex)

---

## 📂 Project Structure

```
ai-resume-analyzer/
│
├── app.py                     # Main Streamlit application entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── README.md                  # Detailed documentation
│
├── services/                  # Business logic & AI services
│   ├── __init__.py
│   ├── ai_service.py          # Modular OpenAI API client + Rule-based NLP fallback
│   ├── resume_parser.py       # PDF/DOCX/DOC/TXT text extraction engine
│   ├── resume_analyzer.py     # Resume analysis coordinator & dynamic scorer
│   └── job_matcher.py         # Job description semantic matcher
│
├── utils/                     # Utility helpers & scoring logic
│   ├── __init__.py
│   ├── scoring.py             # Category weights & score calculation methodology
│   ├── validators.py          # File size, extension, & input validators
│   └── helpers.py             # HTML/CSS pill badges, progress bars, & metric cards
│
├── prompts/                   # System & user prompt templates
│   ├── __init__.py
│   ├── resume_analysis.py     # Resume review JSON prompts
│   └── job_matching.py        # Job match JSON prompts
│
└── assets/
    └── styles.css             # Cyberpunk dark/crimson styling stylesheet
```

---

## ⚖️ Scoring Methodology

Resumes are evaluated out of **100 total points** distributed across 8 weighted categories:

| Category | Max Points | Evaluation Focus |
| :--- | :---: | :--- |
| **ATS Compatibility** | 20 pts | Section headings, structural layout, font readability |
| **Skills Coverage** | 20 pts | Technical skills, frameworks, and tools density |
| **Work Experience** | 15 pts | Career history progression & leadership |
| **Projects Portfolio** | 15 pts | Technical project outcomes and architecture |
| **Keyword Density** | 10 pts | Relevant domain and industry terminology |
| **Achievements & Metrics**| 10 pts | Quantifiable numbers, percentages, and business outcomes |
| **Formatting** | 5 pts | Consistent margins, spacing, and bullet points |
| **Clarity** | 5 pts | Conciseness, tone, and action verb usage |

---

## 🔑 Environment Variables Setup

For local development, add your key to `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Never commit `.env` or paste a real API key into source control. The repository includes only the safe `.env.example` template. If no API key is provided, the application automatically uses its built-in NLP Heuristic Engine.

---

## 🚀 Installation & Setup

### 1. Clone or Navigate to Project Directory
```bash
cd "ai-resume-analyzer"
```

### 2. Create and Activate Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

The application will launch automatically in your web browser at `http://localhost:8501`.

### Deployment Environment Variables

Set these values in your hosting provider's environment-variable or secrets settings; do not upload the local `.env` file:

```text
OPENAI_API_KEY=<your real OpenAI API key>
OPENAI_MODEL=gpt-4o-mini
```

For Streamlit Community Cloud, open the app's **Settings → Secrets** and add the same values in TOML format:

```toml
OPENAI_API_KEY = "your real OpenAI API key"
OPENAI_MODEL = "gpt-4o-mini"
```

The application reads these variables at startup with `python-dotenv`. The real key stays in the deployment platform's secret store while the code remains safe to publish.

---

## 📖 How to Use

1. **Upload Resume**: Use the upload section on the **Home** page, drag and drop your PDF/DOCX resume file (under 5 MB), and click **"Analyze Resume"**.
2. **Review Dashboard**: Explore the interactive dashboard tabs including Overview, ATS Analysis, Skills & Keywords, Section Breakdown, Experience & Projects, and Suggestions.
3. **Match Job Description**: Go to the **Job Match** tab, paste a target job description, and click **"Analyze Job Match"** to get your Job Match Score and missing skills list.
4. **Optimize**: Apply the specific, metric-oriented recommendations to refine your resume.

---

## 🛡️ Security & Best Practices

- **In-Memory Processing**: Uploaded documents are parsed in memory and never permanently stored on disk or database.
- **Environment Isolation**: Sensitive credentials like API keys are kept in local `.env` files or the deployment platform's secret store, never in Git.
- **Input Sanitization**: User text inputs and extracted file text are sanitized before processing.

---

## 🔮 Future Improvements

- [ ] Export detailed resume analysis reports as PDF/HTML artifacts.
- [ ] AI-assisted automated resume bullet point rewriter.
- [ ] Integration with Hugging Face BERT embeddings for fine-grained job matching.
- [ ] Resume history comparison for tracking score progression over time.
