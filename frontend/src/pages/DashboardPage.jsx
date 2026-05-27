import { useState, useEffect } from 'react'
import { FileText, Clock, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react'
import { listCases, getPendingReviews } from '../api/client'
import { Link } from 'react-router-dom'

const STATUS_CONFIG = {
  approved: { icon: CheckCircle, color: 'text-green-600 bg-green-50', label: 'Approved' },
  rejected: { icon: XCircle, color: 'text-red-600 bg-red-50', label: 'Rejected' },
  pending_review: { icon: Clock, color: 'text-yellow-600 bg-yellow-50', label: 'Pending Review' },
  initiated: { icon: FileText, color: 'text-blue-600 bg-blue-50', label: 'Initiated' },
  unknown: { icon: AlertTriangle, color: 'text-gray-600 bg-gray-50', label: 'Unknown' },
}

function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.unknown
  const Icon = config.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${config.color}`}>
      <Icon size={12} /> {config.label}
    </span>
  )
}

export default function DashboardPage() {
  const [cases, setCases] = useState([])
  const [pendingCount, setPendingCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState('all')

  const refresh = async () => {
    setLoading(true)
    try {
      const [casesResp, pendingResp] = await Promise.all([
        listCases(),
        getPendingReviews(),
      ])
      const caseList = casesResp.data.cases || casesResp.data.pending_reviews || []
      setCases(caseList)
      setPendingCount(pendingResp.data.total || 0)
    } catch {
      setCases([])
    }
    setLoading(false)
  }

  useEffect(() => { refresh() }, [])

  const filtered = statusFilter === 'all' ? cases : cases.filter(c => c.status === statusFilter)

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Case Dashboard</h2>
          <p className="text-gray-500 mt-1">Overview of all intervention planning cases</p>
        </div>
        <div className="flex gap-3">
          <button onClick={refresh} disabled={loading} className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
          <Link to="/intake" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium">
            + New Case
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Total Cases</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{cases.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Pending Review</p>
          <p className="text-2xl font-bold text-yellow-600 mt-1">{pendingCount}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Approved</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {cases.filter(c => c.status === 'approved').length}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Rejected</p>
          <p className="text-2xl font-bold text-red-600 mt-1">
            {cases.filter(c => c.status === 'rejected').length}
          </p>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {['all', 'pending_review', 'approved', 'rejected', 'initiated'].map(s => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === s ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {s === 'all' ? 'All' : STATUS_CONFIG[s]?.label || s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Case ID</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Child ID</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Domains</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Goals</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={6} className="text-center py-12 text-gray-400">No cases found. Create a new case to get started.</td></tr>
            )}
            {filtered.map((c, i) => (
              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-indigo-600">{c.case_id || c.plan_id}</td>
                <td className="px-4 py-3 text-sm text-gray-700">{c.child_id || '—'}</td>
                <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                <td className="px-4 py-3 text-sm text-gray-500">{c.domain_count || '—'}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{c.goal_count || '—'}</td>
                <td className="px-4 py-3 text-sm text-gray-400">{c.created_at?.split('T')[0] || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
