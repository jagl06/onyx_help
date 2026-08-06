# PROCEDIMIENTO — Añadir nueva documentación a IFAS

Cómo funciona: IFAS busca con BM25 dentro de `ifas_index.json` (un fragmento por página de PDF) directamente en el navegador, sin backend. Añadir documentación = regenerar ese archivo y subirlo al repo. El estado se confirma en la barra **📚 Documentación** de la app ("X fragmentos listos").

Formato del índice (lo que consume `index.html`):

```json
{"count": 8463, "items": [{"id": 0, "cat": "ANNUNCIATORS", "doc": "15342 Annunciator Control Module ACM-8R Instruction Manual", "page": 1, "text": "..."}]}
```

---

## A. Añadir un manual nuevo al índice BM25

**Requisitos (una sola vez):** Python 3 y `pip install pymupdf`. Los scripts `build_index.py` y `check_index.py` están en la raíz del repo.

**0. Verificar si el documento ya está cargado**

Antes de reindexar, comprueba contra el índice **ya publicado** en la app:

```
python check_index.py FSP-851 --web
```

- `✓ YA CARGADO` → no hace falta hacer nada (salvo que sea una revisión más nueva del manual: en ese caso reemplaza el PDF viejo en la carpeta y reindexa).
- `✗ NO ESTÁ` → continúa con el paso 1.
- Sin término de búsqueda (`python check_index.py --web`) muestra el resumen completo: categorías, documentos y fragmentos cargados.
- Encuentra el modelo aunque lo escribas sin guion (`fsp851` = `FSP-851`). Sin `--web` consulta el `ifas_index.json` local recién generado en lugar del publicado.

**1. Guardar el PDF en la carpeta de su categoría**

```
C:\Users\Jesus\OneDrive - ISELEC\PRODUCTOS\NOTIFIER\PDFS Onyx
```

- La categoría es la **primera subcarpeta** bajo la raíz (ej. `ANNUNCIATORS`, `DETECTORES`). Para una categoría nueva, basta con crear la carpeta.
- **El nombre del archivo importa:** el motor da bonus cuando el nombre coincide con la consulta. Incluye número de documento + modelo + título, ej. `I56-3894 FSP-851 Photoelectric Detector.pdf`.
- El PDF debe tener texto seleccionable. Si es escaneado, pásale OCR antes (el script reporta las páginas sin texto útil).

**2. Regenerar el índice completo**

```
python build_index.py "C:\Users\Jesus\OneDrive - ISELEC\Desktop\PDFS Onyx"
```

Genera `ifas_index.json` en la carpeta actual y reporta por documento cuántas páginas indexó.

**3. Verificar localmente**

- El total de fragmentos debe ser **mayor** al anterior (visible en el `count` y en el resumen del script).
- Validar que el JSON es correcto: `python -m json.tool ifas_index.json > nul`
- Vigilar el tamaño: el índice se descarga completo en el navegador del técnico. Hoy ronda 12 MB; sobre 20 MB conviene depurar.

**4. Subir a GitHub**

1. Repo `onyx_help` → raíz (mismo nivel que `index.html`) → **Add file → Upload files** → arrastrar `ifas_index.json` → **Commit changes**. (El límite web de GitHub es 25 MB por archivo; si el índice lo supera, subir con Git de escritorio.)
2. Esperar 1–2 minutos a que GitHub Pages publique.
3. Abrir `ifas.iselec.com.pa` y forzar recarga con **Ctrl+Shift+R**.

**5. Comprobar en la app**

- La barra 📚 debe mostrar el nuevo total de "fragmentos listos" (en verde).
- Hacer una consulta de prueba mencionando el modelo del manual nuevo y confirmar que la respuesta cita `documento · pág. X` del PDF agregado.

---

## B. Documentos puntuales sin tocar el índice

Para una ficha técnica que se necesita **ya** en campo, no hace falta reindexar: cualquier modo de chat acepta adjuntar el PDF o foto con 📎 y la IA lo analiza en esa conversación. El índice es para documentación permanente del equipo.

> Nota: la versión actual de `index.html` ya no consume manuales de la Files API de Anthropic (el selector de manuales fue reemplazado por el índice BM25). `upload_manuals.py` queda como herramienta legada; solo sería necesario si se reactiva esa vía.

---

## C. Datos estructurados (no van al índice)

| Archivo | Contenido | Cómo añadir |
|---|---|---|
| `fuentes.json` | Fuentes de poder y catálogo de baterías (modo 🔋) | Editar el JSON en el repo con los valores **del datasheet**, marcar `"verificado": true` solo con fuente confirmada. Commit directo, sin tocar `index.html`. |
| `ifas_device_library.json` | Librería de aparatos de notificación (corrientes sb/al) | Igual: agregar el dispositivo con corrientes del datasheet y hacer commit. |

Regla anti-alucinación: **ningún valor entra a estos archivos sin datasheet UL del fabricante.**

---

## Checklist rápido

- [ ] `python check_index.py <modelo> --web` → confirmar que NO está cargado
- [ ] PDF con texto (OCR si es escaneado), nombre con nº de documento + modelo
- [ ] PDF en `PDFS Onyx\<CATEGORÍA>\`
- [ ] `python build_index.py "...\PDFS Onyx"`
- [ ] `count` aumentó y JSON válido
- [ ] Commit de `ifas_index.json` en la raíz de `onyx_help`
- [ ] Esperar 1–2 min → Ctrl+Shift+R → 📚 muestra el nuevo total
- [ ] Consulta de prueba cita el manual nuevo
