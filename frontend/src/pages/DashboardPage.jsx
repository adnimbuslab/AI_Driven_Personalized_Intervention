import { useState, useEffect } from 'react'
import { FileText, Clock, CheckCircle, XCircle, AlertTriangle, RefreshCw, Baby, Shield, Target, Users } from 'lucide-react'
import { listCases, getPendingReviews } from '../api/client'
import { Link } from 'react-router-dom'

const STATUS_CONFIG = {
  approved: { icon: CheckCircle, color: 'text-green-600 bg-green-50', label: 'Approved' },
  rejected: { icon: XCircle, color: 'text-red-600 bg-red-50', label: 'Rejected' },
  pending_review: { icon: Clock, color: 'text-amber-600 bg-amber-50', label: 'Awaiting Review' },
  initiated: { icon: FileText, color: 'text-blue-600 bg-blue-50', label: 'In Progress' },
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
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Baby className="text-teal-600" size={28} />
            Intervention Planning Dashboard
          </h2>
          <p className="text-gray-500 mt-1">Overview of all children's intervention plans across the pipeline</p>
        </div>
        <div className="flex gap-3">
          <button onClick={refresh} disabled={loading} className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
          <Link to="/intake" className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 font-medium text-sm">
            + New Child Assessment
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Baby className="text-teal-500" size={18} />
            <p className="text-sm text-gray-500">Total Children</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{cases.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="text-amber-500" size={18} />
            <p className="text-sm text-gray-500">Awaiting Clinician Review</p>
          </div>
          <p className="text-2xl font-bold text-amber-600">{pendingCount}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="text-green-500" size={18} />
            <p className="text-sm text-gray-500">Plans Approved</p>
          </div>
          <p className="text-2xl font-bold text-green-600">
            {cases.filter(c => c.status === 'approved').length}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Users className="text-blue-500" size={18} />
            <p className="text-sm text-gray-500">Delivered to Families</p>
          </div>
          <p className="text-2xl font-bold text-blue-600">
            {cases.filter(c => c.status === 'approved').length}
          </p>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        {['all', 'pending_review', 'approved', 'rejected', 'initiated'].map(s => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === s ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {s === 'all' ? 'All Children' : STATUS_CONFIG[s]?.label || s}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Case ID</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Child ID</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Plan Status</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Domains</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Goals</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-12">
                  <Baby className="text-gray-300 mx-auto mb-3" size={32} />
                  <p className="text-gray-400">No children found. Start a new assessment to create an intervention plan.</p>
                </td>
              </tr>
            )}
            {filtered.map((c, i) => (
              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-teal-600">{c.case_id || c.plan_id}</td>
                <td className="px-4 py-3 text-sm text-gray-700">{c.child_id || '--'}</td>
                <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                <td className="px-4 py-3 text-sm text-gray-500">{c.domain_count || '--'}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{c.goal_count || '--'}</td>
                <td className="px-4 py-3 text-sm text-gray-400">{c.created_at?.split('T')[0] || '--'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
