"""Convert justificacion_hsv.md to a well-formatted PDF."""

import os
import re
import base64
import markdown
from xhtml2pdf import pisa

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(SCRIPT_DIR, "justificacion_hsv.md")
PDF_FILE = os.path.join(SCRIPT_DIR, "justificacion_hsv.pdf")

# Read markdown
with open(MD_FILE, encoding="utf-8") as f:
    md_text = f.read()


def preprocess_markdown(text):
    """Fix indented tables inside list items so the parser renders them as real tables.

    Strategy: walk through lines, detect table blocks that are indented (inside
    bullet points) and pull them out to root level, closing the list before and
    reopening after if needed.
    """
    lines = text.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        # Detect an indented table header row (inside a list)
        if indent >= 2 and stripped.startswith("|") and i + 1 < len(lines):
            next_stripped = lines[i + 1].lstrip()
            # Check if next line is the separator row  |---|---|
            if next_stripped.startswith("|") and re.search(r"---", next_stripped):
                # Collect all contiguous table lines
                table_lines = []
                while i < len(lines):
                    s = lines[i].lstrip()
                    if s.startswith("|"):
                        table_lines.append(s)  # de-indent
                        i += 1
                    else:
                        break
                # Insert blank line before table to close list context
                result.append("")
                result.extend(table_lines)
                result.append("")
                continue
        result.append(line)
        i += 1
    return "\n".join(result)


md_text = preprocess_markdown(md_text)

# Convert to HTML
html_body = markdown.markdown(md_text, extensions=["tables", "smarty"])

# Embed images as base64 so the PDF is self-contained
def embed_images(html, base_path):
    """Replace local image src with base64 data URIs."""
    import re
    def replacer(match):
        attrs_before = match.group(1)
        src = match.group(2)
        attrs_after = match.group(3)
        img_path = os.path.join(base_path, src.replace("./", ""))
        if os.path.isfile(img_path):
            ext = os.path.splitext(img_path)[1].lower().strip(".")
            if ext == "jpg":
                ext = "jpeg"
            with open(img_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode()
            return f'<img {attrs_before}src="data:image/{ext};base64,{b64}"{attrs_after}>'
        return match.group(0)
    return re.sub(r'<img\s(.*?)src="([^"]+)"(.*?)/?>', replacer, html)

html_body = embed_images(html_body, SCRIPT_DIR)

# Build full HTML document with print-friendly CSS
html_doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 2cm 2.5cm;
  }}
  body {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1a1a1a;
  }}
  h1 {{
    font-size: 18pt;
    color: #1a1a1a;
    border-bottom: 2px solid #333;
    padding-bottom: 8px;
    margin-bottom: 16px;
  }}
  h2 {{
    font-size: 14pt;
    color: #2a2a2a;
    margin-top: 24px;
    border-bottom: 1px solid #999;
    padding-bottom: 4px;
  }}
  h3 {{
    font-size: 12pt;
    color: #333;
    margin-top: 18px;
  }}
  p {{
    text-align: justify;
    margin-bottom: 8px;
  }}
  strong {{
    color: #000;
  }}
  hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 20px 0;
  }}
  blockquote {{
    border-left: 3px solid #2196F3;
    margin: 12px 0;
    padding: 8px 16px;
    background-color: #f0f7ff;
    font-style: italic;
  }}
  table {{
    border-collapse: collapse;
    margin: 12px auto;
    width: auto;
  }}
  th, td {{
    border: 1px solid #555;
    padding: 6px 16px;
    text-align: center;
  }}
  th {{
    background-color: #e8e8e8;
    font-weight: bold;
  }}
  tr:nth-child(even) {{
    background-color: #f9f9f9;
  }}
  ul, ol {{
    margin-bottom: 10px;
  }}
  li {{
    margin-bottom: 6px;
  }}
  img {{
    max-width: 80%;
    display: block;
    margin: 16px auto;
  }}
  em {{
    color: #555;
  }}
  code {{
    background-color: #f4f4f4;
    padding: 2px 4px;
    font-size: 9pt;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

# Generate PDF
with open(PDF_FILE, "wb") as pdf_f:
    status = pisa.CreatePDF(html_doc, dest=pdf_f)

if status.err:
    print(f"Error generating PDF: {status.err}")
else:
    size_kb = os.path.getsize(PDF_FILE) / 1024
    print(f"PDF generated successfully: {PDF_FILE} ({size_kb:.0f} KB)")
