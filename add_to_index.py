#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_to_index.py (v2) — Añade PDFs a ifas_index.json SIN reconstruir el índice completo.
Es la vía OFICIAL para actualizar la documentación de IFAS.

Novedad v2: OCR automático (Tesseract) para PDFs escaneados sin texto.
Requiere ifas_pdf_utils.py en la misma carpeta.

Uso:
    python add_to_index.py "documento.pdf" -c DETECTORS --web
    python add_to_index.py "carpeta_con_pdfs" -c MODULES --web
    python add_to_index.py "documento.pdf" -c DETECTORS                (parte del ifas_index.json local)
    python add_to_index.py "documento.pdf" -c DETECTORS --web --reemplazar   (sustituye una revisión vieja)

--web         parte del índice YA PUBLICADO en ifas.iselec.com.pa (recomendado)
--reemplazar  si el documento ya existe en el índice, elimina la versión anterior y carga la nueva

Salida: ifas_index.json en la carpeta actual → subir al repo con GitHub Desktop.
Si ya había un ifas_index.json local, se respalda como ifas_index_anterior.json.

Requisitos:  pip install pymupdf   ·   OCR opcional: instalar Tesseract (UB Mannheim)
"""
import argparse
import json
import os
import sys

from ifas_pdf_utils import extraer_paginas

URL = "https://ifas.iselec.com.pa/ifas_index.json"


def cargar(web):
    if web:
        from urllib.request import urlopen
        print(f"Descargando índice publicado: {URL} …")
        with urlopen(URL, timeout=120) as r:
            return json.load(r)
    if not os.path.exists("ifas_index.json"):
        sys.exit("No hay ifas_index.json en esta carpeta. Usa --web para partir del publicado.")
    with open("ifas_index.json", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description="Añade PDFs al índice de IFAS de forma incremental.")
    ap.add_argument("ruta", help="PDF o carpeta con PDFs a añadir")
    ap.add_argument("-c", "--categoria", required=True, help="Categoría del índice (ej. DETECTORS, MODULES)")
    ap.add_argument("--web", action="store_true", help="Partir del índice publicado en ifas.iselec.com.pa")
    ap.add_argument("--reemplazar", action="store_true", help="Sustituir documentos que ya existan")
    args = ap.parse_args()

    cat = args.categoria.strip().upper()
    if os.path.isdir(args.ruta):
        pdfs = [os.path.join(args.ruta, f) for f in sorted(os.listdir(args.ruta)) if f.lower().endswith(".pdf")]
    elif os.path.isfile(args.ruta):
        pdfs = [args.ruta]
    else:
        sys.exit(f"No existe: {args.ruta}")
    if not pdfs:
        sys.exit("No hay PDFs en esa ruta.")

    data = cargar(args.web)
    items = data.get("items", [])
    antes = len(items)
    existentes = {it["doc"] for it in items}
    agregados = 0

    for ruta in pdfs:
        doc = os.path.splitext(os.path.basename(ruta))[0]
        if doc in existentes and not args.reemplazar:
            print(f"  ✗ {doc}: YA EXISTE en el índice — omitido (usa --reemplazar para sustituirlo)")
            continue
        try:
            pags, ocr = extraer_paginas(ruta)
        except Exception as e:
            print(f"  ⚠ No se pudo leer {os.path.basename(ruta)}: {e}")
            continue
        if not pags:
            print(f"  ⚠ {doc}: sin texto útil (escaneado sin OCR disponible) — omitido")
            continue
        if doc in existentes:
            items = [it for it in items if it["doc"] != doc]
            print(f"  ↻ {doc}: versión anterior eliminada, se carga la nueva")
        for page, text in pags:
            items.append({"id": 0, "cat": cat, "doc": doc, "page": page, "text": text})
        existentes.add(doc)
        agregados += 1
        print(f"  ✓ [{cat}] {doc}: {len(pags)} páginas" + (" (OCR)" if ocr else ""))

    if agregados == 0 and len(items) == antes:
        sys.exit("\nNada que hacer: no se añadió ningún documento.")

    for i, it in enumerate(items):
        it["id"] = i

    if os.path.exists("ifas_index.json"):
        os.replace("ifas_index.json", "ifas_index_anterior.json")
        print("  (respaldo del local previo en ifas_index_anterior.json)")

    with open("ifas_index.json", "w", encoding="utf-8") as f:
        json.dump({"count": len(items), "items": items}, f, ensure_ascii=False)

    mb = os.path.getsize("ifas_index.json") / 1e6
    docs = len({it["doc"] for it in items})
    print(f"\n✓ ifas_index.json: {len(items)} fragmentos · {docs} documentos ({mb:.1f} MB)")
    print("  Siguiente paso: subirlo a la raíz de onyx_help con GitHub Desktop → esperar 1–2 min → Ctrl+Shift+R.")


if __name__ == "__main__":
    main()
