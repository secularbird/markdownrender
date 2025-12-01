# MarkdownRender

A service to render Markdown documents containing Mermaid diagrams, PlantUML diagrams, and images into HTML, Word (DOCX), Excel (XLSX), and PDF formats.

## Features

- **Markdown Rendering**: Full support for CommonMark with extensions
- **Mermaid Diagrams**: Server-side rendering (with mmdc) or client-side rendering fallback
- **PlantUML Diagrams**: Automatic rendering via PlantUML server
- **Multiple Output Formats**:
  - HTML with responsive styling and syntax highlighting
  - PDF with proper pagination and styling
  - Word (DOCX) with formatting preservation
  - Excel (XLSX) for table data extraction
- **REST API**: Easy-to-use endpoints for programmatic access
- **CLI Tool**: Command-line interface for batch processing

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Render markdown to HTML
markdownrender render document.md -f html -o output.html

# Render markdown to PDF
markdownrender render document.md -f pdf -o output.pdf

# Render markdown to Word document
markdownrender render document.md -f docx -o output.docx

# Render tables to Excel
markdownrender render document.md -f xlsx -o output.xlsx

# Start the API server
markdownrender server --port 5000
```

### API Usage

Start the server:
```bash
markdownrender server
```

Then make requests:

```bash
# Render to HTML
curl -X POST http://localhost:5000/render/html \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello World\n\nThis is **bold** text."}'

# Render to PDF
curl -X POST http://localhost:5000/render/pdf \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# My Document", "title": "My PDF"}' \
  --output document.pdf

# Render to Word
curl -X POST http://localhost:5000/render/docx \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Report\n\n## Summary\n\nContent here."}' \
  --output document.docx

# Unified render endpoint
curl -X POST http://localhost:5000/render \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello", "format": "html", "options": {"include_toc": true}}'
```

### Python Usage

```python
from markdownrender.parser import MarkdownParser
from markdownrender.renderers import HTMLRenderer, PDFRenderer, WordRenderer, ExcelRenderer

# Parse markdown
parser = MarkdownParser()
html_content = parser.parse("# Hello World")

# Render to HTML
html_renderer = HTMLRenderer()
full_html = html_renderer.render("# Hello World", title="My Document", include_toc=True)

# Render to PDF
pdf_renderer = PDFRenderer()
pdf_bytes = pdf_renderer.render("# Hello World", title="My Document")

# Render to Word
word_renderer = WordRenderer()
docx_bytes = word_renderer.render("# Hello World", title="My Document")

# Render to Excel
excel_renderer = ExcelRenderer()
xlsx_bytes = excel_renderer.render("| A | B |\n|---|---|\n| 1 | 2 |")
```

## Supported Markdown Features

### Diagrams

#### Mermaid Diagrams
```markdown
\`\`\`mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
\`\`\`
```

#### PlantUML Diagrams
```markdown
\`\`\`plantuml
Alice -> Bob: Hello
Bob --> Alice: Hi!
\`\`\`
```

### Tables
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### Code Blocks
```markdown
\`\`\`python
def hello():
    print("Hello, World!")
\`\`\`
```

### Other Features
- Headers (h1-h6)
- Bold, italic, strikethrough
- Lists (ordered and unordered)
- Links and images
- Blockquotes
- Horizontal rules
- Table of contents generation

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/render/html` | POST | Render to HTML |
| `/render/pdf` | POST | Render to PDF |
| `/render/docx` | POST | Render to Word |
| `/render/xlsx` | POST | Render to Excel |
| `/render` | POST | Unified render (specify format) |

## Configuration

Environment variables:
- `PLANTUML_SERVER`: PlantUML server URL (default: http://www.plantuml.com/plantuml)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=markdownrender

# Run linter
flake8 src/markdownrender
```

## License

MIT License
