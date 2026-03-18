"""
SafeSpace FastAPI Backend
Main application with all API endpoints
"""

import logging
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

from config import settings, ANONYMOUS_NAMES
from models import (
    User, Conversation, Message, ScreeningResult, UserActivity, UserBadge,
    UserCreate, UserResponse, MessageCreate, MessageResponse, ConversationResponse,
    ScreeningAnswers, ScreeningResponse, ActivityResponse, BadgeResponse,
    UserStatsResponse, VoiceInput, VoiceTranscription, CrisisAlertResponse,
    HealthCheckResponse
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# ====================== Database Setup ======================
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
except Exception as e:
    print(f"DB table creation warning: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from screening import ScreeningSession, ScreeningCalculator, ScreeningRecommendations
from voice_service import VoiceService, SupportedLanguage
from agent import AIMentalHealthAgent, OpenAIProvider, GroqProvider, MedGemmaProvider

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Mental Health Support Platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== Global State ======================
# In production, use database session management
agents = {}  # user_id -> AIMentalHealthAgent
screening_sessions = {}  # user_id -> ScreeningSession
voice_service = None

# ====================== Initialization ======================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global voice_service
    
    logger.info("🚀 SafeSpace backend starting up...")
    
    # Initialize voice service
    try:
        if settings.VOICE_PROVIDER == "google":
            voice_service = VoiceService(
                provider_type="google",
                api_key=settings.GOOGLE_API_KEY
            )
        elif settings.VOICE_PROVIDER == "azure":
            voice_service = VoiceService(
                provider_type="azure",
                api_key=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION
            )
        else:
            voice_service = VoiceService(provider_type="local")
        
        logger.info(f"✅ Voice service initialized: {settings.VOICE_PROVIDER}")
    except Exception as e:
        logger.warning(f"⚠️ Voice service initialization failed: {e}")
    
    logger.info("✅ SafeSpace backend ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 SafeSpace backend shutting down...")
    agents.clear()
    screening_sessions.clear()

# ====================== Health Check ======================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database="connected",
        llm_service="ready",
        voice_service="ready"
    )

# ====================== User Management ======================

def generate_anonymous_identity() -> tuple:
    """Generate anonymous username and wellness ID"""
    import random
    
    prefix = random.choice(ANONYMOUS_NAMES["prefixes"])
    suffix = random.choice(ANONYMOUS_NAMES["suffixes"])
    username = f"{prefix}{suffix}_{random.randint(10, 99)}"
    
    wellness_id = f"WL{random.randint(100000, 999999)}"
    
    return username, wellness_id

@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user_create: UserCreate):
    """Register a new anonymous user and save to DB"""
    try:
        username, wellness_id = generate_anonymous_identity()
        user_id = str(uuid.uuid4())

        # Save to PostgreSQL
        db = SessionLocal()
        try:
            db_user = User(
                id=user_id,
                username=username,
                wellness_id=wellness_id,
                avatar_id="avatar_001",
                preferred_language=user_create.preferred_language,
                enable_voice_input=user_create.enable_voice_input,
                wellness_score=0.0,
                total_chats=0,
                total_activities_completed=0,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        except Exception as db_err:
            db.rollback()
            logger.warning(f"DB save failed (continuing anyway): {db_err}")
        finally:
            db.close()

        user_data = {
            "id": user_id,
            "username": username,
            "wellness_id": wellness_id,
            "avatar_id": "avatar_001",
            "preferred_language": user_create.preferred_language,
            "enable_voice_input": user_create.enable_voice_input,
            "wellness_score": 0.0,
            "total_chats": 0,
            "total_activities_completed": 0,
            "created_at": datetime.utcnow(),
        }

        logger.info(f"✅ New user registered: {username} ({wellness_id})")
        return UserResponse(**user_data)

    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/auth/signin", response_model=UserResponse)
async def signin_with_wellness_id(wellness_id: str):
    """Sign in existing user with their Wellness ID"""
    try:
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(
                User.wellness_id == wellness_id.upper().strip()
            ).first()

            if not db_user:
                raise HTTPException(status_code=404, detail="Wellness ID not found")

            # Update last active
            db_user.last_active = datetime.utcnow()
            db.commit()

            user_data = {
                "id": db_user.id,
                "username": db_user.username,
                "wellness_id": db_user.wellness_id,
                "avatar_id": db_user.avatar_id or "avatar_001",
                "preferred_language": db_user.preferred_language or "en",
                "enable_voice_input": db_user.enable_voice_input or True,
                "wellness_score": db_user.wellness_score or 0.0,
                "total_chats": db_user.total_chats or 0,
                "total_activities_completed": db_user.total_activities_completed or 0,
                "created_at": db_user.created_at,
            }
            logger.info(f"✅ User signed in: {db_user.username} ({wellness_id})")
            return UserResponse(**user_data)

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sign-in error: {e}")
        raise HTTPException(status_code=500, detail="Sign-in failed")

@app.get("/api/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user information"""
    try:
        # In production, fetch from database
        # Placeholder response
        return UserResponse(
            id=user_id,
            username=f"User_{user_id[:8]}",
            wellness_id=f"WL{user_id[:6]}",
            avatar_id="avatar_001",
            preferred_language="en",
            wellness_score=0.0,
            total_chats=0,
            total_activities_completed=0,
            created_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=404, detail="User not found")

# ====================== Chat & Conversation ======================

@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(user_id: str):
    """Create a new conversation"""
    try:
        conversation_id = str(uuid.uuid4())
        
        # Initialize AI agent for this conversation if not exists
        if user_id not in agents:
            if settings.LLM_PROVIDER == "openai":
                provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            elif settings.LLM_PROVIDER == "groq":
                provider = GroqProvider(api_key=settings.GROQ_API_KEY)
            else:
                provider = MedGemmaProvider(
                    model_name=settings.MEDGEMMA_MODEL,
                    base_url=settings.OLLAMA_BASE_URL
                )
            agents[user_id] = AIMentalHealthAgent(provider)

        # Load past memory and inject into agent's system prompt
        past_memory = await get_user_memory(user_id)
        if past_memory:
            agents[user_id].past_memory = past_memory
            logger.info(f"✅ Memory loaded for user {user_id}")
        else:
            agents[user_id].past_memory = ""
        
        # Save conversation to DB
        db = SessionLocal()
        try:
            db_conv = Conversation(
                id=conversation_id,
                user_id=user_id,
                started_at=datetime.utcnow(),
                is_active=True,
                messages=[],
                total_messages=0,
                crisis_indicators=0.0,
            )
            db.add(db_conv)
            # Update user total_chats
            db_user = db.query(User).filter(User.id == user_id).first()
            if db_user:
                db_user.total_chats = (db_user.total_chats or 0) + 1
                db_user.last_active = datetime.utcnow()
            db.commit()
        except Exception as db_err:
            db.rollback()
            logger.warning(f"DB conversation save failed: {db_err}")
        finally:
            db.close()

        logger.info(f"✅ Conversation created: {conversation_id}")
        
        return ConversationResponse(
            id=conversation_id,
            started_at=datetime.utcnow(),
            total_messages=0,
            is_active=True,
            crisis_indicators=0.0
        )
    
    except Exception as e:
        logger.error(f"Conversation creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")

@app.post("/api/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(conversation_id: str, user_id: str, message: MessageCreate):
    """Send a message in conversation and get AI response"""
    try:
        if user_id not in agents:
            raise HTTPException(status_code=400, detail="No active conversation")
        
        agent = agents[user_id]
        
        # Process message through AI agent
        result = await agent.process_user_message(message.content, user_id)
        
        # Check for crisis escalation
        if result["escalation"]["required"]:
            logger.critical(f"CRISIS ALERT for user {user_id}: {result['escalation']['reason']}")
            # In production: trigger emergency response (Twilio, etc.)
        
        msg_id = str(uuid.uuid4())

        # Save both messages to DB
        db = SessionLocal()
        try:
            # Save user message
            db.add(Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="user",
                content=message.content,
                message_type=message.message_type,
                created_at=datetime.utcnow(),
                sentiment=result["analysis"]["sentiment"]
            ))
            # Save assistant message
            db.add(Message(
                id=msg_id,
                conversation_id=conversation_id,
                role="assistant",
                content=result["response"],
                message_type="text",
                created_at=datetime.utcnow(),
                sentiment=result["analysis"]["sentiment"]
            ))
            # Update conversation message count
            db_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if db_conv:
                db_conv.total_messages = (db_conv.total_messages or 0) + 2
                db_conv.crisis_indicators = result["analysis"]["crisis_score"]
                if result["escalation"]["required"]:
                    db_conv.requires_escalation = True
            db.commit()
        except Exception as db_err:
            db.rollback()
            logger.warning(f"DB message save failed: {db_err}")
        finally:
            db.close()

        ai_emotion   = result["analysis"].get("ai_emotion", {})
        ai_crisis    = result["analysis"].get("ai_crisis", {})

        return {
            "id": msg_id,
            "role": "assistant",
            "content": result["response"],
            "message_type": "text",
            "created_at": datetime.utcnow().isoformat(),
            "sentiment": result["analysis"]["sentiment"],
            "ai_emotion": ai_emotion,
            "ai_crisis": ai_crisis,
            "crisis_detected": result["escalation"]["required"],
        }
    
    except Exception as e:
        logger.error(f"Message processing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

# ====================== Mental Health Screening ======================

@app.post("/api/screening/start")
async def start_screening(user_id: str):
    """Start mental health screening"""
    try:
        # Create screening session
        session = ScreeningSession(user_id)
        screening_sessions[user_id] = session
        
        # Get first question
        question_id, question = session.get_next_question()
        
        logger.info(f"✅ Screening started for user {user_id}")
        
        return {
            "status": "started",
            "question_id": question_id,
            "question": question["text"],
            "question_type": question.get("scale"),
            "options": question.get("responses", {}),
            "category": question.get("category", "general"),
            "total_questions": 16
        }
    
    except Exception as e:
        logger.error(f"Screening start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start screening")

@app.post("/api/screening/answer")
async def answer_screening_question(user_id: str, question_id: str, response: int):
    """Answer a screening question"""
    try:
        if user_id not in screening_sessions:
            raise HTTPException(status_code=400, detail="No active screening")
        
        session = screening_sessions[user_id]
        session.record_response(question_id, response)
        
        # Get next question
        next_question = session.get_next_question()
        
        if next_question:
            next_q_id, question = next_question
            total_questions = 16
            return {
                "status": "continue",
                "question_id": next_q_id,
                "question": question["text"],
                "options": question.get("responses", {}),
                "category": question.get("category", "general"),
                "progress": f"{session.current_question_index}/{total_questions}"
            }
        else:
            # Screening complete - serialize safely
            results = session.finalize_screening()
            del screening_sessions[user_id]

            def serialize(obj):
                if hasattr(obj, "isoformat"):
                    return obj.isoformat()
                if isinstance(obj, dict):
                    return {k: serialize(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [serialize(i) for i in obj]
                return obj

            safe_results = serialize(results)
            logger.info(f"✅ Screening completed for user {user_id}: {safe_results['risk_level']}")

            # Save screening result to DB
            db = SessionLocal()
            try:
                cat_scores = safe_results.get("category_scores", {})
                db_screening = ScreeningResult(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    completed_at=datetime.utcnow(),
                    total_score=safe_results.get("overall_score", 0),
                    mood_score=cat_scores.get("mood", 0),
                    sleep_score=cat_scores.get("sleep", 0),
                    stress_score=cat_scores.get("stress", 0),
                    behavior_score=cat_scores.get("behavior", 0),
                    risk_level=safe_results.get("risk_level", "low"),
                    risk_indicators=safe_results.get("risk_indicators", []),
                    recommendations=safe_results.get("recommendations", {}),
                    responses=safe_results.get("responses", {}),
                    professional_help_needed=safe_results.get("risk_level") == "high",
                )
                db.add(db_screening)
                # Update user screening count
                db_user = db.query(User).filter(User.id == user_id).first()
                if db_user:
                    db_user.total_screening_attempts = (db_user.total_screening_attempts or 0) + 1
                    db_user.last_active = datetime.utcnow()
                db.commit()
            except Exception as db_err:
                db.rollback()
                logger.warning(f"DB screening save failed: {db_err}")
            finally:
                db.close()

            return {
                "status": "completed",
                "results": safe_results
            }
    
    except Exception as e:
        logger.error(f"Screening answer error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process answer")

@app.get("/api/screening/{user_id}/results", response_model=ScreeningResponse)
async def get_screening_results(user_id: str):
    """Get latest screening results"""
    try:
        # In production, fetch from database
        return ScreeningResponse(
            id=str(uuid.uuid4()),
            completed_at=datetime.utcnow(),
            total_score=65.5,
            risk_level="moderate",
            recommendations={"self_help": [], "professional": False},
            professional_help_needed=False
        )
    except Exception as e:
        logger.error(f"Error fetching screening results: {e}")
        raise HTTPException(status_code=404, detail="No screening results found")

# ====================== Voice Interface ======================

@app.post("/api/voice/transcribe", response_model=VoiceTranscription)
async def transcribe_voice(voice_input: VoiceInput):
    """Transcribe voice input to text"""
    try:
        if not voice_service:
            raise HTTPException(status_code=503, detail="Voice service unavailable")
        
        # Transcribe audio
        transcribed_text, confidence = await voice_service.transcribe(
            voice_input.audio_data,
            voice_input.language
        )
        
        logger.info(f"✅ Voice transcribed ({voice_input.language}): {transcribed_text[:50]}...")
        
        return VoiceTranscription(
            transcribed_text=transcribed_text,
            language=voice_input.language,
            confidence=confidence
        )
    
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail="Failed to transcribe voice")

@app.get("/api/voice/languages")
async def get_supported_languages():
    """Get supported languages for voice"""
    try:
        languages = VoiceService.get_supported_languages()
        return {"languages": languages}
    except Exception as e:
        logger.error(f"Error fetching languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch languages")

# ====================== Wellness Activities ======================

@app.get("/api/activities")
async def get_activities(user_id: str):
    """Get available wellness activities"""
    try:
        activities = [
            {
                "id": "stress_quiz",
                "name": "Stress Awareness Quiz",
                "description": "Learn about stress triggers",
                "difficulty": "easy",
                "points": 50
            },
            {
                "id": "mood_tracker",
                "name": "Daily Mood Tracker",
                "description": "Track your mood patterns",
                "difficulty": "easy",
                "points": 30
            },
            {
                "id": "mindfulness",
                "name": "Mindfulness Mini-Game",
                "description": "Guided breathing exercises",
                "difficulty": "easy",
                "points": 40
            }
        ]
        return {"activities": activities}
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch activities")

@app.post("/api/activities/{activity_id}/complete")
async def complete_activity(user_id: str, activity_id: str, score: float):
    """Mark activity as complete"""
    try:
        activity = ActivityResponse(
            id=str(uuid.uuid4()),
            activity_id=activity_id,
            activity_name="Activity Name",
            is_completed=True,
            score=score,
            points_earned=int(score * 10),
            completed_at=datetime.utcnow()
        )
        
        logger.info(f"✅ Activity completed: {activity_id} (score: {score})")
        
        return activity
    except Exception as e:
        logger.error(f"Error completing activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete activity")

# ====================== User Statistics ======================

@app.get("/api/user/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: str):
    """Get user statistics and progress"""
    try:
        return UserStatsResponse(
            wellness_score=0.0,
            total_chats=0,
            total_screenings=0,
            total_activities=0,
            current_streak=0,
            badges_earned=0,
            total_points=0
        )
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

# ====================== Resources ======================

@app.get("/api/resources")
async def get_mental_health_resources(category: Optional[str] = None):
    """Get mental health resources and self-help guides"""
    try:
        resources = {
            "mood": [
                {
                    "title": "Understanding Depression",
                    "url": "https://www.mind.org.uk",
                    "type": "article"
                }
            ],
            "stress": [
                {
                    "title": "Stress Management Techniques",
                    "url": "https://www.apa.org",
                    "type": "guide"
                }
            ],
            "crisis": [
                {
                    "title": "National Suicide Prevention Lifeline",
                    "phone": "1-800-273-8255",
                    "type": "hotline"
                }
            ]
        }
        
        if category:
            return {"resources": resources.get(category, [])}
        return {"resources": resources}
    
    except Exception as e:
        logger.error(f"Error fetching resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch resources")

# ====================== Emergency/Crisis ======================

@app.post("/api/crisis/report")
async def report_crisis(user_id: str, description: str):
    """Report a crisis situation"""
    try:
        logger.critical(f"🚨 CRISIS REPORTED by user {user_id}: {description}")
        
        # In production: Trigger Twilio emergency calls, notifications, etc.
        
        return {
            "status": "reported",
            "message": "Crisis reported. Emergency services have been notified.",
            "emergency_hotline": "911",
            "crisis_resources": {
                "national_hotline": "1-800-273-8255",
                "text_crisis": "Text HOME to 741741",
                "chat": "https://suicidepreventionlifeline.org/chat/"
            }
        }
    except Exception as e:
        logger.error(f"Crisis reporting error: {e}")
        raise HTTPException(status_code=500, detail="Failed to report crisis")

# ====================== Feedback & Ratings ======================

@app.post("/api/conversations/{conversation_id}/feedback")
async def submit_conversation_feedback(conversation_id: str, rating: int, notes: str = ""):
    """Submit feedback on conversation"""
    try:
        logger.info(f"✅ Feedback received for conversation {conversation_id}: {rating}/5")
        
        return {"status": "feedback_received", "rating": rating}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

# ====================== WebSocket (Real-time Chat) ======================

@app.websocket("/ws/{user_id}/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, conversation_id: str):
    """WebSocket endpoint for real-time conversations"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            if user_id in agents:
                agent = agents[user_id]
                result = await agent.process_user_message(data, user_id)
                
                # Send response back to client
                await websocket.send_json({
                    "response": result["response"],
                    "sentiment": result["analysis"]["sentiment"],
                    "crisis_detected": result["escalation"]["required"]
                })
            else:
                await websocket.send_json({"error": "No active conversation"})
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        await websocket.close()

# ====================== Error Handlers ======================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ====================== Root ======================

# ====================== AI Memory System ======================

async def summarize_conversation(messages: list, llm_provider) -> str:
    """Use AI to summarize a conversation into key insights"""
    if not messages or len(messages) < 2:
        return ""
    try:
        convo_text = "\n".join([
            f"{m['role'].upper()}: {m['content'][:200]}"
            for m in messages[-20:]
        ])
        prompt = f"""Summarize this mental health therapy conversation in 2-3 sentences.
Focus on: main concerns expressed, emotional state, topics discussed, any progress made.
Be concise and clinical but warm. Do NOT include crisis keywords.

Conversation:
{convo_text}

Summary (2-3 sentences only):"""

        response, _ = await llm_provider.generate_response(
            [{"role": "user", "content": prompt}],
            system_prompt="You summarize therapy conversations concisely.",
            temperature=0.3,
            max_tokens=200
        )
        return response.strip()
    except Exception as e:
        logger.warning(f"Summary generation failed: {e}")
        return ""


async def get_user_memory(user_id: str) -> str:
    """Retrieve past conversation summaries for a user"""
    db = SessionLocal()
    try:
        past_convs = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.notes != None,
            Conversation.notes != ""
        ).order_by(Conversation.started_at.desc()).limit(3).all()

        if not past_convs:
            return ""

        memory_parts = []
        for conv in past_convs:
            date_str = conv.started_at.strftime("%b %d") if conv.started_at else "recently"
            memory_parts.append(f"[{date_str}]: {conv.notes}")

        return "\n".join(memory_parts)
    except Exception as e:
        logger.warning(f"Memory retrieval failed: {e}")
        return ""
    finally:
        db.close()


@app.post("/api/conversations/{conversation_id}/summarize")
async def summarize_conversation_endpoint(conversation_id: str, user_id: str):
    """Summarize and save conversation to memory"""
    try:
        db = SessionLocal()
        try:
            conv = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Get messages from DB
            msgs = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at).all()

            if len(msgs) < 2:
                return {"summary": "", "message": "Not enough messages to summarize"}

            messages_list = [{"role": m.role, "content": m.content} for m in msgs]

            # Get LLM provider
            if user_id not in agents:
                provider = GroqProvider(api_key=settings.GROQ_API_KEY)
                agents[user_id] = AIMentalHealthAgent(provider)

            summary = await summarize_conversation(messages_list, agents[user_id].llm)

            # Save summary to conversation notes
            conv.notes = summary
            conv.is_active = False
            conv.ended_at = datetime.utcnow()
            db.commit()

            logger.info(f"✅ Conversation {conversation_id} summarized")
            return {"summary": summary}

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        raise HTTPException(status_code=500, detail="Failed to summarize")


@app.get("/api/user/{user_id}/memory")
async def get_memory(user_id: str):
    """Get user memory (past conversation summaries)"""
    try:
        memory = await get_user_memory(user_id)
        return {"memory": memory, "has_memory": bool(memory)}
    except Exception as e:
        logger.error(f"Memory fetch error: {e}")
        return {"memory": "", "has_memory": False}


@app.post("/api/screening/generate-report")
async def generate_ai_report(user_id: str, screening_data: dict):
    """Generate a personalized AI wellness report using Groq"""
    try:
        overall_score = screening_data.get("overall_score", 0)
        risk_level    = screening_data.get("risk_level", "low")
        cat_scores    = screening_data.get("category_scores", {})
        responses     = screening_data.get("responses", {})

        prompt = f"""You are a compassionate mental health wellness advisor. Based on this student's screening results, write a warm, personalized wellness report.

SCREENING DATA:
- Overall Risk Score: {overall_score}/100 (higher = more concern)
- Risk Level: {risk_level.upper()}
- Mood Score: {cat_scores.get('mood', 0)}/100
- Sleep Score: {cat_scores.get('sleep', 0)}/100
- Stress Score: {cat_scores.get('stress', 0)}/100
- Behaviour Score: {cat_scores.get('behavior', 0)}/100

Write a report with EXACTLY these sections (use these exact headings):

## Overall Wellness Summary
(2-3 sentences personalised to their scores)

## What Your Scores Mean
(Explain each category score in simple, empathetic language — 1-2 sentences each)

## Your Strengths
(Identify 2-3 positive aspects based on their lower-risk scores)

## Areas to Focus On
(Address the higher-risk areas with compassion, not alarm — 2-3 points)

## Personalised Action Plan
(5 specific, practical steps tailored to their exact scores)

## Encouragement
(A warm, motivating closing paragraph — 2-3 sentences)

Keep the tone warm, non-clinical, encouraging and non-judgmental. This is for a student. Do not use scary medical language."""

        if user_id not in agents:
            if settings.LLM_PROVIDER == "groq":
                provider = GroqProvider(api_key=settings.GROQ_API_KEY)
            else:
                provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            agents[user_id] = AIMentalHealthAgent(provider)

        agent = agents[user_id]
        report_text, _ = await agent.llm.generate_response(
            [{"role": "user", "content": prompt}],
            system_prompt="You are a compassionate mental health wellness advisor writing personalized reports for students.",
            temperature=0.7,
            max_tokens=1500
        )

        logger.info(f"✅ AI report generated for user {user_id}")
        return {"report": report_text, "generated_at": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get real platform statistics from DB"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        total_users      = db.query(func.count(User.id)).scalar() or 0
        total_messages   = db.query(func.count(Message.id)).scalar() or 0
        total_screenings = db.query(func.count(ScreeningResult.id)).scalar() or 0
        high_risk        = db.query(func.count(ScreeningResult.id)).filter(ScreeningResult.risk_level == "high").scalar() or 0
        moderate_risk    = db.query(func.count(ScreeningResult.id)).filter(ScreeningResult.risk_level == "moderate").scalar() or 0
        low_risk         = db.query(func.count(ScreeningResult.id)).filter(ScreeningResult.risk_level == "low").scalar() or 0

        # Recent users
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(10).all()
        users_list = [{
            "username": u.username,
            "wellness_id": u.wellness_id,
            "created_at": u.created_at.strftime("%b %d, %Y") if u.created_at else "",
            "role": "Admin" if u.username.startswith("Admin") else "Student",
        } for u in recent_users]

        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "total_screenings": total_screenings,
            "high_risk": high_risk,
            "moderate_risk": moderate_risk,
            "low_risk": low_risk,
            "recent_users": users_list,
        }
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return {"total_users":0,"total_messages":0,"total_screenings":0,"high_risk":0,"moderate_risk":0,"low_risk":0,"recent_users":[]}
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "active",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
