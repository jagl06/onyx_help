# IFAS — Control de Cambios

App: **IFAS (ISELEC Fire Alarm Support)** · https://ifas.iselec.com.pa
Repo: `jagl06/onyx_help` (GitHub Pages) · Responsable: Jesús González (ISELEC Panamá)

Cómo usar este documento: cada vez que se haga un commit relevante en el repo, agregar una entrada al inicio de la sección "Historial" con este formato:

```
## AAAA-MM-DD — Título corto
**Archivos:** los tocados en el commit
**Cambios:** qué se hizo y por qué
**Verificación:** cómo se comprobó antes de desplegar
```

---

## Estado actual (2026-11-05)

| Componente | Estado |
|---|---|
| Modos | Troubleshooting, Reemplazo HW, Examen, Diccionario, Guía Rápida, Diseño, Batería |
| Modelo API | `claude-sonnet-4-6` (seleccionable: Haiku 4.5, Sonnet 3.5, Haiku 3) |
| Documentación | Índices BM25 por categoría en `idx/` (manifest 2026.1, 12 índices, 18.197 fragmentos, 15 MB) |
| Búsqueda | BM25 con sinónimos bilingües ES↔EN (88 claves, peso 0.4 frente a 1 de lo escrito), 10 fragmentos por consulta, refuerzo a códigos raros y ×3 al documento nombrado |
| Búsqueda agéntica | El modelo puede pedir hasta 3 búsquedas por pregunta con `buscar_documentacion`, resueltas por el motor local; activa en todos los modos salvo Diccionario |
| Datos externos | `fuentes.json` (fuentes/baterías), `ifas_device_library.json` (aparatos) |
| Tema | Claro/oscuro con botón 🌙/☀️, persistente (localStorage `ifas_theme`) |
| Responsive | Breakpoints 380 / 768 / 1100 px; Batería en 2 columnas en escritorio |
| Scripts de soporte | `build_index.py`, `check_index.py` (ver `PROCEDIMIENTO.md`) |

**Pendientes / hoja de ruta**

- Expansión de marcas: Hochiki, Siemens, Simplex (una a la vez, misma metodología ONYX: base de manuales + reglas de system prompt).
- IBAS (bombeo de agua): crear repo `ibas_help`, CNAME `ibas.iselec.com.pa`, desplegar v4.

---

# Historial

## 2026-11-05 — fuentes.json validado contra los manuales (v2026.2)
**Archivos:** fuentes.json, CONTROL_CAMBIOS.md
**Cambios:** las fuentes nuevas de la v2026.1 entraron con datos extraídos por script y sin validar, y la revisión contra los PDF encontró que dos eran falsos: el `nacs` de PSE-6 (5) y de PSE-10 (7) era en realidad la corriente de entrada AC, no el número de salidas NAC. Ambos pasan a `null`, así que el modo Batería se bloquea con esas fuentes en vez de calcular con un número inventado. Se completan los consumos propios de placa que faltaban: AMPS-24 y AMPS-24E a 0.13 A standby y alarma (DN-7070), APS2-6R a 0.041 A, FCPS-24S6 y FCPS-24S8 a 0.065 A y `cargadorMin` 7 AH. Las citas de `fuente_datos` pasan de "extracción automática 2026, sin validar" a referencias por página con lo que se verificó (salidas, límites de corriente, rangos de batería), y cada `nota` dice ahora qué falta y en qué tabla y páginas buscarlo, en lugar del texto genérico de datos candidatos. `nota_candidatos` resuelve la discrepancia de 0.25 A vs 0.35 A de NFS-320/NFS2-640: 0.25 A es la tarjeta sola y 0.35 A incluye el display KDM-R2. `verificado` sigue en 5 de 14 (HPFF8, HPFF12, NFS-320, NFS2-640, NFS2-3030): esta validación documenta y corrige, no habilita fuentes nuevas para cálculo. La sección `baterias` no cambió. Nota de historial: el commit `28cdd50` contiene únicamente `fuentes.json`; los sinónimos y la búsqueda agéntica que menciona su mensaje entraron antes en `4fd65b8`.
**Verificación:** JSON válido y estructura intacta (mismas 6 claves raíz, 14 fuentes, 6 baterías, ninguna entrada añadida ni eliminada); el `fuentes.json` servido por GitHub Pages es byte a byte idéntico al blob del commit `28cdd50`, publicado unos 45 s después del push; reproducido en producción el mismo `fetch('fuentes.json', {cache:'no-cache'})` que hace `loadFuentes()`: HTTP 200, `application/json`, `version` 2026.2, la app recibe las 14 fuentes y las 6 baterías que lee, y `PSE6.nacs` y `PSE10.nacs` llegan en `null`.

## 2026-11-05 — v2026.2: sinónimos bilingües y búsqueda agéntica con tool use (máx. 3)
**Archivos:** index.html, CONTROL_CAMBIOS.md
**Cambios:** el técnico pregunta en español de campo y los manuales están en inglés, así que una consulta como "falla a tierra en la tarjeta madre" no alcanzaba el documento que dice "ground fault" en la "main board"; y cuando los 10 fragmentos inyectados no traían el dato, el modelo contestaba que no lo tenía sin poder volver a buscar. Dos cambios: (1) mapa `SINONIMOS` de 88 claves (español ↔ inglés de los manuales, incluidas frases como "resistencia de fin de línea" → `eol`/`elr`) y `expandQuery`, que añade los sinónimos con peso 0.4 frente al 1 de los términos escritos por el técnico; el refuerzo de código raro queda restringido a los términos escritos (`weights[t]===1`) para que una expansión no lo dispare. (2) Búsqueda agéntica: se expone al modelo la herramienta `buscar_documentacion` (parámetro `consulta`) en todos los modos salvo Diccionario, con hasta `MAX_BUSQUEDAS` = 3 búsquedas adicionales por pregunta resueltas por el motor BM25 local; antes de cada búsqueda se cargan los índices que haga falta (`ensureIndexesFor`), el último `tool_result` lleva el aviso de límite alcanzado para que el modelo responda en vez de seguir pidiendo, las fuentes citadas acumulan los fragmentos de todas las búsquedas deduplicados por documento y página y acotados a 12, y el estado muestra "buscando: …" mientras corre cada una. El `TOOL_PROMPT` fija la estrategia: primero el código o modelo exacto, luego el nombre en inglés del parámetro o trouble, luego el número de documento más el tema, sin repetir consultas.
**Verificación:** sintaxis JS con node (2 bloques, sin fallos); comprobado antes de copiar que `ensureIndexesFor`, `docStatus`, `setDocStatus`, `statusText` y `docPages` ya existían, que es lo que la validación de sintaxis no detecta; el `index.html` servido por GitHub Pages es byte a byte idéntico al blob del commit `4fd65b8`, publicado 17 s después del push, sin errores de consola; probado en producción contra los índices reales: `expandQuery('falla a tierra en la tarjeta madre')` mantiene los términos escritos en 1 y añade `ground, earth, fault, trouble, failure, cpu, board, card, main, module` en 0.4, y la consulta en español "incompatibilidad de software" comparte 7 de 10 hits con "software mismatch", alcanzando documentos en inglés (52546 p.32) que antes no traía. El bucle agéntico no se probó de punta a punta porque pedir las búsquedas exige una llamada real a la API. Detectado al validar: las expansiones a `j` de `jumper`, `puente` y `conector` no se aplican nunca porque `tokenize` descarta los tokens de un carácter — las demás expansiones de esas tres claves sí funcionan, y enganchar `J5` o `J12` exigiría listar los códigos completos.

## 2026-11-05 — v2026.1.1: ranking BM25 con prioridad a códigos y documentos nombrados
**Archivos:** index.html, CONTROL_CAMBIOS.md
**Cambios:** los códigos de borne y puente (TB4, J5, SW2) se diluían entre el contexto genérico ("tarjeta", "panel", "voltaje") y una consulta que nombraba un documento no lo subía a los primeros puestos. Ahora un término con dígito que aparece en menos del 1 % de los fragmentos cuenta como código raro y multiplica el puntaje por 1 + número de aciertos; si la consulta contiene el identificador de un documento (52545SP, DN-7111, 15180) los fragmentos de ese documento se multiplican por 3; el bonus de nombre se acota con `Math.min(nameBonus, 4)` antes del ×1.5 para que un título muy coincidente no tape al resto del índice; TOP_K sube de 8 a 10 fragmentos por consulta; el tokenizer une "letra.dígito" ("tabla h.2" → `h2`); se agregan `docPages` (última página vista por documento) y `docIds`, poblados en `rebuildStats`; el contexto inyectado cita ahora "pág. N de ~M" y se elimina la rama `tipo==='video'`, que era código muerto porque ningún fragmento del índice lleva ese tipo.
**Verificación:** sintaxis JS con node (2 bloques, sin fallos); el `index.html` servido por GitHub Pages es byte a byte idéntico al blob del commit `2eab280`; sin errores de consola; `retrieve()` probado en producción contra los índices reales: "voltaje en TB4 de la NFS-320" devuelve 52745SP p.14 y 52745 p.12 (manual del NFS-320), "que dice 15180 sobre la instalacion" coloca los tres primeros hits en el documento pedido, `docIds` y `docPages` con 215 entradas, tres consultas en 34 ms.

## 2026-11-04 — v2026.1: índices por categoría (Notifier University 2026) + INSPIRE N16
**Archivos:** index.html, fuentes.json, idx/ (nuevo, 13 archivos), ifas_index.json (eliminado), CONTROL_CAMBIOS.md
**Cambios:** loader por manifest con carga base según familia (selector ONYX / INSPIRE N16 / Todas) y carga bajo demanda del otro índice; 18.197 fragmentos de 215 documentos, 8 presentaciones y 8 videos transcritos; BM25 con bonus de nombre 1.5, penalización 0.5 a la familia no seleccionada, preferencia 1.1 por español y máximo 3 fragmentos por documento; system prompt con identidad ONYX + N16, tabla de diagnóstico ampliada y Reglas 8 (firmware antes que hardware), 9 (recuperación de contraseña solo por Password Agreement), 10 (prueba de reaceptación NFPA 72 / 15378) y 11 (N16: capacidades, exclusiones, conversión de base de datos); fuentes.json con nueve fuentes nuevas marcadas por confirmar.
**Verificación:** sintaxis JS con node, JSON válidos, servidor local con todos los archivos en 200, motor BM25 probado contra los índices reales (ONYX 16.287 fragmentos en 1.1 s).

##  2026-08-06 - Actualización y limpieza de indice
**Archivo;** `ifas_index` (actualizo)
**Cambios;**
"Limpieza de duplicados + 8 docs nuevos (8,463 → 8,241 fragmentos, 198 → 196 docs), fix de caché no-cache, reorganización de carpeta NOTIFIER, y scripts v2 con OCR.".

## 2026-07-30 — Tema claro/oscuro + responsive + procedimiento de documentación
**Archivos:** `index.html`, `PROCEDIMIENTO.md` (nuevo), `build_index.py` (nuevo), `check_index.py` (nuevo)
**Cambios:**
- Todos los colores del CSS pasaron a variables (`:root` oscuro, `html.light` claro). Botón 🌙/☀️ en el header; preferencia en localStorage; script anti-parpadeo en `<head>`; colores de modo con variante `colorLight` legible en fondo claro.
- Breakpoints responsive: <380px compacta botones/burbujas; ≥768px ancho 720px; ≥1100px ancho 960px y modo Batería en grid de 2 columnas (panel controlado ahora por clase `.active`, no por `style.display`).
- `PROCEDIMIENTO.md`: procedimiento para añadir documentación (índice BM25, documentos puntuales por chat, `fuentes.json` / `ifas_device_library.json`).
- `build_index.py`: regenera `ifas_index.json` desde `PDFS Onyx\CATEGORÍA\*.pdf` (formato idéntico al índice en producción; requiere `pip install pymupdf`).
- `check_index.py`: verifica si un documento ya está cargado (local o `--web` contra el índice publicado), con búsqueda tolerante a guiones.
**Verificación:** sintaxis JS validada con Node, IDs del DOM auditados, llaves CSS balanceadas, system prompt y motor de Batería intactos; `build_index.py` y `check_index.py` probados con PDF/índice de prueba.

## Fechas anteriores (por confirmar) — hitos previos a este control
> Entradas reconstruidas de memoria; completar fechas si se necesita precisión.

- **Modo 📐 Diseño** — consultas de cobertura/espaciamiento con Regla 7 anti-alucinación (espaciamiento solo de ficha UL / NFPA 72 general).
- **RAG BM25 client-side** — `ifas_index.json` (un fragmento por página), tokenizer que normaliza acentos y conserva modelos con guion, bonus por coincidencia con el nombre del documento (×2.5), TOP_K = 8. Sustituyó la inyección de manuales por Files API (límite de 1M tokens) y a los embeddings semánticos (fricción de Voyage AI).
- **Modo 🔋 Batería** — cálculo determinístico NFPA 72 (la IA solo explica, nunca calcula): specs verificadas HPFF8/HPFF12/NFS-320/NFS2-640/NFS2-3030, configs externalizadas a `fuentes.json`, librería de aparatos en `ifas_device_library.json`, validaciones de NAC/cargador/gabinete, memoria de cálculo imprimible (`window.print`). Regresión validada: HPFF8 2.18 AH → BAT-1270 ✓.
- **Fix NAC multi-fila** — cada selección de aparato crea su propia fila, permitiendo repartir el mismo modelo entre distintos NAC (resuelve el bug de estado indexado por modelo).
- **Lanzamiento IFAS** — single-file `index.html` en GitHub Pages, 5 modos iniciales + system prompt de 6 reglas, API key en localStorage, dictado por voz, análisis de imagen/PDF.

---

## Flujo de despliegue (referencia)

1. Editar/pegar en GitHub → repo `onyx_help` → archivo → lápiz → Commit changes.
2. Esperar 1–2 minutos (publicación de GitHub Pages).
3. `Ctrl+Shift+R` en la app para forzar recarga del caché.
4. Registrar la entrada en este documento.
