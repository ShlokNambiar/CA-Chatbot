/**
 * CA Chatbot Widget - Standalone JavaScript Widget
 * Isolated implementation that won't conflict with React/Framer
 */

class CAChatbotWidget {
  constructor(options = {}) {
    this.apiBase = options.apiBase || 'https://ca-chatbot-ld8v.onrender.com';
    this.webSearchEnabled = options.webSearchEnabled !== false;
    this.sessionId = this.generateSessionId();
    this.isOpen = false;
    this.isLoading = false;
    
    this.init();
  }

  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  init() {
    this.createWidget();
    this.attachEventListeners();
    this.checkAPIHealth();
  }

  createWidget() {
    // Create widget container
    const widget = document.createElement('div');
    widget.id = 'ca-chatbot-widget';
    widget.innerHTML = `
      <style>
        #ca-chatbot-widget {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 10000;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .ca-chat-toggle {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: linear-gradient(135deg, #0066cc, #004499);
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
          transition: all 0.3s ease;
          color: white;
        }
        
        .ca-chat-toggle:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 16px rgba(0, 102, 204, 0.4);
        }
        
        .ca-chat-interface {
          position: absolute;
          bottom: 80px;
          right: 0;
          width: 350px;
          height: 500px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
          display: none;
          flex-direction: column;
          overflow: hidden;
        }
        
        .ca-chat-interface.open {
          display: flex;
          animation: slideUp 0.3s ease;
        }
        
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .ca-chat-header {
          background: linear-gradient(135deg, #0066cc, #004499);
          color: white;
          padding: 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        
        .ca-chat-title {
          font-weight: 600;
          font-size: 16px;
        }
        
        .ca-chat-subtitle {
          font-size: 12px;
          opacity: 0.9;
          margin-top: 2px;
        }
        
        .ca-chat-controls {
          display: flex;
          gap: 8px;
        }
        
        .ca-control-btn {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          width: 32px;
          height: 32px;
          border-radius: 6px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }
        
        .ca-control-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        
        .ca-control-btn.active {
          background: rgba(146, 241, 66, 0.3);
        }
        
        .ca-chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .ca-message {
          display: flex;
          gap: 8px;
          max-width: 85%;
        }
        
        .ca-message.user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }
        
        .ca-message-bubble {
          padding: 12px 16px;
          border-radius: 18px;
          font-size: 14px;
          line-height: 1.4;
        }
        
        .ca-message.user .ca-message-bubble {
          background: #0066cc;
          color: white;
        }
        
        .ca-message.bot .ca-message-bubble {
          background: #f1f3f5;
          color: #333;
        }
        
        .ca-message-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          flex-shrink: 0;
        }
        
        .ca-message.user .ca-message-avatar {
          background: #0066cc;
          color: white;
        }
        
        .ca-message.bot .ca-message-avatar {
          background: #92f142;
          color: #333;
        }
        
        .ca-sources {
          margin-top: 8px;
          padding: 8px;
          background: #f8f9fa;
          border-radius: 8px;
          font-size: 12px;
        }
        
        .ca-sources-header {
          font-weight: 600;
          margin-bottom: 6px;
          color: #666;
        }
        
        .ca-source-item {
          display: flex;
          align-items: center;
          gap: 6px;
          margin: 4px 0;
          padding: 4px;
          border-radius: 4px;
          background: white;
        }
        
        .ca-source-link {
          color: #0066cc;
          text-decoration: none;
          font-size: 11px;
        }
        
        .ca-source-link:hover {
          text-decoration: underline;
        }
        
        .ca-chat-input {
          padding: 16px;
          border-top: 1px solid #e9ecef;
          display: flex;
          gap: 8px;
          align-items: flex-end;
        }
        
        .ca-input-field {
          flex: 1;
          border: 1px solid #ddd;
          border-radius: 20px;
          padding: 10px 16px;
          font-size: 14px;
          resize: none;
          max-height: 100px;
          min-height: 40px;
        }
        
        .ca-input-field:focus {
          outline: none;
          border-color: #0066cc;
        }
        
        .ca-send-btn {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #0066cc;
          border: none;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }
        
        .ca-send-btn:hover:not(:disabled) {
          background: #0052a3;
        }
        
        .ca-send-btn:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
        
        .ca-typing {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 16px;
          color: #666;
          font-size: 14px;
        }
        
        .ca-typing-dots {
          display: flex;
          gap: 4px;
        }
        
        .ca-typing-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #0066cc;
          animation: typing 1.4s infinite;
        }
        
        .ca-typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .ca-typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
          0%, 60%, 100% { opacity: 0.3; }
          30% { opacity: 1; }
        }
        
        .ca-status {
          padding: 8px 16px;
          background: #f8f9fa;
          border-top: 1px solid #e9ecef;
          font-size: 11px;
          color: #666;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .ca-status-online {
          color: #28a745;
        }
        
        .ca-status-offline {
          color: #dc3545;
        }
        
        @media (max-width: 480px) {
          .ca-chat-interface {
            width: calc(100vw - 40px);
            height: calc(100vh - 100px);
            bottom: 80px;
            right: 20px;
          }
        }
      </style>
      
      <!-- Chat Toggle Button -->
      <button class="ca-chat-toggle" id="ca-chat-toggle" title="Open CA Assistant">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H5.17L4 17.17V4H20V16Z"/>
          <path d="M7 9H17V11H7V9ZM7 12H15V14H7V12Z"/>
        </svg>
      </button>
      
      <!-- Chat Interface -->
      <div class="ca-chat-interface" id="ca-chat-interface">
        <!-- Header -->
        <div class="ca-chat-header">
          <div>
            <div class="ca-chat-title">CA Assistant</div>
            <div class="ca-chat-subtitle">India-specific tax & compliance guidance</div>
          </div>
          <div class="ca-chat-controls">
            <button class="ca-control-btn" id="ca-web-search-toggle" title="Toggle Web Search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3S3 5.91 3 9.5S5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5S14 7.01 14 9.5S11.99 14 9.5 14Z"/>
              </svg>
            </button>
            <button class="ca-control-btn" id="ca-chat-close" title="Close Chat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Messages -->
        <div class="ca-chat-messages" id="ca-chat-messages">
          <div class="ca-message bot">
            <div class="ca-message-avatar">🧮</div>
            <div class="ca-message-bubble">
              Hello! I'm your CA Assistant, specialized in Indian tax laws, GST compliance, and accounting regulations. How can I help you today?
            </div>
          </div>
        </div>
        
        <!-- Typing Indicator -->
        <div class="ca-typing" id="ca-typing" style="display: none;">
          <div class="ca-message-avatar">🧮</div>
          <div>
            <span>Assistant is thinking</span>
            <div class="ca-typing-dots">
              <div class="ca-typing-dot"></div>
              <div class="ca-typing-dot"></div>
              <div class="ca-typing-dot"></div>
            </div>
          </div>
        </div>
        
        <!-- Input -->
        <div class="ca-chat-input">
          <textarea 
            id="ca-input-field" 
            class="ca-input-field" 
            placeholder="Ask about GST, tax compliance, PAN requirements..."
            rows="1"></textarea>
          <button class="ca-send-btn" id="ca-send-btn" disabled>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z"/>
            </svg>
          </button>
        </div>
        
        <!-- Status -->
        <div class="ca-status" id="ca-status">
          <span id="ca-connection-status" class="ca-status-offline">Connecting...</span>
          <span id="ca-web-search-status">Web Search: ${this.webSearchEnabled ? 'ON' : 'OFF'}</span>
        </div>
      </div>
    `;
    
    document.body.appendChild(widget);
  }

  attachEventListeners() {
    // Toggle button
    document.getElementById('ca-chat-toggle').addEventListener('click', () => {
      this.toggleChat();
    });
    
    // Close button
    document.getElementById('ca-chat-close').addEventListener('click', () => {
      this.closeChat();
    });
    
    // Web search toggle
    document.getElementById('ca-web-search-toggle').addEventListener('click', () => {
      this.toggleWebSearch();
    });
    
    // Send button
    document.getElementById('ca-send-btn').addEventListener('click', () => {
      this.sendMessage();
    });
    
    // Input field
    const inputField = document.getElementById('ca-input-field');
    inputField.addEventListener('input', () => {
      this.updateSendButton();
      this.autoResize();
    });
    
    inputField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    // ESC key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.closeChat();
      }
    });
  }

  toggleChat() {
    if (this.isOpen) {
      this.closeChat();
    } else {
      this.openChat();
    }
  }

  openChat() {
    this.isOpen = true;
    document.getElementById('ca-chat-interface').classList.add('open');
    document.getElementById('ca-input-field').focus();
  }

  closeChat() {
    this.isOpen = false;
    document.getElementById('ca-chat-interface').classList.remove('open');
  }

  toggleWebSearch() {
    this.webSearchEnabled = !this.webSearchEnabled;
    const toggle = document.getElementById('ca-web-search-toggle');
    const status = document.getElementById('ca-web-search-status');
    
    if (this.webSearchEnabled) {
      toggle.classList.add('active');
      status.textContent = 'Web Search: ON';
    } else {
      toggle.classList.remove('active');
      status.textContent = 'Web Search: OFF';
    }
  }

  updateSendButton() {
    const input = document.getElementById('ca-input-field');
    const sendBtn = document.getElementById('ca-send-btn');
    sendBtn.disabled = !input.value.trim() || this.isLoading;
  }

  autoResize() {
    const input = document.getElementById('ca-input-field');
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 100) + 'px';
  }

  async checkAPIHealth() {
    try {
      const response = await fetch(`${this.apiBase}/health`);
      const data = await response.json();
      
      if (response.ok && data.status === 'healthy') {
        document.getElementById('ca-connection-status').textContent = 'Online';
        document.getElementById('ca-connection-status').className = 'ca-status-online';
      } else {
        throw new Error('API unhealthy');
      }
    } catch (error) {
      document.getElementById('ca-connection-status').textContent = 'Offline';
      document.getElementById('ca-connection-status').className = 'ca-status-offline';
    }
  }

  addMessage(content, isUser = false, sources = null) {
    const messagesContainer = document.getElementById('ca-chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `ca-message ${isUser ? 'user' : 'bot'}`;
    
    messageDiv.innerHTML = `
      <div class="ca-message-avatar">${isUser ? '👤' : '🧮'}</div>
      <div class="ca-message-bubble">
        <div>${content}</div>
        ${sources ? this.createSourcesHTML(sources) : ''}
      </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  createSourcesHTML(sources) {
    if (!sources || sources.length === 0) return '';
    
    const sourcesHTML = sources.slice(0, 3).map(source => {
      if (source.type === 'web' && source.url) {
        return `
          <div class="ca-source-item">
            🌐 <a href="${source.url}" target="_blank" class="ca-source-link">${source.title}</a>
          </div>
        `;
      } else {
        return `
          <div class="ca-source-item">
            📄 <span class="ca-source-link">${source.source || 'Document'}</span>
          </div>
        `;
      }
    }).join('');
    
    return `
      <div class="ca-sources">
        <div class="ca-sources-header">Sources:</div>
        ${sourcesHTML}
      </div>
    `;
  }

  showTyping() {
    document.getElementById('ca-typing').style.display = 'flex';
    const messagesContainer = document.getElementById('ca-chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  hideTyping() {
    document.getElementById('ca-typing').style.display = 'none';
  }

  async sendMessage() {
    const input = document.getElementById('ca-input-field');
    const message = input.value.trim();
    
    if (!message || this.isLoading) return;
    
    // Add user message
    this.addMessage(message, true);
    input.value = '';
    this.updateSendButton();
    this.autoResize();
    
    // Show typing indicator
    this.isLoading = true;
    this.showTyping();
    
    try {
      const response = await fetch(`${this.apiBase}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          web_search_enabled: this.webSearchEnabled,
          session_id: this.sessionId
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        this.addMessage(data.response, false, data.sources);
        this.checkAPIHealth(); // Update status
      } else {
        this.addMessage(`Sorry, I encountered an error: ${data.detail || 'Unknown error'}`, false);
      }
    } catch (error) {
      this.addMessage(`I'm currently offline. Please try again later. (${error.message})`, false);
    } finally {
      this.isLoading = false;
      this.hideTyping();
      this.updateSendButton();
    }
  }
}

// Initialize the chatbot widget when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Wait a bit to avoid conflicts with React hydration
  setTimeout(() => {
    window.caChatbot = new CAChatbotWidget({
      apiBase: 'https://ca-chatbot-ld8v.onrender.com',
      webSearchEnabled: true
    });
  }, 2000);
});
