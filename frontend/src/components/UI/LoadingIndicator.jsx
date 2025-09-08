import React from 'react'

function LoadingIndicator({ message = "AI is thinking..." }) {
  return (
    <div className="loading">
      <span>{message}</span>
      <div className="loading-dots">
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
        <div className="loading-dot"></div>
      </div>
    </div>
  )
}

export default LoadingIndicator