"""Tests for the Flask API."""

import pytest
import json

from markdownrender.api import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "markdownrender"


class TestHTMLEndpoint:
    """Test HTML rendering endpoint."""

    def test_render_html_basic(self, client):
        """Test basic HTML rendering."""
        response = client.post(
            "/render/html",
            json={"markdown": "# Hello World"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.content_type == "text/html; charset=utf-8"
        assert b"Hello World" in response.data

    def test_render_html_with_title(self, client):
        """Test HTML rendering with custom title."""
        response = client.post(
            "/render/html",
            json={"markdown": "# Content", "title": "My Title"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert b"<title>My Title</title>" in response.data

    def test_render_html_fragment(self, client):
        """Test HTML fragment rendering."""
        response = client.post(
            "/render/html",
            json={"markdown": "**bold**", "fragment": True},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" not in response.data
        assert b"<strong>bold</strong>" in response.data

    def test_render_html_missing_markdown(self, client):
        """Test error when markdown is missing."""
        response = client.post(
            "/render/html",
            json={},
            content_type="application/json",
        )
        assert response.status_code == 400


class TestDocxEndpoint:
    """Test Word document rendering endpoint."""

    def test_render_docx_basic(self, client):
        """Test basic DOCX rendering."""
        response = client.post(
            "/render/docx",
            json={"markdown": "# Hello World"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.content_type
        assert response.data[:4] == b"PK\x03\x04"  # ZIP signature

    def test_render_docx_missing_markdown(self, client):
        """Test error when markdown is missing."""
        response = client.post(
            "/render/docx",
            json={},
            content_type="application/json",
        )
        assert response.status_code == 400


class TestXlsxEndpoint:
    """Test Excel rendering endpoint."""

    def test_render_xlsx_basic(self, client):
        """Test basic XLSX rendering."""
        response = client.post(
            "/render/xlsx",
            json={"markdown": "| A | B |\n|---|---|\n| 1 | 2 |"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.content_type
        assert response.data[:4] == b"PK\x03\x04"  # ZIP signature


class TestUnifiedRenderEndpoint:
    """Test unified /render endpoint."""

    def test_render_unified_html(self, client):
        """Test unified render endpoint for HTML."""
        response = client.post(
            "/render",
            json={"markdown": "# Hello", "format": "html"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert b"Hello" in response.data

    def test_render_unified_docx(self, client):
        """Test unified render endpoint for DOCX."""
        response = client.post(
            "/render",
            json={"markdown": "# Hello", "format": "docx"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.data[:4] == b"PK\x03\x04"

    def test_render_unified_invalid_format(self, client):
        """Test unified render endpoint with invalid format."""
        response = client.post(
            "/render",
            json={"markdown": "# Hello", "format": "invalid"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_render_unified_missing_format(self, client):
        """Test unified render endpoint without format."""
        response = client.post(
            "/render",
            json={"markdown": "# Hello"},
            content_type="application/json",
        )
        assert response.status_code == 400
