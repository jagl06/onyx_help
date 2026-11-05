#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contextualizar_indice.py — Recuperación contextual para los índices de IFAS.

Para cada fragmento genera, con Claude Haiku, una línea de contexto ("Manual de programación NFS2-3030,
sección Supervisión: opción AUXILIARY TROUBLE REPORTING para el conector J5 del CPU2-3030") y la antepone
al texto antes de reindexar. Así el BM25 encuentra el fragmento aunque el técnico no escriba el código
exacto. El documento completo va en el prompt con caché, así que el costo por fragmento es bajo.

Uso (raíz del clon, con idx/):
    set ANTHROPIC_API_KEY=sk-ant-...        (PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-...")
    python contextualizar_indice.py --dry-run                  # cuenta fragmentos y estima costo, sin llamar a la API
    python contextualizar_indice.py -c procedimientos          # una categoría (empieza por la pequeña para probar)
    python contextualizar_indice.py                            # todas
    python contextualizar_indice.py -c detectores --limite 50  # prueba corta

Salida: idx/idx_<categoria>.json reescrito con campo "ctx" y "texto" = ctx + texto original (el original queda en
"texto_orig"). Reanudable: los fragmentos que ya tienen "ctx" se saltan. Respaldo previo en idx/respaldo_sin_ctx/.
Requisitos: pip install anthropic
"""
import argparse
import json
import os
import shutil
import sys
import time
from collections import defaultdict

IDX_DIR = "idx"
MODELO = "claude-haiku-4-5-20251001"
MAX_DOC_CHARS = 150_000          # documentos más largos se recortan al entorno del fragmento
VENTANA = 20_000                 # si el doc es muy largo, se envía este contexto alrededor del fragmento

SYSTEM = ("Eres un indexador técnico. Recibes un documento Notifier (manual, datasheet o presentación) y uno de sus "
          "fragmentos. Escribe UNA sola línea, en español, de 15 a 40 palabras, que sitúe el fragmento dentro del documento "
          "para que una búsqueda por palabras lo encuentre: nombre y modelo del equipo, sección o tema, y los términos clave "
          "en inglés y español que un técnico usaría (conector, jumper, trouble, corriente, cargador, etc.). "
          "No resumas el contenido, no inventes datos, no uses markdown ni comillas. Solo la línea.")


def doc_text(frs):
    """Reconstruye el texto del documento a partir de sus fragmentos (ordenados por página)."""
    frs = sorted(frs, key=lambda f: (f["pag"], f["id"]))
    partes, prev = [], ""
    for f in frs:
        t = f.get("texto_orig") or f["texto"]
        if prev and t[:60] and prev.endswith(t[:60][: len(prev)]):
            pass
        partes.append(f"[pág. {f['pag']}] {t}")
        prev = t
    return "\n".join(partes)


def contexto(client, doc_txt, frag_txt):
    if len(doc_txt) > MAX_DOC_CHARS:
        k = doc_txt.find(frag_txt[:80])
        ini = max(0, (k if k >= 0 else 0) - VENTANA // 2)
        doc_txt = doc_txt[ini: ini + VENTANA]
    r = client.messages.create(
        model=MODELO, max_tokens=120, system=SYSTEM,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "<documento>\n" + doc_txt + "\n</documento>",
             "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": "<fragmento>\n" + frag_txt + "\n</fragmento>\nLínea de contexto:"}]}])
    return "".join(b.text for b in r.content if b.type == "text").strip().replace("\n", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--categoria", default=None)
    ap.add_argument("--limite", type=int, default=0, help="procesar solo N fragmentos (prueba)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(os.path.join(IDX_DIR, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    entradas = [e for e in manifest["indices"] if not args.categoria or e["categoria"] == args.categoria]
    if not entradas:
        sys.exit("Categoría no encontrada en el manifest.")

    total_pend = 0
    for e in entradas:
        with open(os.path.join(IDX_DIR, e["archivo"]), encoding="utf-8") as f:
            frs = json.load(f)["fragmentos"]
        pend = sum(1 for x in frs if not x.get("ctx"))
        total_pend += pend
        print(f"{e['categoria']:18} {len(frs):6} fragmentos · {pend:6} sin contexto")
    # estimación: ~2.5k tokens de entrada cacheados + ~300 tokens de salida y fragmento por llamada
    print(f"\nPendientes: {total_pend}. Estimación con Haiku: ~{total_pend*0.0009:.0f}-{total_pend*0.0015:.0f} USD, "
          f"~{total_pend*1.2/60:.0f} min a 1.2 s/llamada.")
    if args.dry_run:
        return
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Falta ANTHROPIC_API_KEY en el entorno.")
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic")
    client = anthropic.Anthropic()

    os.makedirs(os.path.join(IDX_DIR, "respaldo_sin_ctx"), exist_ok=True)
    hechos = 0
    for e in entradas:
        ruta = os.path.join(IDX_DIR, e["archivo"])
        resp = os.path.join(IDX_DIR, "respaldo_sin_ctx", e["archivo"])
        if not os.path.exists(resp):
            shutil.copy(ruta, resp)
        with open(ruta, encoding="utf-8") as f:
            idx = json.load(f)
        frs = idx["fragmentos"]
        por_doc = defaultdict(list)
        for x in frs:
            por_doc[x["doc"]].append(x)
        cache_doc = {}
        t0 = time.time()
        for i, x in enumerate(frs):
            if x.get("ctx"):
                continue
            if args.limite and hechos >= args.limite:
                break
            if x["doc"] not in cache_doc:
                cache_doc[x["doc"]] = doc_text(por_doc[x["doc"]])
            orig = x.get("texto_orig") or x["texto"]
            for intento in range(4):
                try:
                    ctx = contexto(client, cache_doc[x["doc"]], orig)
                    break
                except Exception as ex:
                    espera = 5 * (intento + 1)
                    print(f"  ⚠ {x['id']}: {ex} — reintento en {espera}s")
                    time.sleep(espera)
            else:
                continue
            x["texto_orig"] = orig
            x["ctx"] = ctx
            x["texto"] = ctx + "\n" + orig
            hechos += 1
            if hechos % 25 == 0:
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))
                v = (time.time() - t0) / max(1, hechos)
                print(f"  {e['categoria']}: {hechos} hechos · {v:.1f} s/frag · guardado")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))
        e["bytes"] = os.path.getsize(ruta)
        print(f"✓ {e['categoria']}: guardado ({e['bytes']/1e6:.2f} MB)")
        if args.limite and hechos >= args.limite:
            break
    with open(os.path.join(IDX_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"\nListo: {hechos} fragmentos contextualizados. Después: node test_motor.js → git add idx/ → commit → push.")


if __name__ == "__main__":
    main()
