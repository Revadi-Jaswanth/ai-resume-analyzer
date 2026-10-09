import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
extra_indent = 0

for i, line in enumerate(lines):
    # Check if this line is opening a glass card
    if "st.markdown('<div class=\"glass-card\"" in line and "unsafe_allow_html=True)" in line:
        match = re.match(r'^(\s*)', line)
        base_indent = match.group(1) if match else ""
        new_lines.append(base_indent + "with st.container(border=True):\n")
        extra_indent += 4
    # Check if this line is closing a glass card
    elif "st.markdown('</div>', unsafe_allow_html=True)" in line:
        extra_indent = max(0, extra_indent - 4)
    else:
        if extra_indent > 0:
            if line.strip() == '':
                new_lines.append(line)
            else:
                new_lines.append(' ' * extra_indent + line)
        else:
            new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
