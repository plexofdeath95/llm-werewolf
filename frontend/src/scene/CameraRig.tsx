// Camera: an overview framed to fit the whole ring (seats by day, houses by night) inside the
// part of the screen the HUD leaves free. It gently pans to whoever is speaking: drifts a
// little toward them and turns its gaze, never leaving the overview, never swinging wildly.
import { OrbitControls } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { cameraHold } from '../lib/cameraHold'
import { DAY_RING, frame, NIGHT_RING } from '../lib/framing'
import { seatPosition } from '../lib/seats'

export interface CameraRigProps {
  focusSeat?: number
  count: number
  follow: boolean
  orbit: boolean
  wide: boolean // night: frame the houses too
}

const DIR = new THREE.Vector3(0, 9.2, 9.6).normalize()
const DIR_NIGHT = new THREE.Vector3(0, 10, 7.2).normalize() // steeper: the house ring fits closer
const CENTER = new THREE.Vector3(0, 0.4, 0)
const DOLLY = 0.16 // how far the camera drifts toward the speaker
const GAZE = 0.5 // how far the look target pans from the table centre to the speaker
const EASE = 1.6 // pans settle in ~1.5s, then the view holds still
const at = CENTER.clone()
const goal = new THREE.Vector3()
const look = new THREE.Vector3()

export function CameraRig({ focusSeat, count, follow, orbit, wide }: CameraRigProps) {
  useFrame(({ camera, size }, dt) => {
    if (orbit || cameraHold.on) return
    const fov = (camera as THREE.PerspectiveCamera).fov ?? 46
    const dir = wide ? DIR_NIGHT : DIR
    const f = frame(wide ? NIGHT_RING : DAY_RING, [dir.x, dir.y, dir.z], fov, size.width, size.height)
    goal.copy(dir).multiplyScalar(f.distance).add(new THREE.Vector3(0, 0, f.lookZ))
    look.set(CENTER.x, CENTER.y, CENTER.z + f.lookZ)
    if (follow && focusSeat !== undefined && count > 0 && !wide) {
      const [x, , z] = seatPosition(focusSeat, count)
      goal.add(new THREE.Vector3(x, 0, z).multiplyScalar(DOLLY))
      look.lerp(new THREE.Vector3(x, 1.4, z), GAZE * 0.6)
    }
    const k = Math.min(1, dt * EASE)
    camera.position.lerp(goal, k)
    at.lerp(look, k)
    camera.lookAt(at)
  })
  return orbit ? <OrbitControls target={[0, 0.6, 0]} maxPolarAngle={Math.PI / 2.1} minDistance={6} maxDistance={30} /> : null
}
