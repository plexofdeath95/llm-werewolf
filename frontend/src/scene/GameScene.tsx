// The 3D game room: tavern, round table, seated avatars, and their houses for the night walk.
import { ContactShadows } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { isNight } from '../state/selectors'
import type { Walk } from '../hooks/useNightWalks'
import type { GameView } from '../state/viewTypes'
import { CameraRig } from './CameraRig'
import { createRenderer } from './createRenderer'
import { Houses } from './House'
import { Lighting } from './Lighting'
import { Room } from './Room'
import { Seat } from './Seat'
import { Table } from './Table'

export interface GameSceneProps {
  view: GameView
  god: boolean
  thinking: Set<string>
  follow: boolean
  orbit: boolean
  charsPerSecond: number // speech bubble typewriter speed
  walks: Record<string, Walk> // god view night walks in progress
  selected?: string
  onSelect: (pid: string) => void
}

export function GameScene(p: GameSceneProps) {
  const { view } = p
  const night = isNight(view.phase)
  const speaker = view.speaker ? view.players[view.speaker] : undefined
  const walking = Object.values(p.walks).some((w) => w.movement !== 'none')
  return (
    <Canvas shadows camera={{ position: [0, 9.2, 9.6], fov: 46 }} dpr={[1, 2]} gl={createRenderer}
      onPointerMissed={() => p.onSelect('')}>
      <Lighting night={night} />
      <Room night={night} />
      <Table night={night} />
      <ContactShadows position={[0, 0.015, 0]} opacity={0.45} scale={14} blur={2.4} far={3} />
      <Houses view={view} />
      {view.order.map((pid) => (
        <Seat key={pid} view={view} player={view.players[pid]} god={p.god}
          thinking={p.thinking.has(pid)} selected={p.selected === pid}
          charsPerSecond={p.charsPerSecond} walk={p.walks[pid]} walking={walking} onSelect={p.onSelect} />
      ))}
      <CameraRig focusSeat={speaker?.seat} count={view.order.length}
        follow={p.follow} orbit={p.orbit} wide={night || view.phase === 'dawn'} />
    </Canvas>
  )
}
