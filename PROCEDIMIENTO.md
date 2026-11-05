# PROCEDIMIENTO — Documentación y datos de IFAS (v3, desde v2026.1)

Cómo funciona desde v2026.1: IFAS busca con BM25 en el navegador dentro de `idx/`, que tiene un índice JSON por categoría y un `manifest.json`. Al abrir la app se cargan los índices base de la familia elegida en la barra 📚 (ONYX o INSPIRE N16; "Todas" carga los doce) y el índice de la otra familia se trae solo cuando la consulta lo pide. Además el modelo puede hacer hasta 3 búsquedas propias por pregunta (`buscar_documentacion`), en todos los modos salvo Diccionario. El antiguo `ifas_index.json` ya no existe.

Formato de un fragmento (lo que consume index.html):

```json
{"id":"detectores-000123","doc":"DN-60977","titulo":"DN_60977 FSP-951 Series ... Datasheet","rev":"","familia":"ONYX","idioma":"en","modelos":["FSP-951"],"pag":2,"tipo":"datasheet","texto":"..."}
```

Categorías: paneles_onyx, paneles_n16, fuentes, detectores, modulos, anunciadores_red, notificacion, compatibilidad, cable_norma, liberacion_swift, procedimientos, cursos_2026. Familias: ONYX, N16, COMUN. Tipos: manual, datasheet, install_sheet, compat, listado, presentacion, video, procedimiento, norma, boletin.

Origen del corpus 2026: `C:\Users\Jesus\OneDrive - ISELEC\PRODUCTOS\NOTIFIER\Certificación 2026\IFAS_2026` (00_pdf_limpio, 01_texto, 02_index, 03_videos, 04_datos, 05_reporte, 06_app, 07_validacion). `02_index` es la copia maestra de `idx/`.

---

## Preparación (una sola vez)

1. Clon local de `onyx_help` al día (`git pull`). Los scripts `add_to_index.py` (v3), `ifas_pdf_utils.py`, `check_index.py` y `test_motor.js` viven en la raíz del repo.
2. `pip install pymupdf`
3. Opcional, para PDFs escaneados: Tesseract OCR (instalador Windows de UB Mannheim). Sin Tesseract el script omite las páginas escaneadas y lo avisa.
4. Node.js (para `test_motor.js`).

---

## A. Añadir un manual nuevo

1. Nombre del archivo con número de documento + modelo + título: `DN-62150 FSP-961 Photoelectric Detector Datasheet.pdf`. El número al inicio se convierte en el campo `doc`; el modelo se deduce del nombre y alimenta el bonus de búsqueda y la carga bajo demanda.
2. Comprobar que no esté: buscar el modelo en la app (barra de chat, cualquier modo) o `python check_index.py FSP-961 --web`.
3. Añadirlo, desde la raíz del clon:

```
python add_to_index.py "ruta\al\documento.pdf" -c detectores
python add_to_index.py "ruta\al\documento.pdf" -c paneles_n16 --familia N16
python add_to_index.py "ruta\carpeta" -c modulos --reemplazar
```

Opciones: `--familia ONYX|N16|COMUN` (por defecto ONYX), `--idioma es|en` (por defecto se deduce: SP, "Manual de", "Hoja de Datos" → es), `--tipo` (por defecto datasheet si DN, install_sheet si I56, manual en otro caso), `--modelos FSP-961,B710LP` si el nombre no los trae, `--reemplazar` para revisiones nuevas.

El script fragmenta en trozos de 700-900 caracteres con solapamiento de 120, escribe `idx/idx_<categoria>.json` y actualiza `idx/manifest.json`. Avisa si el índice pasa de 8 MB.

4. Copiar los dos archivos modificados a `IFAS_2026\02_index` (copia maestra) y el PDF a `00_pdf_limpio\<categoria>`.
5. `git add idx/` → commit → push (GitHub Desktop o Code). No usar la subida web de GitHub para los índices grandes.
6. 1-2 min → Ctrl+Shift+R en IFAS → la barra 📚 muestra el nuevo total. Consulta de prueba con el modelo: debe citar `documento · pág. X`.
7. Entrada en `CONTROL_CAMBIOS.md`.

---

## B. Reconstrucción total

Solo si `idx/` se pierde o se corrompe: volver a copiar los 13 archivos de `IFAS_2026\02_index`. Si hay que regenerar todo desde los PDF, el pipeline es el de `INSTRUCCIONES_CHATGPT_IFAS_2026.md` (inventario, texto, fragmentación, índices por categoría), no `build_index.py`, que corresponde al formato antiguo y queda solo como referencia.

---

## C. Documentos puntuales sin tocar el índice

Una ficha que se necesita ya en campo se adjunta con 📎 en cualquier modo de chat y el modelo la analiza en esa conversación. El índice es para documentación permanente.

---

## D. Datos estructurados (no van al índice)

| Archivo | Contenido | Cómo añadir |
|---|---|---|
| `fuentes.json` | Fuentes de poder y catálogo de baterías (modo 🔋) | Editar el JSON con valores del datasheet y poner `verificado: true` solo cuando placa standby/alarma, nacs, nacMax, cargadorMin y cargadorMax estén confirmados. Mientras sea false, la fuente aparece con ⚠ y el cálculo se bloquea. Campo `fuente_datos`: documento y página. |
| `examen.json` | Banco de preguntas del modo Examen (estilo quiz Honeywell) | Una entrada por pregunta: id, tema (clave de `temas`), tipo (unica, multiple, vf), pregunta, opciones A-D, correcta (letras), explicacion y ref {doc, pag} que exista en `idx/`. Una pregunta con `verificar: true` no se sirve hasta confirmarla. Las preguntas reales del curso (capturas del quiz) se transcriben con el mismo formato. |
| `ifas_device_library.json` | Aparatos de notificación (corrientes sb/al) | Formato `{pn, d, t, sb, al}` en amperios. Solo aparatos de NAC: detectores y módulos son carga del SLC y no van aquí. |

Estado de las fuentes pendientes y qué falta a cada una: `IFAS_2026\07_validacion\VALIDACION_DATOS_2026.md`.

Regla: ningún valor entra a estos archivos sin datasheet o manual del fabricante, con documento y página anotados.

---

## E. Ajustar la búsqueda

- Sinónimos: tabla `SINONIMOS` en index.html (español de campo → inglés de los manuales). Añadir una línea por término o frase, clave en minúsculas sin acentos. Peso de los términos expandidos: 0.4 (constante en `expandQuery`).
- Prioridades del ranking (función `retrieve`): términos raros con dígitos (J5, TB4) multiplican la puntuación; documento nombrado en la consulta ×3; familia distinta a la seleccionada ×0.5; español ×1.1; máximo 3 fragmentos por documento; TOP_K = 10.
- Búsqueda agéntica: `MAX_BUSQUEDAS` (3), definición `BUSCAR_TOOL` y texto `TOOL_PROMPT`. Diccionario no la usa.
- Antes de subir cualquier cambio al motor: `node test_motor.js` desde la raíz del clon. Compara 30 consultas de campo con el documento y página esperados y falla si alguna se pierde.

---

## Checklist rápido

- [ ] PDF con nº de documento + modelo en el nombre
- [ ] No está ya en el índice
- [ ] `python add_to_index.py "ruta.pdf" -c <categoria> [--familia] [--reemplazar]`
- [ ] Copia a `IFAS_2026\02_index` y `00_pdf_limpio`
- [ ] `git add idx/` → commit → push
- [ ] 1-2 min → Ctrl+Shift+R → 📚 muestra el total nuevo → consulta de prueba cita el documento
- [ ] Entrada en `CONTROL_CAMBIOS.md`
