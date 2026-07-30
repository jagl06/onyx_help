#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_index.py — Verifica qué documentación ya está cargada en ifas_index.json.

Uso:
    python check_index.py                     Resumen: categorías, documentos y fragmentos (índice local)
    python check_index.py FSP-851             Busca si un documento/modelo ya está en el índice local
    python check_index.py --web               Igual, pero consulta el índice YA PUBLICADO en ifas.iselec.com.pa
    python check_index.py FSP-851 --web       Busca en el índice publicado

Sin instalar nada: usa solo la librería estándar de Python.
"""
import argparse
import json
import os
import sys
import unicodedata

URL = "https://ifas.iselec.com.pa/ifas_index.json"


def normaliza(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def cargar(web):
    if web:
        from urllib.request import urlopen
        print(f"Descargando índice publicado: {URL} …")
        with urlopen(URL, timeout=60) as r:
            return json.load(r)
    ruta = "ifas_index.json"
    if not os.path.exists(ruta):
        sys.exit("No encuentro ifas_index.json en esta carpeta. Usa --web para consultar el publicado.")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description="Verifica documentos cargados en el índice de IFAS.")
    ap.add_argument("busqueda", nargs="?", help="Modelo o parte del nombre del documento (ej. FSP-851)")
    ap.add_argument("--web", action="store_true", help="Consultar el índice publicado en ifas.iselec.com.pa")
    args = ap.parse_args()

    data = cargar(args.web)
    items = data.get("items", [])
    origen = "publicado (web)" if args.web else "local"

    # documentos únicos: {(cat, doc): nº fragmentos}
    docs = {}
    for it in items:
        k = (it["cat"], it["doc"])
        docs[k] = docs.get(k, 0) + 1

    if args.busqueda:
        q = normaliza(args.busqueda)
        q2 = "".join(ch for ch in q if ch.isalnum())  # sin guiones/espacios: fsp851 encuentra FSP-851
        def coincide(texto):
            t = normaliza(texto)
            return q in t or (q2 and q2 in "".join(ch for ch in t if ch.isalnum()))
        hits = [(c, d, n) for (c, d), n in sorted(docs.items()) if coincide(d) or coincide(c)]
        if hits:
            print(f"\n✓ YA CARGADO — {len(hits)} documento(s) coinciden con «{args.busqueda}» en el índice {origen}:\n")
            for c, d, n in hits:
                print(f"  [{c}]  {d}  ({n} páginas)")
        else:
            print(f"\n✗ NO ESTÁ — ningún documento coincide con «{args.busqueda}» en el índice {origen}.")
            print("  Puedes agregarlo siguiendo el Procedimiento A.")
        return

    # resumen general
    cats = {}
    for (c, _), n in docs.items():
        a, b = cats.get(c, (0, 0))
        cats[c] = (a + 1, b + n)
    print(f"\nÍndice {origen}: {len(docs)} documentos · {len(items)} fragmentos · {len(cats)} categorías\n")
    for c in sorted(cats):
        nd, nf = cats[c]
        print(f"  {c:<30} {nd:>3} docs   {nf:>5} fragmentos")
    print("\nPara ver si un manual específico ya está: python check_index.py <modelo>")


if __name__ == "__main__":
    main()
