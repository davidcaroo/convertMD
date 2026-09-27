"""
Motor de conversión de documentos a Markdown usando Microsoft MarkItDown y OCR para imágenes.
Soporta: DOCX, XLSX, PPTX, PDF, CSV, JSON, XML, HTML, TXT, Imágenes (PNG, JPG, etc. con OCR), Audio, etc.
"""

import os
import time
import warnings
from typing import Tuple, Dict, Any, Optional

warnings.filterwarnings("ignore")

from markitdown import MarkItDown
from PIL import Image, ExifTags

# Soporte OCR para Windows
try:
    import winocr
    HAS_WINOCR = True
except ImportError:
    HAS_WINOCR = False


class DocumentConverter:
    """Clase principal que encapsula MarkItDown y OCR para convertir diversos formatos de archivo a Markdown."""

    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".ico"}

    SUPPORTED_EXTENSIONS = {
        # Documentos Office
        ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
        # Documentos y datos
        ".pdf", ".csv", ".json", ".xml", ".html", ".htm", ".txt", ".md",
        # Archivos comprimidos y código
        ".zip", ".ipynb",
        # Multimedia
        ".mp3", ".wav", ".jpg", ".jpeg", ".png", ".bmp", ".webp"
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

    def _convert_image_with_ocr(self, file_path: str) -> str:
        """Extrae metadatos y texto mediante OCR para imágenes."""
        lines = []
        base_name = os.path.basename(file_path)
        lines.append(f"# Imagen: {base_name}\n")

        width, height = 0, 0
        img_format, mode = "", ""
        exif_data = {}

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                img_format = img.format or "Desconocido"
                mode = img.mode

                # Extraer EXIF si está disponible
                raw_exif = getattr(img, "_getexif", lambda: None)()
                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if isinstance(value, (str, int, float)):
                            exif_data[tag_name] = str(value)
        except Exception:
            pass

        # Tabla de propiedades de la imagen
        lines.append("| Propiedad | Detalle |")
        lines.append("| --- | --- |")
        lines.append(f"| **Formato** | {img_format} |")
        lines.append(f"| **Dimensiones** | {width} x {height} px |")
        lines.append(f"| **Modo de Color** | {mode} |")

        for key in ["DateTimeOriginal", "Make", "Model", "Software"]:
            if key in exif_data:
                lines.append(f"| **{key}** | {exif_data[key]} |")

        lines.append("")

        # Reconocimiento OCR de texto
        ocr_text = ""
        if HAS_WINOCR:
            try:
                with Image.open(file_path) as img:
                    result = winocr.recognize_pil_sync(img)
                    if result and isinstance(result, dict):
                        ocr_text = result.get("text", "").strip()
            except Exception as e:
                ocr_text = f"*(Error durante OCR: {e})*"

        if ocr_text:
            lines.append("## Texto Extraído de la Imagen (OCR)\n")
            lines.append(ocr_text)
            lines.append("")
        else:
            lines.append("*(No se detectó texto en la imagen)*\n")

        return "\n".join(lines)

    def convert(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Convierte el archivo a Markdown y retorna una tupla (markdown_text, metadata).
        """
        info = self.get_file_info(file_path)
        ext = info["ext"]
        start_time = time.perf_counter()

        if ext in self.IMAGE_EXTENSIONS:
            # Procesar imagen con metadatos y OCR nativo
            markdown_text = self._convert_image_with_ocr(file_path)
        else:
            # Procesar con Microsoft MarkItDown
            result = self.md.convert(file_path)
            markdown_text = (result.text_content or "").strip()

            # Si el documento estaba vacío o no extrajo texto, crear encabezado descriptivo
            if not markdown_text:
                markdown_text = (
                    f"# {info['filename']}\n\n"
                    f"| Propiedad | Valor |\n"
                    f"| --- | --- |\n"
                    f"| **Nombre** | {info['filename']} |\n"
                    f"| **Tipo** | {info['ext'].upper()} |\n"
                    f"| **Tamaño** | {info['size_formatted']} |\n\n"
                    f"*(El documento procesado no contiene texto legible o tablas)*\n"
                )

        elapsed_time = time.perf_counter() - start_time

        lines_count = len(markdown_text.splitlines())
        words_count = len(markdown_text.split())
        chars_count = len(markdown_text)

        metadata = {
            **info,
            "elapsed_seconds": round(elapsed_time, 2),
            "lines": lines_count,
            "words": words_count,
            "chars": chars_count,
            "title": info["stem"]
        }

        return markdown_text, metadata
