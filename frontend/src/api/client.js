import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Case Management
export const createCase = (data) => api.post('/cases', data)
export const getCase = (caseId) => api.get(`/cases/${caseId}`)
export const getCaseStatus = (caseId) => api.get(`/cases/${caseId}/status`)
export const listCases = () => api.get('/cases')
export const updateConsent = (caseId, granted) => api.put(`/cases/${caseId}/consent`, { granted })

// Documents
export const uploadDocument = (caseId, data) => api.post(`/cases/${caseId}/documents`, data)
export const submitInputs = (caseId, data) => api.post(`/cases/${caseId}/inputs`, data)
export const getInputs = (caseId) => api.get(`/cases/${caseId}/inputs`)

// Workflow
export const startWorkflow = (caseId, data) => api.post(`/cases/${caseId}/workflow/start`, data)
export const getWorkflowState = (caseId) => api.get(`/cases/${caseId}/workflow/state`)

// Plan
export const getPlan = (caseId) => api.get(`/cases/${caseId}/plan`)
export const getPlanProfile = (caseId) => api.get(`/cases/${caseId}/plan/profile`)
export const getPlanDomains = (caseId) => api.get(`/cases/${caseId}/plan/domains`)
export const getPlanGuidelines = (caseId) => api.get(`/cases/${caseId}/plan/guidelines`)
export const getPlanGoals = (caseId) => api.get(`/cases/${caseId}/plan/goals`)
export const getPlanCaregiver = (caseId) => api.get(`/cases/${caseId}/plan/caregiver`)

// Review
export const getPendingReviews = () => api.get('/reviews/pending')
export const submitReview = (caseId, data) => api.post(`/cases/${caseId}/review`, data)
export const getCaseReviews = (caseId) => api.get(`/cases/${caseId}/reviews`)

// Audit
export const getAuditTrail = (caseId) => api.get(`/cases/${caseId}/audit`)

// Chat
export const sendChatMessage = (caseId, message) => api.post(`/chat/${caseId}/message`, { message })
export const getChatHistory = (caseId) => api.get(`/chat/${caseId}/history`)

export default api
