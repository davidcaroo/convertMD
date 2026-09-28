/**
 * ConvertMD Interactive Live Demo Playground
 * Powers the in-browser real-time document-to-markdown preview.
 */

const SAMPLE_DATASETS = {
  excel: {
    name: 'Reporte_Ventas_Q3.xlsx',
    type: 'Microsoft Excel Spreadsheet',
    rawText: `ID | Producto | Categoría | Unidades | Precio Unit. | Total USD
101 | Laptop Developer 16" | Hardware | 45 | $1,850.00 | $83,250.00
102 | Monitor 4K Ultrawide | Monitores | 80 | $520.00 | $41,600.00
103 | Teclado Mecánico RGB | Periféricos | 150 | $120.00 | $18,000.00
104 | Mouse Inalámbrico Pro | Periféricos | 210 | $65.00 | $13,650.00
105 | Servidor Rack NVMe | Infraestructura | 8 | $4,300.00 | $34,400.00
---
TOTAL CONSOLIDADO: 493 unidades vendidas | $190,900.00 USD`,
    markdown: `# Reporte de Ventas Q3 - Consolidado
> Extraído automáticamente con **ConvertMD** (Motor MarkItDown)

## Tabla de Rendimiento de Ventas

| ID | Producto | Categoría | Unidades | Precio Unit. | Total USD |
|:---|:---------|:----------|:--------:|:------------:|:---------:|
| 101 | Laptop Developer 16" | Hardware | 45 | $1,850.00 | $83,250.00 |
| 102 | Monitor 4K Ultrawide | Monitores | 80 | $520.00 | $41,600.00 |
| 103 | Teclado Mecánico RGB | Periféricos | 150 | $120.00 | $18,000.00 |
| 104 | Mouse Inalámbrico Pro | Periféricos | 210 | $65.00 | $13,650.00 |
| 105 | Servidor Rack NVMe | Infraestructura | 8 | $4,300.00 | $34,400.00 |

### Resumen Financiero
- **Unidades Totales Vendidas:** 493 unidades
- **Ingreso Bruto Total:** \`$190,900.00 USD\`
- **Estado de Ingesta IA:** Formato compatible para RAG y análisis con GPT-4 / Claude / Gemini.`
  },

  word: {
    name: 'Especificacion_Tecnica_RAG.docx',
    type: 'Microsoft Word Document',
    rawText: `PROYECTO: ARQUITECTURA DE AGENTES IA Y DOCUMENTACIÓN
Autor: David Caro (@davidcaroo)
Fecha: Septiembre 2024
Estado: Aprobado

1. INTRODUCCIÓN
La ingesta de información no estructurada en modelos de lenguaje requiere eliminar ruido de formato (XML residual, binarios propietarios, estilos CSS redundantes) y conservar la estructura semántica.

2. REQUISITOS DEL PIPELINE
- Soporte para extracción multi-formato sin depender de APIs de terceros.
- Conversión a Markdown puro respetando jerarquías H1 a H4.
- Operación 100% offline para resguardo de privacidad y secreto industrial.
- Tablas legibles sin desalineación de columnas.

3. MOTOR RECOMENDADO
Se selecciona Microsoft MarkItDown integrado en la suite de escritorio ConvertMD.`,
    markdown: `# Especificación Técnica: Arquitectura de Agentes IA y Documentación

**Autor:** David Caro ([@davidcaroo](https://github.com/davidcaroo))  
**Fecha:** Septiembre 2024  
**Estado:** \`Aprobado\`

---

## 1. Introducción
La ingesta de información no estructurada en modelos de lenguaje requiere **eliminar ruido de formato** (XML residual, binarios propietarios, estilos CSS redundantes) y conservar la estructura semántica original.

## 2. Requisitos del Pipeline
* **Soporte multi-formato:** Extracción de Word, Excel, PowerPoint, PDF e imágenes sin APIs externas.
* **Markdown puro:** Respeto riguroso de jerarquías de títulos (\`H1\` a \`H4\`).
* **Privacidad garantizada:** Operación **100% offline**, sin envío de telemetría ni datos sensibles a la nube.
* **Tablas GFM:** Cuadrículas Markdown legibles y listas para incrustación vectorial.

## 3. Motor Recomendado
> Se implementa el motor oficial **Microsoft MarkItDown** optimizado con la interfaz nativa para Windows **ConvertMD**.`
  },

  json: {
    name: 'telemetria_sistema.json',
    type: 'JavaScript Object Notation',
    rawText: `{
  "sistema": "ConvertMD Core",
  "version": "1.0.0",
  "licencia": "MIT",
  "plataforma": "Windows 10/11 x64",
  "capacidades": {
    "ocr_nativo": true,
    "multithreading": true,
    "offline_mode": true
  },
  "formatos_principales": [
    "DOCX", "XLSX", "PPTX", "PDF", "CSV", "JSON", "PNG", "MP3"
  ]
}`,
    markdown: `# Ficha Técnica del Sistema: ConvertMD

\`\`\`json
{
  "sistema": "ConvertMD Core",
  "version": "1.0.0",
  "licencia": "MIT",
  "plataforma": "Windows 10/11 x64",
  "capacidades": {
    "ocr_nativo": true,
    "multithreading": true,
    "offline_mode": true
  }
}
\`\`\`

### Capacidades del Entorno
- **OCR Integrado:** Reconocimiento de caracteres nativo de Windows (WinOCR) sin requerir Tesseract externo.
- **Multihilo (Threading):** Procesamiento asíncrono para mantener la fluidez de la interfaz gráfica al 100%.
- **Seguridad:** Los archivos permanecen en memoria local sin conexiones a servidores externos.`
  }
};

class LiveDemoPlayground {
  constructor() {
    this.rawInputElem = document.getElementById('demo-raw-input');
    this.mdOutputElem = document.getElementById('demo-md-output');
    this.currentFileNameElem = document.getElementById('demo-file-name');
    this.statLinesElem = document.getElementById('stat-lines');
    this.statWordsElem = document.getElementById('stat-words');
    this.statCharsElem = document.getElementById('stat-chars');
    this.copyBtn = document.getElementById('demo-copy-btn');
    this.tabButtons = document.querySelectorAll('.sample-tab-btn');

    this.currentDatasetKey = 'excel';

    this.init();
  }

  init() {
    if (!this.rawInputElem || !this.mdOutputElem) return;

    // Load initial sample
    this.loadSample('excel');

    // Attach tab listeners
    this.tabButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const dataset = e.currentTarget.getAttribute('data-sample');
        this.tabButtons.forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.loadSample(dataset);
      });
    });

    // Handle user manual editing
    this.rawInputElem.addEventListener('input', () => {
      this.handleUserEdit();
    });

    // Copy to clipboard
    if (this.copyBtn) {
      this.copyBtn.addEventListener('click', () => this.copyToClipboard());
    }
  }

  loadSample(key) {
    const data = SAMPLE_DATASETS[key];
    if (!data) return;

    this.currentDatasetKey = key;
    this.currentFileNameElem.textContent = data.name;
    this.rawInputElem.textContent = data.rawText;
    this.mdOutputElem.textContent = data.markdown;

    this.updateStats(data.markdown);
  }

  handleUserEdit() {
    const customText = this.rawInputElem.innerText;
    this.currentFileNameElem.textContent = 'documento_personalizado.txt';

    // Simple reactive markdown converter for live typing
    let generatedMd = customText;
    if (!generatedMd.startsWith('#')) {
      generatedMd = `# Documento Convertido\n> Procesado en vivo por ConvertMD\n\n` + generatedMd;
    }

    this.mdOutputElem.textContent = generatedMd;
    this.updateStats(generatedMd);
  }

  updateStats(text) {
    const lines = text.split('\n').length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;

    if (this.statLinesElem) this.statLinesElem.textContent = lines;
    if (this.statWordsElem) this.statWordsElem.textContent = words;
    if (this.statCharsElem) this.statCharsElem.textContent = chars;
  }

  async copyToClipboard() {
    const textToCopy = this.mdOutputElem.textContent;
    try {
      await navigator.clipboard.writeText(textToCopy);
      const originalText = this.copyBtn.innerHTML;
      this.copyBtn.innerHTML = `<span>✓ ¡Copiado al Portapapeles!</span>`;
      this.copyBtn.classList.remove('btn-primary');
      this.copyBtn.classList.add('btn-emerald');

      setTimeout(() => {
        this.copyBtn.innerHTML = originalText;
        this.copyBtn.classList.remove('btn-emerald');
        this.copyBtn.classList.add('btn-primary');
      }, 2000);
    } catch (err) {
      console.error('Error al copiar al portapapeles:', err);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new LiveDemoPlayground();
});
