#!/usr/bin/env python3
"""
Jupyter Notebook & Python Code to PDF Exporter
Renders .ipynb or .py files to high-fidelity HTML and converts them to PDF using headless Chrome.
Supports both full notebook execution export and pure-code Jupyter CodeMirror styled export.
"""

import sys
import os
import json
import subprocess
import html
import re
import argparse
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def highlight_python(code):
    keywords = {
        'import', 'from', 'as', 'def', 'return', 'class', 'if', 'elif', 'else',
        'for', 'while', 'in', 'is', 'not', 'and', 'or', 'True', 'False', 'None',
        'try', 'except', 'finally', 'with', 'lambda', 'pass', 'break', 'continue'
    }
    builtins = {
        'print', 'range', 'len', 'min', 'max', 'sum', 'enumerate', 'zip', 'map',
        'filter', 'list', 'dict', 'set', 'tuple', 'int', 'float', 'str', 'bool',
        'np', 'pd', 'plt', 'sns', 'array', 'zeros', 'ones', 'arange', 'linspace',
        'reshape', 'mean', 'std', 'var', 'sum', 'dot', 'DataFrame', 'Series'
    }
    
    lines = code.split('\n')
    highlighted_lines = []
    
    for line in lines:
        if not line:
            highlighted_lines.append('')
            continue
            
        comment_idx = -1
        in_str = False
        quote_char = ''
        for i, char in enumerate(line):
            if char in ('"', "'"):
                if not in_str:
                    in_str = True
                    quote_char = char
                elif char == quote_char and (i == 0 or line[i-1] != '\\'):
                    in_str = False
            elif char == '#' and not in_str:
                comment_idx = i
                break
                
        if comment_idx != -1:
            code_part = line[:comment_idx]
            comment_part = line[comment_idx:]
        else:
            code_part = line
            comment_part = ""
            
        def highlight_tokens(text):
            token_pattern = re.compile(
                r'(?P<STRING>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|'
                r'(?P<NUMBER>\b\d+(?:\.\d+)?\b)|'
                r'(?P<WORD>\b[a-zA-Z_]\w*\b)|'
                r'(?P<OTHER>[^\w\s"\'\\]+)'
            )
            
            def replace_match(m):
                if m.group('STRING'):
                    return f'<span class="tok-str">{html.escape(m.group("STRING"))}</span>'
                elif m.group('NUMBER'):
                    return f'<span class="tok-num">{html.escape(m.group("NUMBER"))}</span>'
                elif m.group('WORD'):
                    w = m.group('WORD')
                    if w in keywords:
                        return f'<span class="tok-kw">{html.escape(w)}</span>'
                    elif w in builtins:
                        return f'<span class="tok-builtin">{html.escape(w)}</span>'
                    return html.escape(w)
                elif m.group('OTHER'):
                    return html.escape(m.group('OTHER'))
                return html.escape(m.group(0))
                
            return token_pattern.sub(replace_match, text)
            
        hl_code = highlight_tokens(code_part)
        if comment_part:
            hl_comment = f'<span class="tok-comment">{html.escape(comment_part)}</span>'
            highlighted_lines.append(hl_code + hl_comment)
        else:
            highlighted_lines.append(hl_code)
            
    return '\n'.join(highlighted_lines)

def parse_markdown(text):
    """Simple parser for basic markdown elements in notebook cells."""
    lines = text.split('\n')
    out = []
    in_code_block = False
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            if in_code_block:
                out.append('</code></pre>')
                in_code_block = False
            else:
                out.append('<pre class="md-code-block"><code>')
                in_code_block = True
            continue
            
        if in_code_block:
            out.append(html.escape(line))
            continue
            
        # Lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            item_text = format_inline_md(stripped[2:])
            out.append(f'<li>{item_text}</li>')
            continue
        elif in_list and stripped == '':
            out.append('</ul>')
            in_list = False
            continue
            
        # Headers
        if stripped.startswith('### '):
            out.append(f'<h3>{format_inline_md(stripped[4:])}</h3>')
        elif stripped.startswith('## '):
            out.append(f'<h2>{format_inline_md(stripped[3:])}</h2>')
        elif stripped.startswith('# '):
            out.append(f'<h1>{format_inline_md(stripped[2:])}</h1>')
        elif stripped:
            out.append(f'<p>{format_inline_md(line)}</p>')
        else:
            out.append('')
            
    if in_list:
        out.append('</ul>')
    if in_code_block:
        out.append('</code></pre>')
        
    return '\n'.join(out)

def format_inline_md(text):
    escaped = html.escape(text)
    escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)
    escaped = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', escaped)
    escaped = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', escaped)
    return escaped

def ipynb_to_html(ipynb_path, output_html_path, single_page=False):
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    title = os.path.splitext(os.path.basename(ipynb_path))[0]
    
    font_size = "11px" if single_page else "12.5px"
    code_size = "10.5px" if single_page else "11.5px"
    line_h = "1.35" if single_page else "1.5"
    margin = "10mm 12mm 10mm 12mm" if single_page else "15mm 15mm 15mm 15mm"
    
    html_out = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>
  @page {{
    size: A4 portrait;
    margin: {margin};
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #1f2328;
    background-color: #ffffff;
    line-height: {line_h};
    margin: 0;
    padding: 0;
    font-size: {font_size};
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .notebook-header {{
    border-bottom: 2px solid #0969da;
    padding-bottom: 6px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .notebook-title {{
    font-size: 16px;
    font-weight: 700;
    color: #1f2328;
  }}
  .notebook-meta {{
    font-size: 10.5px;
    color: #656d76;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }}
  .cell {{
    margin-bottom: 12px;
    break-inside: auto;
  }}
  .cell-label {{
    font-size: 11px;
    font-weight: 600;
    color: #0969da;
    margin-bottom: 3px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  }}
  .input-area {{
    border: 1px solid #d0d7de;
    border-radius: 5px;
    background-color: #f8fafc;
    overflow: hidden;
  }}
  .code-container {{
    margin: 0;
    padding: 8px 12px;
    background-color: #f8fafc;
    font-family: "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    font-size: {code_size};
    line-height: {line_h};
    white-space: pre-wrap;
    word-break: break-all;
  }}
  .output-header {{
    font-size: 10.5px;
    font-weight: 600;
    color: #57606a;
    margin-top: 8px;
    margin-bottom: 3px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  }}
  .output-container {{
    margin: 0;
    padding: 8px 12px;
    background-color: #ffffff;
    border: 1px solid #e1e4e8;
    border-left: 3px solid #57606a;
    border-radius: 4px;
    font-family: "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    font-size: {code_size};
    line-height: {line_h};
    white-space: pre-wrap;
    word-break: break-all;
    color: #24292f;
  }}
  .output-error {{
    border-left-color: #cf222e;
    background-color: #fff8f8;
    color: #cf222e;
  }}
  .markdown-cell {{
    padding: 4px 0;
  }}
  .markdown-cell h1 {{ font-size: 18px; margin: 8px 0 4px; }}
  .markdown-cell h2 {{ font-size: 15px; margin: 8px 0 4px; }}
  .markdown-cell h3 {{ font-size: 13px; margin: 6px 0 4px; }}
  .markdown-cell p {{ margin: 4px 0; }}
  .markdown-cell ul {{ margin: 4px 0 4px 20px; padding: 0; }}
  .markdown-cell code {{ background: #eff1f3; padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }}
  .md-code-block {{ background: #f6f8fa; padding: 8px 10px; border-radius: 4px; }}

  /* Syntax Highlighting */
  .tok-kw {{ color: #cf222e; font-weight: 600; }}
  .tok-builtin {{ color: #0969da; font-weight: 600; }}
  .tok-str {{ color: #0a3069; }}
  .tok-num {{ color: #0550ae; font-weight: 500; }}
  .tok-comment {{ color: #6e7781; font-style: italic; }}

  /* Tables */
  table {{
    border-collapse: collapse;
    margin: 6px 0;
    width: 100%;
    font-size: 8px;
  }}
  th, td {{
    border: 1px solid #d0d7de;
    padding: 3px 4px;
    text-align: left;
    white-space: nowrap;
  }}
  th {{
    background-color: #f6f8fa;
    font-weight: 600;
  }}
</style>
</head>
<body>
  <div class="notebook-header">
    <div class="notebook-title">📓 {html.escape(title)}</div>
    <div class="notebook-meta">Jupyter Notebook Document</div>
  </div>
"""

    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type", "")
        exec_count = cell.get("execution_count", 1)
        if exec_count is None:
            exec_count = 1
            
        raw_source = "".join(cell.get("source", [])) if isinstance(cell.get("source"), list) else cell.get("source", "")
        
        if cell_type == "code":
            hl_code = highlight_python(raw_source)
            html_out += f"""
  <div class="cell">
    <div class="cell-label">In [{exec_count}]:</div>
    <div class="input-area">
      <pre class="code-container"><code>{hl_code}</code></pre>
    </div>
"""
            outputs = cell.get("outputs", [])
            for out in outputs:
                out_type = out.get("output_type", "")
                if out_type == "stream":
                    text = "".join(out.get("text", [])) if isinstance(out.get("text"), list) else out.get("text", "")
                    html_out += f"""
    <div class="output-header">Output:</div>
    <pre class="output-container">{html.escape(text)}</pre>
"""
                elif out_type in ("execute_result", "display_data"):
                    data = out.get("data", {})
                    if "image/png" in data:
                        img_b64 = "".join(data["image/png"]) if isinstance(data["image/png"], list) else data["image/png"]
                        html_out += f"""
    <div class="output-header">Output [{exec_count}]:</div>
    <div class="output-container" style="background:#fff; text-align:center;"><img src="data:image/png;base64,{img_b64}" style="max-width:100%; height:auto;" /></div>
"""
                    elif "text/html" in data:
                        h_content = "".join(data["text/html"]) if isinstance(data["text/html"], list) else data["text/html"]
                        html_out += f"""
    <div class="output-header">Output [{exec_count}]:</div>
    <div class="output-container">{h_content}</div>
"""
                    elif "text/plain" in data:
                        p_content = "".join(data["text/plain"]) if isinstance(data["text/plain"], list) else data["text/plain"]
                        html_out += f"""
    <div class="output-header">Output [{exec_count}]:</div>
    <pre class="output-container">{html.escape(p_content)}</pre>
"""
                elif out_type == "error":
                    trace = "\n".join(out.get("traceback", []))
                    clean_trace = re.sub(r'\x1b\[[0-9;]*m', '', trace)
                    html_out += f"""
    <div class="output-header" style="color:#cf222e;">Error:</div>
    <pre class="output-container output-error">{html.escape(clean_trace)}</pre>
"""
            html_out += "  </div>\n"
        elif cell_type == "markdown":
            md_html = parse_markdown(raw_source)
            html_out += f"""
  <div class="cell markdown-cell">
    {md_html}
  </div>
"""

    html_out += """
</body>
</html>
"""
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_out)


def code_only_to_html(source_path, output_html_path, name=None, student_id=None):
    """
    Renders pure Python code to HTML using Jupyter Notebook / CodeMirror style:
    - Pure white background, zero layout/borders
    - Green bold keywords, purple operators, wine-red strings, italic teal comments
    - Block-level page-break avoidance so logical functions/sections are not awkwardly split.
    """
    if source_path.endswith('.ipynb'):
        with open(source_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        blocks = []
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                src = "".join(cell.get("source", [])) if isinstance(cell.get("source"), list) else cell.get("source", "")
                if src.strip():
                    blocks.append(src)
    else:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Split into blocks by major section comments or double empty lines
        raw_sections = re.split(r'\n{3,}|(?=# -{10,})|(?=# ={10,})', content)
        blocks = [s.strip() for s in raw_sections if s.strip()]

    # Prepend student info header if provided and not already present
    prefix = ""
    if name or student_id:
        has_info = any((name and name in b) or (student_id and student_id in b) for b in blocks[:2])
        if not has_info:
            header_lines = []
            if name:
                header_lines.append(f"# 姓名：{name}")
            if student_id:
                header_lines.append(f"# 学号：{student_id}")
            prefix = "\n".join(header_lines) + "\n\n"
            if blocks:
                blocks[0] = prefix + blocks[0]
            else:
                blocks.append(prefix.strip())

    formatter = HtmlFormatter(nowrap=True)
    formatted_blocks = []

    for block in blocks:
        hl = highlight(block, PythonLexer(), formatter)
        # Keep punctuation (.,:;()[]{}) black, only style true math/assignment operators as purple
        hl = re.sub(r'<span class="o">([.,:;()\[\]{}])</span>', r'\1', hl)
        formatted_blocks.append(f'<pre class="code-block">{hl}</pre>')

    body_html = '\n'.join(formatted_blocks)
    title = os.path.splitext(os.path.basename(source_path))[0]

    html_page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 20mm 20mm 20mm 20mm;
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    margin: 0;
    padding: 0;
    background: #ffffff;
    font-family: Consolas, "SFMono-Regular", Menlo, Monaco, "Courier New", monospace;
    font-size: 10pt;
    line-height: 1.45;
  }}
  .code-block {{
    margin: 0 0 14px 0;
    padding: 0;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    white-space: pre-wrap;
    word-break: break-all;
    color: #000000;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  /* Jupyter CodeMirror / Pygments Default Light Theme */
  .k, .ow, .kc {{ color: #008000; font-weight: bold; }}
  .nb {{ color: #008000; }}
  .s, .s1, .s2, .sd {{ color: #BA2121; }}
  .m, .mi, .mf {{ color: #008000; }}
  .c, .c1, .ch, .cm {{ color: #408080; font-style: italic; }}
  .o {{ color: #AA22FF; }}
</style>
</head>
<body>
{body_html}
</body>
</html>
"""
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_page)


def find_browser():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
            
    # Check CLI path
    for name in ["google-chrome", "chromium", "chromium-browser"]:
        try:
            res = subprocess.run(["which", name], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
    return None

def convert_to_pdf(source_path, pdf_path=None, single_page=False, code_only=False, name=None, student_id=None):
    if not os.path.exists(source_path):
        print(f"Error: Source file not found: {source_path}", file=sys.stderr)
        return False

    if pdf_path is None:
        base, _ = os.path.splitext(source_path)
        pdf_path = base + ".pdf"

    browser = find_browser()
    if not browser:
        print("Error: No Chromium-based browser found (e.g. Google Chrome).", file=sys.stderr)
        return False

    temp_html = os.path.splitext(pdf_path)[0] + "_temp_preview.html"
    try:
        if code_only:
            code_only_to_html(source_path, temp_html, name=name, student_id=student_id)
        else:
            ipynb_to_html(source_path, temp_html, single_page=single_page)

        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            f"--print-to-pdf={pdf_path}",
            "--no-pdf-header-footer",
            temp_html
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(pdf_path):
            print(f"Exported successfully: {pdf_path}")
            return True
        else:
            print("Export failed: PDF file was not generated.", file=sys.stderr)
            return False
    finally:
        if os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except Exception:
                pass

def main():
    parser = argparse.ArgumentParser(description="Export Jupyter Notebook (.ipynb) or Python script (.py) to PDF")
    parser.add_argument("source", help="Path to the .ipynb or .py file")
    parser.add_argument("-o", "--output", help="Output .pdf file path (default: same name as source)")
    parser.add_argument("--code-only", action="store_true", help="Pure code export with Jupyter CodeMirror syntax styling (no cell borders, pure white background)")
    parser.add_argument("--single-page", action="store_true", help="Optimize styling to fit compact notebooks onto a single page")
    parser.add_argument("--name", help="Student name to include in header comment")
    parser.add_argument("--student-id", help="Student ID to include in header comment")
    args = parser.parse_args()

    success = convert_to_pdf(
        args.source,
        args.output,
        single_page=args.single_page,
        code_only=args.code_only,
        name=args.name,
        student_id=args.student_id
    )
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
