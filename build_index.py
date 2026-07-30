#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_index.py — Regenera ifas_index.json para IFAS (búsqueda BM25 en el navegador).

Uso:
    python build_index.py "C:\\Users\\Jesus\\OneDrive - ISELEC\\Desktop\\PDFS Onyx"
    python build_index.py "C:\\ruta\\PDFS Onyx" -o ifas_index.json

Estructura de carpetas esperada:
    RAIZ\\CATEGORIA\\documento.pdf      (la categoría es la primera subcarpeta)

Formato de salida (el que consume index.html):
    {"count": N, "items": [{"id", "cat", "doc", "page", "text"}]}

Requisito:  pip install pymupdf
"""
import argparse
import json
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Falta PyMuPDF. Instálalo con:  pip install pymupdf")

MIN_CHARS = 40  # páginas con menos texto se consideran vacías (portadas, escaneadas sin OCR)


def main():
    ap = argparse.ArgumentParser(description="Regenera ifas_index.json a partir de una carpeta de PDFs.")
    ap.add_argument("raiz", help="Carpeta raíz con subcarpetas de categoría y PDFs")
    ap.add_argument("-o", "--salida", default="ifas_index.json", help="Archivo de salida (default: ifas_index.json)")
    args = ap.parse_args()

    raiz = os.path.abspath(args.raiz)
    if not os.path.isdir(raiz):
        sys.exit(f"No existe la carpeta: {raiz}")

    items = []
    docs = 0
    vacias = 0

    for dirpath, dirnames, filenames in os.walk(raiz):
        dirnames.sort()
        for fn in sorted(filenames):
            if not fn.lower().endswith(".pdf"):
                continue
            ruta = os.path.join(dirpath, fn)
            rel = os.path.relpath(dirpath, raiz)
            # Categoría = primera subcarpeta bajo la raíz.
            # (Se calcula desde la ruta RELATIVA para evitar el bug de carpetas duplicadas.)
            cat = "GENERAL" if rel == "." else rel.replace("\\", "/").split("/")[0].upper()
            doc = os.path.splitext(fn)[0]
            try:
                pdf = fitz.open(ruta)
            except Exception as e:
                print(f"  ⚠ No se pudo abrir {fn}: {e}")
                continue
            paginas = 0
            for i, page in enumerate(pdf):
                text = page.get_text("text").strip()
                if len(text) < MIN_CHARS:
                    vacias += 1
                    continue
                items.append({"id": len(items), "cat": cat, "doc": doc, "page": i + 1, "text": text})
                paginas += 1
            pdf.close()
            docs += 1
            print(f"  {cat} / {doc}: {paginas} páginas indexadas")

    data = {"count": len(items), "items": items}
    with open(args.salida, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    mb = os.path.getsize(args.salida) / 1e6
    print(f"\n✓ {args.salida}: {len(items)} fragmentos de {docs} PDFs ({mb:.1f} MB)")
    if vacias:
        print(f"  ⚠ {vacias} páginas sin texto útil (portadas o escaneadas sin OCR)")
    if mb > 20:
        print("  ⚠ El índice supera 20 MB: considera depurar manuales poco usados; se descarga completo en el navegador.")


if __name__ == "__main__":
    main()
