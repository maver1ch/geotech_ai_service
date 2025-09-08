import React from 'react'
import ReactMarkdown from 'react-markdown'
import CitationPanel from '../Citations/CitationPanel'

function MessageBubble({ message, isUser, citations, timestamp }) {
  const messageClass = isUser ? 'message user' : 'message bot'
  
  // Pre-process message to fix escaped newlines and formatting issues
  const processMessage = (msg) => {
    if (isUser) return msg
    
    // Convert escaped newlines to actual newlines and clean up excessive spacing
    return msg
      .replace(/\\n\\n/g, '\n\n')  // Double newlines
      .replace(/\\n/g, '\n')       // Single newlines
      .replace(/\\\*/g, '*')       // Fix escaped asterisks
      .replace(/\\\(/g, '(')       // Fix escaped parentheses
      .replace(/\\\)/g, ')')       // Fix escaped parentheses
      .replace(/\n\s*\n\s*\n/g, '\n\n')  // Reduce triple+ newlines to double
      .replace(/^\s*•\s*/gm, '• ')  // Clean bullet point spacing
      .replace(/\n\s*\*\s*/g, '\n* ') // Clean asterisk bullet spacing
  }

  
  const processedMessage = processMessage(message)
  
  return (
    <div className={messageClass}>
      <div className="message-content">
        {isUser ? (
          message
        ) : (
          <ReactMarkdown>
            {processedMessage}
          </ReactMarkdown>
        )}
      </div>
      {timestamp && (
        <div className={`timestamp ${isUser ? 'user' : 'bot'}`}>
          {timestamp}
        </div>
      )}
      {citations && citations.length > 0 && (
        <CitationPanel citations={citations} />
      )}
    </div>
  )
}

export default MessageBubble