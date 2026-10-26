// A procedural low-poly player: stool, body tinted by model color, head, eyes, hat.
// Speaking -> bounce + glow; thinking -> head tilt; dying -> topples over, then rises as a ghost.
import { useFrame } from '@react-three/fiber'
import { useEffect, useRef, useState, type ReactNode } from 'react'
import * as THREE from 'three'
import { hashSeed } from '../lib/seats'
import { Hat } from './Hat'

const SKINS = ['#f1c9a5', '#d9a77c', '#a8714a', '#7a4e2d', '#ffd9b8', '#c68c5f']
const TOPPLE_MS = 1300

export interface AvatarProps {
  id: string
  color: string
  alive: boolean
  speaking: boolean
  thinking: boolean
  wolfEyes: boolean // god view at night: the pack's eyes glow red
  dim?: boolean // someone else is on a night walk: fade into the background
  onSelect: () => void
  children?: ReactNode // floor rings + Html overlays (name tag, bubbles)
}

export function Avatar(p: AvatarProps) {
  const seed = hashSeed(p.id)
  const body = useRef<THREE.Group>(null)
  const head = useRef<THREE.Group>(null)
  // Already dead when we mount (replay seek) -> straight to ghost; dying now -> topple first.
  const [ghost, setGhost] = useState(!p.alive)
  const fallAt = useRef<number | null>(null)
  useEffect(() => {
    if (p.alive) { setGhost(false); fallAt.current = null; return }
    if (ghost) return
    fallAt.current = performance.now()
    const t = setTimeout(() => setGhost(true), TOPPLE_MS)
    return () => clearTimeout(t)
  }, [p.alive]) // eslint-disable-line react-hooks/exhaustive-deps

  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime + (seed % 100)
    const falling = !p.alive && !ghost && fallAt.current !== null
    if (body.current) {
      const target = ghost ? 0.35 + Math.sin(t * 1.5) * 0.12 : p.speaking ? Math.abs(Math.sin(t * 9)) * 0.08 : 0
      body.current.position.y += (target - body.current.position.y) * Math.min(1, dt * 10)
      const k = falling ? Math.min(1, (performance.now() - fallAt.current!) / (TOPPLE_MS * 0.6)) : 0
      body.current.rotation.x = falling ? -1.35 * k * k : body.current.rotation.x * 0.85
    }
    if (head.current) {
      head.current.rotation.z = p.thinking ? Math.sin(t * 2.2) * 0.18 : head.current.rotation.z * 0.9
      head.current.rotation.x = p.speaking ? Math.sin(t * 7) * 0.08 : 0
    }
  })

  const mat = (color: string) => (
    <meshStandardMaterial color={ghost ? '#cfe3ff' : color} flatShading
      transparent={ghost || p.dim} opacity={ghost ? 0.32 : p.dim ? 0.3 : 1}
      emissive={p.speaking ? color : '#000000'} emissiveIntensity={p.speaking ? 0.35 : 0} />
  )
  const eyes = p.wolfEyes && !ghost
  return (
    <group onClick={(e) => { e.stopPropagation(); p.onSelect() }}>
      {!ghost && (
        <mesh position={[0, 0.25, -0.15]} castShadow>
          <cylinderGeometry args={[0.32, 0.36, 0.5, 8]} />
          <meshStandardMaterial color="#4a2e1a" flatShading />
        </mesh>
      )}
      <group ref={body}>
        <mesh position={[0, 0.95, 0]} castShadow={!ghost}>
          <capsuleGeometry args={[0.3, 0.5, 4, 10]} />
          {mat(p.color)}
        </mesh>
        <group ref={head} position={[0, 1.62, 0]}>
          <mesh castShadow={!ghost}>
            <sphereGeometry args={[0.3, 14, 10]} />
            {mat(SKINS[seed % SKINS.length])}
          </mesh>
          {[-0.1, 0.1].map((x) => (
            <mesh key={x} position={[x, 0.04, 0.27]}>
              <sphereGeometry args={[eyes ? 0.055 : 0.045, 8, 6]} />
              <meshStandardMaterial color={ghost ? '#6a8bd6' : eyes ? '#ff2a2a' : '#1a1a1a'}
                emissive={eyes ? '#ff1a1a' : '#000000'} emissiveIntensity={eyes ? 3 : 0}
                transparent={ghost} opacity={ghost ? 0.5 : 1} />
            </mesh>
          ))}
          {!ghost && <Hat variant={seed % 97} />}
        </group>
      </group>
      {p.children}
    </group>
  )
}
