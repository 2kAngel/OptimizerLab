# AGENTS.md — GUÍA DE DESARROLLO Y PROTOCOLOS PARA AGENTES EN DESIGNLAB

Este documento establece las reglas obligatorias de arquitectura, codificación, límites de recursos y protocolos de verificación para cualquier agente o desarrollador que trabaje en **DesignLab**.

---

## 1. Entorno de Ejecución y Restricciones de Hardware

El entorno de destino es un equipo estándar Windows con especificaciones modestas:
- **CPU:** Intel Core i5-9300H (4C/8T @ 2.40 GHz - 4.10 GHz).
- **RAM:** ~8 GB DDR4.
- **GPU:** Intel UHD Graphics 630 (integrada, memoria compartida).
- **SO:** Windows 10/11 x64, PowerShell.
- **Almacenamiento:** Amplio (~600+ GB libres en disco de trabajo).

### Implicaciones Críticas para el Código:
1. **Sin requerimientos obligatorios de CUDA/GPU:** Todas las operaciones esenciales deben funcionar en CPU de forma eficiente y vectorizada cuando sea posible.
2. **Control Estricto de Memoria:**
   - Limitar el número de procesos/workers en paralelo por defecto a `max_workers = 2`.
   - Limitar el tamaño de las poblaciones en optimizaciones (e.g., 20-50 individuos por generación en pruebas; configurable por experimento).
   - Liberar geometrías intermedias y usar generadores/iteradores en lugar de cargar colecciones masivas de mallas en RAM.
3. **Persistencia fuera de la BD de archivos pesados:** Los archivos STEP, STL, mallas densas o historiales CFD jamás se guardan como blobs en SQLite. Se almacenan en el sistema de archivos (`storage/`) con ruta relativa, hash SHA-256 y metadatos en la base de datos.
4. **Desacoplamiento de Servicios Externos:** No asumir que Docker, WSL2, OpenFOAM, Gmsh u Ollama están corriendo. El sistema debe iniciar limpiamente y ofrecer degradación elegante (graceful degradation) con mocks o evaluadores analíticos cuando un solver externo no esté disponible.

---

## 2. Principios de Arquitectura y Reglas de Codificación

### 2.1 Backend (Python 3.13+)
- **Tipado estricto:** Uso extensivo de type hints (`typing` / Python 3.10+ union types `X | Y`).
- **Validación con Pydantic:** Todas las entidades del dominio, esquemas de API, parámetros de módulos y propuestas de IA deben definirse con modelos Pydantic v2.
- **Base de Datos:** SQLAlchemy 2.0 con SQLite en modo WAL (`journal_mode=WAL`) y `PRAGMA busy_timeout=5000` para soportar accesos concurrentes de workers y API.
- **Cola de Tareas en Base de Datos:** Los jobs de simulación y evaluación se gestionan mediante una tabla de cola persistente (`jobs`), con soporte para estados `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED` y recuperación automática de jobs huérfanos al reiniciar el backend.

### 2.2 Frontend (React 19, TypeScript, Vite)
- TypeScript con modo estricto (`strict: true`).
- Modularidad por características (`viewer3d`, `experiments`, `optimization`, `simulations`, `dashboard`).
- Visualización 3D mediante Three.js / React Three Fiber, con carga asíncrona de geometrías (formato GLB/STL o buffers de polígonos compactos) sin bloquear el hilo principal de la UI.
- Comunicación con el backend a través de un cliente API tipado basado en OpenAPI/FastAPI.

### 2.3 Módulos de Ingeniería (`modules/`)
- El núcleo (`backend/core/`) es completamente agnóstico al dominio.
- Ningún archivo de `backend/core/` o `backend/api/` debe importar lógica específica de turbinas eólicas.
- Toda la lógica de un dominio de ingeniería se implementa a través del contrato abstracto `EngineeringModule`.

### 2.4 Seguridad e Integridad
- **Cero Ejecución de Código Arbitrario:** Las propuestas generadas por LLMs son objetos de datos JSON estructurados que se validan contra los esquemas Pydantic del módulo correspondiente. Jamás se ejecutará `eval()`, `exec()` ni código Python libre recibido de un modelo de lenguaje.
- **Validación de Rutas:** Proteger contra Path Traversal sanitizando cualquier identificador o ruta antes de acceder al sistema de archivos en `storage/`.
- **Reproducibilidad:** Cada candidato debe registrar sus parámetros exactos, semilla aleatoria (seed), versión del generador, hash de geometría y nivel de fidelidad de la evaluación.

---

## 3. Protocolo de Pruebas y Aceptación

1. **Pruebas Automatizadas Obligatorias:** Cada módulo y servicio debe acompañarse de pruebas unitarias (`pytest`).
2. **Pruebas Ligeras y Deterministas:** Las pruebas del flujo principal no deben depender de red externa ni de solvers pesados.
3. **Verificación de Recuperación:** Debe probarse siempre la recuperación tras caída: simular que el backend se interrumpe durante un experimento y verificar que los estados no se corrompen y que los jobs se reanudan o marcan como fallidos limpiamente.
4. **Veracidad de Resultados:** Jamás reportar que una simulación CFD o prueba de integración ha sido ejecutada con éxito si ha sido emulada o no se ha verificado formalmente.
