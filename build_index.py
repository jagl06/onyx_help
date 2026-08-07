#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_index.py (v2) — RECONSTRUYE ifas_index.json completo desde cero.

⚠ Para añadir un manual usa add_to_index.py (vía oficial). Este script solo se usa
si hay que regenerar TODO el índice, y debe recibir TODAS las fuentes de documentación.

Novedades v2 (fiel al índice en producción):
- Acepta VARIAS carpetas raíz. Con "ruta::CATEGORIA" todo lo de esa raíz entra en una
  sola categoría (necesario para PRESENTACIONES).
- OCR automático (Tesseract) para PDFs escaneados. Requiere ifas_pdf_utils.py al lado.
- Exclusiones: carpetas que empiecen con "_" (ej. _DUPLICADOS), archivos "ALL_*"
  y "PRESENTACION CONSOLIDADA" (compilados que duplican contenido).

Reconstrucción completa del índice actual de IFAS:

    python build_index.py "C:\\...\\NOTIFIER\\DOCUMENTACION NOTIFIER ONYX UNIVERSITY" ^
                          "C:\\...\\NOTIFIER\\ENTRENAMIENTO\\PRESENTACIONES::PRESENTACIONES"

Formato de salida: {"count": N, "items": [{"id","cat","doc","page","text"}]}
Requisitos:  pip install pymupdf   ·   OCR: instalar Tesseract (UB Mannheim)
"""
import argparse
import json
import os
import sys

from ifas_pdf_utils import extraer_paginas

EXCLUIR_PREFIJOS = ("ALL_",)
EXCLUIR_NOMBRES = {"PRESENTACION CONSOLIDADA"}


def excluido(doc):
    d = doc.strip().upper()
    return d in EXCLUIR_NOMBRES or any(d.startswith(p) for p in EXCLUIR_PREFIJOS)


def main():
    ap = argparse.ArgumentParser(description="Reconstruye ifas_index.json desde una o más carpetas.")
    ap.add_argument("raices", nargs="+",
                    help='Carpetas raíz. Usa "ruta::CATEGORIA" para forzar una categoría única.')
    ap.add_argument("-o", "--salida", default="ifas_index.json")
    args = ap.parse_args()

    items, docs, ocr_docs, omitidos = [], 0, 0, []

    for espec in args.raices:
        if "::" in espec:
            raiz, cat_fija = espec.split("::", 1)
            cat_fija = cat_fija.strip().upper()
        else:
            raiz, cat_fija = espec, None
        raiz = os.path.abspath(raiz)
        if not os.path.isdir(raiz):
            sys.exit(f"No existe la carpeta: {raiz}")
        print(f"\n── {raiz}" + (f"  (categoría fija: {cat_fija})" if cat_fija else ""))

        for dirpath, dirnames, filenames in os.walk(raiz):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("_"))
            for fn in sorted(filenames):
                if not fn.lower().endswith(".pdf"):
                    continue
                doc = os.path.splitext(fn)[0]
                if excluido(doc):
                    omitidos.append(doc)
                    continue
                rel = os.path.relpath(dirpath, raiz)
                cat = cat_fija or ("GENERAL" if rel == "." else rel.replace("\\", "/").split("/")[0].upper())
                try:
                    pags, ocr = extraer_paginas(os.path.join(dirpath, fn))
                except Exception as e:
                    print(f"  ⚠ No se pudo abrir {fn}: {e}")
                    continue
                if not pags:
                    print(f"  ⚠ [{cat}] {doc}: sin texto útil — omitido")
                    continue
                for page, text in pags:
                    items.append({"id": len(items), "cat": cat, "doc": doc, "page": page, "text": text})
                docs += 1
                ocr_docs += 1 if ocr else 0
                print(f"  ✓ [{cat}] {doc}: {len(pags)} páginas" + (" (OCR)" if ocr else ""))

    with open(args.salida, "w", encoding="utf-8") as f:
        json.dump({"count": len(items), "items": items}, f, ensure_ascii=False)

    mb = os.path.getsize(args.salida) / 1e6
    print(f"\n✓ {args.salida}: {len(items)} fragmentos · {docs} documentos ({mb:.1f} MB)")
    if ocr_docs:
        print(f"  {ocr_docs} documento(s) procesados con OCR")
    if omitidos:
        print(f"  Excluidos (compilados): {', '.join(sorted(set(omitidos)))}")
    print("  Compara contra el publicado antes de subir:  python check_index.py --web")


if __name__ == "__main__":
    main()
