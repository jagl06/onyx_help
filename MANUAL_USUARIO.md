# IFAS — Manual de Usuario

**IFAS (ISELEC Fire Alarm Support)** es el asistente técnico de ISELEC para paneles Notifier ONYX en campo. Funciona desde el navegador del celular o la PC: **https://ifas.iselec.com.pa**

## 1. Primer uso

1. Abre la app. Te pedirá la **API Key de Anthropic** (empieza con `sk-ant-`). Se guarda solo en tu teléfono; nunca se comparte.
2. Deja el modelo recomendado (**Sonnet 4.6**). Si más adelante sale error 404, prueba Haiku 3.
3. Toca **Comenzar →**. Para cambiar la key o el modelo después: botón **⚙️**.

## 2. La pantalla

- **Header:** `Nueva sesión` (limpia el chat), **🌙/☀️** cambia entre tema oscuro y claro (queda guardado), **⚙️** configuración.
- **Barra de modos:** elige qué tipo de ayuda necesitas (obligatorio antes de escribir).
- **Barra 📚 Documentación:** debe decir "X fragmentos listos" en verde — significa que IFAS consulta los manuales oficiales automáticamente y citará documento y página.
- **Entrada:** 📎 adjunta fotos o PDFs (varios a la vez), 🎤 dicta por voz, ↑ envía. También puedes pegar una captura directamente.

## 3. Modos

| Modo | Para qué | Qué dar |
|---|---|---|
| 🔧 Troubleshooting | Diagnosticar una falla | Modelo del panel, **qué cambió recientemente** y el **texto exacto** del error/trouble |
| 🔄 Reemplazo HW | Cambiar CPU, LCM, LEM, fuente… | Componente reemplazado + modelo del panel. Te guía con VeriFire paso a paso |
| 📋 Examen | Practicar/evaluarte | Tema o modelo (NFS-320, VeriFire…). Pregunta una a la vez y lleva puntaje |
| 📖 Diccionario | Definir un término | El término (SLC, NAC, Drift Compensation…) |
| ⚡ Guía Rápida | Valores y límites | Qué parámetro necesitas (corrientes, resistencias EOL, capacidades) |
| 📐 Diseño | Cobertura y espaciamiento | Modelo del detector, altura y tipo de techo, dimensiones del área |
| 🔋 Batería | Calcular baterías NFPA 72 | Ver sección 4 |

Consejos: entre más exacto el error (foto de la pantalla del panel ayuda mucho), mejor el diagnóstico. IFAS pide máximo 3 datos si le falta información — respóndelos en un solo mensaje.

## 4. Modo 🔋 Batería

1. **Fuente de poder:** elige el panel/fuente (✓ verificado = datos de fabricante).
2. **Aparatos de notificación:** busca por modelo o tipo (P2RL, strobe…), asigna NAC y cantidad con +/−. Puedes repetir el mismo modelo en varios NAC.
3. **Cargas auxiliares (TB4):** relés, anunciadores, etc., con corrientes del datasheet.
4. **Parámetros NFPA 72:** deja 24 h + 5 min y derating 1.2 salvo que el AHJ exija otra cosa.
5. **Datos del proyecto:** para el encabezado de la impresión.

Toca **Calcular batería**: el resultado muestra cargas, AH requerido, la batería seleccionada del catálogo y las validaciones (límites de NAC, cargador, gabinete). **🖨️ Imprimir / PDF** genera la memoria de cálculo formal con membrete ISELEC y líneas de firma. **🤖 Explicar** describe el cálculo en palabras (la IA no cambia números: el cálculo es determinístico).

## 5. Adjuntar documentos

- Cualquier ficha técnica en PDF o foto se adjunta con 📎 y la IA la analiza en esa conversación.
- Para que un manual quede **permanente** en el buscador 📚, se agrega al índice (eso lo hace el administrador — ver `PROCEDIMIENTO.md`).

## 6. Problemas comunes

| Síntoma | Solución |
|---|---|
| "API key inválida" | ⚙️ → vuelve a pegar la key completa (`sk-ant-...`) |
| Error 404 | ⚙️ → cambia el modelo (prueba Haiku 3) |
| 📚 "no disponible" | Recarga con `Ctrl+Shift+R` (en móvil: cerrar y reabrir pestaña); si persiste, avisar al administrador |
| La app no refleja una actualización | `Ctrl+Shift+R` — los cambios tardan 1–2 min en publicarse |
| "Error de conexión" | Verifica tu señal/datos e intenta de nuevo |
| El micrófono no aparece | Tu navegador no soporta dictado; escribe el mensaje |

## 7. Importante

Las respuestas citan manuales oficiales (documento y página) cuando usan la documentación. Aun así, **verifica siempre en campo contra el panel y el manual**, y recuerda que el diseño final lo valida el ingeniero responsable y el AHJ. Si IFAS dice que no tiene un dato, es a propósito: no inventa valores.
