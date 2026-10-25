// The tavern: plank floor, round walls, beams, fireplace, barrels and glowing windows.
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

const WOOD = '#5b3a22'
const WALL = '#3e2718'

function Fireplace() {
  const light = useRef<THREE.PointLight>(null)
  useFrame(({ clock }) => {
    if (light.current) light.current.intensity = 7 + Math.sin(clock.elapsedTime * 9) * 1.2
  })
  return (
    <group position={[0, 0, -8.2]}>
      <mesh position={[0, 1.2, 0]} castShadow>
        <boxGeometry args={[3, 2.4, 0.8]} />
        <meshStandardMaterial color="#5c5550" flatShading />
      </mesh>
      <mesh position={[0, 0.7, 0.42]}>
        <boxGeometry args={[1.6, 1, 0.1]} />
        <meshStandardMaterial color="#ff7a1a" emissive="#ff5a00" emissiveIntensity={2.2} />
      </mesh>
      <pointLight ref={light} position={[0, 1, 1.2]} color="#ff8a3a" distance={14} decay={1.6} />
    </group>
  )
}

function Barrel({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={position} castShadow>
      <cylinderGeometry args={[0.45, 0.45, 1.1, 10]} />
      <meshStandardMaterial color="#6e4526" flatShading />
    </mesh>
  )
}

function Window({ angle, night }: { angle: number; night: boolean }) {
  const r = 8.9
  return (
    <mesh position={[Math.cos(angle) * r, 2.6, Math.sin(angle) * r]} rotation={[0, -angle - Math.PI / 2, 0]}>
      <planeGeometry args={[1.4, 1.8]} />
      <meshStandardMaterial
        color={night ? '#1b2a66' : '#ffe2a8'}
        emissive={night ? '#3550c8' : '#ffcf7a'}
        emissiveIntensity={night ? 0.8 : 1.1}
        side={THREE.DoubleSide}
      />
    </mesh>
  )
}

export function Room({ night }: { night: boolean }) {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <circleGeometry args={[9.2, 48]} />
        <meshStandardMaterial color={WOOD} roughness={0.9} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]} receiveShadow>
        <circleGeometry args={[4.4, 40]} />
        <meshStandardMaterial color="#6d1f2a" roughness={1} />
      </mesh>
      <mesh position={[0, 2.5, 0]}>
        <cylinderGeometry args={[9.2, 9.2, 5, 32, 1, true]} />
        <meshStandardMaterial color={WALL} side={THREE.BackSide} flatShading />
      </mesh>
      {[0, 1, 2, 3].map((i) => (
        <mesh key={i} position={[0, 4.6, 0]} rotation={[0, (i * Math.PI) / 4, 0]}>
          <boxGeometry args={[18, 0.25, 0.3]} />
          <meshStandardMaterial color="#2c1a0f" />
        </mesh>
      ))}
      {[0.6, 2.2, 3.9, 5.4].map((a) => <Window key={a} angle={a} night={night} />)}
      <Fireplace />
      <Barrel position={[6.8, 0.55, -4.5]} />
      <Barrel position={[7.4, 0.55, -3.3]} />
      <Barrel position={[-7, 0.55, -4]} />
    </group>
  )
}
