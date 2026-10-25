// Camera: eases across the table to face whoever speaks, or free orbit.
import { OrbitControls } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo } from 'react'
import * as THREE from 'three'
import { seatPosition } from '../lib/seats'

export interface CameraRigProps {
  focusSeat?: number
  count: number
  follow: boolean
  orbit: boolean
  night: boolean
}

const lookAt = new THREE.Vector3(0, 0.9, 0)

export function CameraRig({ focusSeat, count, follow, orbit, night }: CameraRigProps) {
  const goal = useMemo(() => {
    if (!follow || focusSeat === undefined || count === 0) {
      return { pos: new THREE.Vector3(0, night ? 8.5 : 7, night ? 8.5 : 9.5), look: new THREE.Vector3(0, 0.8, 0) }
    }
    const [x, , z] = seatPosition(focusSeat, count)
    const dir = new THREE.Vector3(x, 0, z).normalize()
    // Stand across the table from the speaker, a bit above eye level.
    const pos = dir.clone().multiplyScalar(-4.3).add(new THREE.Vector3(0, 3.4, 0))
    return { pos, look: new THREE.Vector3(x, 1.5, z) }
  }, [focusSeat, count, follow, night])

  useFrame(({ camera }, dt) => {
    if (orbit) return
    const k = Math.min(1, dt * 1.4)
    camera.position.lerp(goal.pos, k)
    lookAt.lerp(goal.look, k)
    camera.lookAt(lookAt)
  })

  return orbit ? <OrbitControls target={[0, 0.9, 0]} maxPolarAngle={Math.PI / 2.1} minDistance={4} maxDistance={16} /> : null
}
