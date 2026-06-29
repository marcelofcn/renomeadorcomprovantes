import { NavLink, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'

const activeClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'nav-link active' : 'nav-link'

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <span className="brand">Renomeador de Comprovantes</span>
          <p className="subtitle">Processamento simples de arquivos e navegação rápida</p>
        </div>
        <nav className="navigation">
          <NavLink to="/" className={activeClass} end>
            Dashboard
          </NavLink>
          <NavLink to="/upload" className={activeClass}>
            Upload
          </NavLink>
        </nav>
      </header>

      <main className="app-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
