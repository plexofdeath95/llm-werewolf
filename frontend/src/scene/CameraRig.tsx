// Camera: overview of the whole table that gently pans to whoever is speaking: it eases a
// little toward the speaker and turns its gaze to them, but never leaves the overview spot,
// so the whole table stays in view and nothing swings wildly.
import { OrbitControls } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo } from 'react'
import * as THREE from 'three'
import { cameraHold } from '../lib/cameraHold'
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
const DOLLY = 0.16 // how far the camera drifts toward the speaker
const GAZE = 0.5   // how far the look target pans from the table centre to the speaker
const EASE = 1.6   // pans settle in ~1.5s, then the view holds still
const at = CENTER.clone()

export function CameraRig({ focusSeat, count, follow, orbit }: CameraRigProps) {
  const goal = useMemo(() => {
    if (!follow || focusSeat === undefined || count === 0) return { pos: HOME, look: CENTER }
    const [x, , z] = seatPosition(focusSeat, count)
    const speaker = new THREE.Vector3(x, 1.4, z)
    return {
      pos: HOME.clone().add(new THREE.Vector3(x, 0, z).multiplyScalar(DOLLY)),
      look: CENTER.clone().lerp(speaker, GAZE),
    }
  }, [focusSeat, count, follow])

  useFrame(({ camera }, dt) => {
    if (orbit || cameraHold.on) return
    const k = Math.min(1, dt * EASE)
    camera.position.lerp(goal.pos, k)
    at.lerp(goal.look, k)
    camera.lookAt(at)
  })

  return orbit ? <OrbitControls target={[0, 0.6, 0]} maxPolarAngle={Math.PI / 2.1} minDistance={6} maxDistance={18} /> : null
}
