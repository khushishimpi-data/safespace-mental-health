# SafeSpace - Setup & Installation Guide

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ (optional, can use SQLite for development)
- Docker (recommended for easy deployment)
- Git

## 🚀 Quick Start (Local Development)

### Step 1: Clone Repository

```bash
git clone <repo-url>
cd SafeSpace
```

### Step 2: Environment Setup

```bash
# Copy example environment variables
cp .env.example .env

# Edit .env with your configuration
# At minimum, set:
# - OPENAI_API_KEY or GROQ_API_KEY
# - DATABASE_URL (optional, defaults to SQLite in dev)
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install separately:
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Step 5: Database Setup (Optional)

For production, use PostgreSQL:

```bash
# Create database
createdb safespace

# Or using psql:
psql -U postgres -c "CREATE DATABASE safespace;"

# Run migrations (when available)
# alembic upgrade head
```

### Step 6: Run Backend

```bash
cd backend
python main.py
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Step 7: Run Frontend (in new terminal)

```bash
cd frontend
streamlit run app.py
```

Frontend will be available at: `http://localhost:8501`

## 🐳 Docker Setup

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker

```bash
# Build backend image
docker build -t safespace-backend ./backend

# Run backend container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/safespace \
  -e OPENAI_API_KEY=your-key \
  safespace-backend

# Build frontend image
docker build -t safespace-frontend ./frontend

# Run frontend container
docker run -p 8501:8501 safespace-frontend
```

## ⚙️ Configuration Guide

### LLM Provider Selection

#### Option 1: OpenAI (Recommended)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-4-turbo
```

Get API key: https://platform.openai.com/api-keys

#### Option 2: Groq (Faster, Free Tier)

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-your-key
```

Get API key: https://console.groq.com

#### Option 3: Local LLM (MedGemma via Ollama)

Install Ollama: https://ollama.ai

```bash
# Pull MedGemma model
ollama pull medgemma:2b

# Run Ollama server
ollama serve
```

```env
USE_LOCAL_LLM=True
OLLAMA_BASE_URL=http://localhost:11434
MEDGEMMA_MODEL=medgemma-2b
```

### Voice Service Setup

#### Option 1: Local (No Setup Required)

```env
VOICE_PROVIDER=local
```

Limited functionality, good for testing.

#### Option 2: Google Cloud Speech

1. Create Google Cloud project
2. Enable Speech-to-Text API
3. Create service account and download JSON credentials
4. Set environment:

```env
VOICE_PROVIDER=google
GOOGLE_CLOUD_SPEECH_CREDENTIALS=/path/to/credentials.json
```

#### Option 3: Azure Cognitive Services

1. Create Azure account
2. Create Speech service resource
3. Copy API key and region

```env
VOICE_PROVIDER=azure
AZURE_SPEECH_KEY=your-key
AZURE_SPEECH_REGION=eastus
```

### Emergency Services (Twilio)

For SMS/call alerts:

1. Create Twilio account: https://www.twilio.com
2. Get phone number
3. Get API credentials

```env
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
EMERGENCY_CONTACT_NUMBER=+1234567890
```

## 📚 API Usage Examples

### Create User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_language": "en",
    "enable_voice_input": true
  }'
```

Response:
```json
{
  "id": "user-123",
  "username": "BlueMind_47",
  "wellness_id": "WL654321",
  "preferred_language": "en",
  "wellness_score": 0.0,
  "total_chats": 0,
  "total_activities_completed": 0,
  "created_at": "2024-02-11T12:00:00"
}
```

### Create Conversation

```bash
curl -X POST http://localhost:8000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123"}'
```

### Send Message

```bash
curl -X POST http://localhost:8000/api/conversations/conv-123/messages \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "content": "I have been feeling stressed lately"
  }'
```

### Start Screening

```bash
curl -X POST http://localhost:8000/api/screening/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123"}'
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/test_screening.py

# Run with verbose output
pytest -v
```

### Test Files

- `tests/test_backend.py` - Backend API tests
- `tests/test_agent.py` - AI Agent tests
- `tests/test_screening.py` - Screening logic tests

## 🔒 Security Checklist

### Before Production Deployment

- [ ] Change `SECRET_KEY` to secure random value
- [ ] Set `DEBUG=False`
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set up CORS properly
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Set up logging and monitoring
- [ ] Enable HIPAA compliance features
- [ ] Audit encryption settings
- [ ] Set up backups
- [ ] Configure firewall rules
- [ ] Use environment secrets management

### Sensitive Data Handling

```python
# DO NOT commit sensitive files
# Add to .gitignore:
.env
.env.local
credentials.json
*.key
*.pem
logs/
```

## 📊 Database Migrations

### Creating Migrations (with Alembic)

```bash
# Initialize Alembic (if not done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add screening table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🚨 Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep -i fastapi

# Check port availability
lsof -i :8000  # Port 8000 in use?

# Try different port
python main.py --port 8001
```

### LLM Connection Issues

```bash
# Test OpenAI API
python -c "from openai import OpenAI; client = OpenAI(api_key='your-key')"

# Test Groq
python -c "from groq import Groq; client = Groq(api_key='your-key')"

# Test Ollama
curl http://localhost:11434/api/tags
```

### Voice Service Issues

```bash
# Test Google Cloud Speech
gcloud auth application-default login

# Test Azure
python -c "import azure.cognitiveservices.speech as speechsdk"

# Test Twilio
from twilio.rest import Client
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql -U postgres -d safespace -c "SELECT 1"

# Check connection string
# DATABASE_URL=postgresql://user:password@localhost:5432/safespace

# Create database if not exists
createdb safespace
```

## 📈 Scaling & Deployment

### AWS Deployment

```bash
# Using Elastic Beanstalk
eb init -p python-3.11 safespace
eb create safespace-env
eb deploy
```

### Google Cloud Deployment

```bash
# Using Cloud Run
gcloud run deploy safespace-backend \
  --source . \
  --platform managed \
  --region us-central1
```

### Docker Swarm / Kubernetes

See `docker-compose.yml` and Kubernetes manifests in `k8s/` directory.

## 📞 Support & Resources

- Documentation: `docs/` directory
- API Docs: `http://localhost:8000/docs`
- Issues: GitHub Issues
- Contact: support@safespace.ai

## 📝 Additional Resources

### Learning Resources

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Streamlit: https://docs.streamlit.io/
- LangChain: https://docs.langchain.com/
- Mental Health: https://www.mind.org.uk/

### Useful Tools

- Postman - API testing
- pgAdmin - PostgreSQL management
- Redis Commander - Redis management
- Swagger UI - Built-in API docs

---

For detailed information on each component, see the respective documentation files in the `docs/` directory.
