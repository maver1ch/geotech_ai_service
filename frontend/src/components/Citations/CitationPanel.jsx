import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'

function CitationPanel({ citations = [] }) {
  const [expandedCitations, setExpandedCitations] = useState({})

  if (!citations || citations.length === 0) {
    return null
  }

  const toggleCitation = (index) => {
    setExpandedCitations(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const truncateLength = 200

  return (
    <div className="citations">
      <h4 style={{ marginBottom: '10px', color: '#374151', fontWeight: 'bold' }}>📚 Sources:</h4>
      {citations.map((citation, index) => {
        const isExpanded = expandedCitations[index] || false
        const shouldTruncate = citation.content && citation.content.length > truncateLength
        
        // Better truncation logic - ensure we don't break words
        let displayContent = citation.content || ''
        if (shouldTruncate && !isExpanded) {
          // Find the last space before the truncation point to avoid breaking words
          const truncatedText = citation.content.substring(0, truncateLength)
          const lastSpaceIndex = truncatedText.lastIndexOf(' ')
          displayContent = lastSpaceIndex > truncateLength * 0.8 
            ? truncatedText.substring(0, lastSpaceIndex)
            : truncatedText
        }

        return (
          <div key={index} className="citation">
            <div className="citation-source">
              <strong>{citation.source_name}</strong>
              {citation.page_index && <span> (Page {citation.page_index})</span>}
            </div>
            {citation.confidence_score && (
              <div className="citation-score" style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '4px',
                marginBottom: '8px'
              }}>
                {citation.confidence_score > 1.0 ? (
                  <>
                    <span style={{ fontSize: '0.8rem' }}>🔍</span>
                    <span style={{ color: '#dc2626', fontWeight: '500' }}>
                      Keyword Matching Score: {(citation.confidence_score * 100).toFixed(1)}%
                    </span>
                  </>
                ) : (
                  <>
                    <span style={{ fontSize: '0.8rem' }}>🧠</span>
                    <span style={{ color: '#059669', fontWeight: '500' }}>
                      Semantic Similarity Score: {(citation.confidence_score * 100).toFixed(1)}%
                    </span>
                  </>
                )}
                <span 
                  style={{ 
                    cursor: 'help',
                    color: '#9ca3af',
                    fontSize: '0.75rem'
                  }}
                  title={citation.confidence_score > 1.0 
                    ? 'High scores indicate strong keyword matches in the text'
                    : 'Score from 0-100% shows semantic similarity to your question'
                  }
                >
                  ℹ️
                </span>
              </div>
            )}
            <div style={{ marginTop: '8px', fontSize: '0.875rem', color: '#6b7280', lineHeight: '1.5' }}>
              <ReactMarkdown
                components={{
                  p: ({node, ...props}) => <p style={{ margin: '0 0 8px 0' }} {...props} />,
                  strong: ({node, ...props}) => <strong style={{ fontWeight: 'bold', color: '#374151' }} {...props} />,
                  em: ({node, ...props}) => <em style={{ fontStyle: 'italic' }} {...props} />,
                  ul: ({node, ...props}) => <ul style={{ margin: '4px 0', paddingLeft: '16px' }} {...props} />,
                  ol: ({node, ...props}) => <ol style={{ margin: '4px 0', paddingLeft: '16px' }} {...props} />,
                  li: ({node, ...props}) => <li style={{ margin: '2px 0' }} {...props} />,
                  code: ({node, inline, ...props}) => (
                    inline ? 
                      <code style={{ backgroundColor: '#f1f5f9', padding: '1px 3px', borderRadius: '2px', fontSize: '0.8em' }} {...props} /> :
                      <code style={{ display: 'block', backgroundColor: '#f1f5f9', padding: '8px', borderRadius: '4px', fontSize: '0.8em', margin: '4px 0' }} {...props} />
                  ),
                  // Add table support for better markdown rendering
                  table: ({node, ...props}) => <table style={{ borderCollapse: 'collapse', width: '100%', margin: '8px 0' }} {...props} />,
                  th: ({node, ...props}) => <th style={{ border: '1px solid #e2e8f0', padding: '4px 8px', backgroundColor: '#f8fafc' }} {...props} />,
                  td: ({node, ...props}) => <td style={{ border: '1px solid #e2e8f0', padding: '4px 8px' }} {...props} />,
                }}
              >
                {displayContent}
              </ReactMarkdown>
              {shouldTruncate && !isExpanded && (
                <span style={{ color: '#9ca3af' }}>...</span>
              )}
              {shouldTruncate && (
                <div style={{ marginTop: '8px' }}>
                  <button
                    onClick={() => toggleCitation(index)}
                    style={{
                      background: '#1e40af',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      padding: '4px 8px',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.target.style.background = '#1d4ed8'}
                    onMouseLeave={(e) => e.target.style.background = '#1e40af'}
                  >
                    {isExpanded ? '▼ Show less' : '▶ Show more'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default CitationPanel