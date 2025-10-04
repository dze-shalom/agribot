# AgriBot - Conversation Logic (Option B) ✅

## How It Works Now

### **One Conversation Per Session**

Users have **ONE continuous conversation** until they manually click **"New Conversation"** button.

---

## User Experience

### **Scenario 1: Normal Chatting**
1. User logs in
2. Sends message: "How to plant cassava?" → **Conversation #1 created**
3. Sends message: "What fertilizer?" → **Same Conversation #1** (adds message)
4. Sends message: "When to harvest?" → **Same Conversation #1** (adds message)
5. Sends 10 more messages → **Same Conversation #1** (13 messages total)

**Database Result:**
- 13 messages = **1 conversation**
- Dashboard shows: **1 conversation** ✅

---

### **Scenario 2: Starting New Conversation**
1. User has existing conversation with 13 messages
2. User clicks **"New Conversation"** button
3. System creates fresh conversation
4. Next message: "Tell me about corn" → **Conversation #2 created**
5. More messages → **Conversation #2** continues

**Database Result:**
- Old conversation: 13 messages
- New conversation: started fresh
- Dashboard shows: **2 conversations** ✅

---

### **Scenario 3: Multiple Users**
**User A:**
- Sends 5 messages without clicking "New Conversation" → **1 conversation**

**User B:**
- Sends 20 messages → **1 conversation**
- Clicks "New Conversation" button → **2 conversations total**
- Sends 5 more messages → **Still 2 conversations**

**Dashboard Shows:**
- Total conversations: **3** (1 from User A, 2 from User B) ✅

---

## Technical Implementation

### **Backend:**
- ✅ `core/conversation_manager.py` - Reuses conversation per session
- ✅ `app/routes/chat.py` - Gets or creates conversation (session-based)
- ✅ **NEW** Endpoint: `POST /chat/conversation/new` - Starts fresh conversation

### **Frontend:**
- ✅ `templates/chatbot.html` - "New Conversation" button
- ✅ Calls `/chat/conversation/new` when clicked
- ✅ Resets UI and clears conversation context

---

## API Endpoints

### **1. Send Message (Continues Current Conversation)**
```javascript
POST /chat/message
{
  "message": "How to plant cassava?",
  "user_name": "John",
  "user_region": "centre"
}
```
**Behavior:** Adds to existing conversation or creates first one

---

### **2. Start New Conversation**
```javascript
POST /chat/conversation/new
```
**Behavior:** Ends current conversation, next message creates new one

**Response:**
```json
{
  "success": true,
  "message": "New conversation started. Your next message will create a fresh conversation."
}
```

---

## Dashboard Counting

**Conversations = Number of times user clicked "New Conversation" + 1**

Example:
- User never clicks "New Conversation", sends 100 messages → **1 conversation**
- User clicks "New Conversation" 5 times during session → **6 conversations total**

This accurately reflects **meaningful conversation sessions** rather than message count.

---

## Session Timeout

Conversations also reset if user is inactive for **120 minutes** (2 hours).

After timeout, next message automatically creates new conversation.

---

## Comparison with Other Options

### ❌ **Option A (Rejected):**
- Every message = new conversation
- 100 messages = 100 conversations
- Dashboard: Inflated numbers

### ✅ **Option B (Current):**
- One conversation per session
- User controls with "New Conversation" button
- Dashboard: Meaningful conversation count

### **Option C (Alternative):**
- New conversation when topic changes
- Automatic detection
- More complex, less control

---

## Migration Note

**Old conversations** (before this change) remain unchanged in database.

**New behavior** starts from now:
- Messages go to same conversation until "New Conversation" clicked
- Dashboard will show accurate counts going forward

---

## Frontend Integration

The "New Conversation" button already exists in `chatbot.html`:

```html
<button class="clear-btn" onclick="clearConversation()">New Conversation</button>
```

**When clicked:**
1. Calls `POST /chat/conversation/new`
2. Clears chat UI
3. Resets conversation context
4. Next message starts fresh conversation

---

## Testing

**Test the flow:**
1. Log in to chatbot
2. Send 3 messages → Check dashboard shows **1 conversation**
3. Click "New Conversation" button
4. Send 2 more messages → Check dashboard shows **2 conversations**
5. Repeat → Each "New Conversation" click increments count

---

## Benefits

✅ **Accurate counting** - Reflects real conversation sessions
✅ **User control** - Users decide when to start fresh
✅ **Context maintained** - AI remembers conversation history
✅ **Clean UX** - Clear "New Conversation" button
✅ **Dashboard clarity** - Numbers match user behavior
