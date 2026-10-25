// Day/night lighting that eases between moods; stars + fog at night.
import { Stars } from '@react-three/drei'
import { useFrame, useThree } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

const DAY = { bg: '#2a1d14', fog: '#2a1d14', sun: '#ffd7a1', sunI: 1.6, amb: 0.55, hemi: '#ffe9c9' }
const NIGHT = { bg: '#070b1d', fog: '#0a1230', sun: '#7f9dff', sunI: 0.55, amb: 0.18, hemi: '#5a6fb0' }

const tmp = new THREE.Color()

export function Lighting({ night }: { night: boolean }) {
  const scene = useThree((s) => s.scene)
  const sun = useRef<THREE.DirectionalLight>(null)
  const amb = useRef<THREE.AmbientLight>(null)
  const hemi = useRef<THREE.HemisphereLight>(null)

  useFrame((_, dt) => {
    const t = night ? NIGHT : DAY
    const k = Math.min(1, dt * 1.6)
    if (!(scene.background instanceof THREE.Color)) scene.background = new THREE.Color(t.bg)
    ;(scene.background as THREE.Color).lerp(tmp.set(t.bg), k)
    if (!scene.fog) scene.fog = new THREE.Fog(t.fog, 9, 26)
    const fog = scene.fog as THREE.Fog
    fog.color.lerp(tmp.set(t.fog), k)
    fog.near += ((night ? 7 : 11) - fog.near) * k
    if (sun.current) {
      sun.current.color.lerp(tmp.set(t.sun), k)
      sun.current.intensity += (t.sunI - sun.current.intensity) * k
    }
    if (amb.current) amb.current.intensity += (t.amb - amb.current.intensity) * k
    if (hemi.current) hemi.current.color.lerp(tmp.set(t.hemi), k)
  })

  return (
    <>
      <ambientLight ref={amb} intensity={0.5} />
      <hemisphereLight ref={hemi} args={['#ffe9c9', '#2b1a10', 0.45]} />
      <directionalLight
        ref={sun}
        position={[6, 10, 4]}
        intensity={1.5}
        castShadow
        shadow-mapSize={[1024, 1024]}
        shadow-camera-left={-8}
        shadow-camera-right={8}
        shadow-camera-top={8}
        shadow-camera-bottom={-8}
      />
      {night && <Stars radius={40} depth={20} count={1800} factor={3} fade speed={0.6} />}
    </>
  )
}
