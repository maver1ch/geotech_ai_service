import React, { useState } from 'react'
import ChatContainer from './components/ChatBot/ChatContainer'
import ConnectionStatus from './components/UI/ConnectionStatus'
import MetricsDashboard from './components/Dashboard/MetricsDashboard'
import logoImage from '../logo.png'

function App() {
  const [showMetrics, setShowMetrics] = useState(false)

  return (
    <div className="container">
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <img 
              src={logoImage} 
              alt="Geotech Logo" 
              style={{ 
                width: '48px', 
                height: '48px',
                borderRadius: '8px',
                backgroundColor: 'rgba(255,255,255,0.1)',
                padding: '4px'
              }}
            />
            <div>
              <h1>RocScience Geotech Chatbot</h1>
              <p>Ask questions about geotechnical engineering, CPT analysis, liquefaction, or request calculations</p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => setShowMetrics(!showMetrics)}
              style={{
                background: showMetrics ? '#1e40af' : 'white',
                color: showMetrics ? 'white' : '#374151',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
              }}
              onMouseEnter={(e) => {
                if (!showMetrics) {
                  e.target.style.backgroundColor = '#f3f4f6'
                  e.target.style.borderColor = '#9ca3af'
                }
              }}
              onMouseLeave={(e) => {
                if (!showMetrics) {
                  e.target.style.backgroundColor = 'white'
                  e.target.style.borderColor = '#d1d5db'
                }
              }}
            >
              📊 {showMetrics ? 'Hide' : 'Show'} Metrics
            </button>
            <ConnectionStatus />
          </div>
        </div>
      </header>
      
      <MetricsDashboard 
        isVisible={showMetrics} 
        onToggle={() => setShowMetrics(false)}
      />
      
      <ChatContainer />
    </div>
  )
}

export default App