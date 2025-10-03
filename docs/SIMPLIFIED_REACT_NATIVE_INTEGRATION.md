# AgriBot React Native Integration - Simplified (No Separate Login)

**For apps where users are already authenticated in your main app**

---

## Overview

This integration allows your React Native app to use AgriBot without requiring users to create separate AgriBot accounts. Your app simply passes user context (name, region, language) to AgriBot with each request.

---

## Two Integration Approaches

### **Option 1: Anonymous Mode (Simplest)**
Users chat with AgriBot without any authentication. Perfect for quick integration.

### **Option 2: User Context Mode (Recommended)**
Your app passes user info to AgriBot for personalized responses.

---

## Option 1: Anonymous Mode (Simplest)

### Installation

```bash
npm install axios react-native-image-picker
```

### Configuration

```javascript
// config/agribot.js
export const AGRIBOT_CONFIG = {
  BASE_URL: 'http://your-server-ip:5000',
  ANONYMOUS_MODE: true  // No auth required
};
```

### Simple API Service

```javascript
// services/AgribotAPI.js
import axios from 'axios';
import { AGRIBOT_CONFIG } from '../config/agribot';

class AgribotAPI {
  constructor() {
    this.client = axios.create({
      baseURL: AGRIBOT_CONFIG.BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  // Simple chat - no auth needed
  async sendMessage(message, userContext = {}) {
    const response = await this.client.post('/api/chat/anonymous', {
      message,
      user_context: {
        name: userContext.name || 'Friend',
        region: userContext.region || 'Unknown',
        language: userContext.language || 'auto'
      }
    });
    return response.data;
  }

  // Upload image for disease detection
  async uploadImage(imageUri, userContext = {}) {
    const formData = new FormData();
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'plant_image.jpg'
    });
    formData.append('user_context', JSON.stringify({
      name: userContext.name || 'Friend',
      region: userContext.region || 'Unknown',
      language: userContext.language || 'auto'
    }));

    const response = await this.client.post('/api/chat/upload-anonymous', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  // Interpret sensor data
  async interpretSensorData(sensorData, userContext = {}) {
    const response = await this.client.post('/api/sensors/interpret-anonymous', {
      ...sensorData,
      user_context: {
        language: userContext.language || 'auto'
      }
    });
    return response.data;
  }
}

export default new AgribotAPI();
```

### Simple Chat Component

```javascript
// screens/ChatScreen.js
import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator
} from 'react-native';
import AgribotAPI from '../services/AgribotAPI';

export default function ChatScreen({ userInfo }) {
  // userInfo comes from your app's auth context
  // e.g., { name: 'John', region: 'Centre', language: 'en' }

  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      text: `Hello ${userInfo.name || 'Friend'}! I'm AgriBot. How can I help you today?`,
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef(null);

  const addMessage = (message) => {
    setMessages((prev) => [...prev, message]);
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    addMessage(userMessage);
    setInputText('');
    setLoading(true);

    try {
      const response = await AgribotAPI.sendMessage(inputText, {
        name: userInfo.name,
        region: userInfo.region,
        language: userInfo.language || 'auto'
      });

      const botMessage = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'bot',
        timestamp: new Date(),
        suggestions: response.suggestions
      };

      addMessage(botMessage);
    } catch (error) {
      addMessage({
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        error: true
      });
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = ({ item }) => (
    <View
      style={[
        styles.messageBubble,
        item.sender === 'user' ? styles.userBubble : styles.botBubble
      ]}
    >
      <Text style={styles.messageText}>{item.text}</Text>

      {item.suggestions && item.suggestions.length > 0 && (
        <View style={styles.suggestionsContainer}>
          {item.suggestions.map((suggestion, index) => (
            <TouchableOpacity
              key={index}
              style={styles.suggestionChip}
              onPress={() => setInputText(suggestion)}
            >
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      <Text style={styles.timestamp}>
        {item.timestamp.toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        })}
      </Text>
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messageList}
        contentContainerStyle={styles.messageListContent}
      />

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color="#4CAF50" />
          <Text style={styles.loadingText}>AgriBot is thinking...</Text>
        </View>
      )}

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Ask me anything about farming..."
          multiline
          maxLength={500}
        />

        <TouchableOpacity
          style={[styles.sendButton, !inputText.trim() && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={!inputText.trim() || loading}
        >
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  messageList: {
    flex: 1
  },
  messageListContent: {
    padding: 10
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 15,
    marginBottom: 10
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#4CAF50'
  },
  botBubble: {
    alignSelf: 'flex-start',
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e0e0e0'
  },
  messageText: {
    fontSize: 15,
    color: '#333'
  },
  timestamp: {
    fontSize: 10,
    color: '#999',
    marginTop: 5,
    alignSelf: 'flex-end'
  },
  suggestionsContainer: {
    marginTop: 10,
    flexDirection: 'row',
    flexWrap: 'wrap'
  },
  suggestionChip: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    marginRight: 5,
    marginBottom: 5
  },
  suggestionText: {
    color: '#1976d2',
    fontSize: 13
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    backgroundColor: '#f0f0f0'
  },
  loadingText: {
    marginLeft: 10,
    color: '#666'
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    alignItems: 'center'
  },
  input: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    maxHeight: 100,
    marginRight: 10
  },
  sendButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc'
  },
  sendButtonText: {
    color: 'white',
    fontWeight: 'bold'
  }
});
```

### Usage in Your App

```javascript
// In your main app navigation
import ChatScreen from './screens/ChatScreen';
import { useAuth } from './context/AuthContext'; // Your app's auth

function MainApp() {
  const { user } = useAuth(); // Your app's authenticated user

  return (
    <Stack.Navigator>
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Chat">
        {(props) => (
          <ChatScreen
            {...props}
            userInfo={{
              name: user.name,
              region: user.region,
              language: user.preferredLanguage || 'en'
            }}
          />
        )}
      </Stack.Screen>
    </Stack.Navigator>
  );
}
```

---

## Option 2: User Context Mode (Recommended)

This approach creates a temporary session for the user without requiring separate login.

### Backend: Add Anonymous Endpoints

Add to `app/routes/chat.py`:

```python
@chat_bp.route('/anonymous', methods=['POST'])
def chat_anonymous():
    """
    Anonymous chat endpoint - no authentication required
    User context is passed with each request
    """
    try:
        data = request.json
        user_input = data.get('message', '')
        user_context = data.get('user_context', {})

        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        # Create temporary session ID based on user context
        session_id = f"anon_{user_context.get('name', 'guest')}_{int(time.time())}"

        # Process message with user context
        response = current_app.agribot.process_message(
            user_input=user_input,
            user_id=None,  # No user ID for anonymous
            user_context=user_context,
            language=user_context.get('language', 'auto')
        )

        return jsonify({
            'success': True,
            'response': response.get('response', ''),
            'suggestions': response.get('suggestions', []),
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Anonymous chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### React Native: Enhanced API with Session

```javascript
// services/AgribotAPI.js (Enhanced)
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AGRIBOT_CONFIG } from '../config/agribot';

class AgribotAPI {
  constructor() {
    this.client = axios.create({
      baseURL: AGRIBOT_CONFIG.BASE_URL,
      timeout: 30000
    });
    this.sessionId = null;
  }

  async getSessionId() {
    if (!this.sessionId) {
      this.sessionId = await AsyncStorage.getItem('agribot_session_id');
    }
    return this.sessionId;
  }

  async setSessionId(sessionId) {
    this.sessionId = sessionId;
    await AsyncStorage.setItem('agribot_session_id', sessionId);
  }

  async sendMessage(message, userContext) {
    const sessionId = await this.getSessionId();

    const response = await this.client.post('/api/chat/anonymous', {
      message,
      user_context: {
        name: userContext.name || 'Friend',
        region: userContext.region || 'Unknown',
        language: userContext.language || 'auto',
        session_id: sessionId
      }
    });

    // Save session ID for conversation continuity
    if (response.data.session_id) {
      await this.setSessionId(response.data.session_id);
    }

    return response.data;
  }

  async clearSession() {
    this.sessionId = null;
    await AsyncStorage.removeItem('agribot_session_id');
  }
}

export default new AgribotAPI();
```

---

## Sensor Integration (No Auth)

### Simple Sensor Analysis

```javascript
// In your sensor dashboard
import AgribotAPI from '../services/AgribotAPI';

function SensorDashboard({ userInfo, sensorData }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeSensors = async () => {
    setLoading(true);
    try {
      const result = await AgribotAPI.interpretSensorData(
        {
          temperature: sensorData.temperature,
          humidity: sensorData.humidity,
          soilMoisture: sensorData.soilMoisture,
          phValue: sensorData.phValue,
          batteryLevel: sensorData.batteryLevel,
          cropType: 'maize'
        },
        {
          language: userInfo.language || 'auto'
        }
      );

      setAnalysis(result.data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      {/* Sensor readings display */}
      <TouchableOpacity onPress={analyzeSensors}>
        <Text>🤖 Get AI Analysis</Text>
      </TouchableOpacity>

      {analysis && (
        <View>
          <Text>{analysis.ai_interpretation}</Text>
          {/* Display alerts and recommendations */}
        </View>
      )}
    </View>
  );
}
```

---

## Complete Minimal Integration

### 1. Install

```bash
npm install axios
```

### 2. Create API Service

```javascript
// services/AgribotAPI.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://YOUR_SERVER_IP:5000',
  timeout: 30000
});

export const AgribotAPI = {
  async chat(message, userName, userRegion, language = 'auto') {
    const response = await api.post('/api/chat/anonymous', {
      message,
      user_context: { name: userName, region: userRegion, language }
    });
    return response.data;
  },

  async analyzeSensor(sensorData, language = 'auto') {
    const response = await api.post('/api/sensors/interpret-anonymous', {
      ...sensorData,
      user_context: { language }
    });
    return response.data;
  }
};
```

### 3. Use in Your App

```javascript
// In any screen
import { AgribotAPI } from '../services/AgribotAPI';

function MyScreen() {
  const { user } = useAuth(); // Your app's auth

  const askAgribot = async (question) => {
    const response = await AgribotAPI.chat(
      question,
      user.name,
      user.region,
      user.language
    );
    console.log(response.response);
  };

  return (
    <Button title="Ask AgriBot" onPress={() => askAgribot('How to plant maize?')} />
  );
}
```

---

## Summary

**For your use case (users already authenticated in your app):**

✅ Use **Anonymous Mode** or **User Context Mode**
✅ No separate AgriBot login required
✅ Pass user info (name, region, language) with each request
✅ AgriBot personalizes responses based on user context
✅ Much simpler integration!

**What you need to do:**

1. Update your AgriBot server to add anonymous endpoints (I can help with this)
2. Use the simplified API service in your React Native app
3. Pass user context from your app's auth to AgriBot
4. Done! 🎉

Would you like me to create the anonymous endpoints for the AgriBot backend?
