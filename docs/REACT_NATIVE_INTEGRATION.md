# AgriBot React Native Integration Guide

Complete guide for integrating AgriBot chatbot into your React Native agricultural app.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [API Documentation](#api-documentation)
3. [Authentication](#authentication)
4. [Chat Component](#chat-component)
5. [Sensor Integration](#sensor-integration)
6. [Image Upload (Disease Detection)](#image-upload)
7. [Multilingual Support](#multilingual-support)

---

## Quick Start

### 1. Install Dependencies

```bash
npm install axios react-native-image-picker
# or
yarn add axios react-native-image-picker
```

### 2. Configuration

Create `config/agribot.js`:

```javascript
// config/agribot.js
export const AGRIBOT_CONFIG = {
  BASE_URL: 'http://your-server-ip:5000', // Change to your AgriBot server
  API_VERSION: 'v1',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
};

export const API_ENDPOINTS = {
  // Authentication
  LOGIN: '/api/auth/login',
  REGISTER: '/api/auth/register',
  LOGOUT: '/api/auth/logout',
  PROFILE: '/api/auth/profile',
  UPDATE_LANGUAGE: '/api/auth/update-language',

  // Chat
  CHAT_MESSAGE: '/chat/message',
  CHAT_UPLOAD: '/chat/upload',
  CHAT_FEEDBACK: '/chat/feedback',

  // Sensors
  SENSOR_INTERPRET: '/api/sensors/interpret',
  SENSOR_QUICK_CHECK: '/api/sensors/quick-check',
  SENSOR_CHAT: '/api/sensors/chat/sensor-context',
  SENSOR_TRENDS: '/api/sensors/analyze-trends'
};
```

---

## API Documentation

### Base API Service

Create `services/AgribotAPI.js`:

```javascript
// services/AgribotAPI.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AGRIBOT_CONFIG, API_ENDPOINTS } from '../config/agribot';

class AgribotAPI {
  constructor() {
    this.client = axios.create({
      baseURL: AGRIBOT_CONFIG.BASE_URL,
      timeout: AGRIBOT_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add request interceptor for authentication
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          await AsyncStorage.removeItem('auth_token');
          // Navigate to login screen
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email, password) {
    const response = await this.client.post(API_ENDPOINTS.LOGIN, {
      email,
      password
    });

    if (response.data.token) {
      await AsyncStorage.setItem('auth_token', response.data.token);
    }

    return response.data;
  }

  async register(userData) {
    const response = await this.client.post(API_ENDPOINTS.REGISTER, userData);
    return response.data;
  }

  async logout() {
    try {
      await this.client.post(API_ENDPOINTS.LOGOUT);
    } finally {
      await AsyncStorage.removeItem('auth_token');
    }
  }

  async getProfile() {
    const response = await this.client.get(API_ENDPOINTS.PROFILE);
    return response.data;
  }

  async updateLanguage(language) {
    const response = await this.client.post(API_ENDPOINTS.UPDATE_LANGUAGE, {
      language
    });
    return response.data;
  }

  // Chat
  async sendMessage(message, conversationId = null) {
    const response = await this.client.post(API_ENDPOINTS.CHAT_MESSAGE, {
      message,
      conversation_id: conversationId
    });
    return response.data;
  }

  async uploadImage(imageUri, conversationId = null) {
    const formData = new FormData();
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'plant_image.jpg'
    });

    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }

    const response = await this.client.post(API_ENDPOINTS.CHAT_UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    return response.data;
  }

  async sendFeedback(messageId, rating, comment = '') {
    const response = await this.client.post(API_ENDPOINTS.CHAT_FEEDBACK, {
      message_id: messageId,
      rating,
      comment
    });
    return response.data;
  }

  // Sensor Integration
  async interpretSensorData(sensorData) {
    const response = await this.client.post(API_ENDPOINTS.SENSOR_INTERPRET, sensorData);
    return response.data;
  }

  async quickSensorCheck(sensorData) {
    const response = await this.client.post(API_ENDPOINTS.SENSOR_QUICK_CHECK, sensorData);
    return response.data;
  }

  async chatWithSensorContext(message, sensorData, language = 'auto') {
    const response = await this.client.post(API_ENDPOINTS.SENSOR_CHAT, {
      message,
      sensorData,
      language
    });
    return response.data;
  }

  async analyzeSensorTrends(historicalData, cropType = 'default', language = 'auto') {
    const response = await this.client.post(API_ENDPOINTS.SENSOR_TRENDS, {
      historicalData,
      cropType,
      language
    });
    return response.data;
  }
}

export default new AgribotAPI();
```

---

## Authentication

### Auth Hook

Create `hooks/useAuth.js`:

```javascript
// hooks/useAuth.js
import { useState, useEffect, createContext, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import AgribotAPI from '../services/AgribotAPI';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        const profile = await AgribotAPI.getProfile();
        setUser(profile.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await AgribotAPI.login(email, password);
    setUser(response.user);
    return response;
  };

  const register = async (userData) => {
    const response = await AgribotAPI.register(userData);
    return response;
  };

  const logout = async () => {
    await AgribotAPI.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

### Login Screen Example

```javascript
// screens/LoginScreen.js
import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { useAuth } from '../hooks/useAuth';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    setLoading(true);
    try {
      await login(email, password);
      navigation.replace('Home');
    } catch (error) {
      alert('Login failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AgriBot</Text>

      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <TouchableOpacity
        style={styles.button}
        onPress={handleLogin}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? 'Logging in...' : 'Login'}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => navigation.navigate('Register')}>
        <Text style={styles.link}>Don't have an account? Register</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: '#f5f5f5'
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 40,
    color: '#2c3e50'
  },
  input: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#ddd'
  },
  button: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold'
  },
  link: {
    color: '#2196F3',
    textAlign: 'center',
    marginTop: 20
  }
});
```

---

## Chat Component

### Full Chat Screen

Create `screens/ChatScreen.js`:

```javascript
// screens/ChatScreen.js
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Image
} from 'react-native';
import { launchImageLibrary, launchCamera } from 'react-native-image-picker';
import AgribotAPI from '../services/AgribotAPI';

export default function ChatScreen() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const flatListRef = useRef(null);

  useEffect(() => {
    // Add welcome message
    addMessage({
      id: 'welcome',
      text: 'Hello! I\'m AgriBot, your agricultural assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date()
    });
  }, []);

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
      const response = await AgribotAPI.sendMessage(inputText, conversationId);

      if (!conversationId && response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
      }

      const botMessage = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date(),
        suggestions: response.data.suggestions,
        metadata: response.data.metadata
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

  const handleImagePick = () => {
    launchImageLibrary(
      {
        mediaType: 'photo',
        quality: 0.8
      },
      async (response) => {
        if (response.didCancel) return;
        if (response.error) {
          alert('Error picking image');
          return;
        }

        const imageUri = response.assets[0].uri;

        // Add image preview to chat
        addMessage({
          id: Date.now().toString(),
          text: 'Uploaded plant image',
          sender: 'user',
          timestamp: new Date(),
          image: imageUri
        });

        setLoading(true);

        try {
          const result = await AgribotAPI.uploadImage(imageUri, conversationId);

          const botMessage = {
            id: (Date.now() + 1).toString(),
            text: result.data.response,
            sender: 'bot',
            timestamp: new Date(),
            diseaseInfo: result.data.disease_info
          };

          addMessage(botMessage);
        } catch (error) {
          addMessage({
            id: (Date.now() + 1).toString(),
            text: 'Sorry, I could not analyze the image. Please try again.',
            sender: 'bot',
            timestamp: new Date(),
            error: true
          });
        } finally {
          setLoading(false);
        }
      }
    );
  };

  const renderMessage = ({ item }) => (
    <View
      style={[
        styles.messageBubble,
        item.sender === 'user' ? styles.userBubble : styles.botBubble
      ]}
    >
      {item.image && (
        <Image source={{ uri: item.image }} style={styles.messageImage} />
      )}

      <Text style={styles.messageText}>{item.text}</Text>

      {item.suggestions && item.suggestions.length > 0 && (
        <View style={styles.suggestionsContainer}>
          {item.suggestions.map((suggestion, index) => (
            <TouchableOpacity
              key={index}
              style={styles.suggestionChip}
              onPress={() => {
                setInputText(suggestion);
              }}
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
        <TouchableOpacity style={styles.imageButton} onPress={handleImagePick}>
          <Text style={styles.imageButtonText}>📷</Text>
        </TouchableOpacity>

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
    backgroundColor: '#4CAF50',
    borderBottomRightRadius: 5
  },
  botBubble: {
    alignSelf: 'flex-start',
    backgroundColor: 'white',
    borderBottomLeftRadius: 5,
    borderWidth: 1,
    borderColor: '#e0e0e0'
  },
  messageText: {
    fontSize: 15,
    color: '#333'
  },
  messageImage: {
    width: 200,
    height: 200,
    borderRadius: 10,
    marginBottom: 8
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
  imageButton: {
    padding: 10,
    marginRight: 5
  },
  imageButtonText: {
    fontSize: 24
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

---

## Sensor Integration

### Sensor Dashboard with AI Insights

Create `components/SensorCard.js`:

```javascript
// components/SensorCard.js
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Modal
} from 'react-native';
import AgribotAPI from '../services/AgribotAPI';

export default function SensorCard({ sensorData, cropType = 'default' }) {
  const [loading, setLoading] = useState(false);
  const [interpretation, setInterpretation] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const analyzeReadings = async () => {
    setLoading(true);
    try {
      const result = await AgribotAPI.interpretSensorData({
        ...sensorData,
        cropType,
        language: 'auto',
        useAI: true
      });

      setInterpretation(result.data);
      setModalVisible(true);
    } catch (error) {
      alert('Failed to analyze sensor data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = () => {
    if (!interpretation) return '#999';
    const status = interpretation.status.status;
    if (status === 'critical') return '#f44336';
    if (status === 'warning') return '#ff9800';
    return '#4CAF50';
  };

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>
          Field {sensorData.fieldId} - Zone {String.fromCharCode(65 + sensorData.zoneId)}
        </Text>
        <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
      </View>

      <View style={styles.readings}>
        <View style={styles.reading}>
          <Text style={styles.readingLabel}>🌡️ Temp</Text>
          <Text style={styles.readingValue}>{sensorData.temperature}°C</Text>
        </View>
        <View style={styles.reading}>
          <Text style={styles.readingLabel}>💧 Moisture</Text>
          <Text style={styles.readingValue}>{sensorData.soilMoisture}</Text>
        </View>
        <View style={styles.reading}>
          <Text style={styles.readingLabel}>⚗️ pH</Text>
          <Text style={styles.readingValue}>{(sensorData.phValue / 100).toFixed(1)}</Text>
        </View>
        <View style={styles.reading}>
          <Text style={styles.readingLabel}>🔋 Battery</Text>
          <Text style={styles.readingValue}>{sensorData.batteryLevel}%</Text>
        </View>
      </View>

      <TouchableOpacity
        style={styles.analyzeButton}
        onPress={analyzeReadings}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator size="small" color="white" />
        ) : (
          <Text style={styles.analyzeButtonText}>🤖 AI Analysis</Text>
        )}
      </TouchableOpacity>

      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>AgriBot Analysis</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            {interpretation && (
              <>
                <View style={[styles.statusBanner, { backgroundColor: getStatusColor() }]}>
                  <Text style={styles.statusText}>
                    {interpretation.status.message}
                  </Text>
                </View>

                {interpretation.alerts.length > 0 && (
                  <View style={styles.alertsSection}>
                    <Text style={styles.sectionTitle}>⚠️ Alerts</Text>
                    {interpretation.alerts.map((alert, index) => (
                      <View key={index} style={styles.alert}>
                        <Text style={styles.alertText}>
                          {alert.icon} {alert.message}
                        </Text>
                        {alert.action && (
                          <Text style={styles.alertAction}>→ {alert.action}</Text>
                        )}
                      </View>
                    ))}
                  </View>
                )}

                {interpretation.ai_interpretation && (
                  <View style={styles.aiSection}>
                    <Text style={styles.sectionTitle}>🤖 AI Insights</Text>
                    <Text style={styles.aiText}>
                      {interpretation.ai_interpretation}
                    </Text>
                  </View>
                )}

                {interpretation.recommendations.length > 0 && (
                  <View style={styles.recommendationsSection}>
                    <Text style={styles.sectionTitle}>💡 Recommendations</Text>
                    {interpretation.recommendations.map((rec, index) => (
                      <Text key={index} style={styles.recommendation}>
                        • {rec}
                      </Text>
                    ))}
                  </View>
                )}
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333'
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6
  },
  readings: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15
  },
  reading: {
    alignItems: 'center'
  },
  readingLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4
  },
  readingValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333'
  },
  analyzeButton: {
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 10,
    alignItems: 'center'
  },
  analyzeButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 14
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '80%'
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333'
  },
  closeButton: {
    fontSize: 24,
    color: '#666'
  },
  statusBanner: {
    padding: 12,
    borderRadius: 10,
    marginBottom: 15
  },
  statusText: {
    color: 'white',
    fontWeight: 'bold',
    textAlign: 'center'
  },
  alertsSection: {
    marginBottom: 15
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333'
  },
  alert: {
    backgroundColor: '#fff3cd',
    padding: 10,
    borderRadius: 8,
    marginBottom: 8
  },
  alertText: {
    color: '#856404',
    marginBottom: 4
  },
  alertAction: {
    color: '#856404',
    fontWeight: 'bold',
    fontSize: 12
  },
  aiSection: {
    marginBottom: 15
  },
  aiText: {
    color: '#555',
    lineHeight: 22
  },
  recommendationsSection: {
    marginBottom: 15
  },
  recommendation: {
    color: '#555',
    marginBottom: 6,
    lineHeight: 20
  }
});
```

---

## Image Upload (Disease Detection)

Already included in the Chat Screen component above. The image picker integration allows users to:

1. Take a photo with camera
2. Upload from gallery
3. Get AI-powered disease detection
4. Receive treatment recommendations

---

## Multilingual Support

### Language Selector Component

```javascript
// components/LanguageSelector.js
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal } from 'react-native';
import AgribotAPI from '../services/AgribotAPI';

const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'pcm', name: 'Pidgin', flag: '🗣️' }
];

export default function LanguageSelector({ currentLanguage, onLanguageChange }) {
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState(currentLanguage || 'en');

  const handleLanguageSelect = async (langCode) => {
    try {
      await AgribotAPI.updateLanguage(langCode);
      setSelectedLanguage(langCode);
      onLanguageChange?.(langCode);
      setModalVisible(false);
    } catch (error) {
      alert('Failed to update language');
    }
  };

  const getCurrentLanguage = () => {
    return LANGUAGES.find(lang => lang.code === selectedLanguage) || LANGUAGES[0];
  };

  return (
    <View>
      <TouchableOpacity
        style={styles.button}
        onPress={() => setModalVisible(true)}
      >
        <Text style={styles.buttonText}>
          {getCurrentLanguage().flag} {getCurrentLanguage().name}
        </Text>
      </TouchableOpacity>

      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Select Language</Text>

            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[
                  styles.languageOption,
                  selectedLanguage === lang.code && styles.selectedOption
                ]}
                onPress={() => handleLanguageSelect(lang.code)}
              >
                <Text style={styles.languageText}>
                  {lang.flag} {lang.name}
                </Text>
                {selectedLanguage === lang.code && (
                  <Text style={styles.checkmark}>✓</Text>
                )}
              </TouchableOpacity>
            ))}

            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.closeButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderRadius: 8
  },
  buttonText: {
    fontSize: 14,
    color: '#333'
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    width: '80%',
    maxWidth: 300
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center'
  },
  languageOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    backgroundColor: '#f5f5f5'
  },
  selectedOption: {
    backgroundColor: '#e3f2fd'
  },
  languageText: {
    fontSize: 16
  },
  checkmark: {
    fontSize: 20,
    color: '#4CAF50'
  },
  closeButton: {
    marginTop: 10,
    padding: 12,
    backgroundColor: '#666',
    borderRadius: 10,
    alignItems: 'center'
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold'
  }
});
```

---

## Complete Example App Structure

```
your-app/
├── src/
│   ├── config/
│   │   └── agribot.js
│   ├── services/
│   │   └── AgribotAPI.js
│   ├── hooks/
│   │   └── useAuth.js
│   ├── screens/
│   │   ├── LoginScreen.js
│   │   ├── RegisterScreen.js
│   │   ├── ChatScreen.js
│   │   └── SensorDashboard.js
│   └── components/
│       ├── SensorCard.js
│       └── LanguageSelector.js
```

---

## Testing

### Test the connection:

```javascript
// Test in your app
import AgribotAPI from './services/AgribotAPI';

async function testConnection() {
  try {
    // Test login
    const loginResult = await AgribotAPI.login('user@gmail.com', 'user123');
    console.log('Login successful:', loginResult);

    // Test chat
    const chatResult = await AgribotAPI.sendMessage('Hello AgriBot!');
    console.log('Chat response:', chatResult);

    // Test sensor interpretation
    const sensorResult = await AgribotAPI.interpretSensorData({
      temperature: 28.5,
      humidity: 65.0,
      soilMoisture: 450,
      phValue: 680,
      batteryLevel: 75,
      cropType: 'maize',
      language: 'en'
    });
    console.log('Sensor analysis:', sensorResult);
  } catch (error) {
    console.error('Test failed:', error);
  }
}
```

---

## Next Steps

1. **Install dependencies** in your React Native app
2. **Update the BASE_URL** in `config/agribot.js` to your server IP
3. **Copy the components** to your app
4. **Test authentication** and chat functionality
5. **Integrate sensor cards** into your dashboard
6. **Enable image upload** for disease detection

---

## Support

For more details:
- AgriBot API: `http://your-server:5000/api`
- Sensor API Docs: `/docs/SENSOR_INTEGRATION_GUIDE.md`
- Full AgriBot Docs: `/docs/`

Happy farming! 🌾🚜
