"""
Motor de conversión de documentos a Markdown usando Microsoft MarkItDown, OCR para imágenes y metadatos de audio.
Soporta: DOCX, XLSX, PPTX, PDF, CSV, JSON, XML, HTML, TXT, Imágenes (con OCR) y Audio (MP3, WAV, etc.).
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

# Soporte para metadatos de audio
try:
    from tinytag import TinyTag
    HAS_TINYTAG = True
except ImportError:
    HAS_TINYTAG = False


class DocumentConverter:
    """Clase principal que encapsula MarkItDown, OCR y metadatos multimedia para convertir a Markdown."""

    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".ico"}
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".wma", ".aac"}

    SUPPORTED_EXTENSIONS = {
        # Documentos Office
        ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
        # Documentos y datos
        ".pdf", ".csv", ".json", ".xml", ".html", ".htm", ".txt", ".md",
        # Archivos comprimidos y código
        ".zip", ".ipynb",
        # Multimedia
        ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".wma", ".aac",
        ".jpg", ".jpeg", ".png", ".bmp", ".webp"
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

                raw_exif = getattr(img, "_getexif", lambda: None)()
                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if isinstance(value, (str, int, float)):
                            exif_data[tag_name] = str(value)
        except Exception:
            pass

        lines.append("| Propiedad | Detalle |")
        lines.append("| --- | --- |")
        lines.append(f"| **Formato** | {img_format} |")
        lines.append(f"| **Dimensiones** | {width} x {height} px |")
        lines.append(f"| **Modo de Color** | {mode} |")

        for key in ["DateTimeOriginal", "Make", "Model", "Software"]:
            if key in exif_data:
                lines.append(f"| **{key}** | {exif_data[key]} |")

        lines.append("")

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

    def _convert_audio(self, file_path: str, info: Dict[str, Any]) -> str:
        """Extrae metadatos y transcripción para archivos de audio de forma segura sin requerir FFmpeg."""
        base_name = info["filename"]
        lines = [f"# Audio: {base_name}\n"]
        lines.append("| Propiedad | Detalle |")
        lines.append("| --- | --- |")
        lines.append(f"| **Formato** | {info['ext'].replace('.', '').upper()} |")
        lines.append(f"| **Tamaño** | {info['size_formatted']} |")

        has_tags = False
        if HAS_TINYTAG:
            try:
                tag = TinyTag.get(file_path)
                if tag.title:
                    lines.append(f"| **Título** | {tag.title} |")
                    has_tags = True
                if tag.artist:
                    lines.append(f"| **Artista** | {tag.artist} |")
                    has_tags = True
                if tag.album:
                    lines.append(f"| **Álbum** | {tag.album} |")
                    has_tags = True
                if tag.year:
                    lines.append(f"| **Año** | {tag.year} |")
                if tag.duration:
                    mins = int(tag.duration // 60)
                    secs = int(tag.duration % 60)
                    lines.append(f"| **Duración** | {mins}:{secs:02d} min ({tag.duration:.1f}s) |")
                if tag.bitrate:
                    lines.append(f"| **Bitrate** | {int(tag.bitrate)} kbps |")
                if tag.samplerate:
                    lines.append(f"| **Frecuencia de Muestreo** | {tag.samplerate} Hz |")
                if tag.channels:
                    ch_desc = "Estéreo" if tag.channels == 2 else ("Mono" if tag.channels == 1 else f"{tag.channels} canales")
                    lines.append(f"| **Canales** | {ch_desc} |")
            except Exception:
                pass

        lines.append("")

        # Intentar transcripción si el sistema dispone de los codecs necesarios
        transcript_text = ""
        try:
            res = self.md.convert(file_path)
            content = (res.text_content or "").strip()
            if "Audio Transcript:" in content:
                transcript_text = content.split("Audio Transcript:")[-1].strip()
        except Exception:
            pass

        if transcript_text:
            lines.append("## Transcripción de Audio\n")
            lines.append(transcript_text)
            lines.append("")
        else:
            lines.append("*(Nota: La transcripción automática de voz a texto de archivos MP3 requiere FFmpeg en el sistema. Los metadatos del archivo se extrajeron correctamente)*\n")

        return "\n".join(lines)

    def convert(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Convierte el archivo a Markdown y retorna una tupla (markdown_text, metadata).
        """
        info = self.get_file_info(file_path)
        ext = info["ext"]
        start_time = time.perf_counter()

        if ext in self.IMAGE_EXTENSIONS:
            markdown_text = self._convert_image_with_ocr(file_path)
        elif ext in self.AUDIO_EXTENSIONS:
            markdown_text = self._convert_audio(file_path, info)
        else:
            # Procesar con Microsoft MarkItDown
            try:
                result = self.md.convert(file_path)
                markdown_text = (result.text_content or "").strip()
            except Exception as e:
                markdown_text = (
                    f"# {info['filename']}\n\n"
                    f"| Propiedad | Valor |\n"
                    f"| --- | --- |\n"
                    f"| **Nombre** | {info['filename']} |\n"
                    f"| **Tipo** | {info['ext'].upper()} |\n"
                    f"| **Tamaño** | {info['size_formatted']} |\n\n"
                    f"> [!WARNING]\n"
                    f"> No se pudo extraer el contenido completo debido a: {e}\n"
                )

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
