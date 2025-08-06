/**
 * CA Chatbot Embed Script
 * Simple one-line integration for any website
 * 
 * Usage: <script src="ca-chatbot-embed.js"></script>
 */

(function() {
  'use strict';
  
  // Configuration
  const CONFIG = {
    apiBase: 'https://ca-chatbot-ld8v.onrender.com',
    webSearchEnabled: true,
    position: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
    theme: 'professional' // professional, modern, minimal
  };

  // Prevent multiple initializations
  if (window.CAChatbotLoaded) return;
  window.CAChatbotLoaded = true;

  // CSS Styles
  const styles = `
    .ca-embed-widget {
      position: fixed;
      z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .ca-embed-widget.bottom-right {
      bottom: 20px;
      right: 20px;
    }
    
    .ca-embed-toggle {
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
    
    .ca-embed-toggle:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 16px rgba(0, 102, 204, 0.4);
    }
    
    .ca-embed-interface {
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
    
    .ca-embed-interface.open {
      display: flex;
      animation: ca-slideUp 0.3s ease;
    }
    
    @keyframes ca-slideUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .ca-embed-header {
      background: linear-gradient(135deg, #0066cc, #004499);
      color: white;
      padding: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    
    .ca-embed-title {
      font-weight: 600;
      font-size: 16px;
    }
    
    .ca-embed-subtitle {
      font-size: 12px;
      opacity: 0.9;
      margin-top: 2px;
    }
    
    .ca-embed-close {
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
    }
    
    .ca-embed-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .ca-embed-message {
      display: flex;
      gap: 8px;
      max-width: 85%;
    }
    
    .ca-embed-message.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }
    
    .ca-embed-bubble {
      padding: 12px 16px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.4;
    }
    
    .ca-embed-message.user .ca-embed-bubble {
      background: #0066cc;
      color: white;
    }
    
    .ca-embed-message.bot .ca-embed-bubble {
      background: #f1f3f5;
      color: #333;
    }
    
    .ca-embed-input {
      padding: 16px;
      border-top: 1px solid #e9ecef;
      display: flex;
      gap: 8px;
      align-items: flex-end;
    }
    
    .ca-embed-textarea {
      flex: 1;
      border: 1px solid #ddd;
      border-radius: 20px;
      padding: 10px 16px;
      font-size: 14px;
      resize: none;
      max-height: 100px;
      min-height: 40px;
      font-family: inherit;
    }
    
    .ca-embed-send {
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
    }
    
    .ca-embed-send:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
    
    @media (max-width: 480px) {
      .ca-embed-interface {
        width: calc(100vw - 40px);
        height: calc(100vh - 100px);
      }
    }
  `;

  // Inject styles
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);

  // Create widget HTML
  const widgetHTML = `
    <div class="ca-embed-widget ${CONFIG.position}">
      <button class="ca-embed-toggle" id="ca-embed-toggle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H5.17L4 17.17V4H20V16Z"/>
        </svg>
      </button>
      
      <div class="ca-embed-interface" id="ca-embed-interface">
        <div class="ca-embed-header">
          <div>
            <div class="ca-embed-title">CA Assistant</div>
            <div class="ca-embed-subtitle">India-specific tax & compliance guidance</div>
          </div>
          <button class="ca-embed-close" id="ca-embed-close">×</button>
        </div>
        
        <div class="ca-embed-messages" id="ca-embed-messages">
          <div class="ca-embed-message bot">
            <div class="ca-embed-bubble">
              Hello! I'm your CA Assistant, specialized in Indian tax laws, GST compliance, and accounting regulations. How can I help you today?
            </div>
          </div>
        </div>
        
        <div class="ca-embed-input">
          <textarea 
            id="ca-embed-textarea" 
            class="ca-embed-textarea" 
            placeholder="Ask about GST, tax compliance, PAN requirements..."
            rows="1"></textarea>
          <button class="ca-embed-send" id="ca-embed-send" disabled>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  `;

  // Widget functionality
  class CAEmbedWidget {
    constructor() {
      this.isOpen = false;
      this.isLoading = false;
      this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      
      this.init();
    }

    init() {
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.create());
      } else {
        this.create();
      }
    }

    create() {
      // Create widget container
      const container = document.createElement('div');
      container.innerHTML = widgetHTML;
      document.body.appendChild(container.firstElementChild);
      
      this.attachEvents();
    }

    attachEvents() {
      document.getElementById('ca-embed-toggle').addEventListener('click', () => this.toggle());
      document.getElementById('ca-embed-close').addEventListener('click', () => this.close());
      document.getElementById('ca-embed-send').addEventListener('click', () => this.sendMessage());
      
      const textarea = document.getElementById('ca-embed-textarea');
      textarea.addEventListener('input', () => this.updateSendButton());
      textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    toggle() {
      if (this.isOpen) {
        this.close();
      } else {
        this.open();
      }
    }

    open() {
      this.isOpen = true;
      document.getElementById('ca-embed-interface').classList.add('open');
      document.getElementById('ca-embed-textarea').focus();
    }

    close() {
      this.isOpen = false;
      document.getElementById('ca-embed-interface').classList.remove('open');
    }

    updateSendButton() {
      const textarea = document.getElementById('ca-embed-textarea');
      const sendBtn = document.getElementById('ca-embed-send');
      sendBtn.disabled = !textarea.value.trim() || this.isLoading;
    }

    addMessage(content, isUser = false) {
      const messagesContainer = document.getElementById('ca-embed-messages');
      const messageDiv = document.createElement('div');
      messageDiv.className = `ca-embed-message ${isUser ? 'user' : 'bot'}`;
      messageDiv.innerHTML = `<div class="ca-embed-bubble">${content}</div>`;
      
      messagesContainer.appendChild(messageDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async sendMessage() {
      const textarea = document.getElementById('ca-embed-textarea');
      const message = textarea.value.trim();
      
      if (!message || this.isLoading) return;
      
      // Add user message
      this.addMessage(message, true);
      textarea.value = '';
      this.updateSendButton();
      
      // Show loading
      this.isLoading = true;
      this.addMessage('Thinking...', false);
      
      try {
        const response = await fetch(`${CONFIG.apiBase}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: message,
            web_search_enabled: CONFIG.webSearchEnabled,
            session_id: this.sessionId
          })
        });
        
        const data = await response.json();
        
        // Remove "Thinking..." message
        const messages = document.getElementById('ca-embed-messages');
        messages.removeChild(messages.lastElementChild);
        
        if (response.ok) {
          this.addMessage(data.response, false);
        } else {
          this.addMessage('Sorry, I encountered an error. Please try again.', false);
        }
      } catch (error) {
        // Remove "Thinking..." message
        const messages = document.getElementById('ca-embed-messages');
        messages.removeChild(messages.lastElementChild);
        this.addMessage('I\'m currently offline. Please try again later.', false);
      } finally {
        this.isLoading = false;
        this.updateSendButton();
      }
    }
  }

  // Initialize widget
  new CAEmbedWidget();
})();
