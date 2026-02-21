/**
 * AI Chatbot for Government Scheme Portal
 * Rule-based chatbot with multi-language support
 */

class GovernmentSchemeChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isTyping = false;
        this.currentLanguage = 'en';
        this.init();
    }

    init() {
        // Create chatbot UI
        this.createChatbotUI();
        
        // Add event listeners
        this.setupEventListeners();
        
        // Show welcome message
        setTimeout(() => {
            this.addBotMessage(this.getWelcomeMessage());
        }, 500);
    }

    createChatbotUI() {
        const chatbotHTML = `
            <button class="chatbot-toggle" id="chatbotToggle" aria-label="Open chatbot">
                💬
            </button>
            <div class="chatbot-panel" id="chatbotPanel">
                <div class="chatbot-header">
                    <span class="chatbot-title">
                        <span>🏛️</span>
                        <span data-i18n="chatbot_title">Govt Scheme Assistant</span>
                    </span>
                    <button class="chatbot-close" id="chatbotClose" aria-label="Close chatbot">×</button>
                </div>
                <div class="chatbot-messages" id="chatbotMessages">
                    <div class="chatbot-typing" id="chatbotTyping">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                    </div>
                </div>
                <div class="quick-suggestions">
                    <button class="quick-btn" data-query="student schemes">🎓 Student</button>
                    <button class="quick-btn" data-query="farmer schemes">🚜 Farmer</button>
                    <button class="quick-btn" data-query="women schemes">👩 Women</button>
                    <button class="quick-btn" data-query="housing schemes">🏠 Housing</button>
                </div>
                <div class="chatbot-input-area">
                    <input type="text" class="chatbot-input" id="chatbotInput" 
                           placeholder="Ask about government schemes..." data-i18n="input_placeholder">
                    <button class="chatbot-send" id="chatbotSend" aria-label="Send message">
                        ➤
                    </button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
        
        // Store references
        this.toggleBtn = document.getElementById('chatbotToggle');
        this.panel = document.getElementById('chatbotPanel');
        this.closeBtn = document.getElementById('chatbotClose');
        this.messagesContainer = document.getElementById('chatbotMessages');
        this.input = document.getElementById('chatbotInput');
        this.sendBtn = document.getElementById('chatbotSend');
        this.typingIndicator = document.getElementById('chatbotTyping');
        this.quickButtons = document.querySelectorAll('.quick-btn');
    }

    setupEventListeners() {
        // Toggle chatbot
        this.toggleBtn.addEventListener('click', () => this.toggle());
        this.closeBtn.addEventListener('click', () => this.toggle());
        
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Quick suggestion buttons
        this.quickButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                this.input.value = query;
                this.sendMessage();
            });
        });
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.panel.classList.toggle('active', this.isOpen);
        
        if (this.isOpen) {
            this.input.focus();
        }
    }

    getWelcomeMessage() {
        const messages = {
            'en': 'Namaste! 🙏 I am your Government Scheme Assistant. I can help you find:\n\n' +
                  '🎓 Student Schemes (scholarships, education)\n' +
                  '🚜 Farmer Schemes (PM Kisan, crop insurance)\n' +
                  '👩 Women Schemes (Beti Bachao, Sukanya Samriddhi)\n' +
                  '🏠 Housing Schemes (PMAY, rural/urban)\n' +
                  '💼 Employment (MGNREGA, Mudra loans)\n' +
                  '❤️ Health (Ayushman Bharat, insurance)\n\n' +
                  'Just tell me what category interests you!',
            'hi': 'नमस्ते! 🙏 मैं आपका सरकारी योजना सहायक हूं। मैं आपकी मदद कर सकता हूं:\n\n' +
                  '🎓 छात्र योजनाएं\n' +
                  '🚜 किसान योजनाएं\n' +
                  '👩 महिला योजनाएं\n' +
                  '🏠 आवास योजनाएं\n' +
                  '💼 रोजगार योजनाएं\n' +
                  '❤️ स्वास्थ्य योजनाएं\n\n' +
                  'बस मुझे बताएं कि आपकी रुचि किस श्रेणी में है!',
            'mr': 'नमस्कार! 🙏 मी तुमचा सरकारी योजना सहायक आहे. मी तुम्हाला मदत करू शकतो:\n\n' +
                  '🎓 विद्यार्थी योजना\n' +
                  '🚜 शेतकरी योजना\n' +
                  '👩 महिला योजना\n' +
                  '🏠 घर योजना\n' +
                  '💼 रोजगार योजना\n' +
                  '❤️ आरोग्य योजना\n\n' +
                  'फक्त सांगा तुम्हाला कोणती योजना हवी आहे!'
        };
        return messages[this.currentLanguage] || messages['en'];
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;
        
        // Add user message
        this.addUserMessage(message);
        this.input.value = '';
        
        // Show typing indicator
        this.showTyping();
        
        try {
            // Send to backend API
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    language: this.currentLanguage
                })
            });
            
            const data = await response.json();
            
            // Hide typing and show response
            this.hideTyping();
            this.addBotMessage(data.response);
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTyping();
            this.addBotMessage(this.getErrorMessage());
        }
    }

    addUserMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message user';
        messageEl.textContent = message;
        
        // Insert before typing indicator
        this.messagesContainer.insertBefore(messageEl, this.typingIndicator);
        this.scrollToBottom();
    }

    addBotMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message bot';
        messageEl.textContent = message;
        
        this.messagesContainer.insertBefore(messageEl, this.typingIndicator);
        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        this.typingIndicator.classList.add('active');
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        this.typingIndicator.classList.remove('active');
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    getErrorMessage() {
        const messages = {
            'en': 'Sorry, I encountered an error. Please try again or contact support.',
            'hi': 'क्षमा करें, मुझे एक त्रुटि मिली। कृपया पुनः प्रयास करें।',
            'mr': 'माफ करा, मला एक त्रुटी आली. कृपया पुन्हा प्रयत्न करा.'
        };
        return messages[this.currentLanguage] || messages['en'];
    }

    setLanguage(lang) {
        this.currentLanguage = lang;
        
        // Update placeholders and titles
        const inputPlaceholder = {
            'en': 'Ask about government schemes...',
            'hi': 'सरकारी योजनाओं के बारे में पूछें...',
            'mr': 'सरकारी योजनाबद्दल विचारा...'
        };
        
        const chatbotTitle = {
            'en': 'Govt Scheme Assistant',
            'hi': 'सरकारी योजना सहायक',
            'mr': 'सरकारी योजना सहायक'
        };
        
        this.input.placeholder = inputPlaceholder[lang] || inputPlaceholder['en'];
        document.querySelector('.chatbot-title span:last-child').textContent = chatbotTitle[lang] || chatbotTitle['en'];
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new GovernmentSchemeChatbot();
});

// Export for global access
window.GovernmentSchemeChatbot = GovernmentSchemeChatbot;
