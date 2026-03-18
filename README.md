# SafeSpace - AI Mental Health Therapist Platform

A comprehensive, privacy-first mental health support system using AI and agentic workflows for student populations.

## 🎯 Overview

SafeSpace is an intelligent mental health support platform that combines:
- **AI-Powered Therapist** (Google MedGemma LLM)
- **Structured Mental Health Screening** (Travia-inspired assessments)
- **Voice-Enabled Multilingual Interface** (Speech-to-text support)
- **Anonymous Identity System** (Auto-generated names & avatars)
- **Gamification & Wellness Activities** (Interactive challenges & rewards)
- **Emergency Response System** (Twilio integration for crisis intervention)

## 🏗️ System Architecture

```
User (Streamlit Frontend)
        ↓
    Backend (FastAPI)
        ↓
    AI Agent (LangGraph/LangChain)
        ↓
    LLM & Tools (MedGemma, Twilio, Location APIs)
```

## 📁 Project Structure

```
SafeSpace/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration & environment variables
│   ├── models.py               # Database models & schemas
│   ├── database.py             # Database setup & connection
│   ├── agent.py                # AI Agent & LLM logic
│   ├── tools.py                # Tool implementations (emergency, location, etc.)
│   ├── screening.py            # Mental health screening logic
│   ├── voice_service.py        # Speech-to-text integration
│   └── requirements.txt        # Backend dependencies
│
├── frontend/
│   ├── app.py                  # Streamlit main application
│   ├── pages/
│   │   ├── 1_Chat.py           # Chat interface
│   │   ├── 2_Screening.py      # Mental health screening
│   │   ├── 3_Wellness_Hub.py   # Gamification & activities
│   │   ├── 4_Progress.py       # User progress tracking
│   │   └── 5_Resources.py      # Self-help resources
│   ├── components/
│   │   ├── avatar.py           # Avatar generation & display
│   │   ├── voice_input.py      # Voice interface
│   │   └── games.py            # Gamification components
│   ├── utils.py                # Utility functions
│   └── requirements.txt        # Frontend dependencies
│
├── data/
│   ├── screening_questions.json # Screening assessment questions
│   ├── wellness_activities.json # Gamification activities
│   ├── resources.json           # Mental health resources
│   └── avatar_styles.json       # Avatar customization data
│
├── tests/
│   ├── test_backend.py         # Backend tests
│   ├── test_agent.py           # AI Agent tests
│   └── test_screening.py       # Screening logic tests
│
├── docs/
│   ├── API.md                  # API documentation
│   ├── ARCHITECTURE.md         # System architecture details
│   ├── SETUP.md                # Setup & installation guide
│   └── SECURITY.md             # Security & privacy documentation
│
├── docker-compose.yml          # Docker configuration
├── .env.example                # Environment variables template
├── requirements.txt            # All dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL or MongoDB
- Docker (optional)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd SafeSpace
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up database**
```bash
python backend/database.py
```

6. **Run the application**

Backend:
```bash
cd backend
python main.py
# API runs on http://localhost:8000
```

Frontend (in another terminal):
```bash
cd frontend
streamlit run app.py
# Frontend runs on http://localhost:8501
```

## 🔧 Configuration

### Environment Variables (.env)
```
# Database
DATABASE_URL=postgresql://user:password@localhost/safespace
MONGODB_URL=mongodb://localhost:27017/safespace

# LLM & APIs
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Twilio (Emergency)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Voice Service
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=eastus

# Environment
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your_secret_key
```

## 🎯 Core Features

### 1. **AI Therapist Chat**
- 24/7 conversational support
- MedGemma LLM for healthcare context
- Empathetic responses & active listening
- Crisis detection & escalation

### 2. **Mental Health Screening**
- Guided diagnostic questions
- Real-time mood, sleep, stress assessment
- Behavioral pattern analysis
- Personalized wellness insights
- Risk indicator identification

### 3. **Voice Interface**
- Microphone-based input
- Speech-to-text integration
- Multilingual support (English, Hindi, Tamil, Bengali)
- Accessibility for all users

### 4. **Anonymous Identity**
- Auto-generated usernames (BlueMind_47, HopeWalker_12)
- Digital avatar profiles (cartoon-style AI-generated)
- Confidential Wellness IDs (non-traceable)
- Zero personal information storage

### 5. **Wellness Gamification**
- Stress awareness quizzes
- Mood tracker challenges
- Mindfulness mini-games
- Emotional resilience activities
- Progress tracking & badges
- Reward system & leaderboards

### 6. **Emergency Response**
- Crisis detection algorithms
- Automatic Twilio emergency calls
- Location-aware therapist matching
- Professional support escalation
- 24/7 crisis hotline integration

## 📊 Development Phases

### Phase 1: Frontend Setup (Week 1-2)
- [x] Streamlit UI framework
- [x] User authentication & onboarding
- [x] Chat interface design
- [x] Avatar selection system

### Phase 2: Backend Setup (Week 3-4)
- [x] FastAPI server implementation
- [x] Request validation & error handling
- [x] Session & user management
- [x] Database schema design

### Phase 3: AI Agent & Tools (Week 5-8)
- [x] MedGemma LLM integration
- [x] LangGraph/LangChain agent setup
- [x] Screening logic implementation
- [x] Tool integration (Twilio, Location APIs)
- [x] Voice service setup

### Phase 4: Testing & Deployment (Week 9+)
- [ ] Unit & integration tests
- [ ] Security audit & HIPAA compliance
- [ ] Load testing & optimization
- [ ] Docker containerization
- [ ] Production deployment

## 🔐 Security & Privacy

### Privacy Measures
- ✅ HIPAA-compliant data encryption
- ✅ End-to-end encryption for communications
- ✅ Anonymous user identification
- ✅ No real names or personal data stored
- ✅ Automatic session timeouts
- ✅ Audit logging of all data access

### Data Protection
- All communications encrypted in transit (TLS 1.3)
- Data encrypted at rest (AES-256)
- Regular security audits
- Penetration testing
- Incident response protocols

## 📈 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| User Adoption | 60% of population | - |
| Response Time | < 2 seconds | - |
| User Satisfaction (NPS) | > 70 | - |
| Screening Completion | 90% of users | - |
| Weekly Engagement | 3+ interactions | - |
| Crisis Detection | 100% escalation | - |
| Platform Uptime | 99.5% | - |
| Multilingual Support | 5+ languages | - |

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Interactive UI framework
- **PyAudio** - Voice input capture
- **Pillow** - Image processing for avatars

### Backend
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - ORM for database
- **Pydantic** - Data validation

### AI & LLM
- **LangChain** - LLM orchestration
- **LangGraph** - Agentic workflows
- **Google MedGemma** - Healthcare-specific LLM
- **OpenAI/Groq** - Backup LLM providers

### Voice & Speech
- **Google Cloud Speech-to-Text** - Speech recognition
- **Azure Cognitive Services** - Multilingual support
- **pyttsx3** - Text-to-speech

### Emergency & Location
- **Twilio** - Emergency calling
- **Google Maps API** - Therapist location matching
- **Geolocation APIs** - User location services

### Database
- **PostgreSQL** - Primary database
- **MongoDB** - Document storage for conversations
- **Redis** - Caching & sessions

### Deployment
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **AWS/GCP/Azure** - Cloud hosting

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - System design & data flow
- [Setup Guide](docs/SETUP.md) - Detailed installation instructions
- [Security & Privacy](docs/SECURITY.md) - Security measures & compliance

## 🤝 Contributing

Contributions are welcome! Please follow our contribution guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues, questions, or suggestions:
- 📧 Email: support@safespace.ai
- 💬 Discord: [Join our community](https://discord.gg/safespace)
- 📖 Documentation: [docs.safespace.ai](https://docs.safespace.ai)

## ⚠️ Important Notice

**SafeSpace is NOT a replacement for professional mental health care.** This platform is designed to:
- Provide immediate support and coping strategies
- Help identify mental health concerns
- Facilitate connection to professional resources
- Support ongoing mental wellness

Always encourage users to seek professional help for serious mental health concerns or emergencies.

---

**Built with ❤️ for student mental health**

@AI.with.Hassan | Powered by MedGemma LLM
