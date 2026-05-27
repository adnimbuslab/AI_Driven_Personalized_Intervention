import { CheckCircle, Circle, Loader2 } from 'lucide-react'

export default function WorkflowProgress({ steps, currentStep }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-4 overflow-x-auto">
      <div className="flex items-center gap-1 min-w-max">
        {steps.map((step, i) => {
          const completed = i < currentStep
          const active = i === currentStep
          return (
            <div key={i} className="flex items-center">
              <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
                completed ? 'bg-green-100 text-green-700' :
                active ? 'bg-indigo-100 text-indigo-700' :
                'bg-gray-100 text-gray-400'
              }`}>
                {completed ? <CheckCircle size={12} /> :
                 active ? <Loader2 size={12} className="animate-spin" /> :
                 <Circle size={12} />}
                <span className="hidden lg:inline">{step}</span>
                <span className="lg:hidden">{i + 1}</span>
              </div>
              {i < steps.length - 1 && (
                <div className={`w-4 h-0.5 mx-0.5 ${completed ? 'bg-green-300' : 'bg-gray-200'}`} />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
