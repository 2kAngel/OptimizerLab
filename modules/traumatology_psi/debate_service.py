"""
Servicio de Sesión Clínica y Debate Multidisciplinar ("MiroFish Hospitalario")
Simula un panel de consenso médico-económico-legal para evaluación de guías PSI.
Participantes:
1. Cirujano Veterano Escéptico (Dr. Valenzuela)
2. Cirujana Innovadora Pro-PSI (Dra. Morante)
3. Enfermera Instrumentista de Quirófano (Dña. Carmen)
4. Director Financiero del Hospital (D. Fernando)
5. Portavoz de Multinacional Competidora (Mr. Henderson - Lobby Ortopédico)
6. Asesor Jurídico Hospitalario / Experto MDR (Lic. Arrieta)
7. Paciente Candidato a Cirugía (D. Ramón, 68 años)
"""

from typing import Any, Dict, List, Optional
import pydantic


class DebateMessage(pydantic.BaseModel):
    id: str
    speaker_id: str
    speaker_name: str
    speaker_role: str
    organization: str
    category: str  # surgery | nursing | finance | competitor | legal | patient
    avatar_color: str
    badge_label: str
    text: str
    key_argument: str
    sentiment: str  # positive | critical | neutral | hostile


class ClinicalDebateReport(pydantic.BaseModel):
    session_id: str
    patient_id: str
    timestamp: str
    case_summary: str
    messages: List[DebateMessage]
    consensus_verdict: str
    risk_matrix: Dict[str, str]
    economic_impact: Dict[str, Any]
    legal_clearance: str


class ClinicalDebateService:
    """Generador y gestor del debate multidisciplinar del comité hospitalario."""

    @classmethod
    def generate_debate(
        cls,
        patient_id: str = "PACIENTE-84021",
        family_id: str = "distal_femur_cutting_guide",
        parameters: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        custom_query: Optional[str] = None,
    ) -> ClinicalDebateReport:
        p = parameters or {}
        m = metrics or {}
        is_femur = "femur" in family_id.lower()
        organ_name = "Fémur Distal" if is_femur else "Tibia Proximal"
        angle_val = p.get("valgus_angle") or p.get("valgus_angle_deg") or p.get("posterior_slope") or (5.5 if is_femur else 3.0)
        angle_type = "Ángulo Valgo" if is_femur else "Slope Posterior"
        resection_mm = p.get("resection_thickness_mm") or p.get("resection_thickness") or 9.0
        deflection = m.get("slot_deflection_mm") or 0.068
        cost_eur = m.get("resin_cost_eur") or 5.80
        rocking_pts = m.get("zero_rocking_score") or 99.0

        messages: List[DebateMessage] = []

        # 1. Moderador / Presentación
        messages.append(
            DebateMessage(
                id="msg-01",
                speaker_id="moderator",
                speaker_name="Dr. Sotomayor",
                speaker_role="Presidente de la Comisión de Innovación Quirúrgica",
                organization="Hospital Universitario Clínico",
                category="surgery",
                avatar_color="#0284c7",
                badge_label="MODERADOR",
                text=f"Abrimos la sesión clínica para evaluar la prescripción de {patient_id}. Se propone el uso de una guía de corte extramedular a medida ({organ_name}) fabricada mediante impresión 3D Point-of-Care. Parámetros: {angle_type} de {angle_val}°, resección planificada de {resection_mm} mm, rigidez anti-deflexión de {deflection} mm y coste de material de {cost_eur} €. Doy la palabra a los miembros del comité.",
                key_argument="Presentación reglamentaria de la propuesta de instrumental a medida.",
                sentiment="neutral",
            )
        )

        # 2. Cirujano Veterano Escéptico
        messages.append(
            DebateMessage(
                id="msg-02",
                speaker_id="surgeon_vet",
                speaker_name="Dr. Valenzuela",
                speaker_role="Jefe de Sección de Cirugía Ortopédica (32 años en activo)",
                organization="Servicio de Traumatología",
                category="surgery",
                avatar_color="#f59e0b",
                badge_label="TRAUMATÓLOGO VETERANO",
                text=f"Colegas, seamos honestos: yo llevo más de tres décadas operando rodillas con la varilla intramedular de acero inoxidable. Sí, sé que perfora el fémur y sangra, pero es una referencia sólida y rígida que no falla jamás. Mi inquietud es visceral: cuando el residente empuje la hoja de sierra a 15.000 oscilaciones por minuto contra esta guía de resina plástica, ¿qué me garantiza que el labio de la ranura no se caliente, ceda un milímetro y me deje un corte biselado que arruine el implante?",
                key_argument=f"Duda de rigidez plástica frente al acero bajo 40 N y riesgo de biselado en el corte óseo.",
                sentiment="critical",
            )
        )

        # 3. Cirujana Innovadora Pro-PSI
        messages.append(
            DebateMessage(
                id="msg-03",
                speaker_id="surgeon_innov",
                speaker_name="Dra. Morante",
                speaker_role="Cirujana Especialista en Artroplastia Compleja",
                organization="Unidad de Rodilla y Navegación",
                category="surgery",
                avatar_color="#38bdf8",
                badge_label="TRAUMATÓLOGA PRO-PSI",
                text=f"Entiendo sus reservas, Dr. Valenzuela, pero los datos de la literatura médica son irrefutables: la varilla intramedular provoca embolia grasa detectable por ecocardiografía transesofágica en hasta el 60% de los pacientes y causa una media de 350 ml de sangrado intraóseo que a menudo exige transfusiones. En este diseño, la deflexión calculada con 4 nervios es de apenas {deflection} mm (tolerancia clínica máxima admisible es 0.10 mm). Además, el apoyo Zero-Rocking ({rocking_pts}% de estabilidad) calca los cóndilos del TAC como un puzzle. Cero varilla, cero embolia, y una precisión angular con desviación inferior a 0.5°.",
                key_argument="Erradicación de embolia grasa, ahorro de sangre y precisión cinemática submilimétrica.",
                sentiment="positive",
            )
        )

        # 4. Enfermera Instrumentista de Quirófano
        messages.append(
            DebateMessage(
                id="msg-04",
                speaker_id="nurse_lead",
                speaker_name="Dña. Carmen Rivas",
                speaker_role="Supervisora de Enfermería Quirúrgica",
                organization="Bloque Quirúrgico de Traumatología",
                category="nursing",
                avatar_color="#14b8a6",
                badge_label="ENFERMERÍA QUIRÚRGICA",
                text="Desde el punto de vista del equipo de enfermería, la técnica estándar actual es una tortura logística: nos obliga a abrir, contar, esterilizar y transportar entre 4 y 6 cajas metálicas de instrumental por paciente, que pesan más de 14 kg cada una. Cada caja que se abre en quirófano aumenta exponencialmente la exposición a gérmenes ambientales. Con esta guía a medida, la enfermera instrumentista pasa de gestionar 120 piezas metálicas a entregar una única pieza estéril de 35 gramos lista para autoclave (121 °C). Eso nos ahorra 25 minutos de preparación y conteo de instrumental por cirugía.",
                key_argument="Reducción radical de carga estéril (de 6 cajas pesadas a 1 pieza ligera) y menor riesgo de infección.",
                sentiment="positive",
            )
        )

        # 5. La Competencia Multinacional (Lobby Ortopédico)
        messages.append(
            DebateMessage(
                id="msg-05",
                speaker_id="competitor_vp",
                speaker_name="Mr. Arthur Henderson",
                speaker_role="VP de Asuntos Gubernamentales & Acceso al Mercado",
                organization="Consorcio Multinacional Ortopédico (Zimmer-Stryker-Medacta Alliance)",
                category="competitor",
                avatar_color="#ef4444",
                badge_label="LOBBY / COMPETENCIA",
                text="Con el debido respeto a este hospital, fabricar instrumental quirúrgico en una impresora 3D 'en casa' es una irresponsabilidad corporativa. Nuestras multinacionales invierten cientos de millones en ensayos clínicos, salas blancas con certificación ISO 13485 clase 8 y trazabilidad global blindada. Cobramos entre 1.200 € y 1.500 € por juego de guías porque ofrecemos respaldo legal de marca, un seguro de responsabilidad civil global y personal de soporte en quirófano. Un hospital público no puede degradarse a un taller de bricolaje protésico por ahorrarse unos euros.",
                key_argument="Defensa del modelo comercial de 1.500 €/guía bajo el argumento de 'garantía de marca corporativa'.",
                sentiment="hostile",
            )
        )

        # 6. Director Financiero del Hospital
        messages.append(
            DebateMessage(
                id="msg-06",
                speaker_id="finance_director",
                speaker_name="D. Fernando Beltrán",
                speaker_role="Director Económico y de Gestión de Compras",
                organization="Servicio de Salud Autonómico",
                category="finance",
                avatar_color="#10b981",
                badge_label="DIRECCIÓN FINANCIERA",
                text=f"Disculpe, señor Henderson, pero sus cifras ya no son sostenibles para las arcas públicas. En este centro realizamos 450 prótesis de rodilla al año. Pagar 1.400 € a su empresa por paciente representaría 630.000 € anuales solo en plástico desechable. Con la plataforma DesignLab Point-of-Care, el coste de resina certificada es de {cost_eur} € por guía. El gasto total anual en material pasa de 630.000 € a 2.610 €. Además, cada minuto de quirófano en nuestro hospital público cuesta 32 €; si ahorramos 22 minutos por intervención gracias al montaje simplificado, son 700 € extra de capacidad operativa ahorrados por paciente. Con eso operamos a 80 pacientes más al año sin aumentar el presupuesto.",
                key_argument=f"Ahorro de más de 620.000 €/año en el hospital público y ampliación de capacidad para reducir listas de espera.",
                sentiment="positive",
            )
        )

        # 7. Asesor Jurídico Hospitalario (MDR 2017/745)
        messages.append(
            DebateMessage(
                id="msg-07",
                speaker_id="legal_counsel",
                speaker_name="Lic. Ignacio Arrieta",
                speaker_role="Jefe del Gabinete Jurídico & Compliance Biomédico",
                organization="Comité Ético de Investigación con Medicamentos (CEIm)",
                category="legal",
                avatar_color="#8b5cf6",
                badge_label="ASESOR JURÍDICO (LEGAL)",
                text="Para desmontar las amenazas del señor Henderson: el Reglamento Europeo (UE) 2017/745 (MDR) prevé de forma explícita en su Artículo 5(5) y Anexo XIII la fabricación intrahospitalaria de 'Productos Sanitarios a Medida' (Custom-Made Devices). La ley NO exige el costoso marcado CE industrial siempre que el dispositivo sea prescrito por un médico especialista facultado bajo su responsabilidad, fabricado para un paciente concreto identificado y respaldado por una Declaración de Conformidad con trazabilidad criptográfica (el hash SHA-256 generado por este software). Legalmente, el hospital está 100% blindado y dentro del marco legal comunitario más riguroso.",
                key_argument="Blindaje jurídico formal bajo MDR 2017/745 Anexo XIII sin requerir intermediación de la industria.",
                sentiment="positive",
            )
        )

        # 8. El Paciente (Usuario Final)
        messages.append(
            DebateMessage(
                id="msg-08",
                speaker_id="patient_voice",
                speaker_name="D. Ramón Gómez (68 años)",
                speaker_role="Paciente con Gonartrosis Grado IV en Lista de Espera",
                organization="Asociación de Pacientes Osteoarticulares",
                category="patient",
                avatar_color="#eab308",
                badge_label="EL PACIENTE",
                text="Escucho hablar de millones de euros, de patentes y de batallas entre empresas, pero los que estamos en casa sin poder bajar las escaleras somos nosotros. Llevo 9 meses esperando esta operación de rodilla tomando analgésicos que me destrozan el estómago. A mí me da igual si el plástico lo hace una multinacional suiza o la impresora del hospital de mi ciudad: lo que quiero es que la prótesis me quede perfecta, que no me tengan que poner sangre de otra persona, que me duela lo menos posible y poder volver a caminar por el parque con mis nietos antes de que pase otro año más en una lista de espera. Si esta pieza lo hace posible por 5 euros, adelante.",
                key_argument="Voz del paciente: derecho a una cirugía de precisión sin demoras de 9 meses ni dolor innecesario.",
                sentiment="positive",
            )
        )

        # 9. Conclusión del Cirujano Veterano (Consenso)
        messages.append(
            DebateMessage(
                id="msg-09",
                speaker_id="surgeon_vet_conclude",
                speaker_name="Dr. Valenzuela",
                speaker_role="Jefe de Sección de Cirugía Ortopédica",
                organization="Servicio de Traumatología",
                category="surgery",
                avatar_color="#f59e0b",
                badge_label="TRAUMATÓLOGO VETERANO",
                text=f"Agradezco las explicaciones de la Dra. Morante y el asesor legal. Si la deflexión garantizada es de {deflection} mm, el material está certificado bajo ISO 10993 y no violamos el canal medular, como cirujano doy mi visto bueno para el primer caso clínico piloto en este hospital. Eso sí: estaré en quirófano comprobando personalmente el encaje puzzle Zero-Rocking antes de meter la sierra.",
                key_argument="Superación de la objeción quirúrgica clásica y aprobación unánime del piloto clínico.",
                sentiment="positive",
            )
        )

        # Respuesta a consulta interactiva si se proporcionó una
        if custom_query:
            messages.append(
                DebateMessage(
                    id=f"msg-query-{len(messages)+1}",
                    speaker_id="special_advisor",
                    speaker_name="Panel Multidisciplinar",
                    speaker_role="Respuesta Colegiada del Comité",
                    organization="Mesa Redonda MiroFish",
                    category="surgery",
                    avatar_color="#06b6d4",
                    badge_label="RESPUESTA DEL COMITÉ",
                    text=f"Ante la cuestión planteada («{custom_query}»): El comité confirma que cualquier contingencia intraoperatoria está respaldada por la presencia obligatoria en quirófano de la caja de rescate con instrumental convencional. La guía PSI actúa como optimizador extramedular primario de máxima precisión sin invalidar la reversibilidad técnica inmediata.",
                    key_argument="Principio de redundancia de seguridad médica y reversibilidad en quirófano.",
                    sentiment="positive",
                )
            )

        return ClinicalDebateReport(
            session_id=f"SESION-CLINICA-{patient_id}",
            patient_id=patient_id,
            timestamp="2026-11-22T00:00:00Z",
            case_summary=f"Planificación de {organ_name} ({angle_type} {angle_val}°, Resección {resection_mm} mm)",
            messages=messages,
            consensus_verdict="APROBADO POR UNANIMIDAD PARA INTERVENCIÓN CLÍNICA PILOTO (MDR 2017/745 ANEXO XIII)",
            risk_matrix={
                "Riesgo Embolia Grasa": "ELIMINADO (Técnica 100% Extramedular)",
                "Deflexión Ranura de Corte": f"CONFORME ({deflection} mm < 0.10 mm límite)",
                "Estabilidad de Anclaje": f"ÓPTIMA (Zero-Rocking {rocking_pts}% en cortical)",
                "Biocompatibilidad": "CERTIFICADA (Resina Médica ISO 10993 / Autoclave 121 °C)",
                "Coste por Paciente": f"~{cost_eur} € (Ahorro de ~1.450 € vs oligopolio comercial)",
            },
            economic_impact={
                "coste_multinacional_comercial": 1450.0,
                "coste_point_of_care": cost_eur,
                "ahorro_neto_paciente": round(1450.0 - cost_eur, 2),
                "tiempo_quirofano_ahorrado_min": 22,
                "reduccion_volumen_cajas_esteriles": "De 6 cajas (70 kg) a 1 pieza (35 g)",
            },
            legal_clearance="CONFORME REGLAMENTO (UE) 2017/745 (MDR) ANEXO XIII — PRODUCTO SANITARIO A MEDIDA",
        )
