# 🔧 CA Chatbot Troubleshooting Guide

## 🚨 **Quick Debugging Steps**

### **Step 1: Check Browser Console**
1. Open your website with the chatbot
2. Press `F12` or right-click → "Inspect Element"
3. Go to the **Console** tab
4. Look for any error messages in red

### **Step 2: Verify Chatbot Visibility**
- ✅ **Expected:** Green chat button in bottom-right corner
- ❌ **If missing:** Check console for JavaScript errors

### **Step 3: Test API Connection**
1. Open browser console
2. Run this command:
```javascript
fetch('https://ca-chatbot-ld8v.onrender.com/health')
  .then(r => r.json())
  .then(d => console.log('API Status:', d))
```
3. **Expected result:** `{status: "healthy", ...}`

## 🐛 **Common Issues & Solutions**

### **Issue 1: Chat Button Not Appearing**

**Symptoms:**
- No green chat button visible
- Console shows JavaScript errors

**Solutions:**
1. **Clear browser cache** (Ctrl+F5)
2. **Check for conflicts** with other scripts
3. **Verify file upload** - ensure complete HTML file uploaded
4. **Wait for initialization** - chatbot loads after 2 seconds

### **Issue 2: Chat Opens But No Response**

**Symptoms:**
- Chat interface opens
- Messages send but no response
- Status shows "Offline"

**Solutions:**
1. **Check API status:**
   ```bash
   curl https://ca-chatbot-ld8v.onrender.com/health
   ```
2. **Verify network connection**
3. **Check browser console** for network errors
4. **Try different message** - test with "Hello"

### **Issue 3: API Connection Errors**

**Symptoms:**
- Console shows fetch errors
- "Network error" messages
- CORS errors

**Solutions:**
1. **Check API URL** in console logs
2. **Verify HTTPS** - ensure secure connection
3. **Test API directly:**
   ```javascript
   fetch('https://ca-chatbot-ld8v.onrender.com/api/chat', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({message: 'test', web_search_enabled: false})
   }).then(r => r.json()).then(console.log)
   ```

### **Issue 4: Styling Problems**

**Symptoms:**
- Wrong colors
- Layout issues
- Mobile display problems

**Solutions:**
1. **Check CSS conflicts** with existing styles
2. **Verify z-index** - chatbot uses `z-index: 999999`
3. **Test on different devices**
4. **Clear browser cache**

## 📊 **Debug Console Commands**

### **Check Chatbot Status:**
```javascript
// Check if chatbot is initialized
console.log('Chatbot element:', document.getElementById('ca-chatbot-widget-container'));

// Check API configuration
console.log('API Base:', 'https://ca-chatbot-ld8v.onrender.com');
```

### **Test API Health:**
```javascript
fetch('https://ca-chatbot-ld8v.onrender.com/health')
  .then(response => response.json())
  .then(data => {
    console.log('API Health:', data);
    console.log('Status:', data.status);
    console.log('Services:', data.services);
  })
  .catch(error => console.error('API Error:', error));
```

### **Test Chat API:**
```javascript
fetch('https://ca-chatbot-ld8v.onrender.com/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'What is GST?',
    web_search_enabled: false,
    session_id: 'test_session'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Chat Response:', data);
  console.log('Response Text:', data.response);
  console.log('Sources:', data.sources);
})
.catch(error => console.error('Chat Error:', error));
```

## 🔍 **Expected Console Output**

### **Successful Initialization:**
```
Initializing CA Chatbot Widget...
CA Chatbot Widget initialized successfully
Checking API health at: https://ca-chatbot-ld8v.onrender.com/health
API health response: {status: "healthy", ...}
API is healthy
```

### **Successful Message Send:**
```
Sending message: What is PAN?
Sending request to: https://ca-chatbot-ld8v.onrender.com/api/chat
Request body: {message: "What is PAN?", web_search_enabled: true, session_id: "..."}
Response status: 200
Response data: {response: "Permanent Account Number (PAN)...", sources: [...]}
```

## 🚀 **Hostinger Deployment Checklist**

### **Pre-Upload:**
- ✅ File size under hosting limits
- ✅ No external dependencies
- ✅ HTTPS API endpoints only

### **Post-Upload:**
- ✅ File uploaded to `public_html`
- ✅ Correct file permissions
- ✅ Website loads without errors
- ✅ Chat button appears
- ✅ API connection works

### **Testing:**
1. **Load website** - check for chat button
2. **Open chat** - verify interface appears
3. **Send test message** - "Hello" or "What is PAN?"
4. **Check response** - should get CA-specific answer
5. **Test web search** - toggle and try current affairs query

## 📞 **Still Having Issues?**

### **Collect Debug Information:**
1. **Browser:** Chrome/Firefox/Safari version
2. **Console errors:** Copy any red error messages
3. **Network tab:** Check for failed requests
4. **API test results:** Run the debug commands above

### **Common Error Messages:**

**"Failed to fetch"**
- Network connectivity issue
- API server might be down
- CORS policy blocking request

**"Unexpected token"**
- Invalid JSON response
- API returning HTML error page
- Server error (500)

**"Cannot read property"**
- JavaScript initialization error
- Missing DOM elements
- Timing issue with page load

### **Quick Fixes:**
1. **Refresh page** (Ctrl+F5)
2. **Try different browser**
3. **Check internet connection**
4. **Wait 30 seconds** for API to wake up (Render free tier)
5. **Test on mobile device**

The chatbot should work perfectly once these issues are resolved! 🎯
