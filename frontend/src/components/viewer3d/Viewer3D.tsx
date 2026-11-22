import React, { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

interface Viewer3DProps {
  geometryHash?: string
  parameters?: Record<string, any>
  metrics?: Record<string, number>
  familyId?: string
  scanId?: string
}

export const Viewer3D: React.FC<Viewer3DProps> = ({ geometryHash, parameters, metrics, familyId, scanId }) => {
  const mountRef = useRef<HTMLDivElement>(null)
  const isTrauma = familyId?.includes('cutting_guide') || false
  const [wireframe, setWireframe] = useState(false)
  const [autoRotate, setAutoRotate] = useState(false)
  const [showHuman, setShowHuman] = useState(!isTrauma)
  const [showAssembly, setShowAssembly] = useState(true)
  const [loading, setLoading] = useState(false)
  const [dimensions, setDimensions] = useState<{ width: number; height: number; depth: number } | null>(null)

  const currentMeshRef = useRef<THREE.Object3D | null>(null)
  const ghostBoneRef = useRef<THREE.Object3D | null>(null)
  const humanRef = useRef<THREE.Group | null>(null)
  const controlsRef = useRef<OrbitControls | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)
  const targetCenterRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 0, 35))
  const optimalDistRef = useRef<number>(150)

  // Función para enfocar, hacer zoom y centrar el objeto en el medio
  const handleFocusAndCenter = () => {
    const camera = cameraRef.current
    const controls = controlsRef.current
    if (!camera || !controls) return

    const mesh = currentMeshRef.current
    if (mesh) {
      const box = new THREE.Box3().setFromObject(mesh)
      const center = box.getCenter(new THREE.Vector3())
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z) || (isTrauma ? 80 : 1000)

      // Guardar el centro y distancia calculados
      targetCenterRef.current.copy(center)
      const fovRad = THREE.MathUtils.degToRad(camera.fov)
      const dist = (maxDim / 2) / Math.tan(fovRad / 2) * 1.55
      optimalDistRef.current = dist

      // Configurar el objetivo de órbita exactamente en el centro de la pieza
      controls.target.copy(center)

      // Colocar cámara con encuadre óptimo (~70% de la pantalla)
      camera.position.set(center.x + dist * 0.75, center.y - dist * 1.05, center.z + dist * 0.65)
      camera.near = Math.max(0.5, dist * 0.01)
      camera.far = Math.max(10000, dist * 50)
      camera.updateProjectionMatrix()
      controls.update()
    } else {
      controls.target.set(0, 0, 35)
      camera.position.set(110, -140, 90)
      camera.updateProjectionMatrix()
      controls.update()
    }
  }

  // Actualizar autoRotate de forma reactiva sin destruir la escena
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = autoRotate
    }
  }, [autoRotate])

  // Actualizar modo alámbrico de forma reactiva sin destruir la escena
  useEffect(() => {
    if (currentMeshRef.current) {
      currentMeshRef.current.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          const m = child as THREE.Mesh
          if (m.material && (m.material as THREE.MeshStandardMaterial).wireframe !== undefined) {
            (m.material as THREE.MeshStandardMaterial).wireframe = wireframe
          }
        }
      })
    }
  }, [wireframe])

  // Actualizar visibilidad de la figura humana reactivamente
  useEffect(() => {
    if (humanRef.current) {
      humanRef.current.visible = showHuman
    }
  }, [showHuman])

  // Actualizar visibilidad del hueso fantasma en modo ensamblaje
  useEffect(() => {
    if (ghostBoneRef.current) {
      ghostBoneRef.current.visible = showAssembly
    }
  }, [showAssembly])

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

    // 2. Cámara (Z como eje vertical superior)
    const width = container.clientWidth
    const height = container.clientHeight
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.5, 1000000)
    camera.up.set(0, 0, 1) // Eje Z vertical para instrumental y CAD
    camera.position.set(120, -150, 100)
    cameraRef.current = camera

    // 3. Renderizador
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(width, height)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.shadowMap.enabled = true
    container.replaceChildren(renderer.domElement)

    // 4. Controles de órbita (giran alrededor del target central de la pieza)
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.08
    controls.autoRotate = autoRotate
    controls.autoRotateSpeed = 2.5
    controlsRef.current = controls

    // 5. Luces
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85)
    scene.add(ambientLight)

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.4)
    dirLight.position.set(6000, 8000, 10000)
    scene.add(dirLight)

    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.7)
    fillLight.position.set(-6000, -4000, -4000)
    scene.add(fillLight)

    let gridHelper: THREE.GridHelper | null = null

    // 6. Carga de Geometría
    const loadGeometry = () => {
      if (currentMeshRef.current) {
        scene.remove(currentMeshRef.current)
        currentMeshRef.current = null
      }
      if (ghostBoneRef.current) {
        scene.remove(ghostBoneRef.current)
        ghostBoneRef.current = null
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
                  color: isTrauma ? 0x38bdf8 : 0x0284c7,
                  metalness: 0.25,
                  roughness: 0.35,
                  wireframe: wireframe,
                })
              }
            })

            // Centrar objeto sobre el origen X=0, Y=0 y base Z=0
            const box = new THREE.Box3().setFromObject(object)
            const center = box.getCenter(new THREE.Vector3())
            const size = box.getSize(new THREE.Vector3())
            setDimensions({
              width: Math.round(size.x),
              height: Math.round(size.y),
              depth: Math.round(size.z),
            })

            const maxDim = Math.max(size.x, size.y, size.z) || (isTrauma ? 80 : 1000)

            // Centrar geométricamente para que el pivote sea el origen
            object.position.x -= center.x
            object.position.y -= center.y
            object.position.z -= box.min.z

            scene.add(object)
            currentMeshRef.current = object

            // Centro geométrico vertical del objeto
            const targetZ = size.z / 2
            targetCenterRef.current.set(0, 0, targetZ)

            // Silueta humana solo en eólica si está activada
            if (showHuman && !isTrauma) {
              const human = createHumanFigure()
              const offsetSide = Math.max(maxDim * 0.65, 800)
              human.position.set(offsetSide, 0, 0)
              scene.add(human)
              humanRef.current = human
            }

            // Cuadrícula métrica proporcional (en Traumatología cuadrícula de ~14 cm con pasos de 1 cm)
            const gridExtent = isTrauma ? Math.max(maxDim * 2.2, 140) : Math.max(maxDim * 2.5, 3500)
            const gridDivisions = isTrauma ? 14 : 24
            gridHelper = new THREE.GridHelper(gridExtent, gridDivisions, isTrauma ? 0x10b981 : 0x38bdf8, 0x1e293b)
            gridHelper.rotation.x = Math.PI / 2
            gridHelper.position.z = 0
            scene.add(gridHelper)

            // Posicionamiento de cámara óptimo centrado con zoom directo
            const fovRad = THREE.MathUtils.degToRad(camera.fov)
            const dist = (maxDim / 2) / Math.tan(fovRad / 2) * 1.55
            optimalDistRef.current = dist

            camera.position.set(dist * 0.75, -dist * 1.05, targetZ + dist * 0.65)
            camera.near = Math.max(0.5, dist * 0.01)
            camera.far = Math.max(10000, dist * 50)
            camera.updateProjectionMatrix()

            // Fijar el objetivo de rotación exactamente en el centro de la pieza
            controls.target.set(0, 0, targetZ)
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

      // Carga del Hueso del Paciente en modo Ensamblaje Quirúrgico ("Ghost Bone")
      if (isTrauma && scanId) {
        const boneLoader = new GLTFLoader()
        boneLoader.load(
          `/api/traumatology/scan/${scanId}/glb`,
          (boneGltf) => {
            const boneObj = boneGltf.scene
            boneObj.traverse((child) => {
              if ((child as THREE.Mesh).isMesh) {
                const m = child as THREE.Mesh
                m.material = new THREE.MeshStandardMaterial({
                  color: 0xf5f0e1, // Tono marfil anatómico óseo
                  metalness: 0.05,
                  roughness: 0.85,
                  transparent: true,
                  opacity: 0.45,
                  depthWrite: false,
                })
              }
            })

            const boneBox = new THREE.Box3().setFromObject(boneObj)
            const boneCenter = boneBox.getCenter(new THREE.Vector3())

            // Centrar hueso en XY para que coapte con el origen donde asienta la guía de corte
            boneObj.position.x -= boneCenter.x
            boneObj.position.y -= boneCenter.y
            // Alinear el cóndilo / platillo con el asiento anatómico de la guía (Z ~ 2-4 mm)
            boneObj.position.z -= (boneBox.min.z - 3.0)

            boneObj.visible = showAssembly
            scene.add(boneObj)
            ghostBoneRef.current = boneObj
          },
          undefined,
          (err) => {
            console.warn('GLB de hueso para ensamblaje no disponible:', err)
          }
        )
      }
    }

    loadGeometry()

    // 7. Bucle de animación (usa controls.update() para autoRotate suave)
    let animationFrameId: number
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate)
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
  }, [geometryHash, familyId, scanId])

  const diameterMm = parameters?.rotor_diameter || dimensions?.width || 0
  const heightMm = parameters?.rotor_height || parameters?.tower_height || dimensions?.depth || 0
  const blades = parameters?.blade_count || 0
  const powerW = metrics?.power_output !== undefined ? metrics.power_output : null
  const massKg = metrics?.rotor_mass !== undefined ? metrics.rotor_mass : null

  return (
    <div style={{ position: 'relative', width: '100%', height: 460, borderRadius: 8, overflow: 'hidden', border: '1px solid #334155', background: '#070b14' }}>
      <div ref={mountRef} style={{ width: '100%', height: '100%' }} />

      {/* Controles superiores izquierda */}
      <div style={{ position: 'absolute', top: 12, left: 12, display: 'flex', gap: 8, zIndex: 10, flexWrap: 'wrap' }}>
        <button
          onClick={handleFocusAndCenter}
          style={{
            padding: '6px 14px',
            borderRadius: 6,
            background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            color: '#fff',
            border: '1px solid #38bdf8',
            fontSize: 12,
            cursor: 'pointer',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            boxShadow: '0 2px 8px rgba(2, 132, 199, 0.45)',
          }}
          title="Centra la pieza 3D en el medio de la pantalla, hace zoom óptimo y alinea el eje de rotación sobre su centro"
        >
          🎯 Enfocar y Centrar
        </button>

        <button
          onClick={() => setAutoRotate(!autoRotate)}
          style={{
            padding: '6px 14px',
            borderRadius: 6,
            background: autoRotate ? '#10b981' : '#1e293b',
            color: '#fff',
            border: autoRotate ? '1px solid #34d399' : '1px solid #475569',
            fontSize: 12,
            cursor: 'pointer',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
          title="Hace rotar el modelo suavemente 360° sobre su propio eje central"
        >
          🔄 {autoRotate ? 'Pausar Rotación' : 'Auto Rotar'}
        </button>

        <button
          onClick={() => setWireframe(!wireframe)}
          style={{
            padding: '6px 12px',
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

        {isTrauma && (
          <button
            onClick={() => setShowAssembly(!showAssembly)}
            style={{
              padding: '6px 12px',
              borderRadius: 6,
              background: showAssembly ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : '#1e293b',
              color: '#fff',
              border: showAssembly ? '1px solid #34d399' : '1px solid #475569',
              fontSize: 12,
              cursor: 'pointer',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              boxShadow: showAssembly ? '0 2px 8px rgba(16, 185, 129, 0.4)' : 'none',
            }}
            title="Alterna entre visualizar la guía quirúrgica en solitario o acoplada en ensamblaje sobre el hueso translúcido del paciente"
          >
            {showAssembly ? '🦴 Ensamblaje Quirúrgico' : '👁️ Solo Guía'}
          </button>
        )}

        {!isTrauma && (
          <button
            onClick={() => setShowHuman(!showHuman)}
            style={{
              padding: '6px 12px',
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
        )}
      </div>

      {/* HUD de Dimensiones Reales (Superior Derecha) */}
      {dimensions && (
        <div style={{
          position: 'absolute',
          top: 12,
          right: 12,
          background: 'rgba(15, 23, 42, 0.92)',
          border: isTrauma ? '1px solid #10b981' : '1px solid #38bdf8',
          borderRadius: 8,
          padding: '10px 14px',
          color: '#f8fafc',
          fontSize: 11,
          fontFamily: 'monospace',
          backdropFilter: 'blur(4px)',
          zIndex: 10,
          maxWidth: 260,
        }}>
          {isTrauma ? (
            <>
              <div style={{ fontWeight: 700, color: '#10b981', marginBottom: 2, fontSize: 12 }}>
                🩺 GUÍA PSI DE CORTE (INSTRUMENTAL IMPRESO EN 3D)
              </div>
              <div style={{ color: '#38bdf8', fontWeight: 600, marginBottom: 4, fontSize: 11 }}>
                {familyId === 'distal_femur_cutting_guide' ? 'Guía Fémur Distal (Ranura Valgo + 2 Torres de Agujas)' : 'Guía Tibia Proximal (Ranura Slope + 2 Torres de Agujas)'}
              </div>
              <div style={{ fontSize: 10, color: '#cbd5e1', marginBottom: 6, background: 'rgba(15,23,42,0.7)', padding: '4px 6px', borderRadius: 4, border: '1px solid #334155', lineHeight: 1.3 }}>
                ℹ️ <strong>Instrumental Quirúrgico:</strong> Esta pieza es la <em>guía física de resina</em> que se esteriliza y ancla al hueso. Los 2 cilindros son las <strong>torres de fijación</strong> para agujas Kirschner de 3.2 mm (no son cóndilos óseos).
              </div>
              <div>Cotas Totales: <strong style={{ color: '#fff' }}>{dimensions.width.toFixed(0)} × {dimensions.depth.toFixed(0)} × {dimensions.height.toFixed(0)} mm</strong></div>
              {parameters?.valgus_angle_deg !== undefined && (
                <div>Ángulo Valgo: <strong style={{ color: '#38bdf8' }}>{parameters.valgus_angle_deg}°</strong></div>
              )}
              {parameters?.posterior_slope_deg !== undefined && (
                <div>Slope Posterior: <strong style={{ color: '#38bdf8' }}>{parameters.posterior_slope_deg}°</strong></div>
              )}
              {parameters?.resection_thickness_mm !== undefined && (
                <div>Resección: <strong style={{ color: '#fff' }}>{parameters.resection_thickness_mm} mm</strong></div>
              )}
              {metrics?.slot_deflection_mm !== undefined && (
                <div>Deflexión Sierra: <strong style={{ color: metrics.slot_deflection_mm < 0.1 ? '#10b981' : '#f43f5e' }}>{metrics.slot_deflection_mm.toFixed(3)} mm</strong></div>
              )}
              {metrics?.material_cost_eur !== undefined && (
                <div>Coste Resina: <strong style={{ color: '#f59e0b' }}>~{metrics.material_cost_eur.toFixed(2)} €</strong> ({metrics.resin_volume_ml?.toFixed(0)} ml)</div>
              )}
              <div style={{ borderTop: '1px solid #334155', marginTop: 6, paddingTop: 4, color: '#94a3b8', fontSize: 10 }}>
                Biocompatible ISO 10993 | Autoclave 121 °C
              </div>
            </>
          ) : (
            <>
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
            </>
          )}
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
