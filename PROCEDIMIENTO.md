# PROCEDIMIENTO — Añadir nueva documentación a IFAS (v2)

Cómo funciona: IFAS busca con BM25 dentro de `ifas_index.json` (un fragmento por página de PDF) directamente en el navegador, sin backend. El **corpus maestro es el propio índice publicado**; los manuales nuevos se suman incrementalmente con `add_to_index.py`. El estado se ve en la barra **📚 Documentación** de la app ("X fragmentos listos").

Formato del índice (lo que consume `index.html`):

```json
{"count": 8241, "items": [{"id": 0, "cat": "ANNUNCIATORS", "doc": "15342 Annunciator Control Module ACM-8R Instruction Manual", "page": 1, "text": "..."}]}
```

**Carpetas fuente de la documentación:**

- `C:\Users\Jesus\OneDrive - ISELEC\PRODUCTOS\NOTIFIER\DOCUMENTACION NOTIFIER ONYX UNIVERSITY` (categoría = primera subcarpeta)
- `C:\Users\Jesus\OneDrive - ISELEC\PRODUCTOS\NOTIFIER\ENTRENAMIENTO\PRESENTACIONES` (todo bajo la categoría PRESENTACIONES)

---

## Preparación (una sola vez)

1. Carpeta de trabajo en tu PC (ej. `C:\Users\Jesus\Desktop\IFAS_scripts`) con los 4 scripts del repo: `add_to_index.py`, `check_index.py`, `build_index.py` e `ifas_pdf_utils.py` (módulo compartido — siempre junto a los otros).
2. `pip install pymupdf`
3. Opcional (para PDFs escaneados): instalar Tesseract OCR — instalador Windows de UB Mannheim: https://github.com/UB-Mannheim/tesseract/wiki. Sin Tesseract los scripts funcionan igual, pero omiten las páginas escaneadas y lo avisan.

---

## A. Añadir un manual nuevo (vía oficial)

**1. Guardar el PDF en su categoría**

```
...\NOTIFIER\DOCUMENTACION NOTIFIER ONYX UNIVERSITY\<CATEGORÍA>\<documento>.pdf
```

- **El nombre del archivo importa:** el motor da bonus cuando el nombre coincide con la consulta. Incluye nº de documento + modelo + título, ej. `I56-3894 FSP-851 Photoelectric Detector.pdf`. Evita nombres tipo `hbt-fire-xxxx` o `scan001`.
- Las categorías existentes se listan con `python check_index.py --web`; para un tipo de equipo nuevo, crea la carpeta.

**2. Verificar que no esté ya cargado**

Abrir `cmd` en la carpeta de trabajo (Explorador → barra de dirección → escribir `cmd` → Enter) y:

```
python check_index.py FSP-951 --web
```

- `✓ YA CARGADO` → nada que hacer (salvo revisión nueva → paso 3 con `--reemplazar`).
- `✗ NO ESTÁ` → continuar.
- Encuentra el modelo aunque se escriba sin guion (`fsp951` = `FSP-951`).

**3. Añadirlo al índice publicado**

```
python add_to_index.py "ruta\completa\al\documento.pdf" -c DETECTORS --web
```

- `--web` parte del índice publicado en ifas.iselec.com.pa, le suma el PDF (con **OCR automático** si es escaneado) y genera `ifas_index.json` en la carpeta de trabajo.
- Varios PDFs de la misma categoría: pasar la carpeta en lugar del archivo.
- Revisión más nueva de un manual existente: agregar `--reemplazar`.
- Si ya había un `ifas_index.json` local, queda respaldado como `ifas_index_anterior.json`.

**4. Subir al repo — con GitHub Desktop**

Copiar/commit del `ifas_index.json` generado a la raíz de `onyx_help` y **push con GitHub Desktop**. (La subida web de GitHub falla en silencio con archivos de ~12 MB — no usarla para el índice.)

**5. Comprobar en la app**

- Esperar 1–2 min (build de GitHub Pages) y recargar IFAS — recarga normal basta (el fetch usa `no-cache`).
- La barra 📚 debe mostrar el nuevo total de fragmentos.
- Consulta de prueba mencionando el modelo → debe citar `documento · pág. X`.

---

## B. Reconstrucción total (solo emergencias)

`build_index.py` regenera TODO el índice desde cero. Solo usarlo si el índice publicado se corrompe o se pierde. Debe recibir **todas** las fuentes:

```
python build_index.py "C:\Users\Jesus\OneDrive - ISELEC\PRODUCTOS\NOTIFIER\DOCUMENTACION NOTIFIER ONYX UNIVERSITY" "C:\Users\Jesus\OneDrive - ISELEC\PRODUCTOS\NOTIFIER\ENTRENAMIENTO\PRESENTACIONES::PRESENTACIONES"
```

- La sintaxis `ruta::CATEGORIA` fuerza una sola categoría para todo lo de esa raíz.
- Excluye automáticamente: carpetas que empiecen con `_`, archivos `ALL_*` y `PRESENTACION CONSOLIDADA` (compilados que duplican contenido).
- Aplica OCR a los escaneados si Tesseract está instalado.
- Antes de subir, comparar contra lo publicado: `python check_index.py --web`.

---

## C. Documentos puntuales sin tocar el índice

Para una ficha que se necesita **ya** en campo, no hace falta indexar: se adjunta con 📎 en cualquier modo de chat y la IA la analiza en esa conversación. El índice es para documentación permanente del equipo.

---

## D. Datos estructurados (no van al índice)

| Archivo | Contenido | Cómo añadir |
|---|---|---|
| `fuentes.json` | Fuentes de poder y catálogo de baterías (modo 🔋) | Editar el JSON en el repo con valores **del datasheet**; `"verificado": true` solo con fuente confirmada. |
| `ifas_device_library.json` | Aparatos de notificación (corrientes sb/al) | Igual: agregar el dispositivo con corrientes del datasheet y hacer commit. |

Regla anti-alucinación: **ningún valor entra a estos archivos sin datasheet UL del fabricante.**

---

## Checklist rápido

- [ ] PDF en su categoría, nombre con nº de documento + modelo
- [ ] `python check_index.py <modelo> --web` → ✗ NO ESTÁ
- [ ] `python add_to_index.py "ruta.pdf" -c CATEGORIA --web` (+ `--reemplazar` si es revisión)
- [ ] Subir `ifas_index.json` con **GitHub Desktop**
- [ ] 1–2 min → recargar IFAS → 📚 muestra el nuevo total
- [ ] Consulta de prueba cita el documento nuevo
- [ ] Registrar la entrada en `CONTROL_CAMBIOS.md`
