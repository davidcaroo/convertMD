"""
Interfaz gráfica moderna para ConvertMD construida con CustomTkinter.
Permite seleccionar archivos, ver la animación de progreso y descargar el resultado en Markdown (.md).
"""

import os
import sys
import threading
import subprocess
import warnings
from typing import Optional, Dict, Any

warnings.filterwarnings("ignore")

import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.converter import DocumentConverter

# Configuración global del tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ConvertMDApp(ctk.CTk):
    """Ventana principal de la aplicación ConvertMD."""

    def __init__(self):
        super().__init__()

        self.title("ConvertMD - Conversor Universal a Markdown")
        self.geometry("860x700")
        self.minsize(760, 600)

        # Configurar icono si existe
        self._setup_icon()

        # Motor de conversión
        self.converter = DocumentConverter()

        # Estado interno
        self.selected_file_path: Optional[str] = None
        self.file_info: Optional[Dict[str, Any]] = None
        self.converted_markdown: Optional[str] = None
        self.conversion_metadata: Optional[Dict[str, Any]] = None
        self.is_converting: bool = False
        self._animation_step: int = 0
        self._animation_running: bool = False

        # Construir la interfaz
        self._build_ui()

    def _setup_icon(self):
        """Asigna el icono de la ventana."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "assets", "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _build_ui(self):
        """Construye todos los elementos de la interfaz."""
        # Contenedor principal con margen
        self.main_container = ctk.CTkFrame(self, corner_radius=16, fg_color="#181825")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Cabecera (Header)
        self._build_header()

        # 2. Tarjeta de selección de archivo
        self._build_file_picker_card()

        # 3. Panel de Progreso / Animación
        self._build_progress_card()

        # 4. Panel de Resultados y Descarga
        self._build_result_card()

    def _build_header(self):
        """Cabecera con logo, título y subtítulo."""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 10))

        title_badge_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_badge_frame.pack(fill="x")

        # Título principal
        title_label = ctk.CTkLabel(
            title_badge_frame,
            text="ConvertMD",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#cdd6f4"
        )
        title_label.pack(side="left")

        # Badge Powered by Microsoft MarkItDown
        badge = ctk.CTkLabel(
            title_badge_frame,
            text="⚡ Powered by Microsoft MarkItDown",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#313244",
            text_color="#89b4fa",
            corner_radius=8,
            padx=10,
            pady=3
        )
        badge.pack(side="left", padx=(12, 0))

        # Subtítulo explicativo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Convierte Word (DOCX), Excel (XLSX), PowerPoint (PPTX), PDF, CSV, JSON e imágenes a Markdown limpio para LLMs e IA.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#a6adc8",
            wraplength=760,
            justify="left"
        )
        subtitle_label.pack(anchor="w", pady=(6, 0))

    def _build_file_picker_card(self):
        """Área interactiva para seleccionar el documento a convertir."""
        self.picker_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#1e1e2e",
            corner_radius=12,
            border_width=1,
            border_color="#313244"
        )
        self.picker_frame.pack(fill="x", padx=24, pady=10)

        content_box = ctk.CTkFrame(self.picker_frame, fg_color="transparent")
        content_box.pack(fill="x", padx=20, pady=18)

        # Icono visual o texto indicador
        self.file_icon_label = ctk.CTkLabel(
            content_box,
            text="📄",
            font=ctk.CTkFont(size=36)
        )
        self.file_icon_label.pack(anchor="center", pady=(0, 4))

        self.file_name_label = ctk.CTkLabel(
            content_box,
            text="Ningún archivo seleccionado todavía",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#cdd6f4"
        )
        self.file_name_label.pack(anchor="center")

        self.file_details_label = ctk.CTkLabel(
            content_box,
            text="Haz clic en el botón de abajo para explorar tus carpetas",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#6c7086"
        )
        self.file_details_label.pack(anchor="center", pady=(2, 12))

        # Botones de acción
        buttons_frame = ctk.CTkFrame(content_box, fg_color="transparent")
        buttons_frame.pack(anchor="center")

        self.btn_select_file = ctk.CTkButton(
            buttons_frame,
            text="📂 Seleccionar Archivo",
            command=self._on_select_file_clicked,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#6366f1",
            hover_color="#4f46e5",
            corner_radius=8,
            height=38,
            width=190
        )
        self.btn_select_file.pack(side="left", padx=6)

        self.btn_convert = ctk.CTkButton(
            buttons_frame,
            text="⚡ Convertir a Markdown",
            command=self._on_convert_clicked,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            corner_radius=8,
            height=38,
            width=190,
            state="disabled"
        )
        self.btn_convert.pack(side="left", padx=6)

    def _build_progress_card(self):
        """Tarjeta de estado del progreso y barra animada."""
        self.progress_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#1e1e2e",
            corner_radius=12,
            border_width=1,
            border_color="#313244"
        )
        # Oculto por defecto
        # self.progress_frame.pack(fill="x", padx=24, pady=10)

        inner = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        self.progress_status_label = ctk.CTkLabel(
            inner,
            text="Iniciando conversión con Microsoft MarkItDown...",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#89b4fa"
        )
        self.progress_status_label.pack(anchor="w", pady=(0, 8))

        # Barra de progreso moderna
        self.progress_bar = ctk.CTkProgressBar(
            inner,
            height=10,
            corner_radius=5,
            progress_color="#6366f1",
            fg_color="#313244"
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        self.progress_subtext_label = ctk.CTkLabel(
            inner,
            text="Procesando estructura del documento...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#a6adc8"
        )
        self.progress_subtext_label.pack(anchor="w", pady=(6, 0))

    def _build_result_card(self):
        """Tarjeta con visor de markdown generado y botón de descarga."""
        self.result_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#1e1e2e",
            corner_radius=12,
            border_width=1,
            border_color="#313244"
        )
        # Oculto inicialmente hasta que haya resultado

        inner = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # Barra superior de resultados con métricas
        top_bar = ctk.CTkFrame(inner, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.result_status_label = ctk.CTkLabel(
            top_bar,
            text="✅ ¡Conversión completada con éxito!",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#a6e3a1"
        )
        self.result_status_label.pack(side="left")

        self.metrics_label = ctk.CTkLabel(
            top_bar,
            text="0 líneas | 0 palabras",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#9399b2"
        )
        self.metrics_label.pack(side="right")

        # Área de previsualización de texto
        self.preview_textbox = ctk.CTkTextbox(
            inner,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#181825",
            text_color="#cdd6f4",
            corner_radius=8,
            wrap="word"
        )
        self.preview_textbox.pack(fill="both", expand=True, pady=(0, 12))

        # Barra de botones de descarga y copia
        actions_bar = ctk.CTkFrame(inner, fg_color="transparent")
        actions_bar.pack(fill="x")

        # Botón Descargar / Guardar Markdown
        self.btn_download = ctk.CTkButton(
            actions_bar,
            text="💾 Descargar Markdown (.md)",
            command=self._on_download_clicked,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            corner_radius=8,
            height=36,
            width=210
        )
        self.btn_download.pack(side="left", padx=(0, 8))

        # Botón Copiar al portapapeles
        self.btn_copy = ctk.CTkButton(
            actions_bar,
            text="📋 Copiar Texto",
            command=self._on_copy_clicked,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#45475a",
            hover_color="#585b70",
            corner_radius=8,
            height=36,
            width=130
        )
        self.btn_copy.pack(side="left", padx=4)

        # Botón Abrir Carpeta
        self.btn_open_folder = ctk.CTkButton(
            actions_bar,
            text="📂 Abrir Carpeta Origen",
            command=self._on_open_source_folder_clicked,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#313244",
            hover_color="#45475a",
            corner_radius=8,
            height=36,
            width=160
        )
        self.btn_open_folder.pack(side="left", padx=4)

        # Botón Nuevo Archivo
        self.btn_reset = ctk.CTkButton(
            actions_bar,
            text="🔄 Convertir Otro",
            command=self._on_reset_clicked,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="transparent",
            hover_color="#313244",
            border_width=1,
            border_color="#45475a",
            corner_radius=8,
            height=36,
            width=130
        )
        self.btn_reset.pack(side="right")

    # ================= Eventos y Lógica =================

    def _on_select_file_clicked(self):
        """Abre el administrador de archivos para escoger un documento."""
        filetypes = [
            ("Todos los archivos compatibles", "*.docx;*.xlsx;*.pptx;*.pdf;*.csv;*.json;*.xml;*.html;*.htm;*.txt;*.zip;*.png;*.jpg;*.jpeg;*.mp3;*.wav"),
            ("Documentos Word (*.docx)", "*.docx"),
            ("Hojas de cálculo Excel (*.xlsx)", "*.xlsx"),
            ("Presentaciones PowerPoint (*.pptx)", "*.pptx"),
            ("Archivos PDF (*.pdf)", "*.pdf"),
            ("Archivos de Datos (*.csv, *.json, *.xml)", "*.csv;*.json;*.xml"),
            ("Páginas Web y Texto (*.html, *.txt)", "*.html;*.htm;*.txt"),
            ("Todos los archivos (*.*)", "*.*")
        ]

        selected_path = filedialog.askopenfilename(
            title="Seleccionar documento para convertir a Markdown",
            filetypes=filetypes
        )

        if not selected_path:
            return

        try:
            self.selected_file_path = selected_path
            self.file_info = self.converter.get_file_info(selected_path)

            # Actualizar interfaz de selección
            self.file_name_label.configure(
                text=self.file_info["filename"],
                text_color="#89b4fa"
            )
            self.file_details_label.configure(
                text=f"Tamaño: {self.file_info['size_formatted']} | Tipo: {self.file_info['ext'].upper()} | Sugerido: {self.file_info['suggested_output_name']}"
            )
            self.file_icon_label.configure(text=self._get_icon_for_ext(self.file_info["ext"]))

            # Habilitar botón de conversión
            self.btn_convert.configure(state="normal")

            # Si había un resultado anterior, ocultarlo para no confundir
            self.result_frame.pack_forget()

        except Exception as e:
            messagebox.showerror("Error al leer archivo", f"No se pudo inspeccionar el archivo:\n{e}")

    def _get_icon_for_ext(self, ext: str) -> str:
        """Devuelve un emoji distintivo según el tipo de archivo."""
        ext = ext.lower()
        if ext in (".docx", ".doc"):
            return "📝"
        elif ext in (".xlsx", ".xls", ".csv"):
            return "📊"
        elif ext in (".pptx", ".ppt"):
            return "📽️"
        elif ext == ".pdf":
            return "📕"
        elif ext in (".json", ".xml", ".html", ".htm"):
            return "🌐"
        elif ext in (".jpg", ".jpeg", ".png"):
            return "🖼️"
        elif ext in (".mp3", ".wav"):
            return "🎵"
        return "📄"

    def _on_convert_clicked(self):
        """Inicia el proceso asíncrono de conversión."""
        if not self.selected_file_path or self.is_converting:
            return

        self.is_converting = True
        self.btn_select_file.configure(state="disabled")
        self.btn_convert.configure(state="disabled")

        # Ocultar resultado previo y mostrar barra de progreso
        self.result_frame.pack_forget()
        self.progress_frame.pack(fill="x", padx=24, pady=10)

        # Iniciar animación fluida
        self._animation_running = True
        self.progress_bar.set(0)
        self.progress_status_label.configure(text="Extrayendo y estructurando contenido con MarkItDown...")
        self._animate_progress_bar()

        # Ejecutar conversión en un hilo secundario para que la UI no se freeze
        conversion_thread = threading.Thread(target=self._run_conversion_worker, daemon=True)
        conversion_thread.start()

    def _animate_progress_bar(self):
        """Efecto dinámico animado de la barra de carga."""
        if not self._animation_running:
            return

        current_val = self.progress_bar.get()
        if current_val >= 0.90:
            # Mantener esperando hasta que termine
            pass
        else:
            self.progress_bar.set(current_val + 0.05)

        self._animation_step += 1
        steps_text = [
            "Leyendo estructura del archivo...",
            "Invocando motor Microsoft MarkItDown...",
            "Extrayendo tablas, texto y jerarquía...",
            "Generando Markdown estandarizado..."
        ]
        text_index = (self._animation_step // 4) % len(steps_text)
        self.progress_subtext_label.configure(text=steps_text[text_index])

        self.after(120, self._animate_progress_bar)

    def _run_conversion_worker(self):
        """Trabajo en segundo plano para procesar la conversión."""
        try:
            markdown_content, metadata = self.converter.convert(self.selected_file_path)
            # Notificar al hilo principal
            self.after(0, self._on_conversion_success, markdown_content, metadata)
        except Exception as e:
            self.after(0, self._on_conversion_error, str(e))

    def _on_conversion_success(self, markdown_content: str, metadata: Dict[str, Any]):
        """Maneja el éxito de la conversión."""
        self._animation_running = False
        self.is_converting = False
        self.progress_bar.set(1.0)

        self.converted_markdown = markdown_content
        self.conversion_metadata = metadata

        # Restaurar controles
        self.btn_select_file.configure(state="normal")
        self.btn_convert.configure(state="normal")
        self.progress_frame.pack_forget()

        # Llenar panel de resultados
        self.metrics_label.configure(
            text=f"⏱️ {metadata['elapsed_seconds']}s  |  📄 {metadata['lines']} líneas  |  🔤 {metadata['words']:,} palabras  |  🔡 {metadata['chars']:,} carácteres"
        )
        self.preview_textbox.delete("1.0", "end")
        self.preview_textbox.insert("1.0", markdown_content)

        # Mostrar panel de resultado
        self.result_frame.pack(fill="both", expand=True, padx=24, pady=10)

    def _on_conversion_error(self, error_message: str):
        """Maneja cualquier error en la conversión."""
        self._animation_running = False
        self.is_converting = False
        self.btn_select_file.configure(state="normal")
        self.btn_convert.configure(state="normal")
        self.progress_frame.pack_forget()

        messagebox.showerror(
            "Error en la conversión",
            f"Ocurrió un error al procesar el archivo con MarkItDown:\n\n{error_message}"
        )

    def _on_download_clicked(self):
        """Permite guardar / descargar el archivo convertido con el nombre original por defecto."""
        if not self.converted_markdown or not self.file_info:
            return

        suggested_name = self.file_info["suggested_output_name"]
        initial_dir = os.path.dirname(self.selected_file_path)

        save_path = filedialog.asksaveasfilename(
            title="Guardar archivo Markdown",
            initialdir=initial_dir,
            initialfile=suggested_name,
            defaultextension=".md",
            filetypes=[("Archivos Markdown (*.md)", "*.md"), ("Todos los archivos (*.*)", "*.*")]
        )

        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.converted_markdown)

            messagebox.showinfo(
                "¡Archivo Guardado!",
                f"El archivo Markdown se guardó exitosamente en:\n{save_path}"
            )
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")

    def _on_copy_clicked(self):
        """Copia el texto Markdown generado al portapapeles."""
        if not self.converted_markdown:
            return

        self.clipboard_clear()
        self.clipboard_append(self.converted_markdown)
        self.update()

        orig_text = self.btn_copy.cget("text")
        self.btn_copy.configure(text="✅ ¡Copiado!", fg_color="#10b981")
        self.after(2000, lambda: self.btn_copy.configure(text=orig_text, fg_color="#45475a"))

    def _on_open_source_folder_clicked(self):
        """Abre la carpeta que contiene el archivo seleccionado en el Explorador de Windows."""
        if not self.selected_file_path or not os.path.exists(self.selected_file_path):
            return

        folder = os.path.dirname(os.path.abspath(self.selected_file_path))
        if sys.platform == "win32":
            subprocess.Popen(["explorer", folder])
        else:
            os.system(f'open "{folder}"')

    def _on_reset_clicked(self):
        """Reinicia la aplicación para procesar otro archivo."""
        self.selected_file_path = None
        self.file_info = None
        self.converted_markdown = None
        self.conversion_metadata = None

        self.file_name_label.configure(
            text="Ningún archivo seleccionado todavía",
            text_color="#cdd6f4"
        )
        self.file_details_label.configure(
            text="Haz clic en el botón de abajo para explorar tus carpetas"
        )
        self.file_icon_label.configure(text="📄")
        self.btn_convert.configure(state="disabled")

        self.result_frame.pack_forget()
        self.progress_frame.pack_forget()


def run_app():
    """Función de inicio de la aplicación GUI."""
    app = ConvertMDApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
