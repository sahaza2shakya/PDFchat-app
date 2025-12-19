import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [pdfs, setPdfs] = useState([])
  const [selectedPdf, setSelectedPdf] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    fetchPdfs()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchPdfs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/pdfs`)
      setPdfs(response.data.pdfs)
    } catch (error) {
      console.error('Error fetching PDFs:', error)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file || !file.name.endsWith('.pdf')) {
      alert('Please select a PDF file')
      return
    }

    // Check file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      alert('File size exceeds 50MB limit')
      return
    }

    setIsUploading(true)
    setUploadStatus('Uploading and processing PDF...')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${API_BASE_URL}/api/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes timeout for large files
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setUploadStatus(`Uploading: ${percentCompleted}%...`)
          }
        }
      })

      setUploadStatus(`Success! PDF processed into ${response.data.chunks} chunks.`)
      setSelectedPdf(response.data.pdf_id)
      setMessages([{
        type: 'system',
        content: `PDF "${file.name}" uploaded and processed successfully. You can now ask questions about it.`
      }])
      await fetchPdfs()
      
      setTimeout(() => setUploadStatus(null), 3000)
    } catch (error) {
      console.error('Error uploading PDF:', error)
      let errorMessage = 'Unknown error occurred'
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout - the file may be too large or processing is taking too long'
      } else if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        errorMessage = 'Network error - please check if the backend server is running on http://localhost:8000'
      } else if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || error.response.data?.message || `Server error: ${error.response.status}`
      } else if (error.request) {
        errorMessage = 'No response from server - please check if the backend is running'
      } else {
        errorMessage = error.message
      }
      
      setUploadStatus(`Error: ${errorMessage}`)
      setTimeout(() => setUploadStatus(null), 8000)
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      type: 'user',
      content: inputMessage
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        question: inputMessage,
        pdf_id: selectedPdf
      })

      const assistantMessage = {
        type: 'assistant',
        content: response.data.answer,
        sources: response.data.source_documents
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        type: 'error',
        content: `Error: ${error.response?.data?.detail || error.message}`
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handlePdfSelect = (pdfId) => {
    setSelectedPdf(pdfId)
    setMessages([{
      type: 'system',
      content: `Switched to PDF: ${pdfs.find(p => p.pdf_id === pdfId)?.pdf_name || pdfId}`
    }])
  }

  const handleDeletePdf = async (pdfId) => {
    if (!confirm('Are you sure you want to delete this PDF?')) return

    try {
      await axios.delete(`${API_BASE_URL}/api/pdfs/${pdfId}`)
      if (selectedPdf === pdfId) {
        setSelectedPdf(null)
        setMessages([])
      }
      await fetchPdfs()
    } catch (error) {
      console.error('Error deleting PDF:', error)
      alert(`Error deleting PDF: ${error.response?.data?.detail || error.message}`)
    }
  }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>📄 PDF Chat</h1>
          <p>Upload PDFs and chat with them</p>
        </div>

        <div className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            id="pdf-upload"
          />
          <label htmlFor="pdf-upload" className="upload-button">
            {isUploading ? 'Processing...' : '📤 Upload PDF'}
          </label>
          {uploadStatus && (
            <div className={`upload-status ${uploadStatus.includes('Error') ? 'error' : 'success'}`}>
              {uploadStatus}
            </div>
          )}
        </div>

        <div className="pdfs-list">
          <h3>Your PDFs</h3>
          {pdfs.length === 0 ? (
            <p className="empty-state">No PDFs uploaded yet</p>
          ) : (
            <ul>
              {pdfs.map((pdf) => (
                <li
                  key={pdf.pdf_id}
                  className={selectedPdf === pdf.pdf_id ? 'active' : ''}
                >
                  <div
                    className="pdf-item"
                    onClick={() => handlePdfSelect(pdf.pdf_id)}
                  >
                    <span className="pdf-name">📄 {pdf.pdf_name}</span>
                    <span className="pdf-chunks">{pdf.total_chunks} chunks</span>
                  </div>
                  <button
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeletePdf(pdf.pdf_id)
                    }}
                  >
                    🗑️
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="main-content">
        <div className="chat-header">
          <h2>
            {selectedPdf
              ? `Chatting with: ${pdfs.find(p => p.pdf_id === selectedPdf)?.pdf_name || 'PDF'}`
              : 'Select or upload a PDF to start chatting'}
          </h2>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h3>Welcome to PDF Chat! 👋</h3>
              <p>Upload a PDF file to start asking questions about its content.</p>
              <p>The system will extract, chunk, and embed the content for intelligent Q&A.</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                <div className="message-content">
                  {message.type === 'user' && <span className="message-icon">👤</span>}
                  {message.type === 'assistant' && <span className="message-icon">🤖</span>}
                  {message.type === 'system' && <span className="message-icon">ℹ️</span>}
                  {message.type === 'error' && <span className="message-icon">⚠️</span>}
                  <div className="message-text">
                    <p>{message.content}</p>
                    {message.sources && message.sources.length > 0 && (
                      <div className="sources">
                        <strong>Sources:</strong>
                        <ul>
                          {message.sources.map((source, idx) => (
                            <li key={idx}>
                              {source.metadata.pdf_name} (chunk {source.metadata.chunk_index + 1})
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <span className="message-icon">🤖</span>
                <div className="message-text">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <textarea
            className="chat-input"
            placeholder={selectedPdf ? "Ask a question about the PDF..." : "Upload a PDF first to start chatting..."}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={!selectedPdf || isLoading}
            rows={3}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!selectedPdf || !inputMessage.trim() || isLoading}
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App

