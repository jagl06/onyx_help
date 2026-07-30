# IFAS — Manual Técnico (lo programado)

Para quien mantenga o modifique el código. App: https://ifas.iselec.com.pa · Repo: `jagl06/onyx_help`.

## 1. Arquitectura

- **Single-file:** todo (HTML + CSS + JS) vive en `index.html`. Sin frameworks, sin build, sin backend.
- **Hosting:** GitHub Pages con CNAME a `ifas.iselec.com.pa`. Los commits tardan 1–2 min en publicarse; forzar recarga con `Ctrl+Shift+R`.
- **API:** llamadas directas del navegador a `api.anthropic.com/v1/messages` con header `anthropic-dangerous-direct-browser-access`. La API key la ingresa el usuario y se guarda **solo** en su localStorage — nunca en el código.
- **Datos externalizados:** lo que cambia con frecuencia vive en JSON aparte para no tocar `index.html`.

## 2. Archivos del repo

| Archivo | Rol |
|---|---|
| `index.html` | Toda la aplicación |
| `ifas_index.json` | Corpus BM25: `{count, items:[{id,cat,doc,page,text}]}` — un fragmento por página de PDF |
| `fuentes.json` | Fuentes de poder y catálogo de baterías del modo 🔋 (`{fuentes:{...}, baterias:[...]}`) |
| `ifas_device_library.json` | Aparatos de notificación (`{dispositivos:[{pn,d,t,sb,al}]}`) |
| `build_index.py` / `check_index.py` | Regenerar / verificar el índice (ver `PROCEDIMIENTO.md`) |
| `PROCEDIMIENTO.md`, `CONTROL_CAMBIOS.md`, manuales | Documentación del proyecto |

## 3. localStorage

| Clave | Contenido |
|---|---|
| `ifas_api_key` | API key de Anthropic |
| `ifas_model` | Modelo activo (default `claude-sonnet-4-6`) |
| `ifas_theme` | `dark` / `light` |

## 4. Estructura de `index.html`

**CSS (en `<head>`):**
- `:root` define las variables del tema oscuro (default); `html.light` las sobreescribe para claro. Grupos: fondos (`--bg`, `--bg-solid`, `--bg-readout`), texto (`--text`, `--text-dim`, `--text-faint`, `--text-ghost`), superficies/bordes (`--surface-1/2`, `--border-1/2/3`), `--yellow`, `--shadow`. **Regla: ningún color nuevo hardcodeado; usar variables.** Los acentos de modo (rojo, naranja…) sí son fijos.
- Responsive: `@media (max-width:380px)` compacta; `(min-width:768px)` ancho 720px; `(min-width:1100px)` ancho 960px + Batería en grid 2 columnas (`#battery-panel.active{display:grid}`; el panel se muestra/oculta con la clase `.active`, **no** con `style.display`).
- `@media print`: hoja de memoria de cálculo (`#bp-print`), independiente del tema.
- Un `<script>` de una línea antes de `</head>` aplica la clase `light` antes del primer render (anti-parpadeo).

**JS (bloque principal):**
- `SYSTEM_PROMPT`: 7 reglas (triage, reemplazo HW, diagnóstico contextual, anti-alucinación, imágenes, formato, diseño) + referencia de hardware NOCM-1116 + definición de modos. Si se modifica, actualizar el bloque completo.
- `MODE_CONFIG`: por modo → `color` (tema oscuro), `colorLight` (tema claro), `bg` (tinte), `label`, `starter`. `modeColor(cfg)` elige el color según el tema; se usa en `selectMode`, `updateSendBtn` y `render`.
- **Tema:** `applyTheme(t)` alterna la clase en `<html>`, cambia el icono del botón `#theme-btn`, persiste y llama `refreshModeStyles()` para repintar botones/burbujas activos.
- **BM25** (`loadIndex`/`retrieve`): tokenizer minúsculas + sin acentos + filtra stopwords; k1=1.5, b=0.75; bonus ×2.5 si la consulta coincide con tokens del nombre del documento (clave para datasheets por modelo); `TOP_K=8` fragmentos se inyectan como primer bloque de texto del último mensaje de usuario (solo en la llamada, no se guardan en el historial). Las fuentes citadas se muestran bajo la respuesta (`src-note`).
- **`send()`:** arma el contenido (imágenes/PDF en base64 + texto con `[Modo activo: X]`), llama a la API con `system` + `cache_control: ephemeral`, `max_tokens: 1024`. Maneja 401 / errores / desconexión con mensajes en el chat.
- **Módulo `BAT`** (IIFE): motor determinístico del modo Batería. Carga `fuentes.json` y `ifas_device_library.json` bajo demanda. `calc()` aplica NFPA 72: `AH = (I_sb×t_sb + I_al×t_al) × derating`, suma corriente interna por NAC en uso (`perNacAdder`), selecciona la menor batería del catálogo que cubra el AH y respete el rango del cargador, y valida excesos de NAC/salida/standby y necesidad de gabinete. **La IA (`explain()`) solo explica el resultado; tiene prohibido recalcular.** `print()` genera la memoria de cálculo y llama `window.print()`.
- Cada fila de aparato en NAC es independiente (permite el mismo modelo en varios NAC); cantidad con +/- y circuito con selector.

## 5. Principios de desarrollo (no negociables)

1. **Anti-alucinación:** specs (espaciamientos, corrientes, AH) solo de datasheets UL / NFPA 72. Nada "típico" inventado, ni en el prompt ni en los JSON.
2. **Externalizar datos:** panel o dispositivo nuevo = editar JSON, no `index.html`.
3. **Verificar antes de desplegar:** sintaxis con `node --check`, IDs del DOM, y regresión del cálculo de batería contra valores conocidos (HPFF8: 2.18 AH → BAT-1270).
4. **Todo cambio se registra** en `CONTROL_CAMBIOS.md`.

## 6. Tareas comunes

| Tarea | Dónde |
|---|---|
| Añadir manual al buscador | `PROCEDIMIENTO.md` §A (`build_index.py` + commit del índice) |
| Verificar si un manual ya está | `python check_index.py <modelo> --web` |
| Añadir fuente de poder / batería | `fuentes.json` (marcar `verificado` solo con datasheet) |
| Añadir aparato de notificación | `ifas_device_library.json` |
| Cambiar modelo de IA por defecto | `index.html`: default de `ifas_model` + chips del setup |
| Nuevo modo de chat | `MODE_CONFIG` + botón en `#modes` + sección en `SYSTEM_PROMPT` |
| Ajustar colores/tema | Variables en `:root` / `html.light` |
