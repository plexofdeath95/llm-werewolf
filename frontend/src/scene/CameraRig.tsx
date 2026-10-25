// Camera: a steady overview of the whole table. "Follow" only nudges the gaze toward the
// speaker (the camera itself never moves), so labels stay put and stay clickable.
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

const HOME = new THREE.Vector3(0, 9.2, 9.6)
const CENTER = new THREE.Vector3(0, 0.4, 0)
const NUDGE = 0.18 // fraction of the way toward the speaker the gaze may drift
const lookAt = CENTER.clone()

export function CameraRig({ focusSeat, count, follow, orbit }: CameraRigProps) {
  const look = useMemo(() => {
    if (!follow || focusSeat === undefined || count === 0) return CENTER
    const [x, , z] = seatPosition(focusSeat, count)
    return CENTER.clone().lerp(new THREE.Vector3(x, 0.8, z), NUDGE)
  }, [focusSeat, count, follow])

  useFrame(({ camera }, dt) => {
    if (orbit) return
    const k = Math.min(1, dt * 1.2)
    camera.position.lerp(HOME, k)
    lookAt.lerp(look, k)
    camera.lookAt(lookAt)
  })

  return orbit ? <OrbitControls target={[0, 0.6, 0]} maxPolarAngle={Math.PI / 2.1} minDistance={6} maxDistance={18} /> : null
}
