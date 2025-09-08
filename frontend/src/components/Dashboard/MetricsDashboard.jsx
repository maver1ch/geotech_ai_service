import React, { useState, useEffect } from 'react'
import { apiService } from '../../services/api'
import MetricsCard from './MetricsCard'

function MetricsDashboard({ isVisible, onToggle }) {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchMetrics = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await apiService.getMetrics()
      if (result.success) {
        setMetrics(result.data)
        setLastUpdated(new Date())
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError('Failed to fetch metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isVisible) {
      fetchMetrics()
      // Auto-refresh every 10 seconds
      const interval = setInterval(fetchMetrics, 10000)
      return () => clearInterval(interval)
    }
  }, [isVisible])

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    return `${hours}h ${minutes}m ${secs}s`
  }

  const formatResponseTime = (ms) => {
    if (ms > 1000) {
      return `${(ms / 1000).toFixed(2)}s`
    }
    return `${Math.round(ms)}ms`
  }

  const calculateSuccessRate = () => {
    if (!metrics) return 0
    const total = metrics.successful_requests + metrics.failed_requests
    if (total === 0) return 100
    return ((metrics.successful_requests / total) * 100).toFixed(1)
  }

  if (!isVisible) return null

  return (
    <div style={{
      backgroundColor: '#f8fafc',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '16px',
      margin: '16px 0',
      transition: 'all 0.3s ease'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h3 style={{ 
          margin: 0, 
          color: '#374151',
          fontSize: '1.125rem',
          fontWeight: '600'
        }}>
          📊 System Metrics
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {lastUpdated && (
            <span style={{ 
              fontSize: '0.75rem', 
              color: '#6b7280',
              fontStyle: 'italic'
            }}>
              Updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchMetrics}
            disabled={loading}
            style={{
              background: loading ? '#9ca3af' : '#1e40af',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 8px',
              fontSize: '0.75rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s'
            }}
          >
            {loading ? '⟳' : '🔄'} Refresh
          </button>
          <button
            onClick={onToggle}
            style={{
              background: 'none',
              border: 'none',
              color: '#6b7280',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            ✕
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          backgroundColor: '#fee2e2',
          color: '#dc2626',
          padding: '8px 12px',
          borderRadius: '6px',
          fontSize: '0.875rem',
          marginBottom: '16px'
        }}>
          Error: {error}
        </div>
      )}

      {metrics && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: '12px'
        }}>
          <MetricsCard
            icon="📈"
            title="Total Requests"
            value={metrics.total_requests}
            color="#1e40af"
          />
          
          <MetricsCard
            icon="✅"
            title="Success Rate"
            value={`${calculateSuccessRate()}%`}
            subtitle={`${metrics.successful_requests}/${metrics.successful_requests + metrics.failed_requests}`}
            color="#059669"
          />

          <MetricsCard
            icon="⚡"
            title="Response Time"
            value={formatResponseTime(metrics.average_response_time)}
            subtitle="Average"
            color="#d97706"
          />

          <MetricsCard
            icon="🔧"
            title="Tool Calls"
            value={metrics.tool_calls}
            color="#7c3aed"
          />

          <MetricsCard
            icon="🔍"
            title="Retrievals"
            value={metrics.retrieval_calls}
            color="#dc2626"
          />

          <MetricsCard
            icon="⏱️"
            title="Uptime"
            value={formatUptime(metrics.uptime_seconds)}
            color="#059669"
          />

          <MetricsCard
            icon="📊"
            title="Requests/Min"
            value={metrics.requests_per_minute}
            color="#0891b2"
          />

          {metrics.failed_requests > 0 && (
            <MetricsCard
              icon="❌"
              title="Failed Requests"
              value={metrics.failed_requests}
              color="#dc2626"
            />
          )}
        </div>
      )}
    </div>
  )
}

export default MetricsDashboard