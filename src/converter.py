"""
Motor de conversión de documentos a Markdown usando Microsoft MarkItDown.
Soporta: DOCX, XLSX, PPTX, PDF, CSV, JSON, XML, HTML, TXT, Imágenes, etc.
"""

import os
import time
from typing import Tuple, Dict, Any
from markitdown import MarkItDown


class DocumentConverter:
    """Clase principal que encapsula MarkItDown para convertir diversos formatos de archivo a Markdown."""

    SUPPORTED_EXTENSIONS = {
        # Documentos Office
        ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
        # Documentos y datos
        ".pdf", ".csv", ".json", ".xml", ".html", ".htm", ".txt", ".md",
        # Archivos comprimidos y código
        ".zip", ".ipynb",
        # Multimedia
        ".mp3", ".wav", ".jpg", ".jpeg", ".png"
    }

    def __init__(self, enable_plugins: bool = False):
        """Inicializa la instancia de MarkItDown."""
        self.md = MarkItDown(enable_plugins=enable_plugins)

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Obtiene información legible sobre el archivo seleccionado."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo no existe: {file_path}")

        file_stat = os.stat(file_path)
        size_bytes = file_stat.st_size

        if size_bytes < 1024:
            size_formatted = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_formatted = f"{size_bytes / 1024:.1f} KB"
        else:
            size_formatted = f"{size_bytes / (1024 * 1024):.2f} MB"

        base_name = os.path.basename(file_path)
        name_without_ext, ext = os.path.splitext(base_name)

        return {
            "path": file_path,
            "filename": base_name,
            "stem": name_without_ext,
            "ext": ext.lower(),
            "suggested_output_name": f"{name_without_ext}.md",
            "size_bytes": size_bytes,
            "size_formatted": size_formatted,
        }

    def convert(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Convierte el archivo a Markdown y retorna una tupla (markdown_text, metadata).
        """
        info = self.get_file_info(file_path)
        start_time = time.perf_counter()

        # Conversión con MarkItDown
        result = self.md.convert(file_path)
        elapsed_time = time.perf_counter() - start_time

        markdown_text = result.text_content or ""
        lines_count = len(markdown_text.splitlines())
        words_count = len(markdown_text.split())
        chars_count = len(markdown_text)

        metadata = {
            **info,
            "elapsed_seconds": round(elapsed_time, 2),
            "lines": lines_count,
            "words": words_count,
            "chars": chars_count,
            "title": getattr(result, "title", None) or info["stem"]
        }

        return markdown_text, metadata
