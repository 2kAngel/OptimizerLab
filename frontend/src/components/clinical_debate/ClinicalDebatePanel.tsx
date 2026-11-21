import React, { useState, useEffect } from 'react'

export interface DebateMessage {
  id: string
  speaker_id: string
  speaker_name: string
  speaker_role: string
  organization: string
  category: 'surgery' | 'nursing' | 'finance' | 'competitor' | 'legal' | 'patient'
  avatar_color: string
  badge_label: string
  text: string
  key_argument: string
  sentiment: 'positive' | 'critical' | 'neutral' | 'hostile'
}

export interface ClinicalDebateReport {
  session_id: string
  patient_id: string
  timestamp: string
  case_summary: string
  messages: DebateMessage[]
  consensus_verdict: string
  risk_matrix: Record<string, string>
  economic_impact: {
    coste_multinacional_comercial: number
    coste_point_of_care: number
    ahorro_neto_paciente: number
    tiempo_quirofano_ahorrado_min: number
    reduccion_volumen_cajas_esteriles: string
  }
  legal_clearance: string
}

interface ClinicalDebatePanelProps {
  patientId: string
  familyId: string
  parameters: Record<string, any>
  metrics: Record<string, any>
}

export const ClinicalDebatePanel: React.FC<ClinicalDebatePanelProps> = ({
  patientId,
  familyId,
  parameters,
  metrics,
}) => {
  const [report, setReport] = useState<ClinicalDebateReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [queryInput, setQueryInput] = useState('')
  const [submittingQuery, setSubmittingQuery] = useState(false)

  const fetchDebate = async (customQuery?: string) => {
    setLoading(true)
    try {
      const res = await fetch('/api/traumatology/clinical-debate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: patientId,
          family_id: familyId,
          parameters,
          metrics,
          custom_query: customQuery || null,
        }),
      })
      if (!res.ok) throw new Error('Error al cargar la sesión clínica')
      const data = await res.json()
      setReport(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
      setSubmittingQuery(false)
    }
  }

  useEffect(() => {
    fetchDebate()
  }, [patientId, familyId])

  const handleAskPanel = (e: React.FormEvent) => {
    e.preventDefault()
    if (!queryInput.trim()) return
    setSubmittingQuery(true)
    fetchDebate(queryInput)
    setQueryInput('')
  }

  const handleDownloadActa = () => {
    if (!report) return
    const lines = [
      `# ACTA DE LA SESIÓN CLÍNICA MULTIDISCIPLINAR — COMITÉ PSI HOSPITALARIO`,
      `**Identificador de Sesión:** ${report.session_id}`,
      `**Paciente:** ${report.patient_id}`,
      `**Caso Clínico:** ${report.case_summary}`,
      `**Fecha / Hora:** ${new Date().toLocaleString()}`,
      `**Marco Normativo:** ${report.legal_clearance}`,
      ``,
      `---`,
      `## DICTAMEN DE CONSENSO QUIRÚRGICO`,
      `**${report.consensus_verdict}**`,
      ``,
      `---`,
      `## IMPACTO ECONÓMICO Y DE EFICIENCIA SANITARIA`,
      `- Coste Guías Comerciales Oligopolio (Zimmer/Stryker/Medacta): ${report.economic_impact.coste_multinacional_comercial} € / paciente`,
      `- Coste Fabricación Point-of-Care (DesignLab): ${report.economic_impact.coste_point_of_care} €`,
      `- Ahorro Neto Directo por Intervención: ${report.economic_impact.ahorro_neto_paciente} €`,
      `- Reducción de Tiempo Quirúrgico: ~${report.economic_impact.tiempo_quirofano_ahorrado_min} minutos / cirugía`,
      `- Carga Logística Esterilización: ${report.economic_impact.reduccion_volumen_cajas_esteriles}`,
      ``,
      `---`,
      `## TRANSCRIPCIÓN DEL DEBATE MULTIDISCIPLINAR`,
      ...report.messages.map(
        (m) =>
          `### [${m.badge_label}] ${m.speaker_name} (${m.speaker_role} — ${m.organization})\n> *«${m.text}»*\n\n**Argumento clave:** ${m.key_argument}\n`
      ),
      `---`,
      `*Documento oficial de auditoría biomédica generado automáticamente bajo MDR 2017/745 Anexo XIII para archivo en el Expediente Clínico del Paciente.*`,
    ]

    const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ACTA_SESION_CLINICA_${report.patient_id}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const filteredMessages =
    report?.messages.filter((m) => {
      if (selectedCategory === 'all') return true
      return m.category === selectedCategory
    }) || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Cabecera del Panel */}
      <div
        style={{
          background: '#1e293b',
          borderRadius: 8,
          padding: 20,
          border: '1px solid #334155',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 16,
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 24 }}>🏛️</span>
            <div>
              <h2 style={{ margin: 0, fontSize: 18, color: '#f8fafc' }}>
                Sesión Clínica Multidisciplinar (Comité Quirúrgico Virtual)
              </h2>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                Debate cruzado entre Traumatología, Enfermería, Finanzas, Competencia (Oligopolio), Asesoría Legal MDR y Paciente.
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <button
            type="button"
            onClick={() => fetchDebate()}
            disabled={loading}
            style={{
              padding: '8px 14px',
              borderRadius: 6,
              background: '#0284c7',
              color: '#fff',
              border: 'none',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            🔄 {loading ? 'Actualizando debate...' : 'Re-ejecutar Debate'}
          </button>
          {report && (
            <button
              type="button"
              onClick={handleDownloadActa}
              style={{
                padding: '8px 14px',
                borderRadius: 6,
                background: '#10b981',
                color: '#fff',
                border: 'none',
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              📄 Descargar Acta Oficial (MDR)
            </button>
          )}
        </div>
      </div>

      {report && (
        <>
          {/* Banner de Veredicto de Consenso */}
          <div
            style={{
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid #10b981',
              borderRadius: 8,
              padding: '14px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 12,
            }}
          >
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#10b981', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                Dictamen Colegiado del Comité Quirúrgico
              </div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#f8fafc', marginTop: 3 }}>
                {report.consensus_verdict}
              </div>
            </div>
            <div style={{ fontSize: 12, color: '#94a3b8', background: '#0f172a', padding: '6px 12px', borderRadius: 6, border: '1px solid #334155' }}>
              ⚖️ {report.legal_clearance}
            </div>
          </div>

          {/* Tarjetas de Métricas de Impacto Global */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
            <div style={{ background: '#1e293b', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
              <div style={{ fontSize: 11, color: '#94a3b8' }}>Ahorro Neto Directo</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: '#10b981', marginTop: 4 }}>
                ~{report.economic_impact.ahorro_neto_paciente.toFixed(2)} €
              </div>
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>
                {report.economic_impact.coste_point_of_care} € vs {report.economic_impact.coste_multinacional_comercial} € comercial
              </div>
            </div>

            <div style={{ background: '#1e293b', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
              <div style={{ fontSize: 11, color: '#94a3b8' }}>Tiempo Quirófano Ahorrado</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: '#38bdf8', marginTop: 4 }}>
                ~{report.economic_impact.tiempo_quirofano_ahorrado_min} min / cirugía
              </div>
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>
                Montaje directo extramedular sin varilla
              </div>
            </div>

            <div style={{ background: '#1e293b', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
              <div style={{ fontSize: 11, color: '#94a3b8' }}>Logística de Esterilización</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#14b8a6', marginTop: 6, lineHeight: 1.3 }}>
                {report.economic_impact.reduccion_volumen_cajas_esteriles}
              </div>
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>
                Drástica reducción de riesgo biológico
              </div>
            </div>

            <div style={{ background: '#1e293b', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
              <div style={{ fontSize: 11, color: '#94a3b8' }}>Riesgo de Embolia Grasa</div>
              <div style={{ fontSize: 14, fontWeight: 800, color: '#22c55e', marginTop: 6 }}>
                0% (100% Extramedular)
              </div>
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>
                Canal medular intacto sin perforación
              </div>
            </div>
          </div>

          {/* Filtros de Categoría de Médicos / Intervinientes */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {[
              { id: 'all', label: `Todos los Sectores (${report.messages.length})`, icon: '👥' },
              { id: 'surgery', label: 'Cirugía & Traumatología', icon: '🦴' },
              { id: 'nursing', label: 'Enfermería Quirúrgica', icon: '🩺' },
              { id: 'finance', label: 'Gestión Económica', icon: '📊' },
              { id: 'competitor', label: 'Lobby Multinacional', icon: '🏢' },
              { id: 'legal', label: 'Asesoría Jurídica MDR', icon: '⚖️' },
              { id: 'patient', label: 'Voz del Paciente', icon: '👤' },
            ].map((cat) => (
              <button
                key={cat.id}
                type="button"
                onClick={() => setSelectedCategory(cat.id)}
                style={{
                  padding: '6px 12px',
                  borderRadius: 6,
                  border: selectedCategory === cat.id ? '1px solid #38bdf8' : '1px solid #334155',
                  background: selectedCategory === cat.id ? '#0284c7' : '#1e293b',
                  color: selectedCategory === cat.id ? '#fff' : '#94a3b8',
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <span>{cat.icon}</span>
                <span>{cat.label}</span>
              </button>
            ))}
          </div>

          {/* Timeline de Mensajes del Debate */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {filteredMessages.map((msg) => {
              const borderColors: Record<string, string> = {
                surgery: '#0284c7',
                nursing: '#14b8a6',
                finance: '#10b981',
                competitor: '#ef4444',
                legal: '#8b5cf6',
                patient: '#eab308',
              }
              const bColor = borderColors[msg.category] || '#334155'

              return (
                <div
                  key={msg.id}
                  style={{
                    background: '#0f172a',
                    borderRadius: 8,
                    padding: 16,
                    border: '1px solid #334155',
                    borderLeft: `5px solid ${bColor}`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 8,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div
                        style={{
                          width: 32,
                          height: 32,
                          borderRadius: 999,
                          background: bColor,
                          color: '#fff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 700,
                          fontSize: 13,
                        }}
                      >
                        {msg.speaker_name.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 700, color: '#f8fafc' }}>
                          {msg.speaker_name}
                        </div>
                        <div style={{ fontSize: 11, color: '#94a3b8' }}>
                          {msg.speaker_role} — <em>{msg.organization}</em>
                        </div>
                      </div>
                    </div>

                    <span
                      style={{
                        padding: '3px 8px',
                        borderRadius: 4,
                        fontSize: 10,
                        fontWeight: 700,
                        background: `${bColor}22`,
                        color: bColor,
                        border: `1px solid ${bColor}44`,
                      }}
                    >
                      {msg.badge_label}
                    </span>
                  </div>

                  <div style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.5, background: '#1e293b', padding: '10px 14px', borderRadius: 6 }}>
                    «{msg.text}»
                  </div>

                  <div style={{ fontSize: 11, color: '#64748b', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <strong>🎯 Tesis principal:</strong>
                    <span>{msg.key_argument}</span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Formulario para Preguntar al Panel */}
          <form
            onSubmit={handleAskPanel}
            style={{
              background: '#1e293b',
              borderRadius: 8,
              padding: 16,
              border: '1px solid #334155',
              display: 'flex',
              gap: 10,
            }}
          >
            <input
              type="text"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              placeholder="Haz una pregunta al comité (ej. ¿Qué pasa si la sierra se traba?, ¿Por qué Zimmer cobra tanto?, ¿Cómo se autoclavea?)..."
              disabled={submittingQuery}
              style={{
                flex: 1,
                padding: '10px 14px',
                borderRadius: 6,
                background: '#0f172a',
                color: '#fff',
                border: '1px solid #475569',
                fontSize: 13,
              }}
            />
            <button
              type="submit"
              disabled={submittingQuery || !queryInput.trim()}
              style={{
                padding: '10px 18px',
                borderRadius: 6,
                background: '#0284c7',
                color: '#fff',
                border: 'none',
                fontWeight: 700,
                fontSize: 13,
                cursor: submittingQuery || !queryInput.trim() ? 'not-allowed' : 'pointer',
              }}
            >
              {submittingQuery ? 'Consultando al Comité...' : 'Preguntar al Panel →'}
            </button>
          </form>
        </>
      )}
    </div>
  )
}
