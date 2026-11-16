# DesignLab — Autonomous Generative Engineering Platform

DesignLab es una plataforma de descubrimiento e ingeniería generativa autónoma diseñada para explorar, optimizar y validar diseños físicos complejos mediante modelos analíticos rápidos y simulaciones avanzadas.

## Requisitos del Sistema
- Python 3.11+
- Node.js 18+ (con npm)
- Diseñado para funcionar en CPU modesta (ej. Intel Core i5, 8 GB RAM, gráficos integrados) sin requerir GPU dedicada ni CUDA.

## Estructura del Proyecto
- `backend/`: API FastAPI, motor de experimentos, optimización evolutiva, persistencia en SQLite WAL y cola de jobs.
- `frontend/`: Interfaz de usuario en React 19, TypeScript, Vite y Three.js.
- `modules/`: Módulos de ingeniería física conectables (desacoplados del núcleo).
- `storage/`: Almacén de artefactos pesados (STEP, STL, GLB, logs de simulación) indexados por hash.
- `docs/`: Documentación técnica de arquitectura, dependencias y guías de desarrollo.

## Ejecución Rápida
Consulte `docs/ROADMAP.md` y `docs/IMPLEMENTATION_PLAN.md` para detalles de las fases de desarrollo.
