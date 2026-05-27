import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { MessageSquare, ClipboardCheck, LayoutDashboard } from 'lucide-react'
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
        active ? 'bg-indigo-100 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <Icon size={18} />
      <span className="font-medium">{children}</span>
    </Link>
  )
}

function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AI</span>
            </div>
            <h1 className="text-lg font-semibold text-gray-900">Intervention Guideline Generator</h1>
          </div>
          <nav className="flex items-center gap-2">
            <NavLink to="/" icon={LayoutDashboard}>Dashboard</NavLink>
            <NavLink to="/intake" icon={MessageSquare}>Intake</NavLink>
            <NavLink to="/review" icon={ClipboardCheck}>Review</NavLink>
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
