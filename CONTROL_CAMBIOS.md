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
| Versión | v2026.4 |
| Modos | Troubleshooting, Reemplazo HW, Examen, Diccionario, Guía Rápida, Diseño, Batería |
| Familias | ONYX (NFS-320, NFS2-640, NFS2-3030) e INSPIRE N16; selector en la barra 📚 (localStorage `ifas_familia`) |
| Modelo API | `claude-sonnet-4-6` (seleccionable: Haiku 4.5, Sonnet 3.5, Haiku 3) |
| Documentación | Índices BM25 por categoría en `idx/` (manifest 2026.1, 12 índices, 18.197 fragmentos, 215 documentos únicos: 197 PDF, 8 presentaciones y 10 procedimientos de video, de los que 8 tienen narración; 15 MB; gzip en Pages) |
| Búsqueda | BM25 + sinónimos bilingües + búsqueda agéntica (`buscar_documentacion`, máx. 3 por pregunta, todos los modos salvo Diccionario) |
| Datos externos | `fuentes.json` v2026.2 (14 fuentes, 5 verificadas), `ifas_device_library.json` (1.346 aparatos NAC), `examen.json` (91 preguntas, 9 temas) |
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

## 2026-11-05 — v2026.4: búsqueda forzada en modos de diagnóstico, reglas de examen externo, banco con Quiz Día 3
**Archivos:** `index.html`, `examen.json`
**Cambios:**
- Verificado en producción (DevTools, Network): `tools` viaja en cada request pero Sonnet responde `end_turn` sin pedir búsquedas. Se fuerza la primera búsqueda con `tool_choice: {type:'tool', name:'buscar_documentacion'}` en Troubleshooting, Reemplazo HW, Examen y Guía Rápida (`FORZAR_BUSQUEDA`); el modelo formula la consulta con los términos del manual y recibe esos fragmentos además de los iniciales. Diccionario y Diseño no cambian. Una llamada extra por pregunta en esos modos.
- Descripción de la herramienta reescrita para pedir términos técnicos del manual (nombre del trouble en inglés, conector, modelo, número de documento).
- System prompt, Examen con pregunta externa: citar antes de elegir y comprobar que la cita no diga lo contrario; en "todas las válidas" evaluar cada opción por separado; buscar el equipo nombrado en una opción antes de descartarlo; nunca "confirmado" sin cita.
- `examen.json` v2026.3: 91 preguntas; entran las 17 del Homework Quiz Día 3 con respuesta confirmada por Honeywell y documento/sección citados por el quiz; correcciones a nfs3030-12 (NCD como display primario, DN-7070) y campo-05 (Strobe FlashScan sin EOLR-1, 52544 4.2).
- Resultado de la prueba contra el Quiz Día 3 con v2026.3: 11/17 (65 %); análisis en `IFAS_2026\07_validacion\RESULTADO_QUIZ_DIA3.md`.
**Verificación:** sintaxis JS con node; `node test_motor.js` 30/30; bucle con `tool_choice` simulado con API falsa (llamada 1 con tool_choice, llamada 2 sin él, resultado de la búsqueda forzada = 52545 pág. 40 Supervision).

## 2026-11-05 — v2026.3.1: ajustes posteriores al despliegue
**Archivos:** `index.html`
**Cambios:**
- Examen: el pool por tema se acota a `EXAMEN_MAX` = 10 preguntas barajadas (antes servía el tema completo, ej. "1 de 16" en nfs3030).
- Sinónimos: eliminadas las expansiones de un carácter (`j`) en jumper, puente y conector, que `tokenize` descartaba; se añade `jp`. Los códigos J5/J6 siguen entrando por el término raro de la consulta.
- Sin cambios en `idx/`, `examen.json` ni `fuentes.json`.
**Verificación:** sintaxis JS con node; `node test_motor.js` 30/30.

## 2026-11-05 — v2026.3: sinónimos bilingües, búsqueda agéntica, banco de examen, fuentes.json validado
**Archivos:** `index.html`, `fuentes.json`, `examen.json` (nuevo), `add_to_index.py` (v3), `PROCEDIMIENTO.md` (v3), `test_motor.js` (nuevo), `contextualizar_indice.py` (nuevo), `CONTROL_CAMBIOS.md`
**Cambios:**
- Modo Examen con banco `examen.json`: 79 preguntas en el estilo del quiz Honeywell (22 capturas del Homework Quiz de Notifier ONYX University como referencia de jerga) (enunciado "En un FACP*…", opción única, múltiple y V/F), 9 temas, cada una con referencia doc + pág. verificada contra `idx/`; la app elige el tema por texto, baraja, inyecta cada pregunta y su respuesta correcta en el mensaje y el modelo presenta, evalúa y lleva el puntaje. Páginas de índice (líneas de puntos) demotadas ×0.3 en el ranking.
- Tabla `SINONIMOS` (≈80 entradas, español de campo → inglés de manuales) aplicada en `expandQuery` con peso 0.4; términos raros con dígitos (J5, TB4, H2) multiplican la puntuación; documento nombrado en la consulta ×3; bonus de nombre acotado; "h.2" se tokeniza como h2; cada fragmento lleva "pág. N de ~M"; TOP_K 10.
- Búsqueda agéntica: herramienta `buscar_documentacion` vía tool use, hasta `MAX_BUSQUEDAS` = 3 por pregunta, atendida por el motor local; bucle en `send()`; activa en todos los modos salvo Diccionario; pie de fuentes acumulado y sin duplicados.
- `fuentes.json` v2026.2: valores de las 9 fuentes nuevas contrastados literalmente con `01_texto` (51 literales); discrepancia 0.25/0.35 A resuelta (tarjeta sola vs tarjeta + KDM-R2); falso positivo num_NAC de PSE corregido; notas con documento, página y dato pendiente por fuente.
- `add_to_index.py` v3 escribe en `idx/idx_<categoria>.json` y actualiza `manifest.json`; `PROCEDIMIENTO.md` reescrito para el flujo por categorías.
**Verificación:** sintaxis JS con node; motor probado en node contra los índices reales (J5 → 52546SP p.33 / 52545SP p.40 y 157 recuperados); bucle de tool use simulado con API falsa (3 llamadas, historial user/assistant/user correcto); `add_to_index.py` probado con PDF sintético sobre copia de `idx/`; `fuentes.json` y todos los `idx_*.json` validados como JSON.

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
**Archivos:** `index.html`, `fuentes.json`, `idx/` (nuevo, 13 archivos), `ifas_index.json` (eliminado)
**Cambios:**
- Corpus Notifier University 2026 (197 PDF deduplicados, 8 presentaciones y 10 videos: 8 transcritos y 2 sin narración; 215 documentos en el índice) convertido a 12 índices por categoría con `manifest.json` (18.197 fragmentos, 15 MB). Pipeline documentado en `INSTRUCCIONES_CHATGPT_IFAS_2026.md`.
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
