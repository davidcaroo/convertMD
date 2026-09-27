"""
Pruebas automatizadas para DocumentConverter.
"""

import os
import unittest
from src.converter import DocumentConverter


class TestDocumentConverter(unittest.TestCase):

    def setUp(self):
        self.converter = DocumentConverter()
        self.samples_dir = os.path.join(os.path.dirname(__file__), "samples")

    def test_file_info_extraction(self):
        sample_file = os.path.join(self.samples_dir, "documento_prueba.docx")
        if os.path.exists(sample_file):
            info = self.converter.get_file_info(sample_file)
            self.assertEqual(info["filename"], "documento_prueba.docx")
            self.assertEqual(info["stem"], "documento_prueba")
            self.assertEqual(info["ext"], ".docx")
            self.assertEqual(info["suggested_output_name"], "documento_prueba.md")
            self.assertGreater(info["size_bytes"], 0)

    def test_convert_docx(self):
        sample_file = os.path.join(self.samples_dir, "documento_prueba.docx")
        if os.path.exists(sample_file):
            md_text, meta = self.converter.convert(sample_file)
            self.assertIn("Informe de", md_text)
            self.assertIn("MarkItDown", md_text)
            self.assertGreater(meta["lines"], 0)
            self.assertGreater(meta["words"], 0)

    def test_convert_xlsx(self):
        sample_file = os.path.join(self.samples_dir, "hoja_calculo.xlsx")
        if os.path.exists(sample_file):
            md_text, meta = self.converter.convert(sample_file)
            self.assertIn("Laptop Pro", md_text)
            self.assertIn("Monitor 4K", md_text)
            self.assertIn("|", md_text)  # Tablas markdown


if __name__ == "__main__":
    unittest.main()
