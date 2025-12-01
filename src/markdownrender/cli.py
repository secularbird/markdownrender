"""
Command-line interface for the Markdown rendering service.
"""

import argparse
import sys
from pathlib import Path

from .parser import MarkdownParser
from .renderers import HTMLRenderer, PDFRenderer, WordRenderer, ExcelRenderer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="markdownrender",
        description="Render Markdown with Mermaid, PlantUML and images to various formats",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Render command
    render_parser = subparsers.add_parser("render", help="Render markdown file to output format")
    render_parser.add_argument("input", help="Input Markdown file path")
    render_parser.add_argument(
        "-o", "--output", help="Output file path (default: input name with new extension)"
    )
    render_parser.add_argument(
        "-f",
        "--format",
        choices=["html", "pdf", "docx", "xlsx"],
        default="html",
        help="Output format (default: html)",
    )
    render_parser.add_argument("-t", "--title", help="Document title (default: filename)")
    render_parser.add_argument(
        "--toc", action="store_true", help="Include table of contents"
    )
    render_parser.add_argument(
        "--no-css", action="store_true", help="Exclude default CSS (HTML only)"
    )

    # Server command
    server_parser = subparsers.add_parser("server", help="Start the rendering API server")
    server_parser.add_argument(
        "-p", "--port", type=int, default=5000, help="Server port (default: 5000)"
    )
    server_parser.add_argument(
        "-H", "--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode"
    )

    args = parser.parse_args()

    if args.command == "render":
        render_file(args)
    elif args.command == "server":
        start_server(args)
    else:
        parser.print_help()
        sys.exit(1)


def render_file(args):
    """Render a Markdown file to the specified format."""
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Read input file
    markdown_text = input_path.read_text(encoding="utf-8")

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        ext_map = {"html": ".html", "pdf": ".pdf", "docx": ".docx", "xlsx": ".xlsx"}
        output_path = input_path.with_suffix(ext_map[args.format])

    # Determine title
    title = args.title or input_path.stem

    # Create renderer
    md_parser = MarkdownParser()

    try:
        if args.format == "html":
            renderer = HTMLRenderer(parser=md_parser)
            html = renderer.render(
                markdown_text,
                title=title,
                include_toc=args.toc,
                include_css=not args.no_css,
            )
            output_path.write_text(html, encoding="utf-8")

        elif args.format == "pdf":
            renderer = PDFRenderer(parser=md_parser)
            renderer.render_to_file(
                markdown_text,
                str(output_path),
                title=title,
                include_toc=args.toc,
            )

        elif args.format == "docx":
            renderer = WordRenderer(parser=md_parser)
            renderer.render_to_file(
                markdown_text,
                str(output_path),
                title=title,
            )

        elif args.format == "xlsx":
            renderer = ExcelRenderer(parser=md_parser)
            renderer.render_to_file(
                markdown_text,
                str(output_path),
                title=title,
            )

        print(f"Successfully rendered to: {output_path}")

    except Exception as e:
        print(f"Error rendering file: {e}", file=sys.stderr)
        sys.exit(1)


def start_server(args):
    """Start the Flask API server."""
    from .api import create_app

    app = create_app()
    print(f"Starting MarkdownRender server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
