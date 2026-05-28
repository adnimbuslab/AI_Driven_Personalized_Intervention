import { useState, useRef, useEffect } from 'react'
import { Send, Upload, Loader2, CheckCircle2, AlertCircle, Baby, Heart } from 'lucide-react'
import { createCase, sendChatMessage, startWorkflow } from '../api/client'
import WorkflowProgress from '../components/shared/WorkflowProgress'

const WORKFLOW_STEPS = [
  'Consent', 'Data Collection', 'Quality Check', 'Child Profile',
  'Domain Priorities', 'Confidence Gate', 'Domain Analysis',
  'Intervention Plan', 'Bias Review', 'SMART Goals',
  'Milestones', 'Parent Guide', 'Clinician Review',
]

const FIELD_CONFIG = {
  age_years: { label: "Child's Age (years)", placeholder: 'e.g., 4', group: 'child' },
  age_months: { label: "Age (months)", placeholder: 'e.g., 6', group: 'child' },
  gender: { label: "Gender", placeholder: 'e.g., Male', group: 'child' },
  support_level: { label: "ASD Support Level (DSM-5)", placeholder: 'Level 1, 2, or 3', group: 'child' },
  screening_tool: { label: "Screening Tool Used", placeholder: 'e.g., ADOS-2, M-CHAT-R', group: 'assessment' },
  primary_domain: { label: "Primary Domain of Concern", placeholder: 'e.g., Communication', group: 'assessment' },
  secondary_domain: { label: "Secondary Domain", placeholder: 'e.g., Social Interaction', group: 'assessment' },
  ados2_social_affect: { label: "ADOS-2 Social Affect Score", placeholder: 'e.g., 12', group: 'assessment' },
  ados2_rrb: { label: "ADOS-2 RRB Score", placeholder: 'e.g., 4', group: 'assessment' },
  home_language: { label: "Home Language", placeholder: 'e.g., English, Spanish', group: 'family' },
  strength_domains: { label: "Child's Strengths", placeholder: 'e.g., Visual learning, Music', group: 'family' },
  gap_domains: { label: "Areas Needing Support", placeholder: 'e.g., Expressive language', group: 'family' },
  family_priorities: { label: "Family's Priorities", placeholder: 'What matters most to the family?', group: 'family' },
  current_services: { label: "Current Therapies/Services", placeholder: 'e.g., Speech therapy 2x/week', group: 'family' },
}

export default function IntakePage() {
  const [caseId, setCaseId] = useState(null)
  const [childId, setChildId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [workflowStep, setWorkflowStep] = useState(-1)
  const [workflowStatus, setWorkflowStatus] = useState(null)
  const [consentGiven, setConsentGiven] = useState(false)
  const [showInputForm, setShowInputForm] = useState(false)
  const [inputData, setInputData] = useState(
    Object.fromEntries(Object.keys(FIELD_CONFIG).map(k => [k, '']))
  )
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (role, content) => {
    setMessages(prev => [...prev, { role, content, time: new Date().toLocaleTimeString() }])
  }

  const handleNewCase = async () => {
    setLoading(true)
    try {
      const resp = await createCase({ reporter_id: 'CLN-001', consent_status: 'PENDING' })
      const data = resp.data
      setCaseId(data.case_id)
      setChildId(data.child_id)
      addMessage('system', `Case ${data.case_id} created for a new child.\n\nBefore we begin, we need to confirm that informed consent has been obtained from the child's parent or legal guardian for data processing and intervention planning.\n\nDoes the authorized reporter have proper consent?`)
    } catch (err) {
      addMessage('system', `Error creating case: ${err.message}`)
    }
    setLoading(false)
  }

  const handleConsent = () => {
    setConsentGiven(true)
    setWorkflowStep(0)
    addMessage('system', 'Consent verified. Thank you.\n\nPlease enter the child\'s screening and assessment data below. This information will be used by our AI agents to build a personalized intervention plan.\n\nInclude as much detail as possible -- the more complete the data, the better the plan.')
    setShowInputForm(true)
  }

  const handleConsentDenied = () => {
    addMessage('system', 'Consent was not granted. The intervention planning workflow cannot proceed without informed consent from the child\'s parent or legal guardian.\n\nThis is required to comply with ethical guidelines for processing sensitive clinical data.')
  }

  const handleInputSubmit = async () => {
    const structured = {}
    for (const [key, val] of Object.entries(inputData)) {
      if (val) {
        if (['age_years', 'age_months', 'ados2_social_affect', 'ados2_rrb'].includes(key)) {
          structured[key] = parseFloat(val)
        } else {
          structured[key] = val
        }
      }
    }

    setShowInputForm(false)
    addMessage('user', 'Submitted screening and assessment data for the child.')
    addMessage('system', 'Data received. Starting the multi-agent intervention planning pipeline...\n\nOur 12 AI agents will now:\n1. Validate data quality\n2. Build a strength-based child profile\n3. Prioritize developmental domains\n4. Generate personalized intervention guidelines\n5. Create SMART goals and milestones\n6. Prepare parent-friendly guidance\n\nThis may take a moment...')
    setLoading(true)

    try {
      const resp = await startWorkflow(caseId, {
        child_id: childId,
        reporter_id: 'CLN-001',
        consent_status: 'GRANTED',
        structured_inputs: structured,
      })
      const data = resp.data
      setWorkflowStatus(data.workflow_status)

      if (data.error) {
        addMessage('system', `The workflow encountered an issue: ${data.error}\n\nThe case has been escalated for clinician review.`)
      } else if (data.workflow_status === 'AWAITING_CLINICIAN_REVIEW') {
        setWorkflowStep(12)
        addMessage('system', `Personalized intervention plan generated successfully!\n\nPlan ID: ${data.plan_id}\n\nThe plan includes:\n- Intervention guidelines with evidence-based approaches\n- SMART developmental goals\n- Short-term and long-term milestones\n- Parent-friendly home activity guide\n\nThe plan is now awaiting clinician review before it can be shared with the family. Go to the Clinician Review page to review and approve.`)
      } else if (data.workflow_status === 'ABSTAINED') {
        addMessage('system', 'The system determined that confidence levels are too low to generate a reliable plan. The case has been flagged for manual clinician review.')
      } else {
        addMessage('system', `Workflow completed with status: ${data.workflow_status}`)
      }
    } catch (err) {
      addMessage('system', `Workflow error: ${err.response?.data?.error || err.message}`)
    }
    setLoading(false)
  }

  const handleSendMessage = async () => {
    if (!input.trim() || !caseId) return
    const msg = input.trim()
    setInput('')
    addMessage('user', msg)
    setLoading(true)

    try {
      const resp = await sendChatMessage(caseId, msg)
      addMessage('system', resp.data.response?.content || 'Thank you for the information.')
    } catch (err) {
      addMessage('system', 'Sorry, there was an error processing your message.')
    }
    setLoading(false)
  }

  const renderFormGroup = (groupKey, title) => {
    const fields = Object.entries(FIELD_CONFIG).filter(([, v]) => v.group === groupKey)
    return (
      <div key={groupKey} className="mb-4">
        <h5 className="text-sm font-semibold text-teal-700 mb-2 uppercase tracking-wide">{title}</h5>
        <div className="grid grid-cols-2 gap-3">
          {fields.map(([key, config]) => (
            <div key={key}>
              <label className="text-xs font-medium text-gray-600">{config.label}</label>
              <input
                type="text"
                value={inputData[key]}
                onChange={e => setInputData(prev => ({ ...prev, [key]: e.target.value }))}
                className="w-full mt-1 px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-teal-500 focus:border-teal-500"
                placeholder={config.placeholder}
              />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Baby className="text-teal-600" size={28} />
          Child Assessment & Intervention Planning
        </h2>
        <p className="text-gray-500 mt-1">Enter screening data to generate a personalized autism intervention plan for the child and their family</p>
      </div>

      {caseId && workflowStep >= 0 && (
        <WorkflowProgress steps={WORKFLOW_STEPS} currentStep={workflowStep} />
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 mt-4">
        <div className="h-[500px] overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && !caseId && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Heart className="text-teal-600" size={28} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Start a New Intervention Plan</h3>
                <p className="text-gray-500 mb-2 max-w-md">
                  Create a personalized, evidence-based intervention plan for a child with autism.
                </p>
                <p className="text-gray-400 text-sm mb-4 max-w-md">
                  Our AI agents will analyze screening data, build a child profile, generate SMART goals,
                  and prepare guidance for parents -- all reviewed by a clinician before delivery.
                </p>
                <button
                  onClick={handleNewCase}
                  disabled={loading}
                  className="px-6 py-2.5 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="animate-spin inline" size={16} /> : 'Begin New Assessment'}
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] rounded-xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-teal-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-teal-200' : 'text-gray-400'}`}>{msg.time}</p>
              </div>
            </div>
          ))}

          {caseId && !consentGiven && (
            <div className="flex justify-center">
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 max-w-md">
                <p className="text-sm font-medium text-amber-800 mb-3 text-center">Informed Consent Verification</p>
                <div className="flex gap-3 justify-center">
                  <button onClick={handleConsent} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 text-sm font-medium">
                    <CheckCircle2 size={16} /> Consent Granted
                  </button>
                  <button onClick={handleConsentDenied} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 text-sm font-medium">
                    <AlertCircle size={16} /> Not Granted
                  </button>
                </div>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-xl px-4 py-3 flex items-center gap-2">
                <Loader2 className="animate-spin text-teal-500" size={20} />
                <span className="text-sm text-gray-500">AI agents processing...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {showInputForm && (
          <div className="border-t border-gray-200 p-4 bg-gray-50 max-h-[400px] overflow-y-auto">
            <h4 className="font-semibold text-gray-800 mb-1">Screening & Assessment Data</h4>
            <p className="text-xs text-gray-500 mb-4">Enter the child's clinical data from screening reports. Fields with more data produce better intervention plans.</p>

            {renderFormGroup('child', 'Child Information')}
            {renderFormGroup('assessment', 'Assessment Results')}
            {renderFormGroup('family', 'Family Context & Strengths')}

            <button
              onClick={handleInputSubmit}
              className="mt-2 px-6 py-2.5 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 flex items-center gap-2"
            >
              <Upload size={16} /> Submit & Generate Intervention Plan
            </button>
          </div>
        )}

        {caseId && consentGiven && !showInputForm && (
          <div className="border-t border-gray-200 p-4 flex gap-3">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask a question or provide additional information..."
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="px-4 py-2.5 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
