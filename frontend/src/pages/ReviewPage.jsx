import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Edit3, AlertTriangle, ChevronDown, ChevronUp, Shield, Target, BookOpen, Users } from 'lucide-react'
import { getPendingReviews, getPlan, submitReview, getAuditTrail } from '../api/client'

function ConfidenceBadge({ score }) {
  if (score == null) return null
  const pct = (score * 100).toFixed(0)
  const color = score >= 0.8 ? 'bg-green-100 text-green-700' : score >= 0.6 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>{pct}% confidence</span>
}

function Section({ title, icon: Icon, confidence, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border border-gray-200 rounded-lg mb-3">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50">
        <div className="flex items-center gap-3">
          {Icon && <Icon size={16} className="text-teal-600" />}
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
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Shield className="text-teal-600" size={28} />
          Clinician Review Dashboard
        </h2>
        <p className="text-gray-500 mt-1">Review and approve AI-generated intervention plans before they reach families</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <h3 className="font-semibold text-gray-700 mb-3">Plans Awaiting Review ({queue.length})</h3>
            {queue.length === 0 && <p className="text-gray-400 text-sm">No intervention plans pending review. New plans will appear here after the AI pipeline completes.</p>}
            {queue.map((item, i) => (
              <button
                key={i}
                onClick={() => selectCase(item)}
                className={`w-full text-left p-3 rounded-lg mb-2 border transition-colors ${
                  selectedPlan?.case_id === item.case_id ? 'border-teal-300 bg-teal-50' : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="font-medium text-sm text-teal-700">{item.case_id}</div>
                <div className="text-xs text-gray-500 mt-1">Child: {item.child_id}</div>
                <div className="text-xs text-gray-400 mt-0.5">
                  {item.domain_count} domain{item.domain_count !== 1 ? 's' : ''} · {item.goal_count} goal{item.goal_count !== 1 ? 's' : ''}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="col-span-8">
          {!selectedPlan && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
              <Shield className="text-gray-300 mx-auto mb-3" size={40} />
              <p className="text-gray-400">Select a child's intervention plan from the queue to review</p>
              <p className="text-gray-300 text-sm mt-1">Every AI-generated plan requires clinician approval before delivery to families</p>
            </div>
          )}

          {selectedPlan && submitted && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
              <CheckCircle className="text-green-600 mx-auto mb-3" size={32} />
              <h3 className="text-lg font-semibold text-green-800">Review Submitted Successfully</h3>
              <p className="text-green-600 mt-1">The intervention plan status has been updated. Select another case to continue reviewing.</p>
            </div>
          )}

          {selectedPlan && !submitted && (
            <div className="space-y-4">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Intervention Plan: {selectedPlan.plan_id || selectedPlan.case_id}</h3>
                    <p className="text-sm text-gray-500 mt-0.5">Child: {selectedPlan.child_id || 'N/A'}</p>
                  </div>
                  <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium">Awaiting Clinician Approval</span>
                </div>

                {selectedPlan.bias_check_result?.concerns?.length > 0 && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4 flex items-start gap-2">
                    <AlertTriangle className="text-amber-600 flex-shrink-0 mt-0.5" size={16} />
                    <div>
                      <p className="font-medium text-amber-800 text-sm">Bias Concerns Detected by AI</p>
                      <p className="text-amber-600 text-xs mt-0.5">The bias monitoring agent flagged the following concerns for your review:</p>
                      {selectedPlan.bias_check_result.concerns.map((c, i) => (
                        <p key={i} className="text-amber-700 text-xs mt-1">- {c.concern || c.bias_type}: {c.recommendation || ''}</p>
                      ))}
                    </div>
                  </div>
                )}

                <Section title="Developmental Domain Priorities" icon={Target} defaultOpen>
                  <p className="text-xs text-gray-500 mt-2 mb-3">Domains prioritized based on the child's assessment data, developmental stage, and interdependencies.</p>
                  <div className="space-y-2">
                    {(selectedPlan.domain_priorities || []).map((dp, i) => (
                      <div key={i} className="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                            dp.priority_level === 'high' ? 'bg-red-500' : dp.priority_level === 'moderate' ? 'bg-amber-500' : 'bg-blue-500'
                          }`}>{i + 1}</span>
                          <span className="text-sm font-medium text-gray-800">{dp.domain}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500 capitalize">{dp.priority_level} priority</span>
                          <ConfidenceBadge score={dp.confidence_score} />
                        </div>
                      </div>
                    ))}
                  </div>
                </Section>

                <Section title="Intervention Guidelines" icon={BookOpen}>
                  <p className="text-xs text-gray-500 mt-2 mb-3">Evidence-based intervention approaches personalized to this child's profile.</p>
                  <div className="space-y-3">
                    {(selectedPlan.guidelines || []).map((g, i) => (
                      <div key={i} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-sm text-gray-800">{g.domain}</span>
                          <ConfidenceBadge score={g.confidence_score} />
                        </div>
                        {g.evidence_based_approaches?.length > 0 && (
                          <p className="text-xs text-teal-700 font-medium mt-1">
                            Approaches: {g.evidence_based_approaches.join(', ')}
                          </p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          Intensity: {g.intervention_intensity || 'N/A'} · Frequency: {g.recommended_frequency || 'N/A'} · Modality: {g.recommended_modality || 'N/A'}
                        </p>
                        {g.home_activities?.length > 0 && (
                          <p className="text-xs text-gray-400 mt-1">Home activities: {g.home_activities.join(', ')}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </Section>

                <Section title="SMART Developmental Goals" icon={Target}>
                  <p className="text-xs text-gray-500 mt-2 mb-3">Specific, Measurable, Achievable, Relevant, and Time-bound goals for the child.</p>
                  <div className="space-y-3">
                    {(selectedPlan.smart_goals || []).map((goal, i) => (
                      <div key={i} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-teal-600 bg-teal-50 px-2 py-0.5 rounded">{goal.domain}</span>
                          <span className="text-xs text-gray-400">{goal.sub_domain}</span>
                          <span className="text-xs text-gray-300 capitalize">{goal.goal_type?.replace('_', '-')}</span>
                        </div>
                        <p className="text-sm text-gray-800">{goal.goal_text}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
                            <div className="bg-gray-400 h-2 rounded-full absolute" style={{ width: `${goal.baseline_percent || 0}%` }} />
                            <div className="bg-teal-500 h-2 rounded-full absolute opacity-30" style={{ width: `${goal.target_percent || 0}%` }} />
                          </div>
                          <span className="text-xs text-gray-500">{goal.baseline_percent}% baseline → {goal.target_percent}% target</span>
                        </div>
                        {goal.weeks_duration && (
                          <p className="text-xs text-gray-400 mt-1">Duration: {goal.weeks_duration} weeks · Measurement: {goal.measurement_method || 'N/A'}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </Section>

                <Section title="Parent & Caregiver Guidance" icon={Users}>
                  <p className="text-xs text-gray-500 mt-2 mb-3">Plain-language activities and strategies for parents to support their child at home.</p>
                  <div className="mt-2">
                    {selectedPlan.caregiver_guidance?.strength_based_encouragement && (
                      <div className="p-3 bg-teal-50 rounded-lg mb-3 border border-teal-100">
                        <p className="text-xs font-medium text-teal-700 mb-1">What Your Child Does Well</p>
                        <p className="text-sm text-teal-800">{selectedPlan.caregiver_guidance.strength_based_encouragement}</p>
                      </div>
                    )}

                    {selectedPlan.caregiver_guidance?.activities?.map((a, i) => (
                      <div key={i} className="p-2.5 border-b border-gray-100 last:border-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-xs font-medium text-teal-600">{a.domain}</span>
                          <span className={`text-xs px-1.5 py-0.5 rounded ${
                            a.difficulty === 'beginner' ? 'bg-green-100 text-green-600' :
                            a.difficulty === 'intermediate' ? 'bg-amber-100 text-amber-600' :
                            'bg-red-100 text-red-600'
                          }`}>{a.difficulty}</span>
                        </div>
                        <p className="text-sm text-gray-800">{a.activity}</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          When: {a.daily_routine_link} · Time: ~{a.estimated_time_minutes} min
                          {a.materials_needed && a.materials_needed !== 'mock_materials_needed' ? ` · Materials: ${a.materials_needed}` : ''}
                        </p>
                      </div>
                    ))}

                    {selectedPlan.caregiver_guidance?.general_strategies?.length > 0 && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                        <p className="text-xs font-medium text-blue-700 mb-1">General Strategies for Parents</p>
                        <ul className="text-xs text-blue-600 space-y-1">
                          {selectedPlan.caregiver_guidance.general_strategies.map((s, i) => (
                            <li key={i}>- {s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {selectedPlan.caregiver_guidance?.progress_tracking_tips?.length > 0 && (
                      <div className="mt-2 p-3 bg-purple-50 rounded-lg border border-purple-100">
                        <p className="text-xs font-medium text-purple-700 mb-1">Tracking Your Child's Progress</p>
                        <ul className="text-xs text-purple-600 space-y-1">
                          {selectedPlan.caregiver_guidance.progress_tracking_tips.map((s, i) => (
                            <li key={i}>- {s}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Section>

                <Section title="Governance & Audit Trail" icon={Shield}>
                  <p className="text-xs text-gray-500 mt-2 mb-3">Every AI agent decision is immutably logged with timestamps and confidence scores.</p>
                  <div className="mt-2 max-h-48 overflow-y-auto">
                    {audit.map((evt, i) => (
                      <div key={i} className="flex items-center gap-3 py-1.5 border-b border-gray-100 last:border-0">
                        <span className="text-xs text-gray-400 w-20 flex-shrink-0 font-mono">{evt.timestamp?.split('T')[1]?.split('.')[0]}</span>
                        <span className="text-xs font-medium text-teal-700 w-36 flex-shrink-0">{evt.agent_id}</span>
                        <span className="text-xs text-gray-500 flex-1">{evt.action}</span>
                        {evt.confidence_score != null && (
                          <ConfidenceBadge score={evt.confidence_score} />
                        )}
                      </div>
                    ))}
                  </div>
                </Section>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <h4 className="font-semibold text-gray-700 mb-1">Clinician Review Decision</h4>
                <p className="text-xs text-gray-400 mb-3">As the reviewing clinician, you are the final authority. No plan reaches the family without your approval.</p>
                <textarea
                  value={reviewNotes}
                  onChange={e => setReviewNotes(e.target.value)}
                  placeholder="Add clinical notes, modifications, or reasoning for your decision..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm mb-4 h-20 resize-none focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                />
                <div className="flex gap-3">
                  <button onClick={() => handleReview('approved')} disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium text-sm">
                    <CheckCircle size={16} /> Approve Plan
                  </button>
                  <button onClick={() => handleReview('modified')} disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium text-sm">
                    <Edit3 size={16} /> Modify & Approve
                  </button>
                  <button onClick={() => handleReview('rejected')} disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 font-medium text-sm">
                    <XCircle size={16} /> Reject Plan
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
