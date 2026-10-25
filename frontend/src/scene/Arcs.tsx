// Night action arcs: animated dashed curves from actor to target, colored by action class.
import { QuadraticBezierLine } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import { classColor } from '../lib/colors'
import { midpoint, seatPosition, type Vec3 } from '../lib/seats'
import type { Arc, GameView } from '../state/viewTypes'

function ArcLine({ arc, from, to }: { arc: Arc; from: Vec3; to: Vec3 }) {
  // drei's Line2 ref; dashOffset animation makes the arc "flow" toward the target.
  const ref = useRef<{ material: { dashOffset: number } } | null>(null)
  useFrame((_, dt) => {
    if (ref.current) ref.current.material.dashOffset -= dt * 1.5
  })
  const color = classColor(arc.cls)
  return (
    <group>
      <QuadraticBezierLine
        ref={ref as never}
        start={from}
        end={to}
        mid={midpoint(from, to, 2.4)}
        color={color}
        lineWidth={3}
        dashed
        dashScale={4}
        dashSize={0.6}
        gapSize={0.35}
        transparent
        opacity={0.9}
      />
      <mesh position={to}>
        <sphereGeometry args={[0.12, 12, 8]} />
        <meshBasicMaterial color={color} />
      </mesh>
    </group>
  )
}

export function Arcs({ view, god }: { view: GameView; god: boolean }) {
  const count = view.order.length
  const lift = (p: Vec3): Vec3 => [p[0], 1.9, p[2]]
  return (
    <group>
      {view.arcs
        .filter((a) => god || !a.private)
        .map((a) => {
          const from = view.players[a.from]
          const to = view.players[a.to]
          if (!from || !to) return null
          return (
            <ArcLine key={`${a.seq}-${a.to}`} arc={a}
              from={lift(seatPosition(from.seat, count))}
              to={lift(seatPosition(to.seat, count))} />
          )
        })}
    </group>
  )
}
