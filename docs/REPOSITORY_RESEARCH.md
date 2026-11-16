# INVESTIGACIÓN DE REPOSITORIOS Y REFERENCIAS DE INGENIERÍA

Este documento analiza los repositorios, librerías y proyectos de referencia especificados para **DesignLab**, evaluando su estado de mantenimiento, licencias, arquitectura y modo de integración.

---

## 1. build123d (`gumyr/build123d`)

- **Repositorio Oficial:** https://github.com/gumyr/build123d
- **Propósito:** Modelador CAD paramétrico de última generación basado en Python y OpenCascade (vía OCP / CadQuery OpenCascade Custom Pybind11).
- **Licencia:** Apache License 2.0.
- **Estado de Mantenimiento:** Activo, moderno, reemplazo superior a CadQuery tradicional por su sintaxis concisa orientada a objetos (álgebra de constructores, `BuildPart`, `BuildSketch`, `BuildLine`).
- **Capacidades Clave:**
  - Creación de B-Rep sólido de alta precisión.
  - Operaciones booleanas exactas (unión, diferencia, intersección).
  - Filetes, chaflanes, barridos (sweeps), transiciones (lofts), extrusiones y revoluciones.
  - Exportación nativa a STEP (sólidos paramétricos), BREP, DXF, SVG y teselación a STL/3MF.
- **Compatibilidad y Dependencias:**
  - Requiere OCP (OpenCASCADE PyPI wheels).
  - En Windows x64 funciona de forma óptima en Python 3.10-3.12 (en 3.13 OCP está finalizando soporte para wheels precompilados).
- **Impacto en Recursos:**
  - Muy eficiente en memoria para piezas individuales (~50-150 MB RAM por sesión de modelado).
- **Decisión de Integración:**
  - **Motor CAD Primario para B-Rep.** Para garantizar funcionamiento robusto en cualquier versión de Python y en fases iniciales, se crea un adaptador modular `GeometryEngine` con backend `build123d` y un backend fallback ligero `numpy/trimesh/primitives` para geometrías analíticas.

---

## 2. LLM-Agent-generated-Quadcopter-Prop (`ostenjap/LLM-Agent-generated-Quadcopter-Prop`)

- **Repositorio Oficial:** https://github.com/ostenjap/LLM-Agent-generated-Quadcopter-Prop
- **Propósito:** Proyecto de investigación que demuestra la generación y optimización autónoma de hélices para cuadricópteros mediante agentes LLM y simulación aerodinámica.
- **Licencia:** MIT / Académica.
- **Lecciones Arquitectónicas Extraídas:**
  - **Representación Paramétrica Acotada:** Los agentes LLM no deben generar código de geometría descontrolado; en su lugar, deben operar sobre un espacio paramétrico bien definido (cuerda, ángulo de torsión/twist, radio de pala, perfil alar NACA/Clark-Y).
  - **Separación entre Generación y Validación Física:** No permitir que el agente declare el empuje o la eficiencia; la física se delega a evaluadores deterministas (BEM, CFD).
  - **Bucle de Retroalimentación:** El agente recibe el historial de experimentos previos, el coeficiente de empuje $C_T$, el coeficiente de potencia $C_P$ y la figura de mérito, permitiéndole formular hipótesis sobre qué cambios geométricos mejoran la eficiencia en puntos de operación específicos.
- **Decisión de Integración:**
  - **Referencia conceptual de arquitectura.** No se importa como dependencia directa de código, sino que se incorpora su filosofía en el diseño de `backend/core/ai/` y el módulo de turbinas eólicas.

---

## 3. OpenFOAM (`OpenFOAM/OpenFOAM-dev` / OpenCFD)

- **Repositorio Oficial:** https://github.com/OpenFOAM/OpenFOAM-dev (The OpenFOAM Foundation) y https://develop.openfoam.com (OpenCFD / ESI Group).
- **Propósito:** Suite de dinámica de fluidos computacional (CFD) de código abierto para simulación de flujos incompresibles, compresibles, multifásicos y con turbulencia.
- **Licencia:** GNU General Public License v3 (GPLv3).
- **Solvers de Interés para Aerodinámica de Turbinas:**
  - `simpleFoam`: Solver estacionario para flujo incompresible y turbulento (RANS con modelos $k$-$\omega$ SST, Spalart-Allmaras).
  - `pimpleFoam`: Solver transitorio para flujos inestables y rotores en movimiento (MRF - Multiple Reference Frame o AMI - Arbitrary Mesh Interface).
- **Retos y Consideraciones en Windows / Hardware Modesto:**
  - OpenFOAM no compila nativamente en MSVC sin capas complejas; típicamente requiere WSL2 o contenedor Docker Linux.
  - Consumo de RAM intensivo: mallas de más de 1-2 millones de celdas desbordarían la RAM de 8 GB.
- **Decisión de Integración:**
  - **Adaptador de Simulación Opcional Nivel 2.** Desacoplado mediante interfaz abstracta (`SimulationAdapter`). Se proporciona un mock ejecutable para pruebas sin dependencias externas, y un adaptador real que genera directorios de casos OpenFOAM (`0/`, `constant/`, `system/`) listos para ejecutarse en WSL2 o un worker remoto.

---

## 4. Gmsh

- **Repositorio Oficial:** https://gitlab.onelab.info/gmsh/gmsh (Official maintained GitLab).
- **Propósito:** Generador de mallas 3D tridimensionales de elementos finitos y volúmenes finitos con motor CAD incorporado y soporte para geometrías OpenCASCADE.
- **Licencia:** GNU General Public License v2+ (GPLv2+).
- **Capacidades:**
  - Mallado superficial no estructurado y volumétrico (tetraedros, prismas de capa límite).
  - API de Python oficial distribuida en PyPI (`gmsh`).
- **Decisión de Integración:**
  - **Adaptador Opcional para Nivel 2.** Complemento del pipeline de CFD para convertir geometrías STEP o STL en mallas compatibles con OpenFOAM.

---

## 5. pymoo (`anyoptimization/pymoo`)

- **Repositorio Oficial:** https://github.com/anyoptimization/pymoo
- **Propósito:** Framework líder en Python para optimización multi-objetivo, algoritmos genéticos y cálculo de frentes de Pareto.
- **Licencia:** Apache License 2.0.
- **Estado de Mantenimiento:** Muy activo, robusto, ampliamente probado en investigación y producción industrial.
- **Capacidades Clave:**
  - Algoritmos: NSGA-II, NSGA-III, MOEA/D, CoDE, GA mono-objetivo.
  - Manejo estricto de restricciones lineales, no lineales e hiper-cajas paramétricas.
  - Operadores de cruce (SBX) y mutación polinomial (PM).
  - Descomposición y cálculo de hipervolumen y frentes de Pareto óptimos.
- **Decisión de Integración:**
  - **Motor Principal de Optimización de DesignLab.** Se implementa un wrapper `EvolutionaryOptimizer` que mapea los candidatos de DesignLab a `Problem` de pymoo de manera transparente y desacoplada.

---

## 6. Anvil (`symbench/Anvil`)

- **Repositorio Oficial:** https://github.com/symbench/Anvil
- **Propósito:** Entorno de optimización de diseño asistido por CFD impulsado por DARPA Symbiotic Design of Cyber-Physical Systems.
- **Licencia:** Apache License 2.0 / MIT.
- **Lecciones:** Arquitectura de pipelines de simulación resilientes, parametrización orientada a componentes y orquestación de solvers.
- **Decisión de Integración:**
  - **Referencia de diseño para pipelines de simulación asíncrona.**

---

## 7. Optuna (`optuna/optuna`)

- **Repositorio Oficial:** https://github.com/optuna/optuna
- **Propósito:** Framework de optimización hiperparamétrica y optimización bayesiana (Tree-structured Parzen Estimator - TPE).
- **Licencia:** MIT License.
- **Decisión de Integración:**
  - **Evaluado como motor secundario para exploración bayesiana de parámetros continuos.** Para el bucle principal multi-objetivo (e.g. Maximizar Potencia vs Minimizar Masa vs Minimizar Velocidad de Arranque), `pymoo` es la herramienta preferente. Optuna se mantiene como alternativa futura para muestreo guiado por modelos subrogados.
