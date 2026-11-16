import React, { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

interface Viewer3DProps {
  geometryHash?: string
  parameters?: Record<string, any>
  metrics?: Record<string, number>
  familyId?: string
}

export const Viewer3D: React.FC<Viewer3DProps> = ({ geometryHash, parameters, metrics, familyId }) => {
  const mountRef = useRef<HTMLDivElement>(null)
  const [wireframe, setWireframe] = useState(false)
  const [autoRotate, setAutoRotate] = useState(false)
  const [showHuman, setShowHuman] = useState(true)
  const [fixedScale, setFixedScale] = useState(false)
  const [loading, setLoading] = useState(false)
  const [dimensions, setDimensions] = useState<{ width: number; height: number; depth: number } | null>(null)

  const currentMeshRef = useRef<THREE.Object3D | null>(null)
  const humanRef = useRef<THREE.Group | null>(null)
  const controlsRef = useRef<OrbitControls | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)

  // Crear silueta humana estilizada de 1.75m (1750mm) de referencia
  const createHumanFigure = () => {
    const humanGroup = new THREE.Group()
    humanGroup.name = 'humanReference'
    const mat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      metalness: 0.1,
      roughness: 0.5,
      transparent: true,
      opacity: 0.85,
    })

    const h = 1750.0 // 1.75 metros

    // Cabeza
    const headRadius = h * 0.07
    const headGeo = new THREE.SphereGeometry(headRadius, 16, 16)
    const headMesh = new THREE.Mesh(headGeo, mat)
    headMesh.position.z = h - headRadius
    humanGroup.add(headMesh)

    // Torso y cuello
    const torsoHeight = h * 0.38
    const torsoRadius = h * 0.085
    const torsoGeo = new THREE.CylinderGeometry(torsoRadius * 0.85, torsoRadius, torsoHeight, 16)
    torsoGeo.rotateX(Math.PI / 2)
    const torsoMesh = new THREE.Mesh(torsoGeo, mat)
    torsoMesh.position.z = h * 0.56
    humanGroup.add(torsoMesh)

    // Brazos
    const armHeight = h * 0.35
    const armRadius = h * 0.03
    const armGeo = new THREE.CylinderGeometry(armRadius, armRadius, armHeight, 8)
    armGeo.rotateX(Math.PI / 2)
    const leftArm = new THREE.Mesh(armGeo, mat)
    leftArm.position.set(-torsoRadius * 1.3, 0, h * 0.55)
    humanGroup.add(leftArm)
    const rightArm = new THREE.Mesh(armGeo, mat)
    rightArm.position.set(torsoRadius * 1.3, 0, h * 0.55)
    humanGroup.add(rightArm)

    // Piernas
    const legHeight = h * 0.45
    const legRadius = h * 0.04
    const legGeo = new THREE.CylinderGeometry(legRadius, legRadius, legHeight, 12)
    legGeo.rotateX(Math.PI / 2)
    const leftLeg = new THREE.Mesh(legGeo, mat)
    leftLeg.position.set(-torsoRadius * 0.45, 0, legHeight / 2)
    humanGroup.add(leftLeg)
    const rightLeg = new THREE.Mesh(legGeo, mat)
    rightLeg.position.set(torsoRadius * 0.45, 0, legHeight / 2)
    humanGroup.add(rightLeg)

    return humanGroup
  }

  useEffect(() => {
    const container = mountRef.current
    if (!container) return

    // 1. Escena
    const scene = new THREE.Scene()
    scene.background = new THREE.Color('#070b14')

    // 2. Cámara
    const width = container.clientWidth
    const height = container.clientHeight
    const camera = new THREE.PerspectiveCamera(45, width / height, 1, 1000000)
    camera.position.set(3000, -3500, 2500)
    cameraRef.current = camera

    // 3. Renderizador
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(width, height)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.shadowMap.enabled = true
    container.replaceChildren(renderer.domElement)

    // 4. Controles de órbita
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.autoRotate = autoRotate
    controls.autoRotateSpeed = 2.0
    controlsRef.current = controls

    // 5. Luces
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8)
    scene.add(ambientLight)

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.4)
    dirLight.position.set(6000, 8000, 10000)
    scene.add(dirLight)

    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.6)
    fillLight.position.set(-6000, -4000, -4000)
    scene.add(fillLight)

    let gridHelper: THREE.GridHelper | null = null

    // 6. Carga de Geometría
    const loadGeometry = () => {
      if (currentMeshRef.current) {
        scene.remove(currentMeshRef.current)
        currentMeshRef.current = null
      }
      if (humanRef.current) {
        scene.remove(humanRef.current)
        humanRef.current = null
      }
      if (gridHelper) {
        scene.remove(gridHelper)
        gridHelper = null
      }

      if (geometryHash) {
        setLoading(true)
        const loader = new GLTFLoader()
        const glbUrl = `/api/geometry/${geometryHash}/glb`

        loader.load(
          glbUrl,
          (gltf) => {
            const object = gltf.scene
            object.traverse((child) => {
              if ((child as THREE.Mesh).isMesh) {
                const m = child as THREE.Mesh
                m.material = new THREE.MeshStandardMaterial({
                  color: 0x38bdf8,
                  metalness: 0.25,
                  roughness: 0.4,
                  wireframe: wireframe,
                })
              }
            })

            // Centrar objeto sobre el origen Z=0
            const box = new THREE.Box3().setFromObject(object)
            const center = box.getCenter(new THREE.Vector3())
            const size = box.getSize(new THREE.Vector3())
            setDimensions({
              width: Math.round(size.x),
              height: Math.round(size.y),
              depth: Math.round(size.z),
            })

            const maxDim = Math.max(size.x, size.y, size.z) || 1000

            object.position.x -= center.x
            object.position.y -= center.y
            object.position.z -= box.min.z

            scene.add(object)
            currentMeshRef.current = object

            // Silueta Humana de Referencia (1.75m) al lado
            if (showHuman) {
              const human = createHumanFigure()
              // Colocar a la derecha del modelo a una distancia proporcional
              const offsetSide = Math.max(maxDim * 0.65, 800)
              human.position.set(offsetSide, 0, 0)
              scene.add(human)
              humanRef.current = human
            }

            // Cuadrícula métrica en el suelo
            const gridExtent = Math.max(maxDim * 2.5, 3500)
            gridHelper = new THREE.GridHelper(gridExtent, 24, 0x38bdf8, 0x1e293b)
            gridHelper.rotation.x = Math.PI / 2
            gridHelper.position.z = 0
            scene.add(gridHelper)

            // Posicionamiento de cámara:
            if (fixedScale) {
              // Vista fija para apreciar diferencias reales de tamaño entre modelos
              camera.position.set(3500, -4200, 2800)
              controls.target.set(0, 0, 1000)
            } else {
              // Auto-encuadre proporcional al objeto
              camera.position.set(maxDim * 1.5, -maxDim * 1.8, maxDim * 1.2 + 200)
              controls.target.set(0, 0, maxDim * 0.45)
            }
            controls.update()
            setLoading(false)
          },
          undefined,
          (err) => {
            console.warn('Error al cargar GLB:', err)
            setLoading(false)
          }
        )
      }
    }

    loadGeometry()

    // 7. Bucle de animación
    let animationFrameId: number
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate)
      controls.autoRotate = autoRotate
      controls.update()
      renderer.render(scene, camera)
    }
    animate()

    // 8. Resize
    const handleResize = () => {
      if (!container) return
      const w = container.clientWidth
      const h = container.clientHeight
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      renderer.setSize(w, h)
    }
    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('resize', handleResize)
      renderer.dispose()
    }
  }, [geometryHash, wireframe, autoRotate, showHuman, fixedScale])

  const diameterMm = parameters?.rotor_diameter || dimensions?.width || 0
  const heightMm = parameters?.rotor_height || parameters?.tower_height || dimensions?.depth || 0
  const blades = parameters?.blade_count || 0
  const powerW = metrics?.power_output !== undefined ? metrics.power_output : null
  const massKg = metrics?.rotor_mass !== undefined ? metrics.rotor_mass : null

  return (
    <div style={{ position: 'relative', width: '100%', height: 460, borderRadius: 8, overflow: 'hidden', border: '1px solid #334155', background: '#070b14' }}>
      <div ref={mountRef} style={{ width: '100%', height: '100%' }} />

      {/* Controles superiores izquierda */}
      <div style={{ position: 'absolute', top: 12, left: 12, display: 'flex', gap: 8, zIndex: 10 }}>
        <button
          onClick={() => setWireframe(!wireframe)}
          style={{
            padding: '5px 12px',
            borderRadius: 6,
            background: wireframe ? '#0284c7' : '#1e293b',
            color: '#fff',
            border: '1px solid #475569',
            fontSize: 12,
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          {wireframe ? 'Modo Sólido' : 'Modo Alámbrico'}
        </button>

        <button
          onClick={() => setAutoRotate(!autoRotate)}
          style={{
            padding: '5px 12px',
            borderRadius: 6,
            background: autoRotate ? '#10b981' : '#1e293b',
            color: '#fff',
            border: '1px solid #475569',
            fontSize: 12,
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          {autoRotate ? 'Pausar Rotación' : 'Auto Rotar'}
        </button>

        <button
          onClick={() => setShowHuman(!showHuman)}
          style={{
            padding: '5px 12px',
            borderRadius: 6,
            background: showHuman ? '#d97706' : '#1e293b',
            color: '#fff',
            border: '1px solid #f59e0b',
            fontSize: 12,
            cursor: 'pointer',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: 4,
          }}
          title="Muestra u oculta la silueta humana de 1.75m para comparar el tamaño real"
        >
          🧍 {showHuman ? 'Escala Humana (1.75m)' : 'Ver Escala Humana'}
        </button>

        <button
          onClick={() => setFixedScale(!fixedScale)}
          style={{
            padding: '5px 12px',
            borderRadius: 6,
            background: fixedScale ? '#7c3aed' : '#1e293b',
            color: '#fff',
            border: '1px solid #a855f7',
            fontSize: 12,
            cursor: 'pointer',
            fontWeight: 600,
          }}
          title="Fija la cámara para que modelos pequeños se vean pequeños y modelos grandes se vean grandes"
        >
          🔍 {fixedScale ? 'Escala 1:1 (Fija)' : 'Auto-Enfocar'}
        </button>
      </div>

      {/* HUD de Dimensiones Reales (Superior Derecha) */}
      {dimensions && (
        <div style={{
          position: 'absolute',
          top: 12,
          right: 12,
          background: 'rgba(15, 23, 42, 0.88)',
          border: '1px solid #38bdf8',
          borderRadius: 8,
          padding: '10px 14px',
          color: '#f8fafc',
          fontSize: 11,
          fontFamily: 'monospace',
          backdropFilter: 'blur(4px)',
          zIndex: 10,
          maxWidth: 240,
        }}>
          <div style={{ fontWeight: 700, color: '#38bdf8', marginBottom: 4, fontSize: 12 }}>
            📐 COTAS FÍSICAS REALES {familyId ? `— ${familyId === 'spherical_vawt' ? 'Esférica' : familyId === 'hawt_conventional' ? 'HAWT' : 'Savonius'}` : ''}
          </div>
          <div>Diámetro D: <strong style={{ color: '#fff' }}>{diameterMm} mm ({(diameterMm / 1000).toFixed(2)} m)</strong></div>
          {heightMm > 0 && <div>Altura H: <strong style={{ color: '#fff' }}>{heightMm} mm ({(heightMm / 1000).toFixed(2)} m)</strong></div>}
          {blades > 0 && <div>Palas / Álabes: <strong style={{ color: '#fff' }}>{blades}</strong></div>}
          {powerW !== null && <div>Potencia: <strong style={{ color: '#10b981' }}>{powerW >= 1000 ? `${(powerW / 1000).toFixed(2)} kW` : `${powerW.toFixed(1)} W`}</strong></div>}
          {massKg !== null && <div>Masa Rotor: <strong style={{ color: '#f59e0b' }}>{massKg >= 1000 ? `${(massKg / 1000).toFixed(2)} t` : `${massKg.toFixed(1)} kg`}</strong></div>}
          <div style={{ borderTop: '1px solid #334155', marginTop: 6, paddingTop: 4, color: '#94a3b8', fontSize: 10 }}>
            {diameterMm < 1000 ? 'Rotor compacto (bajo la rodilla humana)' : diameterMm < 2000 ? 'Escala similar a estatura humana' : 'Rotor gigante (supera la altura humana)'}
          </div>
        </div>
      )}

      {loading && (
        <div style={{ position: 'absolute', bottom: 12, left: 12, background: 'rgba(15, 23, 42, 0.85)', padding: '6px 12px', borderRadius: 4, fontSize: 12, color: '#38bdf8' }}>
          Renderizando geometría 3D escalada...
        </div>
      )}

      {geometryHash && (
        <div style={{ position: 'absolute', bottom: 12, right: 12, display: 'flex', gap: 8, zIndex: 10 }}>
          <a
            href={`/api/geometry/${geometryHash}/export/stl`}
            download
            style={{
              padding: '6px 12px',
              borderRadius: 6,
              background: '#0f172a',
              color: '#38bdf8',
              border: '1px solid #38bdf8',
              fontSize: 12,
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            Exportar STL
          </a>
          <a
            href={`/api/geometry/${geometryHash}/export/glb`}
            download
            style={{
              padding: '6px 12px',
              borderRadius: 6,
              background: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              fontSize: 12,
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            Descargar GLB
          </a>
        </div>
      )}
    </div>
  )
}
