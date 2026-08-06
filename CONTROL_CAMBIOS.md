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

## Estado actual (2026-07-30)

| Componente | Estado |
|---|---|
| Modos | Troubleshooting, Reemplazo HW, Examen, Diccionario, Guía Rápida, Diseño, Batería |
| Modelo API | `claude-sonnet-4-6` (seleccionable: Haiku 4.5, Sonnet 3.5, Haiku 3) |
| Documentación | Índice BM25 `ifas_index.json` — 8,463 fragmentos, 23 categorías (~12 MB) |
| Datos externos | `fuentes.json` (fuentes/baterías), `ifas_device_library.json` (aparatos) |
| Tema | Claro/oscuro con botón 🌙/☀️, persistente (localStorage `ifas_theme`) |
| Responsive | Breakpoints 380 / 768 / 1100 px; Batería en 2 columnas en escritorio |
| Scripts de soporte | `build_index.py`, `check_index.py` (ver `PROCEDIMIENTO.md`) |

**Pendientes / hoja de ruta**

- Expansión de marcas: Hochiki, Siemens, Simplex (una a la vez, misma metodología ONYX: base de manuales + reglas de system prompt).
- IBAS (bombeo de agua): crear repo `ibas_help`, CNAME `ibas.iselec.com.pa`, desplegar v4.

---

# Historial

##  2026-08-06 - Actualización y limpieza de indice
**Archivo;** `ifas_index` (actualizo)
**Cambios;**
"Limpieza de duplicados + 5 docs nuevos (3 con OCR): 8,463 → 8,085 fragmentos, 198 → 193 docs".

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
