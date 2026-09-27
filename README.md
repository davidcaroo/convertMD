# ConvertMD ⚡

> **Conversor Universal de Documentos a Markdown** potenciado por la librería oficial **[Microsoft MarkItDown](https://github.com/microsoft/markitdown)**.

ConvertMD es una aplicación de escritorio nativa para Windows con una interfaz moderna y elegante que permite convertir documentos de oficina (Word, Excel, PowerPoint), archivos PDF, datos tabulares (CSV, JSON, XML) e imágenes a formato **Markdown limpio**, ideal para modelos de lenguaje (LLMs), agentes de Inteligencia Artificial (RAG) o documentación técnica.

---

## ✨ Características Principales

- 🎯 **Conversión en un clic:** Selecciona cualquier archivo a través del Explorador de Windows o el selector nativo.
- ⚡ **Motor Oficial Microsoft MarkItDown:** Extrae tablas, texto jerárquico, encabezados y formato enriquecido.
- 🎨 **Interfaz Gráfica Moderna:**
  - Tema oscuro refinado (*Deep Dark Modern*).
  - Barra de carga animada con información de proceso en tiempo real.
  - No bloquea la interfaz durante la conversión (procesamiento en segundo plano con hilos).
- 💾 **Exportación y Descarga Directa:**
  - Genera el archivo `.md` manteniendo automáticamente el nombre original del documento (ej. `mi_reporte.docx` ➔ `mi_reporte.md`).
  - Previsualización en vivo del contenido convertido con contador de líneas, palabras y caracteres.
  - Botón de **Copiar al Portapapeles** con un clic.
  - Acceso directo para **Abrir la Carpeta de Origen**.
- 🚀 **Dos Formatos de Entrega:**
  - **Ejecutable Portable (`ConvertMD.exe`):** No requiere instalación, llévalo en una memoria USB o ejecútalo directamente.
  - **Instalador de Windows (`ConvertMD_Setup.exe`):** Asistente de instalación estándar con accesos directos en el Escritorio y Menú Inicio.

---

## 📂 Formatos Soportados

| Categoría | Extensiones |
|---|---|
| **Documentos de Office** | `.docx`, `.doc`, `.xlsx`, `.xls`, `.pptx`, `.ppt` |
| **Documentos y Lectura** | `.pdf`, `.txt`, `.md`, `.epub` |
| **Datos Estructurados** | `.csv`, `.json`, `.xml`, `.html`, `.htm` |
| **Cuadernos y Archivos** | `.ipynb`, `.zip` |
| **Multimedia** | `.png`, `.jpg`, `.jpeg`, `.mp3`, `.wav` |

---

## 📦 Descarga y Uso

Los ejecutables listos para usar se encuentran en la carpeta `dist/`:

1. **Ejecutable Portable:**
   - Ubicación: `dist/ConvertMD.exe`
   - Simplemente haz doble clic y comienza a convertir.

2. **Instalador para Windows:**
   - Ubicación: `dist/ConvertMD_Setup.exe`
   - Ejecuta el instalador para instalar la aplicación en tu sistema con acceso directo en el escritorio.

---

## 🛠️ Ejecución desde el Código Fuente

Si deseas ejecutar o modificar el código fuente:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar la aplicación
python main.py
```

### Compilar de nuevo el Portable y el Instalador:

```bash
python build_release.py
```
