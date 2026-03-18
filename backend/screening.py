"""
SafeSpace Mental Health Screening Module
Implements structured assessment inspired by Travia platform
Analyzes mood, sleep, stress, and behavioral patterns
"""

import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ScreeningQuestions:
    """Comprehensive mental health screening questions"""
    
    QUESTIONS = {
        # MOOD ASSESSMENT
        "mood_1": {
            "category": "mood",
            "text": "During the past two weeks, how would you rate your overall mood?",
            "scale": "1-5",
            "weight": 1.0,
            "responses": {
                "1": "Very negative/depressed",
                "2": "Mostly negative",
                "3": "Neutral/Mixed",
                "4": "Mostly positive",
                "5": "Very positive/excellent"
            }
        },
        "mood_2": {
            "category": "mood",
            "text": "How often have you felt sad, empty, or hopeless?",
            "scale": "frequency",
            "weight": 1.2,
            "responses": {
                "1": "Almost every day",
                "2": "Several times a week",
                "3": "Several times a month",
                "4": "Rarely",
                "5": "Never"
            }
        },
        "mood_3": {
            "category": "mood",
            "text": "Have you lost interest in activities you normally enjoy?",
            "scale": "yes_no_partial",
            "weight": 1.1,
            "responses": {
                "1": "Yes, completely",
                "2": "Yes, partially",
                "3": "No change",
                "4": "Increased interest",
                "5": "Much more interested"
            }
        },
        "mood_4": {
            "category": "mood",
            "text": "How would you describe your confidence and self-worth?",
            "scale": "1-5",
            "weight": 1.0,
            "responses": {
                "1": "Very low/worthless",
                "2": "Below average",
                "3": "Average",
                "4": "Good",
                "5": "Excellent/Strong"
            }
        },
        
        # SLEEP ASSESSMENT
        "sleep_1": {
            "category": "sleep",
            "text": "How would you rate your sleep quality?",
            "scale": "1-5",
            "weight": 1.0,
            "responses": {
                "1": "Very poor",
                "2": "Poor",
                "3": "Fair",
                "4": "Good",
                "5": "Excellent"
            }
        },
        "sleep_2": {
            "category": "sleep",
            "text": "How many hours do you typically sleep per night?",
            "scale": "hours",
            "weight": 0.9,
            "responses": {
                "1": "< 4 hours (insomnia)",
                "2": "4-6 hours",
                "3": "6-8 hours (ideal)",
                "4": "> 8 hours",
                "5": "Varies, mostly good"
            }
        },
        "sleep_3": {
            "category": "sleep",
            "text": "How often do you have trouble falling or staying asleep?",
            "scale": "frequency",
            "weight": 1.0,
            "responses": {
                "1": "Almost every night",
                "2": "Several nights a week",
                "3": "Several nights a month",
                "4": "Rarely",
                "5": "Never"
            }
        },
        "sleep_4": {
            "category": "sleep",
            "text": "Do you feel rested after sleeping?",
            "scale": "1-5",
            "weight": 0.9,
            "responses": {
                "1": "Never - always exhausted",
                "2": "Rarely",
                "3": "Sometimes",
                "4": "Usually",
                "5": "Always - fully rested"
            }
        },
        
        # STRESS ASSESSMENT
        "stress_1": {
            "category": "stress",
            "text": "How would you rate your current stress level?",
            "scale": "1-5",
            "weight": 1.0,
            "responses": {
                "1": "Not at all stressed",
                "2": "Slightly stressed",
                "3": "Moderately stressed",
                "4": "Very stressed",
                "5": "Extremely stressed/Overwhelming"
            }
        },
        "stress_2": {
            "category": "stress",
            "text": "How often do you feel overwhelmed by daily responsibilities?",
            "scale": "frequency",
            "weight": 1.1,
            "responses": {
                "1": "Almost every day",
                "2": "Several times a week",
                "3": "Several times a month",
                "4": "Rarely",
                "5": "Never"
            }
        },
        "stress_3": {
            "category": "stress",
            "text": "Do you have effective ways to manage your stress?",
            "scale": "1-5",
            "weight": 1.0,
            "responses": {
                "1": "No coping strategies",
                "2": "Limited coping strategies",
                "3": "Some strategies",
                "4": "Good coping mechanisms",
                "5": "Excellent stress management"
            }
        },
        "stress_4": {
            "category": "stress",
            "text": "How much do your responsibilities affect your well-being?",
            "scale": "1-5",
            "weight": 0.9,
            "responses": {
                "1": "Severely affecting me",
                "2": "Significantly affecting me",
                "3": "Somewhat affecting me",
                "4": "Minimally affecting me",
                "5": "Not affecting me"
            }
        },
        
        # BEHAVIORAL PATTERNS
        "behavior_1": {
            "category": "behavior",
            "text": "How often do you engage in social activities?",
            "scale": "frequency",
            "weight": 0.9,
            "responses": {
                "1": "Very rarely/isolated",
                "2": "Rarely",
                "3": "Moderately",
                "4": "Often",
                "5": "Very frequently"
            }
        },
        "behavior_2": {
            "category": "behavior",
            "text": "Have you withdrawn from friends or family lately?",
            "scale": "yes_no_partial",
            "weight": 1.0,
            "responses": {
                "1": "Significantly withdrawn",
                "2": "Somewhat withdrawn",
                "3": "No change",
                "4": "More engaged",
                "5": "Much more social"
            }
        },
        "behavior_3": {
            "category": "behavior",
            "text": "How would you describe your eating and exercise habits?",
            "scale": "1-5",
            "weight": 0.8,
            "responses": {
                "1": "Very unhealthy (extreme changes)",
                "2": "Somewhat unhealthy",
                "3": "Neutral/Average",
                "4": "Good habits",
                "5": "Excellent habits"
            }
        },
        "behavior_4": {
            "category": "behavior",
            "text": "Have you used alcohol, drugs, or other substances to cope?",
            "scale": "frequency",
            "weight": 1.2,
            "responses": {
                "1": "Daily or almost daily",
                "2": "Several times a week",
                "3": "Occasionally",
                "4": "Rarely",
                "5": "Never"
            }
        },
    }

class ScreeningCalculator:
    """Calculates screening scores and risk assessments"""
    
    @staticmethod
    def calculate_category_score(responses: Dict[str, int], category: str) -> Tuple[float, List[str]]:
        """
        Calculate score for a specific category
        Returns: (score: 0-100, risk_indicators: list of concerning findings)
        """
        category_questions = {
            qid: q for qid, q in ScreeningQuestions.QUESTIONS.items()
            if q["category"] == category
        }
        
        if not category_questions:
            return 0.0, []
        
        total_weight = 0
        weighted_sum = 0
        risk_indicators = []
        
        for q_id, question in category_questions.items():
            if q_id in responses:
                response_value = responses[q_id]
                weight = question["weight"]
                
                # Invert score (1 is bad, 5 is good, we want low score for high risk)
                inverted_score = 6 - response_value
                
                weighted_sum += inverted_score * weight
                total_weight += weight
                
                # Identify concerning responses
                if response_value <= 2:
                    risk_indicators.append(f"{question['text'][:50]}...")
        
        # Normalize to 0-100 scale
        raw_score = (weighted_sum / total_weight) * 20 if total_weight > 0 else 0
        normalized_score = min(100, raw_score)
        
        return normalized_score, risk_indicators
    
    @staticmethod
    def calculate_overall_score(responses: Dict[str, int]) -> Tuple[float, Dict[str, float], str, List[str]]:
        """
        Calculate overall wellness score
        Returns: (overall_score, category_scores, risk_level, all_risk_indicators)
        """
        categories = ["mood", "sleep", "stress", "behavior"]
        category_weights = {
            "mood": 0.35,
            "sleep": 0.20,
            "stress": 0.35,
            "behavior": 0.10
        }
        
        category_scores = {}
        all_risk_indicators = []
        weighted_total = 0
        
        for category in categories:
            cat_score, risk_indicators = ScreeningCalculator.calculate_category_score(responses, category)
            category_scores[category] = cat_score
            all_risk_indicators.extend(risk_indicators)
            weighted_total += cat_score * category_weights[category]
        
        # Determine risk level
        if weighted_total >= 70:
            risk_level = RiskLevel.HIGH
        elif weighted_total >= 50:
            risk_level = RiskLevel.MODERATE
        else:
            risk_level = RiskLevel.LOW
        
        return weighted_total, category_scores, risk_level, all_risk_indicators

class ScreeningRecommendations:
    """Generate personalized recommendations based on screening results"""
    
    SELF_HELP_RESOURCES = {
        "mood": [
            {
                "title": "Understanding Depression",
                "url": "https://www.mind.org.uk/information-support/types-of-mental-health-problems/depression/",
                "type": "article"
            },
            {
                "title": "Mood Tracking Journal",
                "url": "https://www.daytona.edu/2023/09/19/mood-tracking/",
                "type": "tool"
            },
            {
                "title": "Cognitive Behavioral Techniques",
                "url": "https://www.verywellmind.com/cbt-basics-3024853",
                "type": "guide"
            }
        ],
        "sleep": [
            {
                "title": "Sleep Hygiene Guide",
                "url": "https://www.sleepfoundation.org/sleep-hygiene",
                "type": "guide"
            },
            {
                "title": "Relaxation Techniques for Sleep",
                "url": "https://www.healthline.com/health/sleep/relaxation-techniques-for-sleep",
                "type": "guide"
            },
            {
                "title": "Sleep Meditation App",
                "url": "https://www.headspace.com",
                "type": "app"
            }
        ],
        "stress": [
            {
                "title": "Stress Management Techniques",
                "url": "https://www.apa.org/science/about/psa/stress",
                "type": "guide"
            },
            {
                "title": "Breathing Exercises",
                "url": "https://www.calm.com/breathing",
                "type": "tool"
            },
            {
                "title": "Time Management Strategies",
                "url": "https://www.mindtools.com/pages/article/time-management.htm",
                "type": "guide"
            }
        ],
        "behavior": [
            {
                "title": "Building Social Connections",
                "url": "https://www.psychologytoday.com/us/basics/relationships",
                "type": "article"
            },
            {
                "title": "Exercise for Mental Health",
                "url": "https://www.mentalhealth.org.uk/our-work/research-and-campaigns/mental-health-exercise",
                "type": "guide"
            },
            {
                "title": "Healthy Lifestyle Habits",
                "url": "https://www.healthylifestyle.nsw.gov.au/",
                "type": "guide"
            }
        ]
    }
    
    PROFESSIONAL_SERVICES = {
        "low": False,
        "moderate": False,
        "high": True,
        "critical": True
    }
    
    @staticmethod
    def generate_recommendations(
        overall_score: float,
        category_scores: Dict[str, float],
        risk_level: str,
        risk_indicators: List[str]
    ) -> Dict:
        """Generate personalized wellness recommendations"""
        
        recommendations = {
            "overall_assessment": {
                "score": round(overall_score, 1),
                "risk_level": risk_level,
                "interpretation": ScreeningRecommendations._get_interpretation(overall_score)
            },
            "category_insights": {},
            "self_help_resources": {},
            "coping_strategies": [],
            "professional_support": ScreeningRecommendations.PROFESSIONAL_SERVICES.get(risk_level, True),
            "next_steps": ScreeningRecommendations._get_next_steps(risk_level),
            "crisis_resources": {
                "hotline_24_7": "1-800-273-8255 (National Suicide Prevention Lifeline)",
                "text_crisis": "Text HOME to 741741 (Crisis Text Line)",
                "chat_support": "https://suicidepreventionlifeline.org/chat/",
                "emergency": "911 or visit nearest emergency room"
            }
        }
        
        # Category-specific insights
        for category, score in category_scores.items():
            recommendations["category_insights"][category] = {
                "score": round(score, 1),
                "status": "needs attention" if score >= 60 else "manageable" if score >= 40 else "good",
                "resources": ScreeningRecommendations.SELF_HELP_RESOURCES.get(category, [])
            }
        
        # Coping strategies based on high-risk categories
        high_risk_categories = [cat for cat, score in category_scores.items() if score >= 60]
        recommendations["coping_strategies"] = ScreeningRecommendations._get_coping_strategies(high_risk_categories)
        
        return recommendations
    
    @staticmethod
    def _get_interpretation(score: float) -> str:
        """Get interpretation text based on score"""
        if score >= 70:
            return "Your wellness assessment indicates significant stress and mental health concerns. Professional support is strongly recommended."
        elif score >= 50:
            return "Your assessment shows moderate stress levels. Consider implementing coping strategies and self-care practices."
        else:
            return "Your wellness assessment indicates you're managing well. Continue with healthy practices and regular self-check-ins."
    
    @staticmethod
    def _get_next_steps(risk_level: str) -> List[str]:
        """Get actionable next steps based on risk level"""
        steps = {
            "low": [
                "Continue current wellness practices",
                "Schedule monthly wellness check-ins",
                "Explore the wellness activities in SafeSpace",
                "Practice stress management techniques"
            ],
            "moderate": [
                "Review and implement recommended coping strategies",
                "Consider scheduling counseling session",
                "Increase engagement with wellness activities",
                "Track mood and stress patterns weekly",
                "Reach out to trusted friends or family"
            ],
            "high": [
                "Schedule urgent counseling appointment",
                "Contact crisis hotline for immediate support",
                "Reach out to trusted person immediately",
                "Practice intensive self-care",
                "Consider professional mental health evaluation"
            ]
        }
        return steps.get(risk_level, [])
    
    @staticmethod
    def _get_coping_strategies(high_risk_categories: List[str]) -> List[Dict]:
        """Get evidence-based coping strategies for high-risk areas"""
        strategies = {
            "mood": [
                {"strategy": "Behavioral Activation", "description": "Engage in enjoyable activities daily"},
                {"strategy": "Thought Challenging", "description": "Question negative self-beliefs"},
                {"strategy": "Gratitude Practice", "description": "Write 3 things you're grateful for daily"}
            ],
            "sleep": [
                {"strategy": "Sleep Schedule", "description": "Maintain consistent sleep/wake times"},
                {"strategy": "Sleep Hygiene", "description": "Create optimal sleep environment"},
                {"strategy": "Relaxation Techniques", "description": "Practice deep breathing before sleep"}
            ],
            "stress": [
                {"strategy": "Progressive Muscle Relaxation", "description": "Tense and release muscle groups"},
                {"strategy": "Time Management", "description": "Prioritize and break tasks into smaller steps"},
                {"strategy": "Mindfulness Meditation", "description": "Practice 10-15 minutes daily"}
            ],
            "behavior": [
                {"strategy": "Social Connection", "description": "Reach out to friends or family"},
                {"strategy": "Physical Activity", "description": "Exercise for 30 minutes daily"},
                {"strategy": "Limit Substances", "description": "Reduce alcohol and other substance use"}
            ]
        }
        
        result = []
        for category in high_risk_categories:
            result.extend(strategies.get(category, []))
        
        return result[:5]  # Return top 5 strategies

class ScreeningSession:
    """Manages a screening session"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.started_at = datetime.utcnow()
        self.responses = {}
        self.current_question_index = 0
        
    def get_next_question(self) -> Optional[Tuple[str, Dict]]:
        """Get next question in screening"""
        questions_list = list(ScreeningQuestions.QUESTIONS.items())
        
        if self.current_question_index >= len(questions_list):
            return None
        
        q_id, question = questions_list[self.current_question_index]
        self.current_question_index += 1
        
        return q_id, question
    
    def record_response(self, question_id: str, response_value: int):
        """Record user's response to a question"""
        if 1 <= response_value <= 5:
            self.responses[question_id] = response_value
    
    def finalize_screening(self) -> Dict:
        """Calculate final screening results"""
        overall_score, cat_scores, risk_level, risk_indicators = \
            ScreeningCalculator.calculate_overall_score(self.responses)
        
        recommendations = ScreeningRecommendations.generate_recommendations(
            overall_score, cat_scores, risk_level, risk_indicators
        )
        
        duration_minutes = (datetime.utcnow() - self.started_at).total_seconds() / 60
        
        return {
            "user_id": self.user_id,
            "completed_at": datetime.utcnow(),
            "duration_minutes": round(duration_minutes, 1),
            "responses": self.responses,
            "overall_score": round(overall_score, 1),
            "category_scores": {k: round(v, 1) for k, v in cat_scores.items()},
            "risk_level": risk_level,
            "risk_indicators": risk_indicators[:5],
            "recommendations": recommendations
        }
