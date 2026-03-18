"""
SafeSpace Database Models & Schemas
Defines all data structures for users, conversations, screening, and activities
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field
import uuid

Base = declarative_base()

# ====================== SQLAlchemy Models (Database) ======================

class User(Base):
    """User model - stores anonymous user information"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Anonymous Identity
    username = Column(String(50), unique=True, nullable=False, index=True)
    wellness_id = Column(String(20), unique=True, nullable=False, index=True)
    avatar_id = Column(String(100), nullable=True)
    avatar_style = Column(JSON, nullable=True)
    
    # Account Status
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Settings
    preferred_language = Column(String(10), default="en")
    enable_voice_input = Column(Boolean, default=True)
    enable_notifications = Column(Boolean, default=True)
    
    # Wellness Stats
    total_screening_attempts = Column(Integer, default=0)
    total_chats = Column(Integer, default=0)
    total_activities_completed = Column(Integer, default=0)
    wellness_score = Column(Float, default=0.0)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    screening_results = relationship("ScreeningResult", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Conversation(Base):
    """Conversation model - stores chat messages and interactions"""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Conversation Metadata
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Conversation Content
    messages = Column(JSON, default=list)  # List of message objects
    total_messages = Column(Integer, default=0)
    
    # AI Analysis
    sentiment_analysis = Column(JSON, nullable=True)  # Emotional state analysis
    crisis_indicators = Column(Float, default=0.0)    # 0-1 score for crisis risk
    requires_escalation = Column(Boolean, default=False)
    
    # User Feedback
    user_satisfaction = Column(Float, nullable=True)  # 1-5 rating
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation {self.id}>"


class ScreeningResult(Base):
    """Screening Result model - stores mental health screening results"""
    __tablename__ = "screening_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Assessment Details
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    
    # Scoring
    total_score = Column(Float, default=0.0)
    mood_score = Column(Float, default=0.0)
    sleep_score = Column(Float, default=0.0)
    stress_score = Column(Float, default=0.0)
    behavior_score = Column(Float, default=0.0)
    
    # Risk Assessment
    risk_level = Column(String(20), default="low")  # low, moderate, high
    risk_indicators = Column(JSON, default=list)
    
    # Recommendations
    recommendations = Column(JSON, default=dict)
    self_help_resources = Column(JSON, default=list)
    professional_help_needed = Column(Boolean, default=False)
    
    # Questions & Responses
    responses = Column(JSON, default=dict)  # question_id -> response
    
    # Relationships
    user = relationship("User", back_populates="screening_results")
    
    def __repr__(self):
        return f"<ScreeningResult {self.id}>"


class UserActivity(Base):
    """User Activity model - tracks completed wellness activities"""
    __tablename__ = "user_activities"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity Details
    activity_id = Column(String(100), nullable=False)
    activity_name = Column(String(200), nullable=False)
    activity_type = Column(String(50), nullable=False)  # quiz, game, journal, mindfulness
    
    # Completion
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Performance & Scoring
    score = Column(Float, default=0.0)
    points_earned = Column(Integer, default=0)
    performance_metrics = Column(JSON, nullable=True)  # Custom metrics per activity
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    def __repr__(self):
        return f"<UserActivity {self.activity_id}>"


class UserBadge(Base):
    """User Badge model - tracks earned badges and achievements"""
    __tablename__ = "user_badges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Badge Details
    badge_id = Column(String(100), nullable=False)
    badge_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Timeline
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="badges")
    
    def __repr__(self):
        return f"<UserBadge {self.badge_name}>"


class Message(Base):
    """Message model - stores individual chat messages"""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    
    # Message Content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, voice, image
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tokens_used = Column(Integer, default=0)
    
    # Voice-specific fields
    voice_language = Column(String(10), nullable=True)
    transcription_confidence = Column(Float, nullable=True)  # 0-1 for speech-to-text accuracy
    
    # Emotional Analysis
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    emotion_scores = Column(JSON, nullable=True)  # emotion -> confidence scores
    
    def __repr__(self):
        return f"<Message {self.id[:8]}...>"


class CrisisAlert(Base):
    """Crisis Alert model - tracks emergency situations"""
    __tablename__ = "crisis_alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=True)
    
    # Crisis Details
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    risk_score = Column(Float, default=0.0)
    
    # Detection Method
    detection_type = Column(String(50), nullable=False)  # keyword, sentiment, pattern
    crisis_indicators = Column(JSON, default=list)
    
    # Response
    escalation_attempted = Column(Boolean, default=False)
    escalation_timestamp = Column(DateTime, nullable=True)
    escalation_method = Column(String(50), nullable=True)  # twilio, email, notification
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<CrisisAlert {self.risk_level}>"


# ====================== Pydantic Models (API Schemas) ======================

class UserCreate(BaseModel):
    """Schema for user creation"""
    preferred_language: str = "en"
    enable_voice_input: bool = True

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    username: str
    wellness_id: str
    avatar_id: Optional[str]
    preferred_language: str
    wellness_score: float
    total_chats: int
    total_activities_completed: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    """Schema for creating a message"""
    content: str
    message_type: str = "text"
    voice_language: Optional[str] = None

class MessageResponse(BaseModel):
    """Schema for message response"""
    id: str
    role: str
    content: str
    message_type: str
    created_at: datetime
    sentiment: Optional[str] = None
    
    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    initial_message: Optional[str] = None

class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: str
    started_at: datetime
    total_messages: int
    is_active: bool
    crisis_indicators: float
    
    class Config:
        from_attributes = True

class ScreeningAnswers(BaseModel):
    """Schema for screening answers"""
    responses: Dict[str, str]  # question_id -> answer
    duration_seconds: int

class ScreeningResponse(BaseModel):
    """Schema for screening results response"""
    id: str
    completed_at: datetime
    total_score: float
    risk_level: str
    recommendations: Dict[str, Any]
    professional_help_needed: bool
    
    class Config:
        from_attributes = True

class ActivityResponse(BaseModel):
    """Schema for activity response"""
    id: str
    activity_id: str
    activity_name: str
    is_completed: bool
    score: float
    points_earned: int
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BadgeResponse(BaseModel):
    """Schema for badge response"""
    badge_id: str
    badge_name: str
    description: Optional[str]
    earned_at: datetime
    
    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    """Schema for user statistics"""
    wellness_score: float
    total_chats: int
    total_screenings: int
    total_activities: int
    current_streak: int
    badges_earned: int
    total_points: int
    
    class Config:
        from_attributes = True

class VoiceInput(BaseModel):
    """Schema for voice input"""
    audio_data: str  # base64 encoded
    language: str = "en"

class VoiceTranscription(BaseModel):
    """Schema for voice transcription response"""
    transcribed_text: str
    language: str
    confidence: float
    
class CrisisAlertResponse(BaseModel):
    """Schema for crisis alert response"""
    id: str
    risk_level: str
    risk_score: float
    detected_at: datetime
    escalation_attempted: bool
    
    class Config:
        from_attributes = True

class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: datetime
    database: str
    llm_service: str
    voice_service: str
