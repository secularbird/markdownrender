"""Tests for the renderer classes."""

import pytest

from markdownrender.parser import MarkdownParser
from markdownrender.renderers import HTMLRenderer, WordRenderer, ExcelRenderer


class TestHTMLRenderer:
    """Test cases for HTMLRenderer."""

    def test_render_basic_html(self):
        """Test basic HTML rendering."""
        renderer = HTMLRenderer()
        markdown_text = "# Hello World"
        html = renderer.render(markdown_text, title="Test")

        assert "<!DOCTYPE html>" in html
        assert "<title>Test</title>" in html
        assert "<h1" in html
        assert "Hello World" in html

    def test_render_with_css(self):
        """Test HTML rendering includes CSS by default."""
        renderer = HTMLRenderer()
        markdown_text = "# Title"
        html = renderer.render(markdown_text)

        assert "<style>" in html

    def test_render_without_css(self):
        """Test HTML rendering can exclude CSS."""
        renderer = HTMLRenderer()
        markdown_text = "# Title"
        html = renderer.render(markdown_text, include_css=False)

        assert "<style>" not in html

    def test_render_with_toc(self):
        """Test HTML rendering with table of contents."""
        renderer = HTMLRenderer()
        markdown_text = """
# Chapter 1

Content.

# Chapter 2

More content.
"""
        html = renderer.render(markdown_text, include_toc=True)
        assert 'class="toc"' in html

    def test_render_fragment(self):
        """Test rendering HTML fragment without document wrapper."""
        renderer = HTMLRenderer()
        markdown_text = "**Bold text**"
        html = renderer.render_fragment(markdown_text)

        assert "<!DOCTYPE html>" not in html
        assert "<strong>Bold text</strong>" in html

    def test_render_mermaid_script(self):
        """Test that Mermaid script is included."""
        renderer = HTMLRenderer()
        markdown_text = "# Test"
        html = renderer.render(markdown_text, include_mermaid_js=True)

        assert "mermaid.initialize" in html

    def test_render_with_custom_table_style(self):
        """Test HTML rendering with custom table CSS."""
        custom_css = """
        table { border: 2px solid red; }
        th { background-color: #ff0000; }
        """
        renderer = HTMLRenderer(table_style=custom_css)
        markdown_text = """
| Name | Age |
|------|-----|
| Alice | 30 |
"""
        html = renderer.render(markdown_text)
        
        assert "border: 2px solid red" in html
        assert "background-color: #ff0000" in html


class TestWordRenderer:
    """Test cases for WordRenderer."""

    def test_render_basic_docx(self):
        """Test basic Word document rendering."""
        renderer = WordRenderer()
        markdown_text = "# Hello World\n\nThis is a paragraph."
        docx_bytes = renderer.render(markdown_text, title="Test Document")

        # DOCX is a ZIP file with specific signature
        assert docx_bytes[:4] == b"PK\x03\x04"
        assert len(docx_bytes) > 0

    def test_render_with_table(self):
        """Test Word document with table."""
        renderer = WordRenderer()
        markdown_text = """
| Name | Age |
|------|-----|
| Alice | 30 |
"""
        docx_bytes = renderer.render(markdown_text)
        assert len(docx_bytes) > 0

    def test_render_with_code(self):
        """Test Word document with code block."""
        renderer = WordRenderer()
        markdown_text = """
```python
print("hello")
```
"""
        docx_bytes = renderer.render(markdown_text)
        assert len(docx_bytes) > 0

    def test_render_with_lists(self):
        """Test Word document with lists."""
        renderer = WordRenderer()
        markdown_text = """
- Item 1
- Item 2
- Item 3

1. First
2. Second
"""
        docx_bytes = renderer.render(markdown_text)
        assert len(docx_bytes) > 0

    def test_render_with_custom_table_style(self):
        """Test Word document with custom table style."""
        renderer = WordRenderer(table_style="Light Shading")
        markdown_text = """
| Name | Age |
|------|-----|
| Alice | 30 |
"""
        docx_bytes = renderer.render(markdown_text)
        assert len(docx_bytes) > 0
        # Table style is applied internally, just verify it renders


class TestExcelRenderer:
    """Test cases for ExcelRenderer."""

    def test_render_basic_xlsx(self):
        """Test basic Excel rendering."""
        renderer = ExcelRenderer()
        markdown_text = """
| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |
"""
        xlsx_bytes = renderer.render(markdown_text, title="Test")

        # XLSX is also a ZIP file
        assert xlsx_bytes[:4] == b"PK\x03\x04"
        assert len(xlsx_bytes) > 0

    def test_render_multiple_tables(self):
        """Test Excel with multiple tables."""
        renderer = ExcelRenderer()
        markdown_text = """
| A | B |
|---|---|
| 1 | 2 |

Some text.

| C | D |
|---|---|
| 3 | 4 |
"""
        xlsx_bytes = renderer.render(markdown_text)
        assert len(xlsx_bytes) > 0

    def test_render_no_tables(self):
        """Test Excel rendering with no tables - should put text content."""
        renderer = ExcelRenderer()
        markdown_text = "Just some text without tables."
        xlsx_bytes = renderer.render(markdown_text)
        assert len(xlsx_bytes) > 0
