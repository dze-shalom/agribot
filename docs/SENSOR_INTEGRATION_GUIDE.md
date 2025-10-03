# AgriBot Sensor Integration Guide

## Overview
AgriBot can now interpret IoT sensor data from your agricultural monitoring systems and provide intelligent, actionable insights in multiple languages.

---

## Features

### ✅ **What AgriBot Can Do With Sensor Data:**

1. **Real-time Interpretation**
   - Analyze temperature, humidity, soil moisture, pH, NPK, battery levels
   - Detect anomalies and critical conditions
   - Provide instant recommendations

2. **Smart Alerts**
   - Critical alerts (immediate action needed)
   - Warning alerts (attention needed)
   - Info alerts (monitoring)

3. **AI-Powered Insights** (with Claude API)
   - Natural language explanations of sensor readings
   - Context-aware recommendations
   - Crop-specific advice
   - Multilingual support (English, French, Pidgin)

4. **Trend Analysis**
   - Historical data analysis
   - Pattern recognition
   - Predictive insights

---

## API Endpoints

### 1. **Interpret Sensor Readings**
```http
POST /api/sensors/interpret
Content-Type: application/json

{
  "fieldId": 1,
  "zoneId": 0,
  "temperature": 28.5,
  "humidity": 65.0,
  "soilMoisture": 450,
  "phValue": 680,
  "npkValue": 250,
  "waterLevel": 80,
  "batteryLevel": 75,
  "pumpStatus": false,
  "signalStrength": -65,
  "cropType": "maize",
  "language": "auto",
  "useAI": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": {
      "status": "good",
      "message": "All parameters normal",
      "color": "green",
      "critical_alerts": 0,
      "warnings": 0
    },
    "alerts": [],
    "recommendations": [
      "Soil moisture is optimal for maize growth",
      "Temperature is within ideal range"
    ],
    "ai_interpretation": "Your maize field is in excellent condition! The soil moisture level of 450 is perfect for this growth stage...",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### 2. **Quick Health Check**
```http
POST /api/sensors/quick-check
Content-Type: application/json

{
  "temperature": 35.0,
  "humidity": 45.0,
  "soilMoisture": 200,
  "phValue": 520,
  "batteryLevel": 15
}
```

**Response:**
```json
{
  "success": true,
  "status": {
    "status": "critical",
    "message": "Immediate action required",
    "color": "red"
  },
  "alerts": [
    {
      "type": "critical",
      "parameter": "temperature",
      "message": "Temperature too high: 35.0°C",
      "severity": "high",
      "icon": "🔥"
    },
    {
      "type": "critical",
      "parameter": "soil_moisture",
      "message": "Soil very dry: 200",
      "severity": "high",
      "icon": "💧",
      "action": "Start irrigation immediately"
    }
  ],
  "alertCount": 3
}
```

### 3. **Chat with Sensor Context**
```http
POST /api/sensors/chat/sensor-context
Content-Type: application/json

{
  "message": "Why is my soil so dry?",
  "sensorData": {
    "fieldId": 1,
    "zoneId": 0,
    "temperature": 35.0,
    "soilMoisture": 200,
    "humidity": 40.0
  },
  "language": "auto"
}
```

**Response:**
```json
{
  "success": true,
  "response": {
    "response": "Your soil is dry because the moisture reading is 200, which is below the minimum threshold of 250. Combined with high temperature (35°C) and low humidity (40%), the soil is drying out quickly. You should start irrigation immediately...",
    "suggestions": [
      "Turn on irrigation system",
      "Monitor moisture levels closely",
      "Consider mulching to retain moisture"
    ]
  }
}
```

### 4. **Analyze Trends**
```http
POST /api/sensors/analyze-trends
Content-Type: application/json

{
  "historicalData": [
    {
      "temperature": 28.5,
      "humidity": 65.0,
      "soilMoisture": 450,
      "timestamp": "2024-01-01 10:00:00"
    },
    {
      "temperature": 32.0,
      "humidity": 55.0,
      "soilMoisture": 350,
      "timestamp": "2024-01-01 14:00:00"
    }
  ],
  "cropType": "maize",
  "language": "en"
}
```

---

## Integration Examples

### **ESP32 LoRa Gateway Integration**

Add this to your ESP32 gateway code to send data to AgriBot:

```cpp
// Add to your ESP32 gateway
void sendToAgriBot(NodeData* node) {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    http.begin("http://your-agribot-server.com/api/sensors/interpret");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer YOUR_API_TOKEN");

    // Build JSON payload
    StaticJsonDocument<512> doc;
    doc["fieldId"] = node->fieldId;
    doc["zoneId"] = node->zoneId;
    doc["temperature"] = node->temperature / 10.0;
    doc["humidity"] = node->humidity / 10.0;
    doc["soilMoisture"] = node->soilMoisture;
    doc["phValue"] = node->phValue;
    doc["npkValue"] = node->npkValue;
    doc["waterLevel"] = node->waterLevel;
    doc["batteryLevel"] = node->batteryLevel;
    doc["pumpStatus"] = node->pumpStatus;
    doc["signalStrength"] = node->signalStrength;
    doc["cropType"] = "maize";
    doc["language"] = "auto";
    doc["useAI"] = true;

    String payload;
    serializeJson(doc, payload);

    int httpCode = http.POST(payload);

    if (httpCode > 0) {
        String response = http.getString();

        // Parse response
        StaticJsonDocument<1024> responseDoc;
        deserializeJson(responseDoc, response);

        // Display AI interpretation on dashboard
        const char* aiInterpretation = responseDoc["data"]["ai_interpretation"];
        Serial.println("AgriBot Says:");
        Serial.println(aiInterpretation);

        // Handle alerts
        JsonArray alerts = responseDoc["data"]["alerts"];
        for (JsonObject alert : alerts) {
            const char* message = alert["message"];
            const char* action = alert["action"];

            Serial.printf("⚠️ Alert: %s\n", message);
            if (action) {
                Serial.printf("   Action: %s\n", action);
            }
        }
    }

    http.end();
}

// Call this after receiving sensor data
void handleLoRaData() {
    // ... existing code ...

    // After updating node data
    if (nodes[nodeIndex].isOnline) {
        sendToAgriBot(&nodes[nodeIndex]);
    }
}
```

### **Python Integration Example**

```python
import requests

def get_sensor_interpretation(sensor_data):
    url = "http://localhost:5000/api/sensors/interpret"

    response = requests.post(url, json={
        "fieldId": sensor_data['fieldId'],
        "zoneId": sensor_data['zoneId'],
        "temperature": sensor_data['temperature'],
        "humidity": sensor_data['humidity'],
        "soilMoisture": sensor_data['soilMoisture'],
        "phValue": sensor_data['phValue'],
        "batteryLevel": sensor_data['batteryLevel'],
        "pumpStatus": sensor_data['pumpStatus'],
        "cropType": "maize",
        "language": "en",
        "useAI": True
    })

    if response.status_code == 200:
        result = response.json()

        # Display status
        status = result['data']['status']
        print(f"Status: {status['message']} ({status['status']})")

        # Display alerts
        for alert in result['data']['alerts']:
            print(f"{alert['icon']} {alert['message']}")
            if 'action' in alert:
                print(f"   → {alert['action']}")

        # Display AI interpretation
        if result['data']['ai_interpretation']:
            print("\n🤖 AgriBot Analysis:")
            print(result['data']['ai_interpretation'])

        # Display recommendations
        print("\n💡 Recommendations:")
        for rec in result['data']['recommendations']:
            print(f"  • {rec}")

    return result

# Example usage
sensor_data = {
    'fieldId': 1,
    'zoneId': 0,
    'temperature': 28.5,
    'humidity': 65.0,
    'soilMoisture': 450,
    'phValue': 680,
    'batteryLevel': 75,
    'pumpStatus': False
}

interpretation = get_sensor_interpretation(sensor_data)
```

### **JavaScript/Node.js Integration**

```javascript
async function interpretSensorData(sensorData) {
    const response = await fetch('http://localhost:5000/api/sensors/interpret', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fieldId: sensorData.fieldId,
            zoneId: sensorData.zoneId,
            temperature: sensorData.temperature,
            humidity: sensorData.humidity,
            soilMoisture: sensorData.soilMoisture,
            phValue: sensorData.phValue,
            batteryLevel: sensorData.batteryLevel,
            pumpStatus: sensorData.pumpStatus,
            cropType: 'maize',
            language: 'auto',
            useAI: true
        })
    });

    const result = await response.json();

    if (result.success) {
        console.log('Status:', result.data.status.message);

        // Display alerts
        result.data.alerts.forEach(alert => {
            console.log(`${alert.icon} ${alert.message}`);
        });

        // Display AI interpretation
        if (result.data.ai_interpretation) {
            console.log('\n🤖 AgriBot Says:');
            console.log(result.data.ai_interpretation);
        }
    }

    return result;
}
```

---

## Supported Crop Types

- `default` - General agricultural parameters
- `maize` - Optimized for maize/corn
- `tomato` - Optimized for tomatoes
- `rice` - Optimized for rice
- More crop types can be added in `sensor_interpreter.py`

---

## Alert Severity Levels

| Severity | Color | Meaning |
|----------|-------|---------|
| `high` | Red | Critical - Immediate action required |
| `medium` | Orange | Warning - Attention needed soon |
| `low` | Yellow | Info - Monitor the situation |

---

## Language Support

AgriBot supports automatic language detection and responses in:
- **English** (`en`)
- **French** (`fr`)
- **Pidgin English** (`pcm`)

Set `language: "auto"` to let AgriBot auto-detect the language, or specify explicitly.

---

## Requirements

- AgriBot server running
- Authentication (login required for API endpoints)
- Claude API key (optional, for AI-powered interpretations)
- Plant.id API key (optional, for disease detection)

---

## Next Steps

1. Test the API with your sensor data
2. Integrate with your ESP32 gateway
3. Add AgriBot widget to your dashboard
4. Enable Claude API for smarter insights

For more information, visit: http://localhost:5000/api/sensors/health
