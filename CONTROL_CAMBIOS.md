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
| Versión | v2026.3 |
| Modos | Troubleshooting, Reemplazo HW, Examen, Diccionario, Guía Rápida, Diseño, Batería |
| Familias | ONYX (NFS-320, NFS2-640, NFS2-3030) e INSPIRE N16; selector en la barra 📚 (localStorage `ifas_familia`) |
| Modelo API | `claude-sonnet-4-6` (seleccionable: Haiku 4.5, Sonnet 3.5, Haiku 3) |
| Documentación | Índices BM25 por categoría en `idx/` (manifest 2026.1, 12 índices, 18.197 fragmentos, 212 documentos + 8 presentaciones + 8 videos transcritos, 15 MB; gzip en Pages) |
| Búsqueda | BM25 + sinónimos bilingües + búsqueda agéntica (`buscar_documentacion`, máx. 3 por pregunta, todos los modos salvo Diccionario) |
| Datos externos | `fuentes.json` v2026.2 (14 fuentes, 5 verificadas), `ifas_device_library.json` (1.346 aparatos NAC), `examen.json` (79 preguntas, 9 temas, todas verificadas contra idx/) |
| Tema | Claro/oscuro con botón 🌙/☀️, persistente (localStorage `ifas_theme`) |
| Responsive | Breakpoints 380 / 768 / 1100 px; Batería en 2 columnas en escritorio |
| Scripts de soporte | `add_to_index.py` v3 (escribe en `idx/`), `check_index.py`, `test_motor.js`, `contextualizar_indice.py` (ver `PROCEDIMIENTO.md`) |

**Pendientes / hoja de ruta**

- Completar las 9 fuentes nuevas de `fuentes.json` (qué falta a cada una: `IFAS_2026\07_validacion\VALIDACION_DATOS_2026.md`).
- Correr `contextualizar_indice.py` (recuperación contextual con Haiku) y republicar `idx/`.
- Procedimientos de los dos videos sin narración (firmware HS-NCM, diagrama de estación).
- Expansión de marcas: Hochiki, Siemens, Simplex (una a la vez, misma metodología).
- IBAS (bombeo de agua): crear repo `ibas_help`, CNAME `ibas.iselec.com.pa`, desplegar v4.

---

# Historial

## 2026-11-05 — v2026.3: sinónimos bilingües, búsqueda agéntica, banco de examen, fuentes.json validado
**Archivos:** `index.html`, `fuentes.json`, `examen.json` (nuevo), `add_to_index.py` (v3), `PROCEDIMIENTO.md` (v3), `test_motor.js` (nuevo), `contextualizar_indice.py` (nuevo), `CONTROL_CAMBIOS.md`
**Cambios:**
- Modo Examen con banco `examen.json`: 79 preguntas en el estilo del quiz Honeywell (22 capturas del Homework Quiz de Notifier ONYX University como referencia de jerga) (enunciado "En un FACP*…", opción única, múltiple y V/F), 9 temas, cada una con referencia doc + pág. verificada contra `idx/`; la app elige el tema por texto, baraja, inyecta cada pregunta y su respuesta correcta en el mensaje y el modelo presenta, evalúa y lleva el puntaje. Páginas de índice (líneas de puntos) demotadas ×0.3 en el ranking.
- Tabla `SINONIMOS` (≈80 entradas, español de campo → inglés de manuales) aplicada en `expandQuery` con peso 0.4; términos raros con dígitos (J5, TB4, H2) multiplican la puntuación; documento nombrado en la consulta ×3; bonus de nombre acotado; "h.2" se tokeniza como h2; cada fragmento lleva "pág. N de ~M"; TOP_K 10.
- Búsqueda agéntica: herramienta `buscar_documentacion` vía tool use, hasta `MAX_BUSQUEDAS` = 3 por pregunta, atendida por el motor local; bucle en `send()`; activa en todos los modos salvo Diccionario; pie de fuentes acumulado y sin duplicados.
- `fuentes.json` v2026.2: valores de las 9 fuentes nuevas contrastados literalmente con `01_texto` (51 literales); discrepancia 0.25/0.35 A resuelta (tarjeta sola vs tarjeta + KDM-R2); falso positivo num_NAC de PSE corregido; notas con documento, página y dato pendiente por fuente.
- `add_to_index.py` v3 escribe en `idx/idx_<categoria>.json` y actualiza `manifest.json`; `PROCEDIMIENTO.md` reescrito para el flujo por categorías.
**Verificación:** sintaxis JS con node; motor probado en node contra los índices reales (J5 → 52546SP p.33 / 52545SP p.40 y 157 recuperados); bucle de tool use simulado con API falsa (3 llamadas, historial user/assistant/user correcto); `add_to_index.py` probado con PDF sintético sobre copia de `idx/`; `fuentes.json` y todos los `idx_*.json` validados como JSON.

## 2026-11-04 — v2026.1: índices por categoría (Notifier University 2026) + INSPIRE N16
**Archivos:** `index.html`, `fuentes.json`, `idx/` (nuevo, 13 archivos), `ifas_index.json` (eliminado)
**Cambios:**
- Corpus Notifier University 2026 (212 PDF deduplicados, 8 presentaciones, 10 videos transcritos) convertido a 12 índices por categoría con `manifest.json` (18.197 fragmentos, 15 MB). Pipeline documentado en `INSTRUCCIONES_CHATGPT_IFAS_2026.md`.
- Loader nuevo: lee `idx/manifest.json`, carga los índices base según la familia (ONYX / INSPIRE N16 / Todas) y el otro índice de panel bajo demanda cuando la consulta menciona sus modelos (`CAT_TRIGGERS`, lista `modelos` del manifest).
- Ranking: penalización ×0.5 a la familia no seleccionada, preferencia ×1.1 por español, máximo 3 fragmentos por documento. Cada mensaje al modelo lleva `[Modo activo | Familia]`.
- System prompt: identidad ONYX + N16; tabla de diagnóstico ampliada (software mismatch, ground fault, nodo perdido, trouble AMPS-24); Regla 4 reforzada; Reglas 8 (firmware antes que hardware), 9 (recuperación de contraseña solo por Password Agreement), 10 (prueba de reaceptación NFPA 72 / 15378: 100 % afectados + 10 % no afectados, máx. 50) y 11 (N16: capacidades, exclusiones, conversión de base de datos VFT 12.45 → V27 → N16 V5.0, nunca VFT 11.xx).
- Modos: Examen con N16, zonas lógicas y NotiFireNet; Guía Rápida admite procedimientos; starters actualizados.
- `fuentes.json`: 9 fuentes nuevas (AMPS-24/24E, ACPS-610/610E, APS2-6R, FCPS-24S6/S8, PSE-6/10) con `verificado: false`.
**Verificación:** esquema de los 12 índices (0 fragmentos fuera de esquema); carga ONYX 16.287 fragmentos en 1.1 s en node; carga bajo demanda de paneles_n16 al consultar SLM-318; sintaxis JS con node.

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
