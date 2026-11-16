# PLAN DE IMPLEMENTACIÓN DETALLADO — FASE 0

Este plan de trabajo detalla la ejecución precisa de la **Fase 0: Investigación y Cimientos Ejecutables**.

---

## 1. Tareas de la Fase 0

1. **Estructura del Proyecto:**
   - Crear directorios: `backend/`, `frontend/`, `modules/`, `integrations/`, `storage/`, `tests/`, `docs/`.
   - Configuración de Python: `pyproject.toml` con dependencias mínimas estrictas (FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0, aiosqlite/sqlite3, Pytest, HTTPX).
2. **Capa de Persistencia (SQLite en Modo WAL):**
   - Configurar engine SQLAlchemy con `journal_mode=WAL` y `busy_timeout=5000`.
   - Diseñar modelos ORM:
     - `Project`
     - `Experiment`
     - `Job` (Cola persistente de tareas con estados: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`)
     - `Candidate`
     - `EvaluationResult`
3. **Motor de Cola de Trabajos y Recuperación (Crash Recovery):**
   - Implementar `JobQueueWorker` que procesa tareas en segundo plano.
   - Implementar procedimiento de inicio `recover_orphaned_jobs()` que detecta trabajos que quedaron como `RUNNING` antes de un apagado o reinicio imprevisto y los reanuda o finaliza con diagnóstico seguro.
4. **Registro de Módulos del Núcleo:**
   - Implementar la clase base abstracta `EngineeringModule` y sus esquemas Pydantic (`backend/core/module_registry/`).
   - Crear el módulo de prueba de referencia (`TestEngineeringModule`) que simula la definición de un componente mecánico con parámetros, objetivos y evaluación rápida.
5. **API REST FastAPI:**
   - Endpoints:
     - `GET /api/health`
     - `GET /api/modules`
     - `POST /api/projects`
     - `GET /api/projects`
     - `POST /api/experiments`
     - `GET /api/experiments/{id}`
     - `POST /api/experiments/{id}/submit-job`
     - `GET /api/jobs/{id}`
     - `POST /api/jobs/recover`
6. **Frontend Inicial (Vite + React + TypeScript):**
   - Estructura limpia y compilable de interfaz de usuario con dashboard, lista de proyectos, experimentos, estado de workers y comprobación de salud del backend.
7. **Suite de Pruebas Automatizadas:**
   - Pruebas unitarias de la cola de jobs, persistencia, recuperación tras reinicio, registro de módulos y endpoints API con `pytest`.

---

## 2. Criterios de Aceptación de la Fase 0

- [x] Toda la documentación de investigación y arquitectura creada y validada.
- [ ] Backend FastAPI arranca y responde correctamente en `/api/health`.
- [ ] Se puede crear un proyecto y un experimento asociado.
- [ ] El módulo de prueba se registra y valida sus esquemas dinámicamente.
- [ ] Se encola un trabajo en segundo plano, se procesa de forma persistente y guarda su resultado en SQLite.
- [ ] Se verifica la recuperación tras caída: simular reinicio con jobs interrumpidos y constatar que el sistema se recupera de manera segura y sin datos corruptos.
- [ ] Frontend React/Vite arranca y se comunica con la API.
- [ ] Suite de pruebas de pytest pasa al 100%.
