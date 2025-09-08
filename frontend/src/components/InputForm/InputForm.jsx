import React, { useState } from 'react'

function InputForm({ onSubmit, isLoading }) {
  const [question, setQuestion] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (question.trim() && !isLoading) {
      onSubmit(question.trim())
      setQuestion('')
    }
  }

  const exampleQuestions = [
    "What methods does Settle3 use to calculate undrained shear strength from CPT data? (retrieval)",
    "How is normalized cone resistance calculated in CPT analysis? (retrieval)",
    "Calculate settlement for load 1000 kN and Young's modulus 50000 kPa (calculate)",
    "What is ultimate bearing capacity for footing width 3m, unit weight 20 kN/m³, depth 2m, friction angle 35°? (calculate)",
    "Calculate settlement for 800 kN load with E=40 MPa and explain the consolidation theory behind it (both)",
    "What is the moment of inertia calculation for concrete columns? (out of scope)",
    "What is the weather today? (unrelated)"
  ]

  const handleExampleClick = (exampleQuestion) => {
    if (!isLoading) {
      setQuestion(exampleQuestion)
    }
  }

  return (
    <div className="input-form">
      {/* Example questions - show when input is empty */}
      {question === '' && (
        <div className="example-questions">
          <p style={{ marginBottom: '10px', fontSize: '0.875rem', color: '#6b7280' }}>
            💡 Try these example questions:
          </p>
          {exampleQuestions.map((example, index) => (
            <div 
              key={index}
              className="example-question"
              onClick={() => handleExampleClick(example)}
            >
              {example}
            </div>
          ))}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            type="text"
            className="input-field"
            placeholder="Ask a geotechnical engineering question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="submit-button"
            disabled={!question.trim() || isLoading}
          >
            {isLoading ? 'Processing...' : 'Ask'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default InputForm