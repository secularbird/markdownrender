"""
Markdown parser with support for Mermaid, PlantUML diagrams and embedded images.
"""

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class MermaidPreprocessor(Preprocessor):
    """Preprocessor to convert Mermaid code blocks to images."""

    MERMAID_PATTERN = re.compile(
        r"```mermaid\s*\n(.*?)```", re.MULTILINE | re.DOTALL
    )

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config

    def run(self, lines: list) -> list:
        text = "\n".join(lines)
        new_text = self.MERMAID_PATTERN.sub(self._render_mermaid, text)
        return new_text.split("\n")

    def _render_mermaid(self, match) -> str:
        """Render Mermaid diagram to SVG or return placeholder."""
        mermaid_code = match.group(1).strip()

        # Try to render using mmdc (mermaid-cli) if available
        try:
            svg_content = self._render_with_mmdc(mermaid_code)
            if svg_content:
                return f'<div class="mermaid-diagram">{svg_content}</div>'
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        # Fallback: embed as script for client-side rendering
        return self._create_client_side_mermaid(mermaid_code)

    def _render_with_mmdc(self, mermaid_code: str) -> Optional[str]:
        """Render Mermaid diagram using mmdc CLI tool."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".mmd", delete=False
        ) as input_file:
            input_file.write(mermaid_code)
            input_path = input_file.name

        output_path = input_path.replace(".mmd", ".svg")

        try:
            result = subprocess.run(
                ["mmdc", "-i", input_path, "-o", output_path, "-b", "transparent"],
                capture_output=True,
                timeout=30,
            )
            if result.returncode == 0 and Path(output_path).exists():
                with open(output_path, "r") as f:
                    return f.read()
        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

        return None

    def _create_client_side_mermaid(self, mermaid_code: str) -> str:
        """Create HTML for client-side Mermaid rendering."""
        diagram_id = hashlib.md5(mermaid_code.encode()).hexdigest()[:8]
        escaped_code = mermaid_code.replace("<", "&lt;").replace(">", "&gt;")
        return f'<pre class="mermaid" id="mermaid-{diagram_id}">{escaped_code}</pre>'


class PlantUMLPreprocessor(Preprocessor):
    """Preprocessor to convert PlantUML code blocks to images."""

    PLANTUML_PATTERN = re.compile(
        r"```plantuml\s*\n(.*?)```", re.MULTILINE | re.DOTALL
    )

    def __init__(self, md, config):
        super().__init__(md)
        self.config = config
        self.plantuml_server = config.get("plantuml_server", "http://www.plantuml.com/plantuml")

    def run(self, lines: list) -> list:
        text = "\n".join(lines)
        new_text = self.PLANTUML_PATTERN.sub(self._render_plantuml, text)
        return new_text.split("\n")

    def _render_plantuml(self, match) -> str:
        """Render PlantUML diagram to SVG."""
        plantuml_code = match.group(1).strip()

        # Add @startuml/@enduml if not present
        if not plantuml_code.startswith("@start"):
            plantuml_code = f"@startuml\n{plantuml_code}\n@enduml"

        # Generate PlantUML URL for server-side rendering
        encoded = self._encode_plantuml(plantuml_code)
        svg_url = f"{self.plantuml_server}/svg/{encoded}"

        return f'<div class="plantuml-diagram"><img src="{svg_url}" alt="PlantUML Diagram" /></div>'

    def _encode_plantuml(self, text: str) -> str:
        """Encode PlantUML text for URL."""
        import zlib

        compressed = zlib.compress(text.encode("utf-8"))[2:-4]
        return self._encode64(compressed)

    def _encode64(self, data: bytes) -> str:
        """Encode bytes to PlantUML's custom base64."""
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
        result = []

        for i in range(0, len(data), 3):
            chunk = data[i:i + 3]
            if len(chunk) == 3:
                b1, b2, b3 = chunk
                result.append(alphabet[b1 >> 2])
                result.append(alphabet[((b1 & 0x3) << 4) | (b2 >> 4)])
                result.append(alphabet[((b2 & 0xF) << 2) | (b3 >> 6)])
                result.append(alphabet[b3 & 0x3F])
            elif len(chunk) == 2:
                b1, b2 = chunk
                result.append(alphabet[b1 >> 2])
                result.append(alphabet[((b1 & 0x3) << 4) | (b2 >> 4)])
                result.append(alphabet[(b2 & 0xF) << 2])
            elif len(chunk) == 1:
                b1 = chunk[0]
                result.append(alphabet[b1 >> 2])
                result.append(alphabet[(b1 & 0x3) << 4])

        return "".join(result)


class DiagramExtension(Extension):
    """Markdown extension for Mermaid and PlantUML diagrams."""

    def __init__(self, **kwargs):
        self.config = {
            "plantuml_server": [
                "http://www.plantuml.com/plantuml",
                "PlantUML server URL",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            MermaidPreprocessor(md, self.getConfigs()),
            "mermaid",
            priority=30,
        )
        md.preprocessors.register(
            PlantUMLPreprocessor(md, self.getConfigs()),
            "plantuml",
            priority=29,
        )


class MarkdownParser:
    """Parse Markdown content with support for diagrams and images."""

    def __init__(
        self,
        plantuml_server: str = "http://www.plantuml.com/plantuml",
    ):
        self.plantuml_server = plantuml_server
        self._md = self._create_markdown_instance()

    def _create_markdown_instance(self) -> markdown.Markdown:
        """Create configured Markdown instance."""
        return markdown.Markdown(
            extensions=[
                "tables",
                "fenced_code",
                "codehilite",
                "toc",
                "attr_list",
                "md_in_html",
                DiagramExtension(plantuml_server=self.plantuml_server),
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "linenums": False,
                },
                "toc": {
                    "permalink": True,
                },
            },
        )

    def parse(self, markdown_text: str) -> str:
        """Parse Markdown text to HTML."""
        self._md.reset()
        return self._md.convert(markdown_text)

    def get_toc(self) -> str:
        """Get table of contents from last parsed document."""
        return getattr(self._md, "toc", "")

    def extract_images(self, markdown_text: str) -> list[Tuple[str, str]]:
        """Extract image references from Markdown text.

        Returns list of tuples (alt_text, image_path/url)
        """
        image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
        return image_pattern.findall(markdown_text)
