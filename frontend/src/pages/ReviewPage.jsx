import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Edit3, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'
import { getPendingReviews, getPlan, submitReview, getAuditTrail } from '../api/client'

function ConfidenceBadge({ score }) {
  if (score == null) return null
  const pct = (score * 100).toFixed(0)
  const color = score >= 0.8 ? 'bg-green-100 text-green-700' : score >= 0.6 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>{pct}%</span>
}

function Section({ title, confidence, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border border-gray-200 rounded-lg mb-3">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50">
        <div className="flex items-center gap-3">
          <h4 className="font-semibold text-gray-900">{title}</h4>
          <ConfidenceBadge score={confidence} />
        </div>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      {open && <div className="px-4 pb-4 border-t border-gray-100">{children}</div>}
    </div>
  )
}

export default function ReviewPage() {
  const [queue, setQueue] = useState([])
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [audit, setAudit] = useState([])
  const [reviewNotes, setReviewNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => { loadQueue() }, [])

  const loadQueue = async () => {
    try {
      const resp = await getPendingReviews()
      setQueue(resp.data.pending_reviews || [])
    } catch (err) {
      console.error('Failed to load queue', err)
    }
  }

  const selectCase = async (item) => {
    setLoading(true)
    setSubmitted(false)
    try {
      const [planResp, auditResp] = await Promise.all([
        getPlan(item.case_id),
        getAuditTrail(item.case_id),
      ])
      setSelectedPlan({ ...planResp.data, case_id: item.case_id })
      setAudit(auditResp.data.events || [])
    } catch (err) {
      console.error('Failed to load plan', err)
    }
    setLoading(false)
  }

  const handleReview = async (action) => {
    if (!selectedPlan) return
    setLoading(true)
    try {
      await submitReview(selectedPlan.case_id, {
        action,
        reviewer_id: 'CLN-REVIEWER-001',
        plan_id: selectedPlan.plan_id,
        notes: reviewNotes,
      })
      setSubmitted(true)
      loadQueue()
    } catch (err) {
      console.error('Review failed', err)
    }
    setLoading(false)
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Clinician Review Dashboard</h2>

      <div className="grid grid-cols-12 gap-6">
        {/* Queue */}
        <div className="col-span-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="font-semibold text-gray-700 mb-3">Pending Reviews ({queue.length})</h3>
            {queue.length === 0 && <p className="text-gray-400 text-sm">No pending reviews</p>}
            {queue.map((item, i) => (
              <button
                key={i}
                onClick={() => selectCase(item)}
                className={`w-full text-left p-3 rounded-lg mb-2 border transition-colors ${
                  selectedPlan?.case_id === item.case_id ? 'border-indigo-300 bg-indigo-50' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="font-medium text-sm">{item.case_id}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {item.domain_count} domains · {item.goal_count} goals
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Plan Review */}
        <div className="col-span-8">
          {!selectedPlan && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
              <p className="text-gray-400">Select a case from the queue to review</p>
            </div>
          )}

          {selectedPlan && submitted && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
              <CheckCircle className="text-green-600 mx-auto mb-3" size={32} />
              <h3 className="text-lg font-semibold text-green-800">Review Submitted</h3>
              <p className="text-green-600 mt-1">Select another case to continue reviewing.</p>
            </div>
          )}

          {selectedPlan && !submitted && (
            <div className="space-y-4">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Plan: {selectedPlan.plan_id || selectedPlan.case_id}</h3>
                  <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">Pending Review</span>
                </div>

                {selectedPlan.bias_check_result?.concerns?.length > 0 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4 flex items-start gap-2">
                    <AlertTriangle className="text-yellow-600 flex-shrink-0 mt-0.5" size={16} />
                    <div>
                      <p className="font-medium text-yellow-800 text-sm">Bias Concerns Flagged</p>
                      {selectedPlan.bias_check_result.concerns.map((c, i) => (
                        <p key={i} className="text-yellow-700 text-xs mt-1">{c.concern || c.bias_type}</p>
                      ))}
                    </div>
                  </div>
                )}

                <Section title="Domain Priorities" defaultOpen>
                  <div className="mt-3 space-y-2">
                    {(selectedPlan.domain_priorities || []).map((dp, i) => (
                      <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm font-medium">{dp.domain}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">{dp.priority_level}</span>
                          <ConfidenceBadge score={dp.confidence_score} />
                        </div>
                      </div>
                    ))}
                  </div>
                </Section>

                <Section title="Intervention Guidelines">
                  <div className="mt-3 space-y-3">
                    {(selectedPlan.guidelines || []).map((g, i) => (
                      <div key={i} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-sm">{g.domain}</span>
                          <ConfidenceBadge score={g.confidence_score} />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {g.evidence_based_approaches?.join(', ')}
                        </p>
                        <p className="text-xs text-gray-500">
                          Frequency: {g.recommended_frequency} · {g.recommended_modality}
                        </p>
                      </div>
                    ))}
                  </div>
                </Section>

                <Section title="SMART Goals">
                  <div className="mt-3 space-y-3">
                    {(selectedPlan.smart_goals || []).map((goal, i) => (
                      <div key={i} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-indigo-600">{goal.domain}</span>
                          <span className="text-xs text-gray-400">{goal.sub_domain}</span>
                        </div>
                        <p className="text-sm text-gray-800">{goal.goal_text}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${goal.baseline_percent || 0}%` }} />
                          </div>
                          <span className="text-xs text-gray-500">{goal.baseline_percent}% → {goal.target_percent}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Section>

                <Section title="Caregiver Guidance">
                  <div className="mt-3">
                    {selectedPlan.caregiver_guidance?.activities?.map((a, i) => (
                      <div key={i} className="p-2 border-b border-gray-100 last:border-0">
                        <span className="text-xs font-medium text-indigo-600">{a.domain}</span>
                        <p className="text-sm text-gray-800 mt-0.5">{a.activity}</p>
                        <p className="text-xs text-gray-400">{a.daily_routine_link} · {a.estimated_time_minutes} min</p>
                      </div>
                    ))}
                    {selectedPlan.caregiver_guidance?.general_strategies?.length > 0 && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs font-medium text-blue-700 mb-1">General Strategies</p>
                        <ul className="text-xs text-blue-600 space-y-1">
                          {selectedPlan.caregiver_guidance.general_strategies.map((s, i) => (
                            <li key={i}>• {s}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Section>

                <Section title="Audit Trail">
                  <div className="mt-3 max-h-48 overflow-y-auto">
                    {audit.map((evt, i) => (
                      <div key={i} className="flex items-center gap-3 py-1.5 border-b border-gray-100 last:border-0">
                        <span className="text-xs text-gray-400 w-20 flex-shrink-0">{evt.timestamp?.split('T')[1]?.split('.')[0]}</span>
                        <span className="text-xs font-medium text-gray-600 w-32 flex-shrink-0">{evt.agent_id}</span>
                        <span className="text-xs text-gray-500">{evt.action}</span>
                      </div>
                    ))}
                  </div>
                </Section>
              </div>

              {/* Review Actions */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <h4 className="font-semibold text-gray-700 mb-3">Review Decision</h4>
                <textarea
                  value={reviewNotes}
                  onChange={e => setReviewNotes(e.target.value)}
                  placeholder="Add review notes (optional)..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm mb-4 h-20 resize-none"
                />
                <div className="flex gap-3">
                  <button onClick={() => handleReview('approved')} disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50">
                    <CheckCircle size={16} /> Approve
                  </button>
                  <button onClick={() => handleReview('modified')} disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                    <Edit3 size={16} /> Modify & Approve
                  </button>
                  <button onClick={() => handleReview('rejected')} disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
                    <XCircle size={16} /> Reject
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
