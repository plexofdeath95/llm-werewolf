// App shell: routes + top nav (hidden on the full-screen game view).
import { BrowserRouter, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { MusicControls } from './hud/MusicControls'
import { TooltipLayer } from './hud/TooltipLayer'
import { GamePage } from './pages/Game'
import { History } from './pages/History'
import { Lobby } from './pages/Lobby'

function Nav() {
  const loc = useLocation()
  if (loc.pathname.startsWith('/game/')) return null
  return (
    <nav className="topnav">
      <span className="brand">🐺 AI Plays Games</span>
      <NavLink to="/" end>Lobby</NavLink>
      <NavLink to="/history">History</NavLink>
      <span className="spacer" />
      <MusicControls />
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <TooltipLayer />
      <Routes>
        <Route path="/" element={<Lobby />} />
        <Route path="/history" element={<History />} />
        <Route path="/game/:id" element={<GamePage />} />
      </Routes>
    </BrowserRouter>
  )
}
