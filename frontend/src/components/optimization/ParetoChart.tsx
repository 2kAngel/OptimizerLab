import React from 'react'

export interface ParetoPoint {
  id: string
  index: number
  generation: number
  mass: number
  power: number
  torque: number
  isPareto: boolean
  candidate: any
}

interface ParetoChartProps {
  points: ParetoPoint[]
  selectedId: string | null
  onSelectCandidate: (candidate: any) => void
}

export const ParetoChart: React.FC<ParetoChartProps> = ({
  points,
  selectedId,
  onSelectCandidate,
}) => {
  if (points.length === 0) {
    return (
      <div style={{ padding: 24, textAlign: 'center', color: '#64748b', fontSize: 13, background: '#0f172a', borderRadius: 8, border: '1px solid #334155' }}>
        No hay datos de optimización aún. Pulsa el botón "🚀 Optimizar con NSGA-II" para explorar el espacio de diseño y calcular el Frente de Pareto.
      </div>
    )
  }

  // Dimensiones del gráfico SVG
  const width = 640
  const height = 300
  const padLeft = 60
  const padRight = 30
  const padTop = 30
  const padBottom = 40

  const masses = points.map((p) => p.mass)
  const powers = points.map((p) => p.power)

  const minMass = Math.max(0, Math.min(...masses) * 0.9)
  const maxMass = Math.max(...masses) * 1.1 || 10
  const minPower = Math.max(0, Math.min(...powers) * 0.9)
  const maxPower = Math.max(...powers) * 1.1 || 100

  const scaleX = (m: number) => padLeft + ((m - minMass) / (maxMass - minMass || 1)) * (width - padLeft - padRight)
  const scaleY = (p: number) => height - padBottom - ((p - minPower) / (maxPower - minPower || 1)) * (height - padTop - padBottom)

  // Ordenar puntos del frente de Pareto para dibujar la curva límite
  const paretoPoints = points
    .filter((p) => p.isPareto)
    .sort((a, b) => a.mass - b.mass)

  const paretoPath = paretoPoints
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(p.mass)} ${scaleY(p.power)}`)
    .join(' ')

  return (
    <div style={{ background: '#0f172a', padding: 16, borderRadius: 8, border: '1px solid #334155' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#f8fafc' }}>
          Frente de Pareto Multi-Objetivo (Potencia vs Masa)
        </div>
        <div style={{ display: 'flex', gap: 12, fontSize: 11 }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#10b981' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span>
            Frente de Pareto (Óptimos No Dominados)
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#64748b' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#475569', display: 'inline-block' }}></span>
            Diseños Dominados
          </span>
        </div>
      </div>

      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
        {/* Ejes y líneas de cuadrícula */}
        <line x1={padLeft} y1={height - padBottom} x2={width - padRight} y2={height - padBottom} stroke="#334155" strokeWidth={1} />
        <line x1={padLeft} y1={padTop} x2={padLeft} y2={height - padBottom} stroke="#334155" strokeWidth={1} />

        {/* Etiquetas de ejes */}
        <text x={width / 2} y={height - 8} fill="#94a3b8" fontSize={11} textAnchor="middle">
          Masa del Rotor (kg) → [Menor es mejor]
        </text>
        <text x={-height / 2} y={18} fill="#94a3b8" fontSize={11} textAnchor="middle" transform="rotate(-90)">
          Potencia Mecánica (W) → [Mayor es mejor]
        </text>

        {/* Marcas de escala */}
        <text x={padLeft} y={height - padBottom + 16} fill="#64748b" fontSize={10} textAnchor="middle">{minMass.toFixed(1)}</text>
        <text x={width - padRight} y={height - padBottom + 16} fill="#64748b" fontSize={10} textAnchor="middle">{maxMass.toFixed(1)}</text>
        <text x={padLeft - 8} y={scaleY(minPower)} fill="#64748b" fontSize={10} textAnchor="end">{minPower.toFixed(0)}</text>
        <text x={padLeft - 8} y={scaleY(maxPower)} fill="#64748b" fontSize={10} textAnchor="end">{maxPower.toFixed(0)}</text>

        {/* Línea del Frente de Pareto */}
        {paretoPoints.length > 1 && (
          <path d={paretoPath} fill="none" stroke="#10b981" strokeWidth={2} strokeDasharray="4 2" />
        )}

        {/* Puntos de diseño */}
        {points.map((pt) => {
          const cx = scaleX(pt.mass)
          const cy = scaleY(pt.power)
          const isSelected = selectedId === pt.id

          return (
            <g
              key={pt.id}
              onClick={() => onSelectCandidate(pt.candidate)}
              style={{ cursor: 'pointer' }}
            >
              <circle
                cx={cx}
                cy={cy}
                r={isSelected ? 7 : pt.isPareto ? 5.5 : 3.5}
                fill={pt.isPareto ? '#10b981' : '#475569'}
                stroke={isSelected ? '#38bdf8' : pt.isPareto ? '#f8fafc' : 'none'}
                strokeWidth={isSelected ? 2.5 : 1}
                opacity={pt.isPareto || isSelected ? 1 : 0.6}
              />
              <title>{`Candidato #${pt.index} (Gen ${pt.generation})\nPotencia: ${pt.power} W\nMasa: ${pt.mass} kg\nPar: ${pt.torque} N·m`}</title>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
