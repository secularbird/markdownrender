"""
Flask REST API for the Markdown rendering service.
"""

import io
from flask import Flask, request, jsonify, send_file, Response

from .parser import MarkdownParser
from .renderers import HTMLRenderer, PDFRenderer, WordRenderer, ExcelRenderer


def create_app(config: dict = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    if config:
        app.config.update(config)

    # Initialize components
    parser = MarkdownParser(
        plantuml_server=app.config.get(
            "PLANTUML_SERVER", "http://www.plantuml.com/plantuml"
        )
    )
    html_renderer = HTMLRenderer(parser=parser)
    pdf_renderer = PDFRenderer(parser=parser)
    word_renderer = WordRenderer(parser=parser)
    excel_renderer = ExcelRenderer(parser=parser)

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "service": "markdownrender"})

    @app.route("/render/html", methods=["POST"])
    def render_html():
        """Render Markdown to HTML.

        Request body:
            - markdown: str - The markdown content to render
            - title: str (optional) - Document title
            - include_toc: bool (optional) - Include table of contents
            - include_css: bool (optional) - Include default CSS
            - fragment: bool (optional) - Return only HTML fragment without document wrapper

        Returns:
            HTML content as text/html
        """
        data = request.get_json()

        if not data or "markdown" not in data:
            return jsonify({"error": "Missing 'markdown' field in request body"}), 400

        markdown_text = data["markdown"]
        title = data.get("title", "Document")
        include_toc = data.get("include_toc", False)
        include_css = data.get("include_css", True)
        fragment = data.get("fragment", False)

        try:
            if fragment:
                html = html_renderer.render_fragment(markdown_text)
            else:
                html = html_renderer.render(
                    markdown_text,
                    title=title,
                    include_toc=include_toc,
                    include_css=include_css,
                )
            return Response(html, mimetype="text/html")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/render/pdf", methods=["POST"])
    def render_pdf():
        """Render Markdown to PDF.

        Request body:
            - markdown: str - The markdown content to render
            - title: str (optional) - Document title
            - include_toc: bool (optional) - Include table of contents

        Returns:
            PDF file as application/pdf
        """
        data = request.get_json()

        if not data or "markdown" not in data:
            return jsonify({"error": "Missing 'markdown' field in request body"}), 400

        markdown_text = data["markdown"]
        title = data.get("title", "Document")
        include_toc = data.get("include_toc", False)

        try:
            pdf_bytes = pdf_renderer.render(
                markdown_text, title=title, include_toc=include_toc
            )
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"{title}.pdf",
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/render/docx", methods=["POST"])
    def render_docx():
        """Render Markdown to Word document (DOCX).

        Request body:
            - markdown: str - The markdown content to render
            - title: str (optional) - Document title

        Returns:
            DOCX file as application/vnd.openxmlformats-officedocument.wordprocessingml.document
        """
        data = request.get_json()

        if not data or "markdown" not in data:
            return jsonify({"error": "Missing 'markdown' field in request body"}), 400

        markdown_text = data["markdown"]
        title = data.get("title", "Document")

        try:
            docx_bytes = word_renderer.render(markdown_text, title=title)
            return send_file(
                io.BytesIO(docx_bytes),
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                as_attachment=True,
                download_name=f"{title}.docx",
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/render/xlsx", methods=["POST"])
    def render_xlsx():
        """Render Markdown tables to Excel (XLSX).

        Request body:
            - markdown: str - The markdown content to render
            - title: str (optional) - Document/sheet title

        Returns:
            XLSX file as application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        """
        data = request.get_json()

        if not data or "markdown" not in data:
            return jsonify({"error": "Missing 'markdown' field in request body"}), 400

        markdown_text = data["markdown"]
        title = data.get("title", "Document")

        try:
            xlsx_bytes = excel_renderer.render(markdown_text, title=title)
            return send_file(
                io.BytesIO(xlsx_bytes),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=f"{title}.xlsx",
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/render", methods=["POST"])
    def render():
        """Unified render endpoint with format selection.

        Request body:
            - markdown: str - The markdown content to render
            - format: str - Output format (html, pdf, docx, xlsx)
            - title: str (optional) - Document title
            - options: dict (optional) - Format-specific options

        Returns:
            Rendered document in the requested format
        """
        data = request.get_json()

        if not data or "markdown" not in data:
            return jsonify({"error": "Missing 'markdown' field in request body"}), 400

        if "format" not in data:
            return jsonify({"error": "Missing 'format' field in request body"}), 400

        output_format = data["format"].lower()
        markdown_text = data["markdown"]
        title = data.get("title", "Document")
        options = data.get("options", {})

        try:
            if output_format == "html":
                html = html_renderer.render(
                    markdown_text,
                    title=title,
                    include_toc=options.get("include_toc", False),
                    include_css=options.get("include_css", True),
                )
                return Response(html, mimetype="text/html")

            elif output_format == "pdf":
                pdf_bytes = pdf_renderer.render(
                    markdown_text,
                    title=title,
                    include_toc=options.get("include_toc", False),
                )
                return send_file(
                    io.BytesIO(pdf_bytes),
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=f"{title}.pdf",
                )

            elif output_format == "docx":
                docx_bytes = word_renderer.render(markdown_text, title=title)
                docx_mime = "application/vnd.openxmlformats-officedocument"
                docx_mime += ".wordprocessingml.document"
                return send_file(
                    io.BytesIO(docx_bytes),
                    mimetype=docx_mime,
                    as_attachment=True,
                    download_name=f"{title}.docx",
                )

            elif output_format == "xlsx":
                xlsx_bytes = excel_renderer.render(markdown_text, title=title)
                return send_file(
                    io.BytesIO(xlsx_bytes),
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    as_attachment=True,
                    download_name=f"{title}.xlsx",
                )

            else:
                err_msg = f"Unsupported format: {output_format}. "
                err_msg += "Supported formats: html, pdf, docx, xlsx"
                return jsonify({"error": err_msg}), 400

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


# Application instance for gunicorn
app = create_app()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host="0.0.0.0", port=5000)
