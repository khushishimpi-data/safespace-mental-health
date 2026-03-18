"""
SafeSpace AI Agent
Implements intelligent mental health therapist using LangGraph
Integrates MedGemma LLM with crisis detection and tool integration
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)

class EmotionalAnalyzer:
    """Analyzes emotional content in text"""
    
    CRISIS_KEYWORDS = [
        "suicide", "kill myself", "end my life", "no point living",
        "self-harm", "cutting", "overdose", "give up", "worthless",
        "nobody cares", "better off dead", "pain", "suffering"
    ]
    
    EMOTION_INDICATORS = {
        "happy": ["happy", "joy", "excellent", "great", "wonderful", "amazing"],
        "sad": ["sad", "depressed", "down", "blue", "unhappy", "miserable"],
        "anxious": ["anxious", "worried", "nervous", "afraid", "scared", "panic"],
        "angry": ["angry", "furious", "mad", "frustrated", "annoyed", "irritated"],
        "hopeful": ["hope", "better", "improving", "positive", "optimistic"],
        "hopeless": ["hopeless", "helpless", "desperate", "lost", "pointless"]
    }
    
    @staticmethod
    def analyze_sentiment(text: str) -> Tuple[str, Dict[str, float]]:
        """
        Analyze sentiment in text
        Returns: (sentiment, emotion_scores)
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in EmotionalAnalyzer.EMOTION_INDICATORS.items():
            score = sum(text_lower.count(kw) for kw in keywords)
            emotion_scores[emotion] = score
        
        # Determine overall sentiment
        if emotion_scores["sad"] > emotion_scores["happy"] or emotion_scores["hopeless"] > emotion_scores["hopeful"]:
            sentiment = "negative"
        elif emotion_scores["happy"] > emotion_scores["sad"] and emotion_scores["hopeful"] > emotion_scores["hopeless"]:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        
        return sentiment, emotion_scores
    
    @staticmethod
    async def ai_detect_emotion(text: str, llm_client) -> Dict[str, Any]:
        """
        Use AI (Groq) to detect emotion from text with high accuracy.
        Returns rich emotion data including primary emotion, intensity and insight.
        """
        try:
            prompt = f"""Analyze the emotional state in this message and respond ONLY with a JSON object.

Message: "{text}"

Respond with EXACTLY this JSON format (no extra text):
{{
  "primary_emotion": "one of: happy, sad, anxious, angry, frustrated, hopeful, hopeless, calm, overwhelmed, lonely, grateful, confused, fearful, neutral",
  "intensity": "one of: low, medium, high",
  "sentiment": "one of: positive, negative, neutral",
  "emoji": "single emoji that best represents the emotion",
  "insight": "one short sentence (max 10 words) describing what the person seems to be feeling"
}}"""

            if llm_client is None:
                raise ValueError("No LLM client")

            messages = [{"role": "user", "content": prompt}]
            response_text, _ = await llm_client.generate_response(
                messages, 
                system_prompt="You are an emotion detection AI. Always respond with valid JSON only.",
                temperature=0.1,
                max_tokens=200
            )
            
            # Clean and parse JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                emotion_data = json.loads(json_match.group())
                return emotion_data
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.warning(f"AI emotion detection failed: {e}, using keyword fallback")
            # Fallback to keyword-based detection
            text_lower = text.lower()
            if any(w in text_lower for w in ["happy", "great", "wonderful", "excited", "love"]):
                return {"primary_emotion": "happy", "intensity": "medium", "sentiment": "positive", "emoji": "😊", "insight": "Feeling positive and upbeat"}
            elif any(w in text_lower for w in ["sad", "depressed", "crying", "hurt", "miss"]):
                return {"primary_emotion": "sad", "intensity": "medium", "sentiment": "negative", "emoji": "😢", "insight": "Experiencing sadness or grief"}
            elif any(w in text_lower for w in ["anxious", "worried", "nervous", "scared", "panic"]):
                return {"primary_emotion": "anxious", "intensity": "medium", "sentiment": "negative", "emoji": "😰", "insight": "Feeling anxious or worried"}
            elif any(w in text_lower for w in ["angry", "furious", "hate", "frustrated", "mad"]):
                return {"primary_emotion": "angry", "intensity": "medium", "sentiment": "negative", "emoji": "😤", "insight": "Feeling frustrated or angry"}
            elif any(w in text_lower for w in ["stressed", "overwhelmed", "too much", "can't cope"]):
                return {"primary_emotion": "overwhelmed", "intensity": "high", "sentiment": "negative", "emoji": "😩", "insight": "Feeling overwhelmed by pressure"}
            elif any(w in text_lower for w in ["lonely", "alone", "isolated", "no one"]):
                return {"primary_emotion": "lonely", "intensity": "medium", "sentiment": "negative", "emoji": "😔", "insight": "Feeling isolated or alone"}
            elif any(w in text_lower for w in ["hope", "better", "improving", "trying"]):
                return {"primary_emotion": "hopeful", "intensity": "medium", "sentiment": "positive", "emoji": "🌱", "insight": "Showing signs of hope and resilience"}
            else:
                return {"primary_emotion": "neutral", "intensity": "low", "sentiment": "neutral", "emoji": "😐", "insight": "Sharing thoughts and feelings"}

    @staticmethod
    async def ai_predict_crisis_risk(conversation_history: list, llm_client) -> Dict[str, Any]:
        """
        Analyse conversation patterns to predict crisis risk BEFORE explicit keywords appear.
        Looks for: declining mood trajectory, hopelessness patterns, withdrawal signals,
        cognitive distortions, sleep/appetite mentions, social isolation indicators.
        Triggers every 3 user messages for efficiency.
        """
        user_messages = [m for m in conversation_history if m["role"] == "user"]
        if len(user_messages) < 3:
            return {"risk_level": "low", "risk_score": 0.0, "warning": None, "patterns": []}

        try:
            # Build conversation excerpt (last 6 user messages)
            recent = user_messages[-6:]
            convo_text = "\n".join([
                f"Message {i+1}: {m['content'][:300]}"
                for i, m in enumerate(recent)
            ])

            prompt = f"""You are a mental health risk assessment AI. Analyse these consecutive messages from a student for early warning signs of mental health deterioration.

Messages (in order):
{convo_text}

Look for these PATTERN indicators (not just keywords):
- Declining mood trajectory across messages (getting worse over time)
- Increasing hopelessness or helplessness language
- Social withdrawal or isolation references  
- Sleep disturbances or appetite changes mentioned
- Loss of interest in activities
- Cognitive distortions (all-or-nothing thinking, catastrophising)
- Expressions of being a burden to others
- Future-negative thinking patterns
- Increased self-criticism or worthlessness

Respond ONLY with this JSON (no extra text):
{{
  "risk_level": "low|moderate|high",
  "risk_score": 0.0,
  "patterns_detected": ["list of concerning patterns found, empty if none"],
  "trajectory": "improving|stable|declining",
  "warning_message": "null or a gentle 1-sentence supportive message to show the user if moderate/high risk",
  "recommendation": "none|suggest_resources|suggest_professional|immediate_support"
}}

Be conservative — only flag moderate/high if there are clear multi-message patterns, not single mentions."""

            messages = [{"role": "user", "content": prompt}]
            response_text, _ = await llm_client.generate_response(
                messages,
                system_prompt="You are a mental health risk assessment AI. Respond only with valid JSON.",
                temperature=0.1,
                max_tokens=300
            )

            import re as _re
            json_match = _re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                risk_data = json.loads(json_match.group())
                logger.info(f"Crisis predictor: {risk_data.get('risk_level')} ({risk_data.get('trajectory')})")
                return risk_data
            raise ValueError("No JSON in response")

        except Exception as e:
            logger.warning(f"Crisis prediction failed: {e}")
            return {"risk_level": "low", "risk_score": 0.0, "warning": None, "patterns": [], "trajectory": "stable", "recommendation": "none"}

    @staticmethod
    def detect_crisis_indicators(text: str) -> Tuple[float, List[str]]:
        """
        Detect crisis indicators in text
        Returns: (risk_score: 0-1, indicators: list)
        """
        text_lower = text.lower()
        indicators = []
        
        # Check for crisis keywords
        for keyword in EmotionalAnalyzer.CRISIS_KEYWORDS:
            if keyword in text_lower:
                indicators.append(keyword)
        
        # Calculate risk score
        if indicators:
            # Immediate escalation keywords
            immediate_keywords = ["suicide", "overdose", "gun", "rope", "bleeding"]
            if any(kw in text_lower for kw in immediate_keywords):
                risk_score = 0.95
            elif len(indicators) >= 3:
                risk_score = 0.8
            elif len(indicators) >= 1:
                risk_score = 0.6
            else:
                risk_score = 0.3
        else:
            risk_score = 0.0
        
        return min(1.0, risk_score), list(set(indicators))


class TherapistPrompt:
    """Generates system prompts for therapist behavior"""
    
    SYSTEM_PROMPT = """You are SafeSpace, an empathetic AI Mental Health Support Therapist. Your role is to:

1. **Listen actively**: Show genuine interest in the user's feelings and experiences
2. **Validate emotions**: Acknowledge their feelings without judgment
3. **Ask clarifying questions**: Help users explore their concerns deeper
4. **Provide coping strategies**: Suggest evidence-based techniques when appropriate
5. **Never diagnose**: You provide support, not medical diagnosis
6. **Recognize severity**: Identify crisis situations and escalate appropriately
7. **Encourage professional help**: Recommend counseling when serious concerns arise

## Communication Style
- Be warm, compassionate, and non-judgmental
- Use their preferred language and communication style
- Ask open-ended questions (avoid yes/no when possible)
- Summarize understanding to confirm accuracy
- Validate their experiences and emotions
- Offer practical, actionable advice when helpful

## Important Guidelines
- NEVER provide medical advice or diagnose conditions
- NEVER suggest harmful coping mechanisms
- ALWAYS prioritize user safety
- Escalate to crisis hotline for suicidal ideation
- Respect confidentiality and anonymity
- Do not collect personal information

## Crisis Response
If you detect signs of immediate crisis:
1. Express immediate concern
2. Encourage them to contact crisis services
3. Provide crisis hotline numbers
4. Ask if they're safe RIGHT NOW
5. Suggest emergency services if severe

Start each conversation by greeting the user warmly and understanding their current state."""
    
    @staticmethod
    def get_system_prompt() -> str:
        return TherapistPrompt.SYSTEM_PROMPT
    
    @staticmethod
    def get_context_prompt(user_history: List[Dict]) -> str:
        """Generate context-aware prompt from user history"""
        if not user_history:
            return ""
        
        context = "\n## Recent Conversation History:\n"
        for msg in user_history[-5:]:  # Last 5 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content'][:100]}...\n"
        
        return context


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Tuple[str, int]:  # (response, tokens_used)
        """Generate response from LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            logger.warning("OpenAI library not installed")
            self.client = None
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Tuple[str, int]:
        """Generate response using OpenAI GPT"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            # Prepare messages with system prompt
            all_messages = [
                {"role": "system", "content": system_prompt},
                *messages
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=all_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return content, tokens_used
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise


class GroqProvider(LLMProvider):
    """Groq API provider (faster inference)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=api_key)
        except ImportError:
            logger.warning("Groq library not installed")
            self.client = None
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Tuple[str, int]:
        """Generate response using Groq"""
        if not self.client:
            raise RuntimeError("Groq client not initialized")
        
        try:
            all_messages = [
                {"role": "system", "content": system_prompt},
                *messages
            ]
            
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=all_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return content, tokens_used
            
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise


class MedGemmaProvider(LLMProvider):
    """Google MedGemma provider for healthcare-specific responses"""
    
    def __init__(self, model_name: str = "medgemma-2b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        try:
            import requests
            self.requests = requests
        except ImportError:
            logger.warning("requests library not installed")
            self.requests = None
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Tuple[str, int]:
        """Generate response using MedGemma via Ollama"""
        if not self.requests:
            raise RuntimeError("requests not available")
        
        try:
            # Prepare prompt
            prompt = system_prompt + "\n\n"
            for msg in messages:
                role = msg["role"].upper()
                prompt += f"{role}: {msg['content']}\nASSISTANT: "
            
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json().get("response", "")
                tokens_used = len(content.split())  # Approximate
                return content, tokens_used
            else:
                raise Exception(f"MedGemma request failed: {response.status_code}")
            
        except Exception as e:
            logger.error(f"MedGemma error: {e}")
            raise


class AIMentalHealthAgent:
    """Main AI Agent for mental health support"""
    
    def __init__(self, llm_provider: LLMProvider, enable_crisis_detection: bool = True):
        self.llm = llm_provider
        self.enable_crisis_detection = enable_crisis_detection
        self.analyzer = EmotionalAnalyzer()
        self.conversation_history = []
        self.past_memory = ""  # Stores summaries of past sessions
    
    async def process_user_message(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """
        Process user message and generate response
        Returns comprehensive response with analysis
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow()
        })
        
        # Analyze emotional content (keyword-based fallback)
        sentiment, emotion_scores = self.analyzer.analyze_sentiment(user_message)
        
        # AI-powered emotion detection (runs in parallel with response)
        ai_emotion = await EmotionalAnalyzer.ai_detect_emotion(user_message, self.llm)
        
        # Detect crisis indicators
        crisis_score, crisis_indicators = self.analyzer.detect_crisis_indicators(user_message)
        
        # Prepare context with memory
        context_prompt = TherapistPrompt.get_context_prompt(self.conversation_history)
        memory_prompt = ""
        if self.past_memory:
            memory_prompt = f"""

## Student's Past Session Summaries (USE THIS TO PERSONALISE YOUR RESPONSE):
{self.past_memory}

Important: If this is the first message, warmly acknowledge what you remember from past sessions.
Reference specific concerns they mentioned before when relevant. This builds trust and continuity."""

        system_prompt = TherapistPrompt.get_system_prompt() + memory_prompt + context_prompt
        
        # AI Pattern-based crisis prediction (every 3 user messages)
        ai_crisis_prediction = {"risk_level": "low", "risk_score": 0.0, "warning_message": None, "patterns_detected": [], "trajectory": "stable", "recommendation": "none"}
        user_msg_count = len([m for m in self.conversation_history if m["role"] == "user"])
        if self.enable_crisis_detection and user_msg_count >= 3 and user_msg_count % 3 == 0:
            ai_crisis_prediction = await EmotionalAnalyzer.ai_predict_crisis_risk(
                self.conversation_history, self.llm
            )
            if ai_crisis_prediction.get("risk_level") == "high":
                logger.critical(f"AI CRISIS PREDICTOR: High risk pattern for user {user_id}: {ai_crisis_prediction.get('patterns_detected')}")

        # Check for crisis escalation (keyword + pattern combined)
        requires_escalation = False
        escalation_reason = None
        
        keyword_crisis = self.enable_crisis_detection and crisis_score >= 0.8
        pattern_crisis = ai_crisis_prediction.get("risk_level") == "high" and ai_crisis_prediction.get("risk_score", 0) >= 0.75

        if keyword_crisis or pattern_crisis:
            requires_escalation = True
            if keyword_crisis:
                escalation_reason = f"Crisis keyword detected: {', '.join(crisis_indicators)}"
            else:
                escalation_reason = f"Crisis pattern detected: {', '.join(ai_crisis_prediction.get('patterns_detected', []))}"
            logger.critical(f"Crisis escalation for user {user_id}: {escalation_reason}")
        
        # Generate AI response - strip timestamps before sending to LLM
        clean_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]
        try:
            response_text, tokens_used = await self.llm.generate_response(
                clean_history,
                system_prompt,
                temperature=0.7,
                max_tokens=1500
            )
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            response_text = "I'm experiencing a temporary issue. Please try again or contact support."
            tokens_used = 0
        
        # Prepare response
        result = {
            "response": response_text,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "tokens_used": tokens_used,
            "analysis": {
                "sentiment": ai_emotion.get("sentiment", sentiment),
                "emotions": emotion_scores,
                "crisis_score": crisis_score,
                "crisis_indicators": crisis_indicators,
                "ai_emotion": ai_emotion,
                "ai_crisis": ai_crisis_prediction,
            },
            "escalation": {
                "required": requires_escalation,
                "reason": escalation_reason,
                "crisis_resources": {
                    "national_hotline": "1-800-273-8255",
                    "text_crisis": "Text HOME to 741741",
                    "emergency": "911"
                } if requires_escalation else None
            }
        }
        
        return result
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation so far"""
        if not self.conversation_history:
            return {}
        
        total_exchanges = len([m for m in self.conversation_history if m["role"] == "user"])
        
        # Extract emotions over time
        emotions_over_time = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                _, emotions = self.analyzer.analyze_sentiment(msg["content"])
                emotions_over_time.append({
                    "timestamp": msg["timestamp"],
                    "emotions": emotions
                })
        
        return {
            "total_user_messages": total_exchanges,
            "conversation_length": len(self.conversation_history),
            "emotions_progression": emotions_over_time,
            "started_at": self.conversation_history[0]["timestamp"],
            "last_message_at": self.conversation_history[-1]["timestamp"]
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")


# Tool definitions for agent workflow
class ToolManager:
    """Manages tools available to AI Agent"""
    
    TOOLS = {
        "escalate_to_crisis": {
            "description": "Escalate to crisis response team",
            "requires": ["user_id", "reason"]
        },
        "recommend_resources": {
            "description": "Recommend mental health resources",
            "requires": ["category"]
        },
        "find_therapists": {
            "description": "Find nearby licensed therapists",
            "requires": ["location", "specialization"]
        },
        "schedule_followup": {
            "description": "Schedule follow-up screening",
            "requires": ["user_id", "days_until"]
        },
        "log_session": {
            "description": "Log session for records",
            "requires": ["user_id", "session_summary"]
        }
    }
    
    @staticmethod
    def validate_tool_call(tool_name: str, params: Dict) -> bool:
        """Validate tool call parameters"""
        if tool_name not in ToolManager.TOOLS:
            return False
        
        required = ToolManager.TOOLS[tool_name]["requires"]
        return all(param in params for param in required)


# Example usage
async def test_agent():
    """Test the AI agent"""
    # Using Groq provider
    provider = GroqProvider(api_key="test_key")
    agent = AIMentalHealthAgent(provider)
    
    # Simulate conversation
    test_messages = [
        "Hi, I've been feeling really overwhelmed lately",
        "Everything just feels too much right now"
    ]
    
    for msg in test_messages:
        try:
            result = await agent.process_user_message(msg, user_id="test_user")
            print(f"User: {msg}")
            print(f"AI: {result['response'][:100]}...")
            print(f"Crisis Score: {result['analysis']['crisis_score']}")
            print("---")
        except Exception as e:
            logger.error(f"Test error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())
