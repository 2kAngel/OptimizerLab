# MATRIZ DE DECISIÓN DE DEPENDENCIAS Y TECNOLOGÍAS

Este documento define formalmente la selección de dependencias para **DesignLab**, justificando cada elección en función de la arquitectura modular, las licencias y la máquina de destino (Windows, i5-9300H, 8 GB RAM, sin GPU obligatoria).

---

## 1. Tabla Resumen de Decisiones

| Tecnología | Categoría | Estado | Licencia | Justificación | Alternativa Considerada |
|---|---|---|---|---|---|
| **Python (3.11 - 3.13)** | Backend Runtime | **Seleccionada (Core)** | PSF | Ecosistema líder en computación científica, CAD y simulación. | Rust / C++ (mayor coste de desarrollo) |
| **FastAPI** | Backend Framework | **Seleccionada (Core)** | MIT | Rendimiento asíncrono, OpenAPI nativo y tipado estricto con Pydantic v2. | Flask, Django (más pesados o síncronos) |
| **Pydantic v2** | Validación y Schemas | **Seleccionada (Core)** | MIT | Rendimiento extremo en C/Rust core, contratos tipados y serialización JSON. | Marshmallow, dataclasses puras |
| **SQLAlchemy 2.0** | ORM / Persistencia | **Seleccionada (Core)** | MIT | Estándar de la industria, soporte síncrono y asíncrono, gestión de transacciones robusta. | Tortoise-ORM, SQLModel |
| **SQLite (WAL mode)** | Base de Datos | **Seleccionada (Core)** | Public Domain | Cero configuración, sin servicios externos, altamente confiable con WAL para lecturas concurrentes. | PostgreSQL (exceso de sobrecarga para app local) |
| **React 19 + TypeScript + Vite** | Frontend Framework | **Seleccionada (Core)** | MIT | Desarrollo rápido, tipado estricto, bundle ligero y reactividad óptima. | Next.js (innecesario para SPA local de ingeniería) |
| **Three.js / React Three Fiber** | Visualización 3D | **Seleccionada (Core)** | MIT | Renderizado WebGL acelerado por hardware para mallas y B-Rep teselado. | Babylon.js, VTK.js |
| **build123d** | CAD Paramétrico (B-Rep) | **Seleccionada (Primario CAD)** | Apache 2.0 | Excelente ergonomía en Python para sólidos exactos, operaciones booleanas y exportación STEP. | CadQuery (más verboso), FreeCAD puro |
| **Trimesh** | Geometría de Malla | **Seleccionada (Core Mesh)** | MIT | Manipulación de mallas, manifoldness, cálculo de volumen/masa y exportación STL/OBJ/GLB. | Open3D (más pesado de instalar en Windows) |
| **pymoo** | Optimización Multi-objetivo | **Seleccionada (Core Opt)** | Apache 2.0 | Líder en algoritmos evolutivos (NSGA-II, NSGA-III), frentes de Pareto y restricciones. | DEAP (menos enfocado a Pareto), Platypus |
| **Optuna** | Optimización Bayesiana | **Opcional / Futuro** | MIT | Excelente para optimización bayesiana mono-objetivo; secundario para fases avanzadas. | Hyperopt, Scikit-Optimize |
| **OpenFOAM** | CFD Nivel 2 | **Opcional (Adaptador)** | GPLv3 | Simulación de fluidos de alta fidelidad. Aislado como subproceso externo (WSL2/Docker). | SU2, Ansys Fluent (comercial) |
| **Gmsh** | Mallador Nivel 2 | **Opcional (Adaptador)** | GPLv2+ | Mallado 3D estructurado y no estructurado. | Salome, snappyHexMesh nativo |
| **Ollama / OpenAI API** | Asistente IA | **Opcional (Adaptador)** | MIT / Comercial | Análisis de datos y sugerencias paramétricas estructuradas sin comprometer la ejecución física. | Transformers locales (requeriría GPU dedicada) |

---

## 2. Clasificación por Nivel de Integración

### A. Dependencias Obligatorias del Núcleo (Core Run-Time)
- No requieren configuraciones externas complejas ni privilegios de administrador.
- Se instalan en el entorno virtual Python y en el proyecto Node.js estándar.
- Permiten crear proyectos, definir experimentos, generar candidatos, ejecutar evaluaciones analíticas Nivel 1, calcular frentes de Pareto, visualizar modelos 3D y exportar geometrías.

### B. Integraciones Opcionales de Alta Fidelidad (Level 2 Pluggable Adapters)
- Diseñadas bajo el patrón **Adapter**.
- Si el ejecutable de OpenFOAM o Gmsh no se detecta en el sistema, la plataforma no falla:
  - Marca la capacidad como "No disponible localmente".
  - Proporciona un adaptador emulador (mock con advertencia explícita) para pruebas y validación del pipeline.
  - Ofrece instrucciones claras de configuración de WSL2 o Docker para activarlo cuando el usuario lo desee.

### C. Integraciones de Inteligencia Artificial
- La plataforma es 100% operativa sin ningún LLM conectado.
- Cuando se habilita un proveedor (Ollama local o API OpenAI-compatible), el motor de IA actúa como un agente de consulta sobre el historial de la base de datos y formula propuestas paramétricas dentro de los límites del módulo.
