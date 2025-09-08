import React from 'react'

function MetricsCard({ icon, title, value, subtitle, color = '#374151' }) {
  return (
    <div style={{
      backgroundColor: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '16px',
      minWidth: '140px',
      textAlign: 'center',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      transition: 'transform 0.2s ease, box-shadow 0.2s ease'
    }}
    onMouseEnter={(e) => {
      e.target.style.transform = 'translateY(-2px)'
      e.target.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)'
    }}
    onMouseLeave={(e) => {
      e.target.style.transform = 'translateY(0)'
      e.target.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}
    >
      <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>
        {icon}
      </div>
      <div style={{ 
        fontSize: '1.25rem', 
        fontWeight: 'bold', 
        color: color,
        marginBottom: '4px'
      }}>
        {value}
      </div>
      <div style={{ 
        fontSize: '0.75rem', 
        color: '#374151',
        fontWeight: '500',
        marginBottom: '2px'
      }}>
        {title}
      </div>
      {subtitle && (
        <div style={{ 
          fontSize: '0.625rem', 
          color: '#6b7280',
          fontStyle: 'italic'
        }}>
          {subtitle}
        </div>
      )}
    </div>
  )
}

export default MetricsCard