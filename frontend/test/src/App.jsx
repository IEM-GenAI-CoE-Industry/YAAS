import { useState } from 'react'
import './App.css'

// Get API URL from environment variables or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

function App() {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [useLocalLLM, setUseLocalLLM] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!question.trim()) {
      setError('Please enter a question')
      return
    }

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await fetch(`${API_URL}/YAAS/content/v1/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question.trim(),
          local_llm: useLocalLLM
        })
      })

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }

      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err.message || 'Failed to generate content. Please make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setQuestion('')
    setResponse(null)
    setError(null)
  }

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <div className="icon-wrapper">
            <svg className="icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h1 className="title">YAAS</h1>
          <p className="subtitle">Ask any question and get AI-powered insights</p>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <div className="input-wrapper">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your question here..."
              className="input"
              rows="4"
              disabled={loading}
            />
          </div>

          <div className="toggle-container">
            <label className="toggle-label">
              <span className="toggle-text">
                <svg className="toggle-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 3H5C3.89543 3 3 3.89543 3 5V9C3 10.1046 3.89543 11 5 11H9C10.1046 11 11 10.1046 11 9V5C11 3.89543 10.1046 3 9 3Z" stroke="currentColor" strokeWidth="2"/>
                  <path d="M19 3H15C13.8954 3 13 3.89543 13 5V9C13 10.1046 13.8954 11 15 11H19C20.1046 11 21 10.1046 21 9V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" strokeWidth="2"/>
                  <path d="M9 13H5C3.89543 13 3 13.8954 3 15V19C3 20.1046 3.89543 21 5 21H9C10.1046 21 11 20.1046 11 19V15C11 13.8954 10.1046 13 9 13Z" stroke="currentColor" strokeWidth="2"/>
                  <path d="M19 13H15C13.8954 13 13 13.8954 13 15V19C13 20.1046 13.8954 21 15 21H19C20.1046 21 21 20.1046 21 19V15C21 13.8954 20.1046 13 19 13Z" stroke="currentColor" strokeWidth="2"/>
                </svg>
                Use Local LLM
              </span>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={useLocalLLM}
                  onChange={(e) => setUseLocalLLM(e.target.checked)}
                  disabled={loading}
                  className="toggle-input"
                />
                <span className="toggle-slider"></span>
              </div>
            </label>
            <p className="toggle-description">
              {useLocalLLM ? 'Using local LLM for generation' : 'Using cloud AI services'}
            </p>
          </div>

          <div className="button-group">
            <button
              type="submit"
              className="button button-primary"
              disabled={loading || !question.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Generating...
                </>
              ) : (
                <>
                  <svg className="button-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Generate Content
                </>
              )}
            </button>

            {(response || error) && (
              <button
                type="button"
                onClick={handleClear}
                className="button button-secondary"
                disabled={loading}
              >
                Clear
              </button>
            )}
          </div>
        </form>

        {error && (
          <div className="alert alert-error">
            <svg className="alert-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
              <path d="M12 8V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="12" cy="16" r="1" fill="currentColor"/>
            </svg>
            <p>{error}</p>
          </div>
        )}

        {response && (
          <div className="response-card">
            <div className="response-header">
              <svg className="response-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
              </svg>
              <h2 className="response-title">{response.status.charAt(0).toUpperCase() + response.status.slice(1)}</h2>
            </div>

            <p className="response-message">{response.message}</p>

            <div className="response-content">
              <h3 className="content-label">Generated Content:</h3>
              <div className="content-text">{response.data}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
