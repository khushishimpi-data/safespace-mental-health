"""
SafeSpace Voice Service
Handles speech-to-text conversion with multilingual support
Supports Google Cloud Speech API and Azure Cognitive Services
"""

import base64
import asyncio
from typing import Optional, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class SupportedLanguage(str, Enum):
    """Supported languages for voice interaction"""
    ENGLISH = "en-US"
    HINDI = "hi-IN"
    TAMIL = "ta-IN"
    BENGALI = "bn-IN"
    TELUGU = "te-IN"
    KANNADA = "kn-IN"
    MALAYALAM = "ml-IN"

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "ta": "தமிழ் (Tamil)",
    "bn": "বাংলা (Bengali)",
    "te": "తెలుగు (Telugu)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ml": "മലയാളം (Malayalam)",
}

class VoiceProvider(ABC):
    """Abstract base class for voice service providers"""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: str) -> Tuple[str, float]:
        """
        Transcribe audio to text
        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en', 'hi')
        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        pass
    
    @abstractmethod
    async def synthesize(self, text: str, language: str) -> bytes:
        """
        Convert text to speech
        Args:
            text: Text to convert
            language: Language code
        Returns:
            Audio bytes
        """
        pass


class GoogleCloudVoiceProvider(VoiceProvider):
    """Google Cloud Speech-to-Text provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://speech.googleapis.com/v1/speech:recognize"
        try:
            from google.cloud import speech
            self.client = speech.SpeechClient()
        except ImportError:
            logger.warning("Google Cloud Speech library not installed")
            self.client = None
    
    async def transcribe(self, audio_data: bytes, language: str = "en") -> Tuple[str, float]:
        """Transcribe audio using Google Cloud Speech-to-Text"""
        if not self.client:
            raise RuntimeError("Google Cloud Speech client not initialized")
        
        try:
            from google.cloud.speech import RecognitionConfig, RecognitionAudio
            
            # Map language code to Google Cloud language
            lang_map = {
                "en": "en-US",
                "hi": "hi-IN",
                "ta": "ta-IN",
                "bn": "bn-IN",
                "te": "te-IN",
                "kn": "kn-IN",
                "ml": "ml-IN",
            }
            
            language_code = lang_map.get(language, "en-US")
            
            config = RecognitionConfig(
                encoding=RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
            )
            
            audio = RecognitionAudio(content=audio_data)
            
            response = self.client.recognize(config=config, audio=audio)
            
            if not response.results:
                return "", 0.0
            
            # Get best result
            result = response.results[0]
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence
                
                logger.info(f"Transcribed ({language}): {transcript[:50]}...")
                return transcript, float(confidence)
            
            return "", 0.0
            
        except Exception as e:
            logger.error(f"Google Cloud transcription error: {e}")
            raise
    
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """Synthesize speech from text using Google Cloud"""
        try:
            from google.cloud import texttospeech
            
            client = texttospeech.TextToSpeechClient()
            
            # Map language code to Google TTS language
            lang_map = {
                "en": "en-US",
                "hi": "hi-IN",
                "ta": "ta-IN",
                "bn": "bn-IN",
            }
            
            lang_code = lang_map.get(language, "en-US")
            
            input_text = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )
            
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Google Cloud synthesis error: {e}")
            raise


class AzureVoiceProvider(VoiceProvider):
    """Microsoft Azure Cognitive Services voice provider"""
    
    def __init__(self, api_key: str, region: str = "eastus"):
        self.api_key = api_key
        self.region = region
        self.base_url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
        
        try:
            import azure.cognitiveservices.speech as speechsdk
            self.speechsdk = speechsdk
            self.speech_config = speechsdk.SpeechConfig(
                subscription=api_key,
                region=region
            )
        except ImportError:
            logger.warning("Azure Speech SDK not installed")
            self.speechsdk = None
    
    async def transcribe(self, audio_data: bytes, language: str = "en") -> Tuple[str, float]:
        """Transcribe audio using Azure Speech Services"""
        if not self.speechsdk:
            raise RuntimeError("Azure Speech SDK not initialized")
        
        try:
            import io
            
            # Language code mapping for Azure
            lang_map = {
                "en": "en-US",
                "hi": "hi-IN",
                "ta": "ta-IN",
                "bn": "bn-IN",
            }
            
            lang_code = lang_map.get(language, "en-US")
            
            # Create speech recognizer with audio stream
            audio_stream = io.BytesIO(audio_data)
            audio_config = self.speechsdk.audio.AudioConfig(stream=audio_stream)
            
            speech_config = self.speechsdk.SpeechConfig(
                subscription=self.api_key,
                region=self.region
            )
            speech_config.speech_recognition_language = lang_code
            
            recognizer = self.speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            result = recognizer.recognize_once()
            
            if result.reason == self.speechsdk.ResultReason.RecognizedSpeech:
                transcript = result.text
                # Azure doesn't provide direct confidence, use proxy
                confidence = 0.85
                
                logger.info(f"Azure transcribed ({language}): {transcript[:50]}...")
                return transcript, confidence
            elif result.reason == self.speechsdk.ResultReason.NoMatch:
                logger.warning("No speech recognized")
                return "", 0.0
            elif result.reason == self.speechsdk.ResultReason.Canceled:
                logger.error(f"Speech recognition canceled: {result.cancellation_details.error_details}")
                return "", 0.0
            
        except Exception as e:
            logger.error(f"Azure transcription error: {e}")
            raise
    
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """Synthesize speech from text using Azure"""
        if not self.speechsdk:
            raise RuntimeError("Azure Speech SDK not initialized")
        
        try:
            lang_map = {
                "en": "en-US",
                "hi": "hi-IN",
                "ta": "ta-IN",
                "bn": "bn-IN",
            }
            
            lang_code = lang_map.get(language, "en-US")
            
            speech_config = self.speechsdk.SpeechConfig(
                subscription=self.api_key,
                region=self.region
            )
            
            # Use neural voice for better quality
            voice_name = {
                "en-US": "en-US-AriaNeural",
                "hi-IN": "hi-IN-SwaraNeural",
                "ta-IN": "ta-IN-JarvathanNeural",
                "bn-IN": "bn-IN-TanayaNeural",
            }.get(lang_code, "en-US-AriaNeural")
            
            speech_config.speech_synthesis_voice_name = voice_name
            
            output_audio = self.speechsdk.audio.AudioOutputConfig()
            synthesizer = self.speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=output_audio
            )
            
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                raise RuntimeError(f"Speech synthesis failed: {result}")
            
        except Exception as e:
            logger.error(f"Azure synthesis error: {e}")
            raise


class LocalVoiceProvider(VoiceProvider):
    """Local fallback voice provider using pyttsx3"""
    
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        except ImportError:
            logger.warning("pyttsx3 not installed - using mock provider")
            self.engine = None
    
    async def transcribe(self, audio_data: bytes, language: str = "en") -> Tuple[str, float]:
        """Local transcription (placeholder - requires actual speech recognition)"""
        logger.warning("Local transcription not supported - returning empty")
        return "", 0.0
    
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """Synthesize speech locally using pyttsx3"""
        if not self.engine:
            raise RuntimeError("pyttsx3 not available")
        
        try:
            import io
            import wave
            
            # This is a simplified mock - in production, use proper implementation
            logger.info(f"Local synthesis (mock): {text[:50]}...")
            return b"MOCK_AUDIO_DATA"
            
        except Exception as e:
            logger.error(f"Local synthesis error: {e}")
            raise


class VoiceService:
    """Main voice service orchestrator"""
    
    def __init__(self, provider_type: str = "google", **kwargs):
        """
        Initialize voice service
        Args:
            provider_type: 'google', 'azure', or 'local'
            **kwargs: Provider-specific configuration
        """
        self.provider_type = provider_type
        
        if provider_type == "google":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Google Cloud API key required")
            self.provider = GoogleCloudVoiceProvider(api_key)
        
        elif provider_type == "azure":
            api_key = kwargs.get("api_key")
            region = kwargs.get("region", "eastus")
            if not api_key:
                raise ValueError("Azure API key required")
            self.provider = AzureVoiceProvider(api_key, region)
        
        elif provider_type == "local":
            self.provider = LocalVoiceProvider()
        
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        logger.info(f"Voice service initialized with provider: {provider_type}")
    
    async def transcribe(self, audio_base64: str, language: str = "en") -> Tuple[str, float]:
        """
        Transcribe base64-encoded audio
        Args:
            audio_base64: Base64-encoded audio data
            language: Language code
        Returns:
            Tuple of (transcribed_text, confidence)
        """
        try:
            # Decode base64
            audio_bytes = base64.b64decode(audio_base64)
            
            # Transcribe
            text, confidence = await self.provider.transcribe(audio_bytes, language)
            
            return text, confidence
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def synthesize(self, text: str, language: str = "en") -> str:
        """
        Synthesize text to speech
        Args:
            text: Text to synthesize
            language: Language code
        Returns:
            Base64-encoded audio data
        """
        try:
            audio_bytes = await self.provider.synthesize(text, language)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            return audio_base64
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            raise
    
    @staticmethod
    def get_supported_languages() -> dict:
        """Get list of supported languages"""
        return LANGUAGE_NAMES
    
    @staticmethod
    def get_language_code(language_name: str) -> Optional[str]:
        """Get language code from language name"""
        reverse_map = {v: k for k, v in LANGUAGE_NAMES.items()}
        return reverse_map.get(language_name)


# Example usage
async def test_voice_service():
    """Test voice service"""
    try:
        # Using local provider for testing
        voice_service = VoiceService(provider_type="local")
        
        # Synthesize
        audio_base64 = await voice_service.synthesize(
            "Hello, how are you today?",
            language="en"
        )
        print(f"Synthesized audio length: {len(audio_base64)}")
        
        # Get languages
        langs = VoiceService.get_supported_languages()
        print(f"Supported languages: {langs}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_service())
