"""
SafeSpace Backend Configuration
Handles all environment variables and configuration settings
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "SafeSpace - AI Mental Health Therapist"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://safespace:safespace@localhost:5432/safespace"
    )
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017/safespace"
    )
    
    # LLM & AI Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # LLM Model Selection
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai, groq, google
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo")
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1500
    
    # MedGemma Configuration
    MEDGEMMA_MODEL: str = "medgemma-2b"  # or medgemma-7b
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "False").lower() == "true"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Twilio Configuration (Emergency Response)
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    EMERGENCY_CONTACT_NUMBER: Optional[str] = os.getenv("EMERGENCY_CONTACT_NUMBER")
    
    # Voice Service Configuration
    VOICE_PROVIDER: str = os.getenv("VOICE_PROVIDER", "google")  # google or azure
    AZURE_SPEECH_KEY: Optional[str] = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION: Optional[str] = os.getenv("AZURE_SPEECH_REGION", "eastus")
    GOOGLE_CLOUD_SPEECH_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_CLOUD_SPEECH_CREDENTIALS")
    
    # Supported Languages
    SUPPORTED_LANGUAGES: list = [
        "en",  # English
        "hi",  # Hindi
        "ta",  # Tamil
        "bn",  # Bengali
        "te",  # Telugu
        "kn",  # Kannada
        "ml",  # Malayalam
    ]
    
    # Location Services
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    ENABLE_LOCATION_SERVICES: bool = os.getenv("ENABLE_LOCATION_SERVICES", "True").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
        "http://localhost",
    ]
    
    # Email Configuration (for notifications)
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM", "support@safespace.ai")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/safespace.log")
    
    # Feature Flags
    ENABLE_SCREENING: bool = True
    ENABLE_VOICE_INPUT: bool = True
    ENABLE_GAMIFICATION: bool = True
    ENABLE_EMERGENCY_RESPONSE: bool = True
    ENABLE_LOCATION_MATCHING: bool = True
    
    # Screening Configuration
    SCREENING_QUESTIONS_FILE: str = "data/screening_questions.json"
    MIN_SCREENING_SCORE: float = 0.0
    MAX_SCREENING_SCORE: float = 100.0
    HIGH_RISK_THRESHOLD: float = 70.0
    MODERATE_RISK_THRESHOLD: float = 50.0
    
    # Gamification Configuration
    ENABLE_LEADERBOARD: bool = True
    ENABLE_BADGES: bool = True
    ENABLE_REWARDS: bool = True
    DAILY_CHALLENGE_LIMIT: int = 5
    WEEKLY_CHALLENGE_LIMIT: int = 25
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSIONS_PER_USER: int = 5
    
    # API Documentation
    API_DOCS_URL: str = "/docs"
    OPENAPI_URL: str = "/openapi.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()

# Screening Configuration
SCREENING_CONFIG = {
    "categories": {
        "mood": {
            "weight": 0.3,
            "questions": [
                "How have you been feeling emotionally in the past week?",
                "Do you experience frequent sadness or emptiness?",
                "Have you lost interest in activities you normally enjoy?",
            ]
        },
        "sleep": {
            "weight": 0.2,
            "questions": [
                "How would you describe your sleep quality?",
                "Do you have difficulty falling or staying asleep?",
                "Do you feel rested after sleeping?",
            ]
        },
        "stress": {
            "weight": 0.3,
            "questions": [
                "How stressed do you feel about your responsibilities?",
                "Can you manage your stress effectively?",
                "Do you feel overwhelmed by daily tasks?",
            ]
        },
        "behavior": {
            "weight": 0.2,
            "questions": [
                "Have you noticed any changes in your social interactions?",
                "Do you withdraw from social activities?",
                "Have your eating or substance use habits changed?",
            ]
        }
    },
    "risk_levels": {
        "low": {"min": 0, "max": 40, "color": "green"},
        "moderate": {"min": 40, "max": 70, "color": "yellow"},
        "high": {"min": 70, "max": 100, "color": "red"},
    }
}

# Gamification Activities
GAMIFICATION_CONFIG = {
    "activities": [
        {
            "id": "stress_quiz",
            "name": "Stress Awareness Quiz",
            "description": "Learn about stress triggers and coping mechanisms",
            "difficulty": "easy",
            "points": 50,
            "duration_minutes": 5
        },
        {
            "id": "mood_tracker",
            "name": "Daily Mood Tracker",
            "description": "Track your mood patterns throughout the day",
            "difficulty": "easy",
            "points": 30,
            "duration_minutes": 2
        },
        {
            "id": "mindfulness_game",
            "name": "Mindfulness Mini-Game",
            "description": "Guided breathing and meditation exercises",
            "difficulty": "easy",
            "points": 40,
            "duration_minutes": 10
        },
        {
            "id": "resilience_challenge",
            "name": "Emotional Resilience Challenge",
            "description": "Build emotional coping skills through interactive scenarios",
            "difficulty": "medium",
            "points": 75,
            "duration_minutes": 15
        },
        {
            "id": "journal_entry",
            "name": "Journal Entry Challenge",
            "description": "Write reflective journal entries for self-discovery",
            "difficulty": "easy",
            "points": 50,
            "duration_minutes": 10
        },
    ],
    "badges": [
        {"id": "first_chat", "name": "First Step", "description": "Completed first chat"},
        {"id": "screening_complete", "name": "Self-Aware", "description": "Completed wellness screening"},
        {"id": "week_streak", "name": "Consistent", "description": "7-day engagement streak"},
        {"id": "month_streak", "name": "Committed", "description": "30-day engagement streak"},
        {"id": "game_master", "name": "Wellness Master", "description": "Completed 10 activities"},
    ],
    "rewards": [
        {"id": "reward_1", "points": 100, "description": "Unlock exclusive content"},
        {"id": "reward_2", "points": 250, "description": "Free counseling session access"},
        {"id": "reward_3", "points": 500, "description": "Premium wellness resources"},
    ]
}

# Anonymous Name Generation
ANONYMOUS_NAMES = {
    "prefixes": [
        "Blue", "Hope", "Quiet", "Calm", "Bright", "Gentle", "Serene",
        "Peaceful", "Mindful", "Strong", "Wise", "Brave", "Kind"
    ],
    "suffixes": [
        "Mind", "Walker", "Thought", "Wave", "Light", "Path", "Spirit",
        "Seeker", "Heart", "Soul", "Joy", "Peace", "Strength"
    ]
}

# Emergency Response Configuration
EMERGENCY_CONFIG = {
    "crisis_keywords": [
        "suicide", "kill myself", "self-harm", "cutting",
        "overdose", "die", "end my life", "no point living",
        "worthless", "nobody cares", "give up"
    ],
    "crisis_phrases": [
        "i want to hurt myself",
        "i can't take this anymore",
        "life is not worth living",
        "i don't deserve to live"
    ],
    "escalation_score_threshold": 0.8,  # 80% confidence
    "immediate_escalation_keywords": [
        "suicide", "overdose", "bleeding", "gun", "rope"
    ]
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "level": "DEBUG",
            "filename": "logs/safespace.log",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

# Print configuration on startup (development only)
if settings.DEBUG:
    print(f"🔧 SafeSpace Configuration Loaded")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Database: {settings.DATABASE_URL[:30]}...")
    print(f"   LLM Provider: {settings.LLM_PROVIDER}")
    print(f"   Voice Provider: {settings.VOICE_PROVIDER}")
    print(f"   Debug Mode: {settings.DEBUG}")
