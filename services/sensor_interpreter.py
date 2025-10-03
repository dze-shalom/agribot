"""
Sensor Data Interpretation Service
Location: agribot/services/sensor_interpreter.py

Analyzes IoT sensor readings from agricultural monitoring systems
and provides intelligent insights using AI
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SensorInterpreter:
    """Service for interpreting agricultural sensor data"""

    def __init__(self, claude_service=None):
        """Initialize sensor interpreter with optional Claude service"""
        self.claude_service = claude_service
        self.logger = logging.getLogger(__name__)

        # Optimal ranges for different crops (can be expanded)
        self.crop_parameters = {
            'default': {
                'temperature': {'min': 15, 'max': 35, 'optimal': (20, 30)},
                'humidity': {'min': 40, 'max': 80, 'optimal': (50, 70)},
                'soil_moisture': {'min': 250, 'max': 600, 'optimal': (350, 500)},
                'ph': {'min': 5.5, 'max': 7.5, 'optimal': (6.0, 7.0)},
                'battery': {'min': 20, 'max': 100, 'critical': 15}
            },
            'maize': {
                'temperature': {'min': 18, 'max': 32, 'optimal': (21, 27)},
                'soil_moisture': {'min': 300, 'max': 600, 'optimal': (400, 550)},
                'ph': {'min': 5.8, 'max': 7.0, 'optimal': (6.0, 6.8)}
            },
            'tomato': {
                'temperature': {'min': 18, 'max': 30, 'optimal': (20, 25)},
                'soil_moisture': {'min': 350, 'max': 550, 'optimal': (400, 500)},
                'ph': {'min': 6.0, 'max': 6.8, 'optimal': (6.2, 6.5)}
            },
            'rice': {
                'temperature': {'min': 20, 'max': 35, 'optimal': (25, 30)},
                'soil_moisture': {'min': 500, 'max': 800, 'optimal': (600, 750)},
                'ph': {'min': 5.5, 'max': 7.0, 'optimal': (6.0, 6.5)}
            }
        }

    def interpret_readings(
        self,
        sensor_data: Dict[str, Any],
        crop_type: str = 'default',
        language: str = 'auto',
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Interpret sensor readings and provide insights

        Args:
            sensor_data: Dictionary with sensor readings
            crop_type: Type of crop being monitored
            language: Language for response (auto, en, fr, pcm)
            use_ai: Whether to use Claude AI for interpretation

        Returns:
            Dictionary with interpretation, alerts, and recommendations
        """
        try:
            # Basic rule-based analysis
            alerts = self._generate_alerts(sensor_data, crop_type)
            status = self._assess_overall_status(sensor_data, crop_type)
            recommendations = self._get_basic_recommendations(sensor_data, crop_type, language)

            # AI-powered interpretation if Claude is available
            ai_interpretation = None
            if use_ai and self.claude_service:
                ai_interpretation = self._get_ai_interpretation(
                    sensor_data, crop_type, alerts, language
                )

            return {
                'status': status,
                'alerts': alerts,
                'recommendations': recommendations,
                'ai_interpretation': ai_interpretation,
                'sensor_data': sensor_data,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error interpreting sensor data: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'alerts': [],
                'recommendations': []
            }

    def _generate_alerts(
        self,
        sensor_data: Dict[str, Any],
        crop_type: str
    ) -> List[Dict[str, Any]]:
        """Generate alerts based on sensor thresholds"""
        alerts = []
        params = self.crop_parameters.get(crop_type, self.crop_parameters['default'])

        # Temperature alerts
        temp = sensor_data.get('temperature', 0)
        if temp > 0:
            temp_params = params.get('temperature', {})
            if temp < temp_params.get('min', 0):
                alerts.append({
                    'type': 'warning',
                    'parameter': 'temperature',
                    'message': f'Temperature too low: {temp}°C',
                    'severity': 'medium',
                    'icon': '🥶'
                })
            elif temp > temp_params.get('max', 100):
                alerts.append({
                    'type': 'critical',
                    'parameter': 'temperature',
                    'message': f'Temperature too high: {temp}°C',
                    'severity': 'high',
                    'icon': '🔥'
                })

        # Soil moisture alerts
        moisture = sensor_data.get('soilMoisture', 0)
        if moisture > 0:
            moisture_params = params.get('soil_moisture', {})
            if moisture < moisture_params.get('min', 0):
                alerts.append({
                    'type': 'critical',
                    'parameter': 'soil_moisture',
                    'message': f'Soil very dry: {moisture}',
                    'severity': 'high',
                    'icon': '💧',
                    'action': 'Start irrigation immediately'
                })
            elif moisture > moisture_params.get('max', 1000):
                alerts.append({
                    'type': 'warning',
                    'parameter': 'soil_moisture',
                    'message': f'Soil too wet: {moisture}',
                    'severity': 'medium',
                    'icon': '🌊',
                    'action': 'Stop irrigation, check drainage'
                })

        # pH alerts
        ph = sensor_data.get('phValue', 0)
        if ph > 0:
            ph_value = ph / 100.0 if ph > 10 else ph  # Handle scaled values
            ph_params = params.get('ph', {})
            if ph_value < ph_params.get('min', 0):
                alerts.append({
                    'type': 'warning',
                    'parameter': 'ph',
                    'message': f'Soil too acidic: pH {ph_value:.1f}',
                    'severity': 'medium',
                    'icon': '⚗️',
                    'action': 'Add lime to raise pH'
                })
            elif ph_value > ph_params.get('max', 14):
                alerts.append({
                    'type': 'warning',
                    'parameter': 'ph',
                    'message': f'Soil too alkaline: pH {ph_value:.1f}',
                    'severity': 'medium',
                    'icon': '⚗️',
                    'action': 'Add sulfur to lower pH'
                })

        # Battery alerts
        battery = sensor_data.get('batteryLevel', 100)
        battery_params = params.get('battery', {})
        if battery < battery_params.get('critical', 15):
            alerts.append({
                'type': 'critical',
                'parameter': 'battery',
                'message': f'Battery critically low: {battery}%',
                'severity': 'high',
                'icon': '🔋',
                'action': 'Replace battery or check solar panel'
            })
        elif battery < battery_params.get('min', 20):
            alerts.append({
                'type': 'warning',
                'parameter': 'battery',
                'message': f'Battery low: {battery}%',
                'severity': 'low',
                'icon': '🔋'
            })

        # Signal strength alerts
        rssi = sensor_data.get('signalStrength', 0)
        if rssi < -100:
            alerts.append({
                'type': 'warning',
                'parameter': 'signal',
                'message': f'Weak signal: {rssi} dBm',
                'severity': 'low',
                'icon': '📡',
                'action': 'Check antenna or relocate gateway'
            })

        return alerts

    def _assess_overall_status(
        self,
        sensor_data: Dict[str, Any],
        crop_type: str
    ) -> Dict[str, Any]:
        """Assess overall field status"""
        alerts = self._generate_alerts(sensor_data, crop_type)

        critical_count = sum(1 for a in alerts if a.get('severity') == 'high')
        warning_count = sum(1 for a in alerts if a.get('severity') == 'medium')

        if critical_count > 0:
            status = 'critical'
            message = 'Immediate action required'
            color = 'red'
        elif warning_count > 0:
            status = 'warning'
            message = 'Attention needed'
            color = 'orange'
        else:
            status = 'good'
            message = 'All parameters normal'
            color = 'green'

        return {
            'status': status,
            'message': message,
            'color': color,
            'critical_alerts': critical_count,
            'warnings': warning_count
        }

    def _get_basic_recommendations(
        self,
        sensor_data: Dict[str, Any],
        crop_type: str,
        language: str
    ) -> List[str]:
        """Get basic recommendations based on sensor data"""
        recommendations = []
        alerts = self._generate_alerts(sensor_data, crop_type)

        # Map recommendations based on language
        rec_templates = {
            'en': {
                'dry_soil': 'Turn on irrigation system',
                'wet_soil': 'Stop irrigation and improve drainage',
                'high_temp': 'Provide shade or increase watering',
                'low_temp': 'Protect crops from cold',
                'acidic': 'Apply lime to raise pH',
                'alkaline': 'Apply sulfur to lower pH',
                'low_battery': 'Check solar panel and battery connections'
            },
            'fr': {
                'dry_soil': 'Activez le système d\'irrigation',
                'wet_soil': 'Arrêtez l\'irrigation et améliorez le drainage',
                'high_temp': 'Fournissez de l\'ombre ou augmentez l\'arrosage',
                'low_temp': 'Protégez les cultures du froid',
                'acidic': 'Appliquez de la chaux pour augmenter le pH',
                'alkaline': 'Appliquez du soufre pour baisser le pH',
                'low_battery': 'Vérifiez le panneau solaire et les connexions de batterie'
            },
            'pcm': {
                'dry_soil': 'On the water pump make ground get water',
                'wet_soil': 'Off the pump, water don too much',
                'high_temp': 'Make shade for the plant, sun don too hot',
                'low_temp': 'Cover the plant, cold fit kill am',
                'acidic': 'Put lime for ground make pH rise',
                'alkaline': 'Put sulfur for ground make pH drop',
                'low_battery': 'Check the solar panel and battery wire'
            }
        }

        lang = language if language in rec_templates else 'en'
        templates = rec_templates[lang]

        # Generate recommendations based on alerts
        for alert in alerts:
            param = alert['parameter']
            action = alert.get('action')

            if action:
                recommendations.append(action)
            elif param == 'soil_moisture':
                moisture = sensor_data.get('soilMoisture', 0)
                if moisture < 300:
                    recommendations.append(templates['dry_soil'])
                elif moisture > 600:
                    recommendations.append(templates['wet_soil'])
            elif param == 'temperature':
                temp = sensor_data.get('temperature', 0)
                if temp > 32:
                    recommendations.append(templates['high_temp'])
                elif temp < 15:
                    recommendations.append(templates['low_temp'])
            elif param == 'ph':
                ph = sensor_data.get('phValue', 700) / 100.0
                if ph < 6.0:
                    recommendations.append(templates['acidic'])
                elif ph > 7.5:
                    recommendations.append(templates['alkaline'])
            elif param == 'battery':
                recommendations.append(templates['low_battery'])

        # Remove duplicates while preserving order
        return list(dict.fromkeys(recommendations))

    def _get_ai_interpretation(
        self,
        sensor_data: Dict[str, Any],
        crop_type: str,
        alerts: List[Dict[str, Any]],
        language: str
    ) -> Optional[str]:
        """Get AI-powered interpretation using Claude"""
        if not self.claude_service:
            return None

        try:
            # Build comprehensive prompt for Claude
            prompt = self._build_sensor_analysis_prompt(
                sensor_data, crop_type, alerts
            )

            # Get Claude's interpretation
            response = self.claude_service.get_response(
                user_input=prompt,
                conversation_id=f"sensor_{sensor_data.get('fieldId', 0)}_{sensor_data.get('zoneId', 0)}",
                language=language
            )

            return response.content

        except Exception as e:
            self.logger.error(f"AI interpretation failed: {str(e)}")
            return None

    def _build_sensor_analysis_prompt(
        self,
        sensor_data: Dict[str, Any],
        crop_type: str,
        alerts: List[Dict[str, Any]]
    ) -> str:
        """Build analysis prompt for Claude"""

        prompt = f"""I have sensor readings from Field {sensor_data.get('fieldId', '?')} Zone {chr(65 + sensor_data.get('zoneId', 0))}.
Please analyze these readings and provide practical advice:

**Sensor Readings:**
- Temperature: {sensor_data.get('temperature', 0)}°C
- Humidity: {sensor_data.get('humidity', 0)}%
- Soil Moisture: {sensor_data.get('soilMoisture', 0)}
- pH Level: {sensor_data.get('phValue', 0) / 100.0:.2f}
- NPK Value: {sensor_data.get('npkValue', 0)}
- Water Level: {sensor_data.get('waterLevel', 0)}%
- Battery: {sensor_data.get('batteryLevel', 0)}%
- Pump Status: {'ON' if sensor_data.get('pumpStatus', False) else 'OFF'}

**Crop Type:** {crop_type}

**Current Alerts:** {len(alerts)} alert(s)
"""

        if alerts:
            prompt += "\n**Issues Detected:**\n"
            for alert in alerts:
                prompt += f"- {alert.get('icon', '⚠️')} {alert.get('message')}\n"

        prompt += """
Please provide:
1. Overall field condition assessment
2. Specific concerns if any
3. Immediate actions needed (if any)
4. Long-term recommendations for optimal growth

Be practical and specific to the readings shown."""

        return prompt

    def interpret_trends(
        self,
        historical_data: List[Dict[str, Any]],
        crop_type: str = 'default',
        language: str = 'auto'
    ) -> Dict[str, Any]:
        """Analyze trends in historical sensor data"""
        if not historical_data or len(historical_data) < 2:
            return {'error': 'Insufficient data for trend analysis'}

        # Calculate trends
        trends = {
            'temperature': self._calculate_trend([d.get('temperature', 0) for d in historical_data]),
            'humidity': self._calculate_trend([d.get('humidity', 0) for d in historical_data]),
            'soil_moisture': self._calculate_trend([d.get('soilMoisture', 0) for d in historical_data])
        }

        return {
            'trends': trends,
            'period': f'{len(historical_data)} readings',
            'insights': self._generate_trend_insights(trends, language)
        }

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and magnitude"""
        if len(values) < 2:
            return {'direction': 'stable', 'change': 0}

        first_val = values[0]
        last_val = values[-1]
        change = last_val - first_val
        percent_change = (change / first_val * 100) if first_val != 0 else 0

        if abs(percent_change) < 5:
            direction = 'stable'
        elif percent_change > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'

        return {
            'direction': direction,
            'change': change,
            'percent_change': percent_change,
            'current': last_val
        }

    def _generate_trend_insights(
        self,
        trends: Dict[str, Any],
        language: str
    ) -> List[str]:
        """Generate insights from trends"""
        insights = []

        moisture_trend = trends.get('soil_moisture', {})
        if moisture_trend.get('direction') == 'decreasing':
            if moisture_trend.get('percent_change', 0) < -20:
                insights.append('Soil moisture dropping rapidly - increase irrigation')

        temp_trend = trends.get('temperature', {})
        if temp_trend.get('direction') == 'increasing':
            if temp_trend.get('current', 0) > 30:
                insights.append('Temperature rising - monitor for heat stress')

        return insights
