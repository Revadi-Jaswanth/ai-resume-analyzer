"""
Validators for file upload, size restrictions, and user input validation.
"""
import os
from typing import Tuple, Optional

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit


def validate_uploaded_file(uploaded_file) -> Tuple[bool, Optional[str]]:
    """
    Validates an uploaded file object from Streamlit.
    Returns (is_valid, error_message).
    """
    if uploaded_file is None:
        return False, "No file uploaded."

    filename = uploaded_file.name
    file_size = uploaded_file.size if hasattr(uploaded_file, "size") else 0

    # Extension check
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed formats: PDF, DOCX, DOC, TXT."

    # Size check
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        return False, f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of 5.0 MB."

    if file_size == 0:
        return False, "Uploaded file appears to be empty (0 bytes)."

    return True, None


def validate_job_description(jd_text: str) -> Tuple[bool, Optional[str]]:
    """
    Validates user-provided job description text.
    """
    if not jd_text or not jd_text.strip():
        return False, "Please paste or enter a job description."

    cleaned = jd_text.strip()
    if len(cleaned) < 30:
        return False, "Job description is too short. Please enter a more detailed job description for accurate matching."

    return True, None


def sanitize_text(text: str) -> str:
    """
    Sanitizes raw extracted or user-provided text.
    """
    if not text:
        return ""
    # Remove null bytes or non-printable control characters except line breaks
    sanitized = "".join(ch for ch in text if ch == "\n" or ch == "\r" or ch == "\t" or 32 <= ord(ch) <= 126 or ord(ch) > 127)
    return sanitized.strip()
