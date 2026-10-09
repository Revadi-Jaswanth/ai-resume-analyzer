import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix upload col
content = content.replace(
    "st.markdown('<div class=\"glass-card\">', unsafe_allow_html=True)\n        st.markdown('<div class=\"card-title\"><span>📥</span> Select Resume File</div>', unsafe_allow_html=True)",
    "with st.container(border=True):\n            st.markdown('<div class=\"card-title\"><span>📥</span> Select Resume File</div>', unsafe_allow_html=True)"
)

content = content.replace(
    "st.markdown('</div>', unsafe_allow_html=True)\n\n    with info_col:",
    "\n    with info_col:"
)

# Fix job match col
content = content.replace(
    "st.markdown('<div class=\"glass-card\">', unsafe_allow_html=True)\n    st.markdown('<div class=\"card-title\"><span>📋</span> Paste Target Job Description</div>', unsafe_allow_html=True)",
    "with st.container(border=True):\n        st.markdown('<div class=\"card-title\"><span>📋</span> Paste Target Job Description</div>', unsafe_allow_html=True)"
)

content = content.replace(
    "match_btn = st.button(\"🎯 Analyze Job Match\", key=\"btn_match_jd\")\n    st.markdown('</div>', unsafe_allow_html=True)",
    "    match_btn = st.button(\"🎯 Analyze Job Match\", key=\"btn_match_jd\")"
)

# Fix plotly radar col
content = content.replace(
    "st.markdown('<div class=\"glass-card\" style=\"height: 100%;\">', unsafe_allow_html=True)\n        st.markdown('<div class=\"card-title\"><span>🕸️</span> Profile Radar</div>', unsafe_allow_html=True)\n        render_score_radar_chart(breakdown)\n        st.markdown('</div>', unsafe_allow_html=True)",
    "with st.container(border=True):\n            st.markdown('<div class=\"card-title\"><span>🕸️</span> Profile Radar</div>', unsafe_allow_html=True)\n            render_score_radar_chart(breakdown)"
)

# Ensure uploaded_file block is properly indented in render_analyze_page
# Wait, replacing `st.markdown('<div class=\"glass-card\">'` with `with st.container(border=True):` means everything below it until `with info_col:` needs an extra level of indentation.
# Actually, we can just replace `with st.container(border=True):` without changing indentation of the rest, it's valid Python if the next line is indented!
# Let's fix the indentation properly.

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed app.py")
