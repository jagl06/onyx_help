#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_to_index.py (v3, IFAS 2026) — Añade PDFs a los índices por categoría de idx/ sin reconstruirlos.
Es la vía OFICIAL para actualizar la documentación de IFAS desde v2026.1.

Uso (desde la carpeta raíz del clon de onyx_help, donde está idx/):
    python add_to_index.py "documento.pdf" -c detectores --modelos FSP-951 --familia ONYX
    python add_to_index.py "carpeta_con_pdfs" -c modulos
    python add_to_index.py "documento.pdf" -c paneles_n16 --familia N16 --idioma en --tipo manual --reemplazar

Categorías válidas: paneles_onyx paneles_n16 fuentes detectores modulos anunciadores_red
                    notificacion compatibilidad cable_norma liberacion_swift procedimientos cursos_2026
Tipos válidos:      manual datasheet install_sheet compat listado presentacion video procedimiento norma boletin

Qué hace: extrae el texto por página (OCR automático si hay Tesseract), lo fragmenta en trozos de
700-900 caracteres con 120 de solapamiento (mismo criterio que el paquete IFAS_2026), lo añade a
idx/idx_<categoria>.json y actualiza idx/manifest.json (fragmentos, bytes, docs, modelos).
Si el documento ya existe en el índice se omite, salvo --reemplazar.

Requisitos: pip install pymupdf  ·  ifas_pdf_utils.py en la misma carpeta  ·  OCR opcional (Tesseract).
Después: commit de idx/idx_<categoria>.json e idx/manifest.json → push → 1-2 min → Ctrl+Shift+R.
"""
import argparse
import json
import os
import re
import sys
from datetime import date

from ifas_pdf_utils import extraer_paginas

IDX_DIR = "idx"
CATS = ["paneles_onyx", "paneles_n16", "fuentes", "detectores", "modulos", "anunciadores_red",
        "notificacion", "compatibilidad", "cable_norma", "liberacion_swift", "procedimientos", "cursos_2026"]
TIPOS = ["manual", "datasheet", "install_sheet", "compat", "listado", "presentacion", "video",
         "procedimiento", "norma", "boletin"]
OBJ, MAX, SOLAPE = 700, 900, 120
MODELO_RE = re.compile(r"\b(NFS2?-\d{3,4}\w*|N16\w*|AMPS-24E?|ACPS-\d+E?|APS2-6R|FCPS-24S\d|PSE-\d+|HS-NCM\w*|NCM-\w|"
                       r"F[A-Z]{2,3}-\d{3}\w*|B\d{3}\w*|NBG-12\w*|FMM-\w+|FCM-\w+|FRM-\w+|FZM-\w+|FDM-\w+|ISO-X|XP\d+-\w|"
                       r"LCM-320|LEM-320|CPU2?-\w+|SLM-318|ACM-\w+|CAB-\d|RLD|NCA-2|NCD|LCD-?\d*-?\d*|FDU-80|SWIFT|FW-\w+)\b", re.I)


def fragmentar(texto):
    """Corta en punto, salto de línea o fin de fila de tabla; nunca a mitad de palabra."""
    texto = re.sub(r"[ \t]+", " ", texto).strip()
    if len(texto) <= MAX:
        return [texto] if texto else []
    out, i, n = [], 0, len(texto)
    while i < n:
        fin = min(i + MAX, n)
        if fin < n:
            corte = -1
            for sep in ("\n", ". ", " | ", "; ", " "):
                k = texto.rfind(sep, i + OBJ, fin)
                if k != -1:
                    corte = k + len(sep)
                    break
            if corte != -1:
                fin = corte
        trozo = texto[i:fin].strip()
        if trozo:
            out.append(trozo)
        if fin >= n:
            break
        i = max(fin - SOLAPE, i + 1)
    return out


def num_doc(nombre):
    """Número Notifier al inicio del nombre de archivo, si lo hay (52745SP, DN-7111, I56-3518, LS10239-000NF-E)."""
    m = re.match(r"^(DN[-_ ]?\d+\w*|I56-[\d-]+\w*|LS\d{5}-\w+(?:-\w)?|\d{4,5}[A-Z]{0,3})", nombre, re.I)
    return m.group(1).upper().replace("_", "-").replace(" ", "-") if m else nombre


def main():
    ap = argparse.ArgumentParser(description="Añade PDFs a los índices por categoría de IFAS.")
    ap.add_argument("ruta", help="PDF o carpeta con PDFs")
    ap.add_argument("-c", "--categoria", required=True, choices=CATS)
    ap.add_argument("--familia", default="ONYX", choices=["ONYX", "N16", "COMUN"])
    ap.add_argument("--idioma", default=None, choices=["es", "en"], help="Por defecto se deduce del nombre (SP, Manual de, Hoja de Datos → es)")
    ap.add_argument("--tipo", default=None, choices=TIPOS, help="Por defecto: datasheet si el nombre empieza por DN, install_sheet si I56, manual en otro caso")
    ap.add_argument("--modelos", default="", help="Modelos separados por coma; si se omite se deducen del nombre")
    ap.add_argument("--reemplazar", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(IDX_DIR):
        sys.exit(f"No existe la carpeta {IDX_DIR}/ aquí. Ejecuta el script desde la raíz del clon de onyx_help.")
    if os.path.isdir(args.ruta):
        pdfs = [os.path.join(args.ruta, f) for f in sorted(os.listdir(args.ruta)) if f.lower().endswith(".pdf")]
    elif os.path.isfile(args.ruta):
        pdfs = [args.ruta]
    else:
        sys.exit(f"No existe: {args.ruta}")
    if not pdfs:
        sys.exit("No hay PDFs en esa ruta.")

    cat = args.categoria
    ruta_idx = os.path.join(IDX_DIR, f"idx_{cat}.json")
    ruta_man = os.path.join(IDX_DIR, "manifest.json")
    with open(ruta_man, encoding="utf-8") as f:
        manifest = json.load(f)
    if os.path.exists(ruta_idx):
        with open(ruta_idx, encoding="utf-8") as f:
            idx = json.load(f)
    else:
        idx = {"categoria": cat, "version": manifest.get("version", "2026.1"), "generado": "", "fragmentos": []}
    frs = idx["fragmentos"]
    existentes = {fr["doc"] for fr in frs}
    agregados = 0

    for ruta in pdfs:
        nombre = os.path.splitext(os.path.basename(ruta))[0]
        doc = num_doc(nombre)
        if doc in existentes and not args.reemplazar:
            print(f"  ✗ {doc}: ya existe en idx_{cat}.json — omitido (usa --reemplazar)")
            continue
        try:
            pags, ocr = extraer_paginas(ruta)
        except Exception as e:
            print(f"  ⚠ No se pudo leer {os.path.basename(ruta)}: {e}")
            continue
        if not pags:
            print(f"  ⚠ {doc}: sin texto útil — omitido")
            continue
        if doc in existentes:
            frs[:] = [fr for fr in frs if fr["doc"] != doc]
            print(f"  ↻ {doc}: versión anterior eliminada")
        idioma = args.idioma or ("es" if re.search(r"(?<![A-Za-z])SP\b|Manual de|Hoja de Datos|Gu[ií]a", nombre, re.I) else "en")
        tipo = args.tipo or ("datasheet" if doc.startswith("DN") else "install_sheet" if doc.startswith("I56") else "manual")
        modelos = [m.strip().upper() for m in args.modelos.split(",") if m.strip()] or \
                  sorted({m.upper() for m in MODELO_RE.findall(nombre)})
        n = 0
        for page, text in pags:
            for trozo in fragmentar(text):
                frs.append({"id": "", "doc": doc, "titulo": nombre, "rev": "", "familia": args.familia,
                            "idioma": idioma, "modelos": modelos, "pag": page, "tipo": tipo, "texto": trozo})
                n += 1
        existentes.add(doc)
        agregados += 1
        print(f"  ✓ [{cat}] {doc}: {len(pags)} páginas → {n} fragmentos" + (" (OCR)" if ocr else "") + f" · modelos {modelos or '—'}")

    if agregados == 0:
        sys.exit("\nNada que hacer.")

    for i, fr in enumerate(frs, 1):
        fr["id"] = f"{cat}-{i:06d}"
    idx["generado"] = date.today().isoformat()
    with open(ruta_idx, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))

    entrada = next((e for e in manifest["indices"] if e["categoria"] == cat), None)
    if entrada is None:
        entrada = {"categoria": cat, "archivo": f"idx_{cat}.json"}
        manifest["indices"].append(entrada)
    entrada.update({"fragmentos": len(frs), "bytes": os.path.getsize(ruta_idx),
                    "docs": len({fr["doc"] for fr in frs}),
                    "modelos": sorted({m for fr in frs for m in fr.get("modelos", [])})})
    manifest["generado"] = date.today().isoformat()
    with open(ruta_man, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    mb = entrada["bytes"] / 1e6
    print(f"\n✓ idx_{cat}.json: {len(frs)} fragmentos · {entrada['docs']} documentos ({mb:.2f} MB)" +
          ("  ⚠ supera 8 MB: considera partirlo" if mb > 8 else ""))
    print("  Siguiente: git add idx/ → commit → push → 1-2 min → Ctrl+Shift+R en IFAS.")


if __name__ == "__main__":
    main()
