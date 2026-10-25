// Procedural hats/accessories: cheap variety so every seat is recognisable.
const HAT_COLORS = ['#3b2a6b', '#1f1f24', '#b8322f', '#d9a520', '#2f6b3b', '#5a3a1e']

export const HAT_COUNT = 6

export function Hat({ variant, color }: { variant: number; color?: string }) {
  const c = color ?? HAT_COLORS[variant % HAT_COLORS.length]
  const mat = <meshStandardMaterial color={c} flatShading />
  switch (variant % HAT_COUNT) {
    case 0: // wizard
      return (
        <group position={[0, 0.28, 0]} rotation={[0.15, 0, 0.1]}>
          <mesh castShadow><coneGeometry args={[0.3, 0.7, 10]} />{mat}</mesh>
          <mesh position={[0, -0.32, 0]}><cylinderGeometry args={[0.42, 0.42, 0.04, 16]} />{mat}</mesh>
        </group>
      )
    case 1: // top hat
      return (
        <group position={[0, 0.3, 0]}>
          <mesh castShadow><cylinderGeometry args={[0.22, 0.22, 0.38, 14]} />{mat}</mesh>
          <mesh position={[0, -0.18, 0]}><cylinderGeometry args={[0.36, 0.36, 0.04, 16]} />{mat}</mesh>
          <mesh position={[0, -0.1, 0]}><cylinderGeometry args={[0.225, 0.225, 0.07, 14]} />
            <meshStandardMaterial color="#c9a227" /></mesh>
        </group>
      )
    case 2: // beanie with pompom
      return (
        <group position={[0, 0.12, 0]}>
          <mesh castShadow><sphereGeometry args={[0.31, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2]} />{mat}</mesh>
          <mesh position={[0, 0.33, 0]}><sphereGeometry args={[0.09, 8, 6]} />
            <meshStandardMaterial color="#f2efe6" /></mesh>
        </group>
      )
    case 3: // crown
      return (
        <group position={[0, 0.3, 0]}>
          <mesh><cylinderGeometry args={[0.24, 0.24, 0.16, 10, 1, true]} />
            <meshStandardMaterial color="#e6b422" metalness={0.6} roughness={0.3} side={2} /></mesh>
          {[0, 1, 2, 3, 4].map((i) => (
            <mesh key={i} position={[Math.cos(i * 1.256) * 0.24, 0.12, Math.sin(i * 1.256) * 0.24]}>
              <coneGeometry args={[0.04, 0.12, 4]} /><meshStandardMaterial color="#e6b422" />
            </mesh>
          ))}
        </group>
      )
    case 4: // wide-brim hat
      return (
        <group position={[0, 0.24, 0]} rotation={[-0.1, 0, 0]}>
          <mesh castShadow><cylinderGeometry args={[0.2, 0.26, 0.22, 12]} />{mat}</mesh>
          <mesh position={[0, -0.1, 0]}><cylinderGeometry args={[0.5, 0.5, 0.03, 18]} />{mat}</mesh>
        </group>
      )
    default: // headband with feather
      return (
        <group position={[0, 0.08, 0]}>
          <mesh rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[0.3, 0.035, 6, 20]} />{mat}</mesh>
          <mesh position={[0.22, 0.25, -0.1]} rotation={[0, 0, -0.4]}>
            <coneGeometry args={[0.05, 0.45, 5]} /><meshStandardMaterial color="#f2c14e" />
          </mesh>
        </group>
      )
  }
}
