# -*- coding: utf-8 -*-
"""Funciones compartidas de extracción de texto para los scripts del índice IFAS.
Debe estar en la misma carpeta que add_to_index.py y build_index.py."""
import os
import shutil
import subprocess
import sys
import tempfile

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Falta PyMuPDF. Instálalo con:  pip install pymupdf")

MIN_CHARS = 40

_TESSERACT = shutil.which("tesseract") or (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe") else None
)
_ocr_avisado = False


def _ocr_pagina(page):
    """OCR de una página renderizada a 300 dpi. Devuelve texto o ''."""
    global _ocr_avisado
    if not _TESSERACT:
        if not _ocr_avisado:
            print("  ⚠ Página escaneada detectada y Tesseract no está instalado: se omitirá el OCR.")
            print("    Para habilitarlo: https://github.com/UB-Mannheim/tesseract/wiki (instalador Windows)")
            _ocr_avisado = True
        return ""
    with tempfile.TemporaryDirectory() as td:
        png = os.path.join(td, "p.png")
        page.get_pixmap(dpi=300).save(png)
        try:
            r = subprocess.run([_TESSERACT, png, "-", "--psm", "3"],
                               capture_output=True, text=True, timeout=120)
            return r.stdout.strip()
        except Exception:
            return ""


def extraer_paginas(ruta):
    """Devuelve (paginas, ocr_usado): lista de (nº página, texto) con OCR de respaldo
    para páginas sin texto nativo (PDFs escaneados)."""
    pdf = fitz.open(ruta)
    pags, ocr_usado = [], False
    for i, page in enumerate(pdf):
        t = page.get_text("text").strip()
        if len(t) < MIN_CHARS:
            t2 = _ocr_pagina(page)
            if len(t2) >= MIN_CHARS:
                t, ocr_usado = t2, True
            else:
                continue
        pags.append((i + 1, t))
    pdf.close()
    return pags, ocr_usado
