# HOJA DE RUTA DE DESARROLLO (ROADMAP)

El desarrollo de **DesignLab** se estructura en fases rigurosas y secuenciales para garantizar calidad técnica, estabilidad y verificación exhaustiva antes de pasar a la siguiente etapa.

---

## Fases del Proyecto

### Fase 0 — Investigación y Cimientos (Fase Actual)
- **Objetivo:** Inspeccionar el entorno de trabajo, investigar compatibilidades y dependencias, documentar la arquitectura, diseñar los contratos e interfaces del núcleo, y construir una base ejecutable completa con FastAPI, SQLite WAL, cola de trabajos persistente, persistencia de proyectos y experimentos, módulo de prueba y recuperación ante caídas.
- **Entregables:**
  - Toda la documentación técnica (`DESIGNLAB_SPEC.md`, `AGENTS.md`, `docs/*`).
  - Backend funcional FastAPI con SQLite WAL.
  - Cola persistente de jobs con estados y crash recovery.
  - Registro de módulos de ingeniería (`ModuleRegistry`).
  - Módulo de prueba de referencia (`TestEngineeringModule`).
  - Frontend inicial con Vite + React + TypeScript conectado al backend.
  - Pruebas automatizadas de la Fase 0 (`pytest`).

---

### Fase 1 — Cimientos de Geometría
- **Objetivo:** Implementar la abstracción unificada de geometría: CAD paramétrico B-Rep (build123d / OpenCascade) y mallas (Trimesh / Manifold3D).
- **Entregables:**
  - Generación, validación de estanqueidad/manifoldness y cálculo de masa/volumen.
  - Exportación a STEP sólido nativo y STL/GLB.
  - Visor 3D interactivo en frontend (Three.js / React Three Fiber).

---

### Fase 2 — Experimentos y Optimización
- **Objetivo:** Orquestación formal de experimentos, espacio paramétrico y motor de optimización multi-objetivo evolutivo.
- **Entregables:**
  - Integración de `pymoo` para cálculo de frentes de Pareto (NSGA-II).
  - Poblaciones iniciales mediante muestreo acotado (LHS).
  - Visualización interactiva del frente de Pareto y ranking de candidatos.

---

### Fase 3 — Framework de Simulación Híbrida
- **Objetivo:** Sistema de adaptadores de simulación desacoplados y transparentes.
- **Entregables:**
  - Clasificación estricta de fidelidad (Nivel 1, Nivel 2, Nivel 3).
  - Adaptador Nivel 1 analítico de alta velocidad.
  - Adaptador Nivel 2 OpenFOAM desacoplado y mock para entornos sin WSL2.
  - Métricas de convergencia y telemetría de solvers.

---

### Fase 4 — Bucle de Optimización Autónoma y Asistencia IA
- **Objetivo:** Bucle cerrado de evolución sin supervisión humana obligatoria y asistente IA estructurado.
- **Entregables:**
  - Bucle autónomo generacional con checkpoints y control de saturación.
  - Conector IA con proveedores configurables (Ollama / OpenAI-compatible).
  - Validación de esquemas Pydantic para propuestas de diseño sin ejecución de código arbitrario.

---

### Fase 5 — Módulo de Ingeniería Eólica
- **Objetivo:** Implementación completa del primer módulo real de demostración.
- **Entregables:**
  - Familia Savonius (eje vertical, arrastre).
  - Familia Darrieus / Helicoidal (eje vertical, sustentación).
  - Familia HAWT (eje horizontal multipalas).
  - Modelos aerodinámicos dedicados (BEM / DMST - Double Multiple Streamtube).
  - Comparativa de familias y exploración de frentes de Pareto de potencia vs masa vs par de arranque.

---

### Fase 6 — Editor de Ingeniería y Exportación Avanzada
- **Objetivo:** Panel de inspección y modificación de candidatos con control de versiones.
- **Entregables:**
  - Editor de parámetros con previsualización en vivo sin sobrescribir el historial original.
  - Generación de informes técnicos de experimentos (PDF/Markdown).
  - Exportación de paquetes de fabricación (STEP, STL, planos 2D DXF).
