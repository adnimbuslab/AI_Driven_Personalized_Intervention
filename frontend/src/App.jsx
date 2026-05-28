import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { FileText, ClipboardCheck, LayoutDashboard } from 'lucide-react'
import IntakePage from './pages/IntakePage'
import ReviewPage from './pages/ReviewPage'
import DashboardPage from './pages/DashboardPage'

function NavLink({ to, icon: Icon, children }) {
  const location = useLocation()
  const active = location.pathname === to
  return (
    <Link
      to={to}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
        active ? 'bg-teal-100 text-teal-700' : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <Icon size={18} />
      <span className="font-medium">{children}</span>
    </Link>
  )
}

function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-3 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-teal-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AIG</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900 leading-tight">Autism Intervention Guideline Generator</h1>
              <p className="text-xs text-gray-400">AI-Driven Personalized Intervention Planning</p>
            </div>
          </div>
          <nav className="flex items-center gap-2">
            <NavLink to="/" icon={LayoutDashboard}>Dashboard</NavLink>
            <NavLink to="/intake" icon={FileText}>New Child</NavLink>
            <NavLink to="/review" icon={ClipboardCheck}>Clinician Review</NavLink>
          </nav>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/intake" element={<IntakePage />} />
          <Route path="/review" element={<ReviewPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
