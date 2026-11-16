# ANÁLISIS DE LICENCIAS Y CUMPLIMIENTO LEGAL

Este documento establece las políticas de licencias para **DesignLab** y el análisis de compatibilidad de todas las dependencias evaluadas.

---

## 1. Licencia de DesignLab

El núcleo de **DesignLab** está concebido bajo una licencia permisiva de código abierto:
- **Licencia Recomendada:** **Apache License 2.0** o **MIT License**.
- Proporciona máxima libertad para uso en investigación, ingeniería y posibles desarrollos comerciales derivados, protegiendo las patentes de contribuyentes (en el caso de Apache 2.0).

---

## 2. Mapa de Licencias de Terceros

| Componente | Licencia | Tipo | Impacto en DesignLab |
|---|---|---|---|
| **FastAPI, Pydantic, SQLAlchemy** | MIT | Permisiva | Totalmente compatible. |
| **React, Vite, Three.js** | MIT | Permisiva | Totalmente compatible. |
| **build123d** | Apache 2.0 | Permisiva con patentes | Totalmente compatible. |
| **OCP (OpenCASCADE bindings)** | LGPL v2.1 | Copyleft débil en bibliotecas | Compatible mediante enlace dinámico/importación estándar sin exigir que el código de la aplicación sea LGPL. |
| **Trimesh** | MIT | Permisiva | Totalmente compatible. |
| **pymoo** | Apache 2.0 | Permisiva | Totalmente compatible. |
| **Optuna** | MIT | Permisiva | Totalmente compatible. |
| **Gmsh** | GPL v2+ | Copyleft fuerte | Se comunica a través de procesos aislados o módulo adaptador opcional. |
| **OpenFOAM** | GPL v3 | Copyleft fuerte | **IMPORTANTE:** OpenFOAM se ejecuta exclusivamente como un subproceso o contenedor externo mediante archivos de entrada/salida (`0/`, `constant/`, `system/`, logs). No se vincula estáticamente ni dinámicamente código C++ de OpenFOAM en el backend de DesignLab, preservando la independencia de licencias. |

---

## 3. Directrices de Aislamiento para Herramientas GPL

1. **Sin Vinculación de Código Fuente:** Ningún código fuente bajo GPL (como OpenFOAM) se incluirá en el árbol de código principal de DesignLab.
2. **Comunicación por IPC / Archivos de Caso:** La integración con OpenFOAM se realiza generando plantillas de casos (`case directories`), invocando ejecutables de línea de comandos (`blockMesh`, `snappyHexMesh`, `simpleFoam`) en un proceso independiente (host, WSL2 o contenedor) y parseando los ficheros de salida y logs.
3. **Mantenimiento de Atribuciones:** Todos los avisos de derechos de autor de las bibliotecas utilizadas se conservarán en los encabezados y en el archivo `THIRD_PARTY_LICENSES.md` generado en la distribución.
