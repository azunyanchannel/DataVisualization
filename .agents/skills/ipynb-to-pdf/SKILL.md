---
name: ipynb-to-pdf
description: >-
  Exports and converts Jupyter Notebook (.ipynb) or Python script (.py) files to clean, professionally formatted PDF documents
  using headless Chrome. Supports both rich multi-page/single-page notebooks and pure-code Jupyter CodeMirror styled PDFs
  ("导出PDF", "转成pdf", "生成pdf", "纯代码pdf", "export notebook to pdf").
---

# Jupyter Notebook & Python to PDF Exporter

This skill provides an automated workflow to export Jupyter Notebook (`.ipynb`) and Python script (`.py`) files into high-quality PDF files without requiring LaTeX or Pandoc. It renders files into styled HTML and prints to PDF via headless Google Chrome / Chromium.

## When to Use
- User asks to export, convert, or download a `.ipynb` or `.py` file as PDF.
- User needs a submission-ready (A4) document of their notebook code and outputs.
- User specifically requests a **pure-code** PDF with student info, matching the classic Jupyter Notebook / CodeMirror editor style.

## Export Modes

### Mode 1: 纯代码 PDF 导出 (Jupyter CodeMirror / Word 粘贴风格)
**适用场景**：用户要求“纯代码、姓名、学号”、“像从 Jupyter Notebook 复制到 Word 粘贴一样”、“不要任何额外 layout/边框/输出”。

```bash
# 从 .py 文件导出纯代码 PDF
python3 ~/.gemini/config/skills/ipynb-to-pdf/scripts/export_notebook.py \
  "path/to/script.py" \
  -o "path/to/17420249605674沈美梓.pdf" \
  --code-only \
  --name "沈美梓" \
  --student-id "17420249605674"

# 从 .ipynb 文件仅提取代码导出纯代码 PDF
python3 ~/.gemini/config/skills/ipynb-to-pdf/scripts/export_notebook.py \
  "path/to/notebook.ipynb" \
  -o "path/to/17420249605674沈美梓.pdf" \
  --code-only \
  --name "沈美梓" \
  --student-id "17420249605674"
```

**视觉特性：**
- **纯白底色，零 Layout**：无单元格灰色背景框、无外边框、无 `In [x]`、无运行输出，如纯白页面直接粘贴代码。
- **Jupyter Notebook 经典代码高亮**（与 CodeMirror 1:1 对齐）：
  - 关键字 (`for`, `in`, `import`, `True`)：加粗绿色 (`#008000; font-weight: bold;`)
  - 运算与赋值符 (`=`, `+`, `*`, `==`)：经典紫色 (`#AA22FF;`)
  - 字符串 (`'...'`, `"..."`)：经典酒红色 (`#BA2121;`)
  - 数值 (`0`, `2020`)：纯绿色 (`#008000;`)
  - 注释与个人信息 (`# ...`)：斜体青灰色 (`#408080; font-style: italic;`)
  - 变量名/括号/标点：纯黑色 (`#000000;`)
- **智能分页控制**：每个逻辑块/函数自动配置 `break-inside: avoid;`，避免跨页在函数调用参数中间截断。
- **单一文件输出**：只生成一份目标 PDF，避免生成同名冗余副本造成混淆。

---

### Mode 2: 完整 Notebook 导出 (含 Markdown、代码、图表输出)
**适用场景**：需要展示完整作业报告、图表可视化结果与 Markdown 分析结论。

```bash
# 标准多页完整导出
python3 ~/.gemini/config/skills/ipynb-to-pdf/scripts/export_notebook.py "/path/to/notebook.ipynb"

# 单页紧凑导出 (适合简短作业)
python3 ~/.gemini/config/skills/ipynb-to-pdf/scripts/export_notebook.py "/path/to/notebook.ipynb" --single-page

# 自定义输出路径
python3 ~/.gemini/config/skills/ipynb-to-pdf/scripts/export_notebook.py "/path/to/notebook.ipynb" -o "/path/to/output.pdf"
```

**视觉特性：**
- 代码语法高亮与单元格标签 (`In [x]`)
- 自动渲染 stdout 终端输出、HTML 表格以及 Matplotlib/Seaborn 高清 PNG 图片
- 优先展示高清图表输出，自动过滤冗余的 `<Figure size ...>` 文本
