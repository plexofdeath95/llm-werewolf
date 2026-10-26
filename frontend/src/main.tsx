import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles/theme.css'
import './styles/lobby.css'
import './styles/hud.css'
import './styles/bubbles.css'
import './styles/stats.css'
import './styles/insight.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
