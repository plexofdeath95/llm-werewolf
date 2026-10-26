// Floor rings under an avatar: speaking/selected, urgency (god view).
import { urgencyColor } from '../lib/colors'

export interface RingsProps {
  color: string
  alive: boolean
  speaking: boolean
  selected: boolean
  urgency?: number
}

function Ring({ inner, outer, color, opacity, y, scale = 1 }: {
  inner: number; outer: number; color: string; opacity: number; y: number; scale?: number
}) {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, y, 0]} scale={scale}>
      <ringGeometry args={[inner, outer, 36]} />
      <meshBasicMaterial color={color} transparent opacity={opacity} />
    </mesh>
  )
}

export function Rings(p: RingsProps) {
  if (!p.alive) return null
  return (
    <group>
      {(p.speaking || p.selected) && (
        <Ring inner={0.55} outer={0.7} color={p.selected ? '#ffffff' : p.color} opacity={0.8} y={0.03} />
      )}
      {p.urgency !== undefined && (
        <Ring inner={0.75} outer={0.82} color={urgencyColor(p.urgency)} opacity={0.85} y={0.02}
          scale={0.6 + p.urgency * 0.06} />
      )}
    </group>
  )
}
