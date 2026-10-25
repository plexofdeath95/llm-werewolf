// The 3D game room: tavern, round table, seated avatars, night arcs, camera.
import { ContactShadows } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import type { LiveThought } from '../hooks/useGameSocket'
import { isNight } from '../state/selectors'
import type { GameView } from '../state/viewTypes'
import { Arcs } from './Arcs'
import { CameraRig } from './CameraRig'
import { createRenderer } from './createRenderer'
import { Lighting } from './Lighting'
import { Room } from './Room'
import { Seat } from './Seat'
import { Table } from './Table'

export interface GameSceneProps {
  view: GameView
  god: boolean
  thinking: Set<string>
  live: Record<string, LiveThought>
  follow: boolean
  orbit: boolean
  selected?: string
  onSelect: (pid: string) => void
}

export function GameScene(p: GameSceneProps) {
  const { view } = p
  const night = isNight(view.phase)
  const speaker = view.speaker ? view.players[view.speaker] : undefined
  return (
    <Canvas shadows camera={{ position: [0, 9.2, 9.6], fov: 46 }} dpr={[1, 2]} gl={createRenderer}
      onPointerMissed={() => p.onSelect('')}>
      <Lighting night={night} />
      <Room night={night} />
      <Table night={night} />
      <ContactShadows position={[0, 0.015, 0]} opacity={0.45} scale={14} blur={2.4} far={3} />
      {view.order.map((pid) => {
        const player = view.players[pid]
        return (
          <Seat key={pid} view={view} player={player} god={p.god}
            thinking={p.thinking.has(pid)} live={p.live[pid]}
            selected={p.selected === pid} onSelect={p.onSelect} />
        )
      })}
      <Arcs view={view} god={p.god} />
      <CameraRig focusSeat={speaker?.seat} count={view.order.length}
        follow={p.follow} orbit={p.orbit} night={night} />
    </Canvas>
  )
}
