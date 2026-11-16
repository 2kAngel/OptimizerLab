# DESIGNLAB — ESPECIFICACIÓN MAESTRA DEL PROYECTO

Plataforma autónoma de descubrimiento e ingeniería generativa para diseño computacional, simulación híbrida, optimización evolutiva multi-objetivo y experimentación reproducible.

---

## 1. Rol y Visión

**DesignLab** no es una simple aplicación CAD, un visor 3D, una interfaz de CFD ni un chatbot con IA.

Es un laboratorio de ingeniería virtual autónomo capaz de:
1. Definir problemas de ingeniería formalmente (objetivos, restricciones, condiciones operativas, límites de cómputo).
2. Generar múltiples alternativas de diseño automáticamente.
3. Crear geometrías 3D válidas mediante parámetros y métodos generativos (B-Rep y mallas).
4. Evaluar diseños usando modelos analíticos y aproximaciones numéricas rápidas (Nivel 1).
5. Ejecutar simulaciones avanzadas de mayor fidelidad en candidatos prometedores (Nivel 2 - CFD/OpenFOAM, Gmsh).
6. Comparar resultados frente a múltiples objetivos de ingeniería (frentes de Pareto).
7. Optimizar y hacer evolucionar diseños a lo largo de generaciones sucesivas.
8. Aprender de experimentos previos (modelos subrogados y análisis asistido por IA).
9. Proponer variaciones de diseño de forma autónoma con salvaguardas estrictas.
10. Preservar reproducibilidad total permitiendo inspeccionar, modificar y exportar los mejores diseños (STEP, STL, GLB).

El primer módulo de demostración es un **laboratorio experimental de turbinas eólicas**, pero la plataforma está desacoplada y construida como un núcleo genérico para soportar cualquier disciplina de ingeniería futura (engranajes, intercambiadores de calor, perfiles alares, estructuras optimizadas).

---

## 2. Decisiones Fundamentales de Diseño

### 2.1 Autonomía
- Flujo cerrado de optimización sin necesidad de aprobación humana paso a paso:
  1. Generar población inicial diversa (LHS / muestreo acotado).
  2. Validar geometría (solidez, estanqueidad, límites).
  3. Evaluación rápida Nivel 1 (filtrado y descartes con motivos registrados).
  4. Selección de finalistas según Pareto, diversidad e incertidumbre.
  5. Simulación avanzada Nivel 2 (opcional y con límites de recursos).
  6. Operadores evolutivos (cruce, mutación, perturbación paramétrica).
  7. Persistencia estricta de todo el historial.
- Intervención manual opcional pero nunca bloqueante para la autonomía del bucle.

### 2.2 Estrategia de Simulación Híbrida
- **Nivel 1 (Evaluación Rápida):** Fórmulas analíticas, BEM (Blade Element Momentum) u otras aproximaciones de bajo coste computacional para cribar grandes poblaciones.
- **Nivel 2 (Simulación Avanzada):** CFD desacoplado mediante OpenFOAM y mallado con Gmsh (ejecución opcional/asíncrona).
- **Nivel 3 (Capacidades Futuras):** FEA, análisis térmico, modelos subrogados entrenados (surrogates con incertidumbre).
- **Transparencia radical:** Jamás presentar un resultado aproximado como simulación de alta fidelidad. Cada métrica registra método, versión de solver, estado de convergencia y nivel de fidelidad.

### 2.3 Sistema de Geometría Dual
- **CAD Paramétrico B-Rep:** Dimensiones, operaciones booleanas, extrusiones, barridos, exportación STEP nativa sólida (motor principal: build123d / OpenCascade).
- **Geometría Libre / Malla:** Mallas orgánicas, deformaciones procedurales, manifoldness, exportación STL/GLB (Trimesh / Manifold3D).
- No tratar todo como malla de triángulos; preservar la distinción sólida B-Rep.

---

## 3. Restricciones de Hardware y Entorno

- **Plataforma:** Windows 10/11 x64.
- **CPU:** Intel Core i5-9300H (4 núcleos / 8 hilos).
- **Memoria:** ~8 GB RAM.
- **Gráficos:** Intel UHD 630 integrada (sin GPU dedicada obligatoria).
- **Sin CUDA obligatorio:** Todo el flujo central de generación, evaluación Nivel 1 y optimización debe correr en CPU de manera fluida.
- **Límites de concurrencia:** Máximo 1 a 2 workers pesados concurrentes para no saturar memoria.
- **Desacoplamiento de herramientas pesadas:** OpenFOAM, Gmsh y Ollama son adaptadores opcionales; la aplicación debe iniciar, funcionar, evaluar y optimizar sin requerirlos instalados en el host.

---

## 4. Stack Tecnológico

- **Backend:** Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async/sync), SQLite en modo WAL con cola de tareas persistente en base de datos.
- **Frontend:** React 19, TypeScript, Vite, TailwindCSS / UI modular, Three.js / React Three Fiber para visualización 3D y gráficos interactivos (frentes de Pareto, convergencia).
- **Geometría:** Abstracción unificada; build123d para CAD paramétrico B-Rep, Trimesh para análisis y manipulación de mallas.
- **Optimización:** pymoo para algoritmos genéticos y multi-objetivo (NSGA-II, NSGA-III), con fallback y operadores personalizados.
- **IA:** Adaptador desacoplado para LLMs (OpenAI-compatible / Ollama) restringido a generación de propuestas estructuradas y análisis de patrones, sin ejecución arbitraria de código.

---

## 5. Módulo Inicial: Turbinas Eólicas Experimentales

- Exploración de múltiples familias aerodinámicas sin asumir 3 palas horizontales por defecto:
  - Savonius (eje vertical, arrastre, autoarranque).
  - Darrieus (eje vertical, sustentación, alta velocidad de punta).
  - Helicoidales / Gorlov (par de torsión uniforme, reducción de vibraciones).
  - Eje horizontal HAWT convencional y multipala.
  - Conceptos con difusor / ducto (DAWT).
- Física rigurosa: no aplicar la misma fórmula simplificada ni el límite de Betz indiscriminadamente a turbinas de eje vertical.
