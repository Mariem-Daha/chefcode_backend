# ChefCode ChatGPT Multi-Language Support Guide

## Overview
The ChefCode ChatGPT integration now supports both **English** and **Italian** responses. The system dynamically adjusts the AI's language based on the request.

## Features
- ✅ Default language: **English** (`en`)
- ✅ Supported languages: **English** (`en`) and **Italian** (`it`)
- ✅ Language-specific system prompts
- ✅ Language-specific context templates
- ✅ Automatic fallback to English for invalid language codes
- ✅ Secure API key management via `.env` file

## API Endpoint

### POST `/api/chatgpt-smart`

**Request Body:**
```json
{
  "prompt": "Your question or request here",
  "language": "en"  // Optional: "en" or "it" (defaults to "en")
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "content": "AI response in the requested language"
      }
    }
  ]
}
```

## Language Configuration

### System Prompts

**English:**
```
You are ChefCode AI Assistant. Always respond in fluent, clear English.
```

**Italian:**
```
Sei l'assistente AI di ChefCode. Rispondi sempre in italiano chiaro e corretto.
```

### Context Templates

Both languages include context about:
- ChefCode being a restaurant inventory and recipe management system
- User managing inventory, recipes, and production tasks
- Request for helpful, specific advice
- Concise and actionable responses

## Testing

### 1. Test with PowerShell (Windows)

**Test English (Default):**
```powershell
$body = @{
    prompt = "How do I organize my inventory?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/chatgpt-smart" -Method Post -Body $body -ContentType "application/json"
```

**Test Italian:**
```powershell
$body = @{
    prompt = "Come posso organizzare il mio inventario?"
    language = "it"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/chatgpt-smart" -Method Post -Body $body -ContentType "application/json"
```

### 2. Test with curl (Linux/Mac/Git Bash)

**Test English (Default):**
```bash
curl -X POST "http://127.0.0.1:8000/api/chatgpt-smart" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How do I organize my inventory?"}'
```

**Test English (Explicit):**
```bash
curl -X POST "http://127.0.0.1:8000/api/chatgpt-smart" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How do I organize my inventory?", "language": "en"}'
```

**Test Italian:**
```bash
curl -X POST "http://127.0.0.1:8000/api/chatgpt-smart" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Come posso organizzare il mio inventario?", "language": "it"}'
```

### 3. Test with JavaScript (Frontend)

**Using the ChefCodeAPI class:**

```javascript
// Initialize API
const api = new ChefCodeAPI('http://127.0.0.1:8000');

// Test English (default)
const englishResponse = await api.sendChatMessage("How do I organize my inventory?");
console.log('English:', englishResponse);

// Test English (explicit)
const englishResponseExplicit = await api.sendChatMessage("How do I organize my inventory?", "en");
console.log('English:', englishResponseExplicit);

// Test Italian
const italianResponse = await api.sendChatMessage("Come posso organizzare il mio inventario?", "it");
console.log('Italian:', italianResponse);
```

### 4. Test with FastAPI Docs (Swagger UI)

1. Open browser: `http://127.0.0.1:8000/docs`
2. Find `POST /api/chatgpt-smart` endpoint
3. Click "Try it out"
4. Enter test data:
   ```json
   {
     "prompt": "How do I organize my inventory?",
     "language": "en"
   }
   ```
5. Click "Execute"
6. View response

## Frontend Integration

### React Native (Mobile App)

```javascript
// In your component
const sendMessage = async () => {
  try {
    // Get user's preferred language from settings or device
    const userLanguage = await getUserLanguage(); // 'en' or 'it'
    
    const response = await api.sendChatMessage(
      userMessage,
      userLanguage
    );
    
    const aiResponse = response.choices[0].message.content;
    setMessages([...messages, { role: 'assistant', content: aiResponse }]);
  } catch (error) {
    console.error('Chat error:', error);
  }
};
```

### Web Interface

```javascript
// Add language selector to your UI
function sendChatMessage() {
  const prompt = document.getElementById('chatInput').value;
  const language = document.getElementById('languageSelect').value; // 'en' or 'it'
  
  api.sendChatMessage(prompt, language)
    .then(response => {
      const message = response.choices[0].message.content;
      displayMessage(message);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}
```

### HTML Language Selector Example

```html
<select id="languageSelect">
  <option value="en">English</option>
  <option value="it">Italiano</option>
</select>

<input type="text" id="chatInput" placeholder="Ask a question...">
<button onclick="sendChatMessage()">Send</button>
```

## Environment Setup

### .env File
Create a `.env` file in the Backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Security Notes
- ✅ API key is loaded from environment variables (not hardcoded)
- ✅ `.env` file should be in `.gitignore`
- ✅ Never commit API keys to version control
- ✅ Use separate API keys for development and production

## Health Check Endpoint

### GET `/api/chat/health`

Check ChatGPT integration status and supported languages:

```bash
curl http://127.0.0.1:8000/api/chat/health
```

**Response:**
```json
{
  "status": "available",
  "message": "ChatGPT integration ready",
  "supported_languages": ["en", "it"],
  "default_language": "en"
}
```

## Error Handling

### Mock Response (No API Key)
If `OPENAI_API_KEY` is not set, the endpoint returns a helpful message in the requested language:

**English:**
```
ChatGPT integration ready. Please set OPENAI_API_KEY environment variable to enable AI functionality.
```

**Italian:**
```
Integrazione ChatGPT pronta. Imposta la variabile d'ambiente OPENAI_API_KEY per abilitare la funzionalità AI.
```

### API Errors
Errors are returned in the requested language:

**English:** `ChatGPT error: [error details]`  
**Italian:** `Errore ChatGPT: [error details]`

## Example Questions

### English Examples
- "How do I organize my inventory?"
- "What's the best way to track expiration dates?"
- "How can I calculate recipe costs?"
- "Give me tips for reducing food waste"

### Italian Examples
- "Come posso organizzare il mio inventario?"
- "Qual è il modo migliore per tracciare le date di scadenza?"
- "Come posso calcolare i costi delle ricette?"
- "Dammi consigli per ridurre gli sprechi alimentari"

## Future Enhancements
- 🔄 Support for additional languages (Spanish, French, German, etc.)
- 🔄 User language preference storage
- 🔄 Auto-detection of user language from browser/device settings
- 🔄 Conversation history with language consistency
- 🔄 Language-specific response formatting

## Troubleshooting

### Issue: Always receiving English responses
- Check that the `language` parameter is being sent in the request body
- Verify the value is exactly `"it"` for Italian
- Check browser console for API request details

### Issue: API key not working
- Verify `.env` file exists in the Backend directory
- Check that the key is formatted correctly: `OPENAI_API_KEY=sk-...`
- Restart the FastAPI server after adding/changing the `.env` file

### Issue: Responses in wrong language
- Verify the OpenAI API account has sufficient credits
- Check the system prompts in `routes/chat.py`
- Test with the `/api/chat/health` endpoint to verify configuration

## Support
For issues or questions, check:
1. FastAPI logs for error details
2. Browser console for frontend errors
3. `/docs` endpoint for API documentation
4. This guide for testing procedures
