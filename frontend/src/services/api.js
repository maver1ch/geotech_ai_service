import axios from 'axios'

// Get API URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 150000, // 2.5 minutes for agent processing
  headers: {
    'Content-Type': 'application/json',
  },
})

// API service functions
export const apiService = {
  // Ask a question to the geotech AI assistant
  async askQuestion(question) {
    try {
      const response = await api.post('/ask', { question })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      console.error('API Error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to get response'
      }
    }
  },

  // Check backend health
  async checkHealth() {
    try {
      const response = await api.get('/health')
      return { success: true, data: response.data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  },

  // Get metrics (optional)
  async getMetrics() {
    try {
      const response = await api.get('/metrics')
      return { success: true, data: response.data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }
}

export default apiService