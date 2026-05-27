import { useState, useRef, useEffect } from 'react'
import { Send, Upload, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import { createCase, sendChatMessage, startWorkflow } from '../api/client'
import WorkflowProgress from '../components/shared/WorkflowProgress'

const WORKFLOW_STEPS = [
  'Consent', 'Input Collection', 'Data Validation', 'Profile Building',
  'Domain Prioritization', 'Confidence Check', 'Domain Analysis',
  'Guideline Generation', 'Bias Check', 'Goal Generation',
  'Milestone Planning', 'Caregiver Guidance', 'Clinician Review',
]

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
  const [inputData, setInputData] = useState({
    age_years: '', age_months: '', gender: '', support_level: '',
    screening_tool: '', primary_domain: '', secondary_domain: '',
    home_language: '', ados2_social_affect: '', ados2_rrb: '',
    strength_domains: '', gap_domains: '', family_priorities: '', current_services: '',
  })
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
      addMessage('system', `Case ${data.case_id} created. Before we proceed, we need to verify consent for data processing. Do you have proper consent from the authorized reporter?`)
    } catch (err) {
      addMessage('system', `Error creating case: ${err.message}`)
    }
    setLoading(false)
  }

  const handleConsent = () => {
    setConsentGiven(true)
    setWorkflowStep(0)
    addMessage('system', 'Consent verified. Please provide the child\'s screening and assessment data. You can enter the information using the form below.')
    setShowInputForm(true)
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
    addMessage('user', 'Submitted screening data for the child.')
    addMessage('system', 'Data received. Starting the intervention planning workflow...')
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
        addMessage('system', `Workflow encountered an issue: ${data.error}`)
      } else if (data.workflow_status === 'AWAITING_CLINICIAN_REVIEW') {
        setWorkflowStep(12)
        addMessage('system', `Intervention plan generated successfully! Plan ID: ${data.plan_id}. The plan is now awaiting clinician review. Go to the Review page to review and approve.`)
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

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Clinical Intake</h2>
        <p className="text-gray-500 mt-1">Upload screening reports and provide assessment data</p>
      </div>

      {caseId && workflowStep >= 0 && (
        <WorkflowProgress steps={WORKFLOW_STEPS} currentStep={workflowStep} />
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 mt-4">
        <div className="h-[500px] overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && !caseId && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="text-indigo-600" size={24} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Start a New Case</h3>
                <p className="text-gray-500 mb-4 max-w-sm">
                  Create a new case to begin the intervention planning workflow
                </p>
                <button
                  onClick={handleNewCase}
                  disabled={loading}
                  className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="animate-spin inline" size={16} /> : 'New Case'}
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] rounded-xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-indigo-200' : 'text-gray-400'}`}>{msg.time}</p>
              </div>
            </div>
          ))}

          {caseId && !consentGiven && (
            <div className="flex justify-center">
              <div className="flex gap-3">
                <button onClick={handleConsent} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2">
                  <CheckCircle2 size={16} /> Consent Granted
                </button>
                <button onClick={() => addMessage('system', 'Consent denied. Workflow cannot proceed without consent.')} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2">
                  <AlertCircle size={16} /> Consent Denied
                </button>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-xl px-4 py-3">
                <Loader2 className="animate-spin text-gray-400" size={20} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {showInputForm && (
          <div className="border-t border-gray-200 p-4 bg-gray-50">
            <h4 className="font-semibold text-gray-700 mb-3">Screening Data Input</h4>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(inputData).map(([key, val]) => (
                <div key={key}>
                  <label className="text-xs font-medium text-gray-500 capitalize">{key.replace(/_/g, ' ')}</label>
                  <input
                    type="text"
                    value={val}
                    onChange={e => setInputData(prev => ({ ...prev, [key]: e.target.value }))}
                    className="w-full mt-1 px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder={key.includes('age') ? 'e.g., 3' : ''}
                  />
                </div>
              ))}
            </div>
            <button
              onClick={handleInputSubmit}
              className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700"
            >
              Submit & Start Workflow
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
              placeholder="Type a message..."
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
