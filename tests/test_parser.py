"""Tests for the MarkdownParser class."""

import pytest

from markdownrender.parser import MarkdownParser


class TestMarkdownParser:
    """Test cases for MarkdownParser."""

    def test_parse_basic_markdown(self):
        """Test parsing basic markdown elements."""
        parser = MarkdownParser()
        markdown_text = "# Hello World\n\nThis is a paragraph."
        html = parser.parse(markdown_text)

        assert "<h1" in html
        assert "Hello World" in html
        assert "<p>This is a paragraph.</p>" in html

    def test_parse_code_blocks(self):
        """Test parsing fenced code blocks."""
        parser = MarkdownParser()
        markdown_text = """
```python
def hello():
    print("Hello")
```
"""
        html = parser.parse(markdown_text)
        assert "highlight" in html or "<code" in html
        assert "hello" in html

    def test_parse_tables(self):
        """Test parsing markdown tables."""
        parser = MarkdownParser()
        markdown_text = """
| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |
"""
        html = parser.parse(markdown_text)
        assert "<table>" in html or "<table" in html
        assert "Alice" in html
        assert "30" in html

    def test_parse_mermaid_diagram(self):
        """Test parsing mermaid diagrams."""
        parser = MarkdownParser()
        markdown_text = """
```mermaid
graph TD
    A --> B
    B --> C
```
"""
        html = parser.parse(markdown_text)
        # Should create mermaid pre element or diagram div
        assert "mermaid" in html
        assert "A -->" in html or "A --&gt;" in html

    def test_parse_plantuml_diagram(self):
        """Test parsing PlantUML diagrams."""
        parser = MarkdownParser()
        markdown_text = """
```plantuml
Bob -> Alice : hello
```
"""
        html = parser.parse(markdown_text)
        # Should create plantuml diagram with image
        assert "plantuml" in html.lower()
        assert "img" in html or "plantuml-diagram" in html

    def test_get_toc(self):
        """Test table of contents generation."""
        parser = MarkdownParser()
        markdown_text = """
# Introduction

Some text.

## Chapter 1

More text.

## Chapter 2

Even more text.
"""
        parser.parse(markdown_text)
        toc = parser.get_toc()
        # TOC should contain links to headings
        assert "Introduction" in toc or "chapter" in toc.lower()

    def test_extract_images(self):
        """Test image extraction from markdown."""
        parser = MarkdownParser()
        markdown_text = """
# Document with images

![Logo](images/logo.png)
![Photo](https://example.com/photo.jpg)
"""
        images = parser.extract_images(markdown_text)
        assert len(images) == 2
        assert ("Logo", "images/logo.png") in images
        assert ("Photo", "https://example.com/photo.jpg") in images

    def test_parse_inline_formatting(self):
        """Test inline formatting like bold, italic, code."""
        parser = MarkdownParser()
        markdown_text = "**bold** and *italic* and `code`"
        html = parser.parse(markdown_text)

        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
        assert "<code>code</code>" in html

    def test_parse_links(self):
        """Test parsing links."""
        parser = MarkdownParser()
        markdown_text = "[Click here](https://example.com)"
        html = parser.parse(markdown_text)

        assert '<a href="https://example.com"' in html
        assert "Click here</a>" in html

    def test_parser_reset(self):
        """Test that parser resets between parses."""
        parser = MarkdownParser()

        # First parse
        parser.parse("# First")
        toc1 = parser.get_toc()

        # Second parse
        parser.parse("# Second")
        toc2 = parser.get_toc()

        assert "First" not in toc2
        assert "Second" in toc2
