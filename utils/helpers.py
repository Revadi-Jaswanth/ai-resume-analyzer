"""
Helper utilities for UI rendering, badge tags, formatting, and HTML components.
"""
import html
from typing import List
import streamlit as st


def format_file_size(size_bytes: int) -> str:
    """Formats file size in human-readable units."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def render_badges(items: List[str], badge_type: str = "success") -> str:
    """
    Renders list of strings as HTML pill badges.
    badge_type: 'success', 'danger', 'warning', 'neutral'
    """
    if not items:
        return "<span style='color: #8E92A8; font-style: italic;'>None detected</span>"
    
    badge_class = f"badge badge-{badge_type}"
    icon_map = {
        "success": "✓",
        "danger": "✕",
        "warning": "⚠",
        "neutral": "•"
    }
    icon = icon_map.get(badge_type, "•")
    
    html_parts = ['<div class="badge-container">']
    for item in items:
        clean_item = html.escape(str(item).strip())
        if clean_item:
            html_parts.append(f'<span class="{badge_class}"><span>{icon}</span> {clean_item}</span>')
    html_parts.append('</div>')
    
    return "".join(html_parts)


def render_score_circle(score: int, label: str, title: str = "OVERALL SCORE") -> str:
    """
    Renders a circular conic-gradient score widget matching the dark red theme.
    """
    # Color selection based on score
    if score >= 85:
        score_color = "#00E676"
    elif score >= 70:
        score_color = "#00E5FF"
    elif score >= 50:
        score_color = "#FFD600"
    else:
        score_color = "#FF1744"

    return f"""
    <div class="score-hero-card">
        <div style="font-size: 0.85rem; color: #8E92A8; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 0.75rem; text-transform: uppercase;">
            {html.escape(title)}
        </div>
        <div class="score-circle-outer" style="--score: {score}; background: radial-gradient(circle, #08090D 62%, transparent 63%), conic-gradient({score_color} calc({score} * 1%), #1A1D28 0);">
            <div class="score-circle-inner">
                <div class="score-number">{score}</div>
                <div class="score-max">/ 100</div>
            </div>
        </div>
        <div class="score-label" style="color: {score_color};">
            {html.escape(label)}
        </div>
    </div>
    """


def render_category_progress(name: str, score: float, max_score: float) -> str:
    """
    Renders a category score bar with percentage fill.
    """
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    percentage = min(max(percentage, 0), 100)
    
    return f"""
    <div style="margin-bottom: 1rem;">
        <div class="cat-metric-row">
            <span class="cat-metric-name">{html.escape(name)}</span>
            <span class="cat-metric-val">{score:.1f} / {max_score}</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {percentage}%;"></div>
        </div>
    </div>
    """


def render_list_items(items: List[str], icon_type: str = "check") -> str:
    """
    Renders a styled list with custom icons.
    icon_type: 'check', 'alert', 'bullet'
    """
    if not items:
        return "<p style='color: #8E92A8;'>No items to display.</p>"
    
    icon_html = {
        "check": '<span class="icon-check">✓</span>',
        "alert": '<span class="icon-alert">!</span>',
        "bullet": '<span class="icon-bullet">•</span>'
    }.get(icon_type, '<span class="icon-bullet">•</span>')
    
    html_parts = ['<ul class="feature-list">']
    for item in items:
        clean_text = html.escape(str(item).strip())
        if clean_text:
            html_parts.append(f'<li>{icon_html} <span>{clean_text}</span></li>')
    html_parts.append('</ul>')
    
    return "".join(html_parts)
