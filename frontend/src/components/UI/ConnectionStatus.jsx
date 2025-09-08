import React, { useState, useEffect } from 'react'
import { apiService } from '../../services/api'

function ConnectionStatus() {
  const [status, setStatus] = useState('checking') // checking, connected, disconnected
  const [responseTime, setResponseTime] = useState(null)
  const [quickMetrics, setQuickMetrics] = useState(null)
  const [showDetails, setShowDetails] = useState(false)
  const [lastCheck, setLastCheck] = useState(null)
  
  useEffect(() => {
    const checkConnection = async () => {
      const startTime = Date.now()
      
      try {
        const healthResult = await apiService.checkHealth()
        const endTime = Date.now()
        const responseTimeMs = endTime - startTime
        
        if (healthResult.success) {
          setStatus('connected')
          setResponseTime(responseTimeMs)
          setLastCheck(new Date())
          
          // Fetch quick metrics if connected
          try {
            const metricsResult = await apiService.getMetrics()
            if (metricsResult.success) {
              setQuickMetrics({
                totalRequests: metricsResult.data.total_requests,
                uptime: metricsResult.data.uptime_seconds,
                successRate: ((metricsResult.data.successful_requests / 
                  (metricsResult.data.successful_requests + metricsResult.data.failed_requests)) * 100).toFixed(1)
              })
            }
          } catch (metricsError) {
            // Metrics fetch failed, but health is OK
            console.warn('Metrics fetch failed:', metricsError)
          }
        } else {
          setStatus('disconnected')
          setResponseTime(null)
          setQuickMetrics(null)
        }
      } catch (error) {
        setStatus('disconnected')
        setResponseTime(null)
        setQuickMetrics(null)
        setLastCheck(new Date())
      }
    }
    
    // Check immediately
    checkConnection()
    
    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000)
    return () => clearInterval(interval)
  }, [])
  
  const getStatusColor = () => {
    switch (status) {
      case 'connected': return '#059669' // green
      case 'disconnected': return '#dc2626' // red  
      case 'checking': return '#d97706' // orange
      default: return '#6b7280' // gray
    }
  }
  
  const getStatusText = () => {
    switch (status) {
      case 'connected': return 'Connected'
      case 'disconnected': return 'Disconnected'
      case 'checking': return 'Checking...'
      default: return 'Unknown'
    }
  }
  
  const formatUptime = (seconds) => {
    if (!seconds) return 'N/A'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  return (
    <div style={{ position: 'relative' }}>
      <div 
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          fontSize: '0.875rem',
          color: '#374151',
          fontWeight: '500',
          cursor: 'pointer',
          padding: '6px 12px',
          borderRadius: '6px',
          border: '1px solid #d1d5db',
          backgroundColor: 'white',
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          e.target.style.backgroundColor = '#f3f4f6'
          e.target.style.borderColor = '#9ca3af'
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = 'white'
          e.target.style.borderColor = '#d1d5db'
        }}
        onClick={() => setShowDetails(!showDetails)}
      >
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: getStatusColor()
        }} />
        <span>Backend: {getStatusText()}</span>
        {responseTime && status === 'connected' && (
          <span style={{ color: '#6b7280', fontSize: '0.75rem', fontWeight: '400' }}>
            ({responseTime}ms)
          </span>
        )}
        <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
          {showDetails ? '▼' : '▶'}
        </span>
      </div>

      {showDetails && (
        <div style={{
          position: 'absolute',
          right: 0,
          top: '100%',
          marginTop: '4px',
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '12px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          minWidth: '200px',
          zIndex: 1000,
          fontSize: '0.75rem'
        }}>
          <div style={{ fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            📋 System Status
          </div>
          
          <div style={{ display: 'grid', gap: '4px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#6b7280' }}>Status:</span>
              <span style={{ 
                color: getStatusColor(), 
                fontWeight: '500'
              }}>
                {getStatusText()}
              </span>
            </div>
            
            {responseTime && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#6b7280' }}>Response Time:</span>
                <span style={{ color: '#374151' }}>{responseTime}ms</span>
              </div>
            )}
            
            {lastCheck && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#6b7280' }}>Last Check:</span>
                <span style={{ color: '#374151' }}>{lastCheck.toLocaleTimeString()}</span>
              </div>
            )}
            
            {quickMetrics && (
              <>
                <hr style={{ margin: '8px 0', border: 'none', borderTop: '1px solid #e5e7eb' }} />
                <div style={{ fontWeight: '500', marginBottom: '4px', color: '#374151' }}>
                  📊 Quick Metrics
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#6b7280' }}>Total Requests:</span>
                  <span style={{ color: '#374151' }}>{quickMetrics.totalRequests}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#6b7280' }}>Uptime:</span>
                  <span style={{ color: '#374151' }}>{formatUptime(quickMetrics.uptime)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#6b7280' }}>Success Rate:</span>
                  <span style={{ color: quickMetrics.successRate >= 95 ? '#059669' : '#d97706' }}>
                    {quickMetrics.successRate}%
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ConnectionStatus