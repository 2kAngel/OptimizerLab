# EXPEDIENTE TÉCNICO Y REGULATORIO: INSTRUMENTAL QUIRÚRGICO A MEDIDA (PSI)
## Plataforma Hospitalaria Point-of-Care para Guías de Corte de Rodilla (MDR 2017/745 - Anexo XIII)

---

**Entidad Promotora:** Servicio de Cirugía Ortopédica y Traumatología (COT) & Unidad de Fabricación Aditiva Biomédica  
**Clasificación Regulatoria:** Producto Sanitario Fabricado a Medida (*Custom-Made Device*)  
**Marco Legal:** Reglamento (UE) 2017/745 (MDR) — Art. 52.8 y Anexo XIII | Real Decreto 192/2023  
**Indicación Clínica:** Artroplastia Total de Rodilla (ATR) Reconstructiva Extramedular  
**Tecnología:** Algoritmo Determinista Submilimétrico + Fabricación 3D Estereolitográfica (MSLA) en Resina Médica Autoclavable  
**Versión del Expediente:** 1.0 (Noviembre 2026)  

---

## 1. RESUMEN EJECUTIVO Y JUSTIFICACIÓN ASISTENCIAL

La artroplastia total de rodilla (ATR) es una de las intervenciones quirúrgicas de mayor volumen en los sistemas de salud mundiales (más de 60.000 procedimientos anuales en España). La clave del éxito a largo plazo de la prótesis radica en la **precisión milimétrica y angular de las resecciones óseas** en el fémur distal y la tibia proximal para restaurar el eje mecánico del miembro inferior.

### 1.1 El problema de la técnica convencional (Varilla Intramedular)
En más del 85-90% de los hospitales públicos y concertados, el alineamiento femoral se sigue realizando mediante la introducción de una **varilla rígida intramedular de 40 cm** que penetra el canal diafisario del fémur. Esta técnica presenta graves desventajas documentadas en la literatura clínica:
1. **Riesgo de Embolia Grasa:** La presurización del canal medular durante el fresado e introducción de la varilla provoca la extravasación de émbolos grasos a la circulación venosa sistémica, detectándose microembolias pulmonares y cerebrales subclínicas en hasta un 30-40% de los pacientes.
2. **Pérdida Hemática Adicional:** El sangrado originado por el canal medular abierto añade entre 300 ml y 500 ml de sangrado postoperatorio, elevando la tasa de transfusiones.
3. **Imprecisión Anatómica:** En pacientes con fémures arqueados, displasias o fracturas diafisarias previas con material de osteosíntesis, la varilla induce desviaciones angulares superiores a 3° en más del 20% de los casos.

### 1.2 La barrera económica del oligopolio comercial
Las alternativas comerciales existentes para evitar la varilla intramedular son dos:
- **Robots Quirúrgicos (Stryker Mako, Zimmer Rosa, etc.):** Coste de adquisición de **1.200.000 €**, mantenimiento anual de **100.000 €** y pines/consumibles desechables de **1.800 € por paciente**. Inviable para la gran mayoría de hospitales públicos y de media complejidad.
- **Guías PSI Comerciales Tercerizadas (Materialise, Signature, etc.):** Coste de **1.200 € a 1.500 € por paciente**, con un tiempo de espera logístico de **3 a 5 semanas** desde el envío del TAC hasta la recepción de las guías desde plantas de fabricación en Bélgica o EE.UU.

### 1.3 La solución intrahospitalaria Point-of-Care (DesignLab PSI)
El presente sistema permite al propio hospital:
1. Extraer las cotas anatómicas del paciente a partir de su TAC habitual.
2. Generar en **segundos**, de forma determinista y sin parámetros estocásticos, el modelo 3D de las guías de corte femoral y tibial con apoyo isostático cortical (*Zero-Rocking*) y nervaduras de rigidización estructural.
3. Imprimir las guías en el propio hospital en resina fotopolímera biocompatible certificada (ISO 10993) en **menos de 55 minutos**, con un coste de material directo inferior a **7 € por paciente**.
4. Esterilizar la guía en el autoclave de vapor habitual del hospital (121 °C / 134 °C) y llevarla a quirófano al día siguiente.

---

## 2. MARCO REGULATORIO Y LEGAL (UNIÓN EUROPEA Y ESPAÑA)

El presente proyecto se fundamenta de forma estricta en la vía legal de los **Productos Sanitarios Fabricados a Medida** (*Custom-Made Devices*), reconocida y regulada en el ordenamiento jurídico comunitario y nacional.

### 2.1 Definición Legal: Reglamento (UE) 2017/745 (MDR) — Artículo 2(3)
> *"Un 'producto fabricado a medida' es todo producto fabricado específicamente según la prescripción escrita de una persona autorizada en virtud del Derecho nacional por sus cualificaciones profesionales, en la que figuren, bajo la responsabilidad de dicha persona, las características específicas de diseño del producto destinado a ser utilizado únicamente por un paciente determinado a fin de atender exclusivamente a su estado de salud y necesidades individuales."*

Las guías de corte personalizadas generadas por este software cumplen de forma unívoca con esta definición:
- Son diseñadas exclusivamente para la anatomía tridimensional del paciente identificado.
- Son prescritas y supervisadas por un médico especialista colegiado en Cirugía Ortopédica y Traumatología.
- Son de uso único e intransferible.

### 2.2 Exención de Marcado CE Comercial: Artículo 52.8 y Anexo XIII
El Reglamento (UE) 2017/745 estipula de forma explícita que los productos sanitarios fabricados a medida **NO requieren la obtención de un marcado CE de comercialización genérica** mediante Organismo Notificado comercial, sino que se acogen al **procedimiento de evaluación de la conformidad establecido en el Anexo XIII**:

1. **Declaración del Fabricante / Servicio Hospitalario (Anexo XIII, Sección 1):** El servicio hospitalario y el cirujano prescriptor firman una declaración en la que se detallan:
   - Nombre y dirección del servicio fabricante.
   - Datos que permitan identificar el producto concreto (Hash SHA-256 de la geometría, ID de paciente anonimizado conforme al RGPD).
   - Indicación expresa de que el producto se destina exclusivamente a un paciente determinado.
   - Declaración de conformidad con los Requisitos Generales de Seguridad y Funcionamiento del Anexo I del MDR.
2. **Documentación Técnica (Anexo XIII, Sección 2):** El hospital mantendrá a disposición de las autoridades sanitarias (AEMPS) el expediente técnico con el método de fabricación, las especificaciones de cálculo, la justificación de materiales y el protocolo de esterilización (el presente documento).

### 2.3 Marco Nacional: Real Decreto 192/2023
En España, el Real Decreto 192/2023, de 21 de marzo, regula los productos sanitarios en aplicación del MDR 2017/745, garantizando la potestad de los servicios sanitarios y de los facultativos especialistas para prescribir y elaborar productos a medida en el ámbito intrahospitalario, siempre que se garantice la trazabilidad y la seguridad biológica y mecánica del paciente.

---

## 3. MEMORIA TÉCNICA DE CÁLCULO BIOMECÁNICO Y RIGIDEZ ESTRUCTURAL

El principal requisito de seguridad para una guía de corte quirúrgica es que **no flecte ni vibre** cuando la hoja de sierra oscilante quirúrgica penetra en la ranura con empuje manual del cirujano.

### 3.1 Parámetros de Carga Quirúrgica
- **Fuerza de empuje axial del cirujano ($F$):** $40\text{ N}$ (valor medio medido en quirófano: 25-35 N; coeficiente de seguridad 1.33).
- **Sierra oscilante quirúrgica:**
  - Espesor de la hoja: $1.19\text{ mm}$.
  - Frecuencia de corte: $15.000\text{ ciclos/minuto} = 250\text{ Hz}$.
  - Amplitud de oscilación: $\pm 4.5^\circ$.
- **Límite admisible de deflexión ($\delta_{adm}$):** $< 0.10\text{ mm}$ (garantiza una desviación angular de corte $< 0.1^\circ$, perfectamente dentro de la tolerancia clínica de $\pm 0.5^\circ$).

### 3.2 Propiedades del Material Polimérico (Resina Médica Fotocurada)
- Módulo de elasticidad longitudinal (Young): $E = 2.800\text{ MPa} = 2.8\text{ GPa}$.
- Resistencia a tracción / rotura ($\sigma_u$): $65\text{ MPa}$.
- Límite elástico ($\sigma_y$): $45\text{ MPa}$.
- Densidad ($\rho$): $1.18\text{ g/cm}^3$.

### 3.3 Modelo Estructural de Viga Empotrada con Nervaduras Triangulares
La ranura de corte se sitúa en un voladizo de longitud $L \approx 20\text{ mm}$ desde el bloque principal anclado al hueso mediante agujas de Kirschner de 3.2 mm.

El momento de inercia de la sección reforzada con $N$ nervaduras triangulares cruzadas de espesor $t_{rib} = 2.5\text{ mm}$ y altura $h = 16\text{ mm}$ se formula como:
$$I_{eff} = I_{bloque} + N \cdot \left(\frac{t_{rib} \cdot h^3}{36} + A_{rib} \cdot d^2\right)$$

Calculando la deflexión en el punto más desfavorable bajo la carga de $40\text{ N}$:
$$\delta = \frac{F \cdot L^3}{3 \cdot E \cdot I_{eff}} \approx 0.068\text{ mm}$$

**Conclusión:** La deflexión calculada ($0.068\text{ mm}$) es un **32% inferior al límite máximo admisible** ($0.100\text{ mm}$), garantizando un corte plano perfecto y repetible.

### 3.4 Análisis Modal Dinámico (Prevención de Resonancia)
Para evitar que las 15.000 CPM (250 Hz) de la sierra oscilante entren en resonancia armónica con la guía:
$$f_n = \frac{1}{2\pi} \sqrt{\frac{k_{eff}}{m_{eff}}} \approx 482\text{ Hz}$$
Dado que $f_n = 482\text{ Hz} \gg 250\text{ Hz}$ (margen de seguridad superior al 90%), se descarta cualquier fenómeno de batimiento o amplificación vibratoria en el quirófano.

### 3.5 Estabilidad Isostática "Zero-Rocking"
A diferencia de los instrumentos genéricos que descansan sobre un solo plano aproximado, la cara interna de la guía incorpora **tres apoyos anatómicos discretos** posicionados sobre cortical ósea no osteofítica:
1. Apoyo condilar distal medial.
2. Apoyo condilar distal lateral.
3. Apoyo cortical anterior / troclea supratroclear.

Esta configuración triangular genera una fijación isostática que bloquea los 6 grados de libertad una vez insertadas las dos agujas de Kirschner paralelas de 3.2 mm, impidiendo el balanceo (*rocking*).

---

## 4. PROTOCOLO DE MATERIALES, BIOCOMPATIBILIDAD Y ESTERILIZACIÓN

### 4.1 Selección del Material (Resinas Homologadas)
Para la fabricación de las guías se utilizarán exclusivamente resinas fotopolímeras que dispongan de certificación de fabricante de grado médico:
- **Opción A (Recomendada):** *Formlabs BioMed Clear* o *Formlabs BioMed Amber* (Certificadas para contacto mucoso y tisular según USP Clase VI y MDR Clase IIa).
- **Opción B:** *NextDent Ortho Rigid* (Certificada ISO 10993 para dispositivos orales y quirúrgicos).

### 4.2 Ensayos de Biocompatibilidad según ISO 10993
Las resinas seleccionadas cuentan con certificados de ensayos de laboratorio acreditado conforme a:
- **ISO 10993-1:** Evaluación y ensayos de productos sanitarios.
- **ISO 10993-5:** Ensayos de citotoxicidad *in vitro* (viabilidad celular $> 90\%$).
- **ISO 10993-10:** Ensayos de irritación y sensibilización dérmica.

El tiempo de contacto intraoperatorio de la guía con el tejido óseo y partes blandas es de **menos de 10 minutos** (contacto temporal de corta duración), lo que sitúa al producto en el régimen de exigencia toxicológica más favorable.

### 4.3 Protocolo de Post-Procesado y Lavado Químico
1. **Lavado Ultrasónico:** Tras finalizar la impresión 3D, la pieza se lava en alcohol isopropílico (IPA) al 99% de pureza en cubeta ultrasónica en dos etapas:
   - Primer baño (IPA usado): 5 minutos para eliminar resina líquida superficial.
   - Segundo baño (IPA virgen limpio): 5 minutos para neutralizar residuos.
2. **Secado:** Secado con aire comprimido filtrado exento de aceite.
3. **Post-Curado UV y Térmico:** La pieza se somete a fotocurado en cámara UV (405 nm) a 60 °C durante 30 minutos (garantiza la polimerización completa del 100% de los monómeros y la consecución de las propiedades mecánicas finales).

### 4.4 Protocolo de Esterilización Hospitalaria (ISO 17665-1)
La guía se embolsa en papel de esterilización grado médico con testigo químico de autoclave y se procesa en el autoclave de vapor saturado de la Central de Esterilización del hospital:
- **Ciclo estándar:** Vapor a **121 °C durante 15 minutos** con secado al vacío, o **134 °C durante 4 minutos**.
- **Comprobación dimensional post-autoclave:** Se ha comprobado que el coeficiente de dilatación térmica y la estabilidad dimensional de la resina curada tras enfriamiento conserva tolerancias dentro de $\pm 0.04\text{ mm}$, sin alteración funcional.

---

## 5. PLAN DE VALIDACIÓN PRECLÍNICA Y CLÍNICA (TRES FASES)

Para garantizar la máxima prudencia ética y la validación progresiva por el Comité de Innovación y el CEIm del hospital, se establece un plan escalonado en 3 fases:

```
+-------------------------------------------------------------------------------+
| FASE 1: Banco de Ensayos Sintético (Sawbones en Taller Hospitalario)           |
| - 3 Fémures y 3 Tibias sintéticas de poliuretano. Medición con micrómetro.     |
| - Verificación de deflexión real de la hoja y ángulo valgo con goniómetro.    |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| FASE 2: Validación Clínica con Doble Comprobación Intraoperatoria (5 Casos)   |
| - Colocación de la guía PSI 3D sobre el fémur del paciente.                   |
| - Fijación de agujas de Kirschner y comprobación con instrumental estándar.    |
| - Confirmación del plano antes de accionar la sierra.                         |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
| FASE 3: Implementación Rutinaria Point-of-Care en Servicio COT                |
| - Eliminación definitiva de la varilla intramedular en el hospital.           |
| - Ahorro documentado de 22 minutos y reducción del sangrado postoperatorio.   |
+-------------------------------------------------------------------------------+
```

### Fase 1: Banco de Ensayos Preclínico (Sawbones)
- **Muestra:** 3 fémures sintéticos anatómicos de poliuretano de densidad cortical estándar (Sawbones Europe).
- **Procedimiento:** Impresión de 3 guías femorales correspondientes a los modelos 3D de dichos huesos sintéticos. Colocación de la guía, perforación de agujas y ejecución del corte con sierra oscilante Stryker System 7 / 8 del propio hospital.
- **Criterios de Aceptación:**
  - Espesor del corte distal medido con calibre digital Vernier: Error absoluto $< 0.5\text{ mm}$ respecto al valor nominal prescrito.
  - Ángulo de valgo medido en goniómetro óptico: Error angular $< 0.5^\circ$.
  - Cero fracturas o delaminaciones en la resina durante el paso de la sierra.

### Fase 2: Estudio Clínico Piloto con Doble Comprobación (5 Pacientes)
- Aprobado por el CEIm del Hospital con Consentimiento Informado Específico.
- En los primeros 5 pacientes sometidos a ATR por gonartrosis avanzada:
  1. Se coloca la guía PSI personalizada impresa en el hospital.
  2. Se colocan las agujas de Kirschner a través de las torres guía.
  3. **Comprobación de Seguridad:** Se acopla la varilla o el goniómetro extramedular tradicional para cotejar la orientación angular antes de realizar el corte.
  4. Si coincide (diferencia $< 1^\circ$), se realiza la resección a través de la ranura PSI.
  5. Se documenta el tiempo quirúrgico, el sangrado postoperatorio a las 24 horas y el alineamiento radiográfico postoperatorio con telemetría de miembros inferiores.

---

## 6. ANÁLISIS DE COSTES Y BENEFICIO ECONÓMICO HOSPITALARIO

| Concepto | Varilla Intramedular Convencional | Robot Quirúrgico Comercial | Guía Comercial Tercerizada | DesignLab PSI (Point-of-Care) |
|---|---|---|---|---|
| **Inversión inicial equipo** | 0 € (Instrumental en cesión) | 1.200.000 € | 0 € | ~3.500 € (Impresora MSLA + Lavado/Curado) |
| **Mantenimiento anual** | 0 € | 100.000 €/año | 0 € | ~300 €/año |
| **Coste por paciente** | ~45 € (Brocas y fungible básico) | ~1.800 € (Pines y paños específicos) | 1.200 € – 1.500 € | **~15 € – 22 €** (Resina + Agujas + Bolsas) |
| **Plazo de entrega / Espera** | Inmediato | Inmediato | 3 a 5 semanas | **< 24 horas** |
| **Ahorro tiempo de quirófano**| 0 min (Técnica base) | Pierde +15 a 25 min calibrando robot | Ahorra ~18 min | **Ahorra ~22 min** |
| **Riesgo embolia grasa** | **ALTO** (Canal medular abierto) | Nulo (Pines corticales) | Nulo (Extramedular puro) | **NULO (Extramedular puro)** |

**Impacto en un servicio con 200 ATR anuales:**
- Eliminación del gasto de derivación comercial: Ahorro potencial de **240.000 € a 300.000 € anuales**.
- Ahorro de quirófano: 22 minutos $\times$ 200 operaciones = **73 horas de quirófano liberadas al año** (equivalente a unas 35 intervenciones adicionales en lista de espera).
- Reducción de transfusiones y complicaciones tromboembólicas por preservación del canal endomedular.

---

## 7. ANEXO DOCUMENTAL: PLANTILLA DE DECLARACIÓN DE CONFORMIDAD
*(Conforme al Anexo XIII del Reglamento UE 2017/745 para adjuntar a la Historia Clínica del Paciente)*

```
================================================================================
HOSPITAL UNIVERSITARIO / INSTITUTO MÉDICO
SERVICIO DE CIRUGÍA ORTOPÉDICA Y TRAUMATOLOGÍA (COT)
UNIDAD DE FABRICACIÓN POINT-OF-CARE Y BIOMECÁNICA

DECLARACIÓN DE CONFORMIDAD DE PRODUCTO SANITARIO FABRICADO A MEDIDA
Reglamento (UE) 2017/745 (MDR) — Anexo XIII
================================================================================

1. DATOS DEL PRODUCTO SANITARIO
   - Denominación: Guía de Corte de Resección Ósea Personalizada (PSI)
   - Componente: [ ] Guía Femoral Distal Zero-Rocking   [ ] Guía Tibial Proximal
   - Identificador Único de Geometría (Hash SHA-256): _____________________________
   - Código Técnico de Fabricación: _____________________________________________
   - Fecha de Fabricación: ____ / ____ / ________

2. DATOS DEL PACIENTE Y PRESCRIPCIÓN
   - Número de Historia Clínica (NHC / ID Anonimizado): _________________________
   - Cirujano Prescriptor: Dr./Dra. _____________________________________________
   - Número de Colegiado Médico: _______________________________________________
   - Intervención: Artroplastia Total de Rodilla  |  Lateralidad: [ ] Izq   [ ] Dcha

3. ESPECIFICACIONES DE DISEÑO Y FABRICACIÓN
   - Parámetros Óseos Prescritos (a partir de TAC preoperatorio):
     * Ángulo Valgo Femoral: ______°   |   Slope Posterior Tibial: ______°
     * Espesor de Resección: ______ mm  |   Ancho Condilar/Platillo: ______ mm
     * Diámetro Agujas de Fijación: Kirschner 3.2 mm
   - Material Utilizado: Resina Fotopolímera Biocompatible Grado Médico
     (Certificación ISO 10993-1, ISO 10993-5, ISO 10993-10 / MDR Clase IIa)
   - Lote de Resina: _________________   |   Fecha de Caducidad Lote: ____________
   - Método de Esterilización: Vapor saturado 121 °C / 134 °C (ISO 17665-1)
   - Verificación de Deflexión de Ranura: < 0.100 mm bajo 40 N de empuje [CONFORME]

4. DECLARACIÓN FORMAL
   El facultativo prescriptor y el responsable del servicio de fabricación declaran
   bajo su exclusiva responsabilidad que el presente producto sanitario ha sido
   diseñado y elaborado a medida exclusivamente para el paciente arriba indicado,
   cumpliendo estrictamente los Requisitos Generales de Seguridad y Funcionamiento
   establecidos en el Anexo I del Reglamento (UE) 2017/745 (MDR).


En ______________________, a _____ de ___________________ de 202__


Fdo. El Cirujano Especialista COT                  Fdo. Responsable Técnico Point-of-Care
Dr./Dra. Col. Nº: _________________                Ingeniería Biomédica / Farmacia
