# -*- coding: utf-8 -*-
"""hereda_encabezado.py — enriquecimiento determinista de los índices de IFAS.

Problema: al trocear los manuales, una tabla queda en un fragmento y su rótulo ("Table 3.4 Default
Timers") en el siguiente, así que el fragmento con el dato no tiene ni una palabra que lo nombre y
BM25 no lo encuentra salvo citando sus propias celdas.

Arreglo: a cada fragmento SIN encabezado propio se le antepone el encabezado que le corresponde —
la sección más cercana hacia atrás y, si parece tabla, el rótulo del fragmento vecino. Sin API y
reproducible. No toca los fragmentos que ya traen su propio encabezado.

Uso:  python hereda_encabezado.py [--dir idx] [--dry-run]
Deja  texto_orig (texto original) y ctxh (el encabezado heredado) en cada fragmento modificado.
"""
import argparse, glob, json, os, re, sys

SEC = re.compile(r'(?<![\d.])((?:\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)|(?:[A-H]\.\d{1,2}(?:\.\d{1,2})?))\s+'
                 r'([A-Z][A-Za-zÁÉÍÓÚÑáéíóúñ][^\n|]{2,58})')
TAB = re.compile(r'\b(Table|Tabla|Figure|Figura)\s+(\d{1,2}\.\d{1,2})\s+([^\n|]{2,58})')
MALA = re.compile(r'^(on page|de la p|see |refer|consulte|por |y |o |en |the |and )', re.I)
ROTULO_ANTES = re.compile(r'(Table|Tabla|Figure|Figura)\s*$')
# un rotulo es un nombre, no una frase: "Figure 1.1 illustrates the typical..." es una referencia cruzada
FRASE = re.compile(r'(is|are|was|were|illustrates?|shows?|lists?|provides?|describes?|displays?|'
                   r'contains?|gives?|indicates?|ilustra|muestra|presenta|contiene|describe|indica|'
                   r'se\s+muestra|es\s+un|son\s+l)', re.I)

def limpia(t):
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.split(r'\s+(?:Press|Presione|Refer|Consulte|This |Esta |Este )', t)[0]
    t = t.strip(' .:·')
    # si se corto a media palabra por el limite de 58 caracteres, recorta al ultimo espacio
    if len(t) >= 54 and ' ' in t:
        t = t.rsplit(' ', 1)[0]
    return t.strip(' .:·,;')

def util(t):
    """Un encabezado sirve si es un nombre corto, no una frase ni un '(Continued)'."""
    if len(t) < 4 or MALA.match(t) or FRASE.search(t):
        return False
    if re.match(r'^\(?(Continued|Continuacion|Continuación)\)?$', t, re.I):
        return False
    return True

def encabezados(texto):
    secs, rots = [], []
    for m in SEC.finditer(texto):
        # "Table 3.3 AC Fail…" no es una sección 3.3
        if ROTULO_ANTES.search(texto[max(0, m.start() - 8):m.start()]):
            continue
        tit = limpia(m.group(2))
        if not util(tit) or re.match(r'^[A-Z]{2,}\s*[:=]', tit):
            continue
        secs.append('%s %s' % (m.group(1), tit))
    for m in TAB.finditer(texto):
        tit = limpia(m.group(3))
        if not util(tit):
            continue
        rots.append('%s %s %s' % (m.group(1), m.group(2), tit))
    return secs, rots

def es_tabla(t):
    return t.count('|') >= 3

def procesa(frs, ventana=12):
    """Devuelve (n_enriquecidos, n_total). Modifica frs en sitio.

    Idempotente: primero deshace cualquier enriquecimiento anterior y recalcula desde el texto
    original, así que correrlo dos veces da el mismo resultado y un encabezado heredado nunca
    sirve de fuente para heredar a un vecino."""
    for f in frs:
        quita_encabezado(f)
    porDoc = {}
    for f in frs:
        porDoc.setdefault(f['doc'], []).append(f)
    n = 0
    for doc, lista in porDoc.items():
        lista.sort(key=lambda f: (f.get('pag') or 0, f['id']))
        enc = [encabezados(f['texto']) for f in lista]
        for i, f in enumerate(lista):
            secs, rots = enc[i]
            if secs or rots:
                continue                                  # ya se nombra solo
            sec = None
            for j in range(i - 1, max(-1, i - 1 - ventana), -1):
                if enc[j][0]:
                    sec = enc[j][0][-1]; break
            rot = None
            if es_tabla(f['texto']):
                for j in (i + 1, i - 1):                  # el rótulo de una tabla suele ir después
                    if 0 <= j < len(lista) and enc[j][1]:
                        rot = enc[j][1][0]; break
            partes = [p for p in (sec, rot) if p]
            if not partes:
                continue
            ctxh = ' · '.join(partes)
            f.setdefault('texto_orig', f['texto'])
            f['ctxh'] = ctxh
            f['texto'] = '[' + ctxh + ']\n' + f['texto_orig']
            n += 1
    return n, len(frs)

def quita_encabezado(f):
    """Deshace el enriquecimiento de un fragmento, con o sin texto_orig."""
    if 'texto_orig' in f:
        f['texto'] = f.pop('texto_orig')
    elif f.get('ctxh'):
        pref = '[' + f['ctxh'] + ']\n'
        if f['texto'].startswith(pref):
            f['texto'] = f['texto'][len(pref):]
    f.pop('ctxh', None)
    return f


def refresca_manifest(dirname):
    """Pone al día bytes y generado del manifest (la app no los lee, pero quedan correctos)."""
    import datetime
    mp = os.path.join(dirname, 'manifest.json')
    if not os.path.exists(mp):
        print('sin manifest.json en %s' % dirname); return
    m = json.load(open(mp, encoding='utf-8'))
    for e in m.get('indices', []):
        fp = os.path.join(dirname, e['archivo'])
        if os.path.exists(fp):
            e['bytes'] = os.path.getsize(fp)
    m['generado'] = datetime.date.today().isoformat()
    json.dump(m, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('manifest.json: bytes actualizados y generado = %s' % m['generado'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='idx')
    ap.add_argument('-c', '--categoria', action='append', metavar='CAT',
                    help='solo esta categoría (repetible); por defecto, las 12')
    ap.add_argument('--dry-run', action='store_true', help='cuenta sin escribir')
    ap.add_argument('--sin-original', action='store_true',
                    help='no guarda texto_orig (ahorra ~4 MB; ctxh basta para deshacerlo)')
    ap.add_argument('--manifest', action='store_true', help='actualiza bytes y generado del manifest')
    ap.add_argument('--revertir', action='store_true', help='deshace el enriquecimiento')
    a = ap.parse_args()
    if a.categoria:
        rutas = [os.path.join(a.dir, 'idx_%s.json' % c) for c in a.categoria]
        faltan = [r for r in rutas if not os.path.exists(r)]
        if faltan:
            sys.exit('no existe: %s' % ', '.join(faltan))
    else:
        rutas = sorted(glob.glob(os.path.join(a.dir, 'idx_*.json')))
    tot = enr = 0
    for p in rutas:
        d = json.load(open(p, encoding='utf-8'))
        if a.revertir:
            n = sum(1 for f in d['fragmentos'] if f.get('ctxh') or 'texto_orig' in f)
            for f in d['fragmentos']:
                quita_encabezado(f)
            t = len(d['fragmentos'])
            print('%-26s %5d fragmentos · %5d revertidos' % (os.path.basename(p), t, n))
        else:
            n, t = procesa(d['fragmentos'])
            if a.sin_original:
                for f in d['fragmentos']:
                    f.pop('texto_orig', None)
            print('%-26s %5d fragmentos · %5d con encabezado heredado (%.1f%%)'
                  % (os.path.basename(p), t, n, 100.0 * n / t if t else 0))
        tot += t; enr += n
        if not a.dry_run:
            json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('\ntotal: %d fragmentos · %d %s (%.1f%%)%s'
          % (tot, enr, 'revertidos' if a.revertir else 'enriquecidos',
             100.0 * enr / tot if tot else 0, '  [dry-run, nada escrito]' if a.dry_run else ''))
    if a.manifest and not a.dry_run:
        refresca_manifest(a.dir)


main()
