# AgriBot - Advanced Agricultural AI Assistant for Cameroon

A sophisticated conversational AI system providing agricultural guidance across all 10 regions of Cameroon.

## Features

- **Multi-service Data Integration**: OpenWeatherMap, FAO, NASA POWER APIs
- **Advanced NLP**: Intent classification, entity extraction, sentiment analysis
- **Comprehensive Knowledge Base**: Diseases, fertilizers, planting procedures, pest control
- **Context-aware Conversations**: Maintains conversation history and context
- **Regional Expertise**: Specialized advice for all Cameroon regions
- **Analytics Dashboard**: Conversation insights and user feedback systems
- **Production Ready**: Scalable architecture with caching and database persistence

## Quick Start

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python run.py
```

## Project Architecture

```
agribot/
├── core/           # Conversation engine and logic
├── knowledge/      # Agricultural domain expertise  
├── nlp/           # Natural language processing
├── services/      # External API integrations
├── database/      # Data persistence and analytics
└── utils/         # Utility functions and helpers
```

## Supported Crops

Maize, cassava, plantain, cocoa, coffee, oil palm, rice, beans, pepper, tomatoes, yam, groundnuts, cotton, millet, sorghum, and 30+ other crops grown in Cameroon.

## Supported Regions

All 10 regions with climate-specific advice: Centre, Littoral, West, Northwest, Southwest, East, North, Far North, Adamawa, South.

## API Documentation

- `/api/chat` - Conversational interface
- `/api/weather/{region}` - Weather data  
- `/api/crops/{crop}/diseases` - Disease information
- `/api/analytics` - Usage analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - See LICENSE file for details
