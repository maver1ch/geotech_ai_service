import React, { useState, useRef, useEffect } from 'react'
import MessageBubble from '../MessageHistory/MessageBubble'
import InputForm from '../InputForm/InputForm'
import LoadingIndicator from '../UI/LoadingIndicator'
import { apiService } from '../../services/api'

function ChatContainer() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  // Format timestamp
  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  // Handle question submission
  const handleQuestionSubmit = async (question) => {
    const timestamp = new Date()
    
    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      message: question,
      isUser: true,
      timestamp: formatTime(timestamp)
    }
    setMessages(prev => [...prev, userMessage])
    
    // Clear any previous errors
    setError(null)
    setIsLoading(true)

    try {
      // Call the API
      const result = await apiService.askQuestion(question)
      
      if (result.success) {
        // Add bot response
        const botMessage = {
          id: Date.now() + 1,
          message: result.data.answer,
          isUser: false,
          timestamp: formatTime(new Date()),
          citations: result.data.citations || []
        }
        setMessages(prev => [...prev, botMessage])
      } else {
        // Handle API error
        const errorMessage = {
          id: Date.now() + 1,
          message: `❌ Sorry, I encountered an error: ${result.error}`,
          isUser: false,
          timestamp: formatTime(new Date())
        }
        setMessages(prev => [...prev, errorMessage])
        setError(result.error)
      }
    } catch (error) {
      // Handle unexpected errors
      const errorMessage = {
        id: Date.now() + 1,
        message: `❌ Unexpected error: ${error.message}`,
        isUser: false,
        timestamp: formatTime(new Date())
      }
      setMessages(prev => [...prev, errorMessage])
      setError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>👋 Welcome to RocScience Geotech Chatbot</h2>
            <p>I can help you with geotechnical engineering questions, calculations, and provide insights from Settle3 documentation.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg.message}
              isUser={msg.isUser}
              citations={msg.citations}
              timestamp={msg.timestamp}
            />
          ))
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="message bot">
            <div className="message-content">
              <LoadingIndicator message="Processing your question (Plan → Execute → Synthesize)..." />
            </div>
          </div>
        )}
        
        {/* Auto scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      <InputForm onSubmit={handleQuestionSubmit} isLoading={isLoading} />
    </div>
  )
}

export default ChatContainer