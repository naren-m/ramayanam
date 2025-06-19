"""
Chat service for AI-powered conversations about sacred texts.
Provides context-aware responses with text citations and references.
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import os

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from api.models.text_models import TextUnit
from api.services.text_service import get_text_service


class ChatIntent(Enum):
    """Types of chat interactions."""
    SEARCH = "search"
    ANALYZE = "analyze"
    COMPARE = "compare"
    EXPLAIN = "explain"
    DISCUSS = "discuss"
    GENERAL = "general"


class AIProvider(Enum):
    """Available AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"  # For testing without API keys


@dataclass
class TextReference:
    """Reference to a specific text unit in conversation."""
    text_id: str
    unit_id: str
    hierarchy_path: str
    excerpt: str
    relevance_score: float = 0.0


@dataclass
class ChatContext:
    """Context for a chat conversation."""
    active_text: Optional[str] = None
    discussion_topic: Optional[str] = None
    referenced_units: List[str] = None
    user_intent: ChatIntent = ChatIntent.GENERAL
    
    def __post_init__(self):
        if self.referenced_units is None:
            self.referenced_units = []


@dataclass
class ChatMessage:
    """A message in a chat conversation."""
    message_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    references: List[TextReference] = None
    context: Optional[ChatContext] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "message_id": self.message_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "references": [asdict(ref) for ref in self.references],
            "context": asdict(self.context) if self.context else None
        }


class ChatService:
    """Service for managing AI-powered chat conversations."""
    
    def __init__(self, provider: AIProvider = AIProvider.OPENAI):
        self.provider = provider
        self.text_service = get_text_service()
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI client based on provider
        self.client = None
        self._initialize_ai_client()
        
        # Conversation storage (in production, use database)
        self.conversations: Dict[str, List[ChatMessage]] = {}
        
        # System prompts for different contexts
        self.system_prompts = {
            "general": """You are a knowledgeable assistant specializing in ancient Indian sacred texts including the Ramayana, Mahabharata, Bhagavad Gita, and other Hindu scriptures. 

Your role is to:
1. Provide accurate information about these texts
2. Explain philosophical concepts and teachings
3. Help users understand the context and meaning of verses
4. Cite specific verses when relevant
5. Be respectful of the sacred nature of these texts
6. Acknowledge when you're unsure about something

Always maintain a scholarly but accessible tone. When referencing verses, use the format [Text:Hierarchy] (e.g., [Ramayana:1.2.3] for Kanda 1, Sarga 2, Sloka 3).""",
            
            "search": """You are helping a user search through sacred texts. When they ask about specific topics, characters, or concepts:

1. Suggest relevant search terms
2. Explain what they might find
3. Provide context about the topic
4. Reference specific verses if you know them
5. Guide them to the most relevant sections

Be helpful in refining their search and understanding what they're looking for.""",
            
            "analysis": """You are analyzing sacred text verses or passages. Your role is to:

1. Explain the literal meaning
2. Discuss deeper philosophical significance
3. Provide historical and cultural context
4. Compare with related verses or concepts
5. Explain symbolism and metaphors
6. Discuss different interpretations

Be thorough but clear in your analysis."""
        }
    
    def _initialize_ai_client(self):
        """Initialize the AI client based on the provider."""
        if self.provider == AIProvider.OPENAI and OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.logger.info("OpenAI client initialized")
            else:
                self.logger.warning("OpenAI API key not found, falling back to mock")
                self.provider = AIProvider.MOCK
        
        elif self.provider == AIProvider.ANTHROPIC and ANTHROPIC_AVAILABLE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.logger.info("Anthropic client initialized")
            else:
                self.logger.warning("Anthropic API key not found, falling back to mock")
                self.provider = AIProvider.MOCK
        
        else:
            self.provider = AIProvider.MOCK
            self.logger.info("Using mock AI provider")
    
    def create_conversation(self, conversation_id: str) -> None:
        """Create a new conversation."""
        self.conversations[conversation_id] = []
        self.logger.info(f"Created conversation {conversation_id}")
    
    def get_conversation(self, conversation_id: str) -> List[ChatMessage]:
        """Get conversation history."""
        return self.conversations.get(conversation_id, [])
    
    def add_message(self, conversation_id: str, message: ChatMessage) -> None:
        """Add a message to conversation."""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        
        self.conversations[conversation_id].append(message)
    
    def _detect_intent(self, message: str) -> ChatIntent:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['search', 'find', 'look for', 'show me']):
            return ChatIntent.SEARCH
        elif any(word in message_lower for word in ['analyze', 'explain', 'meaning', 'what does']):
            return ChatIntent.ANALYZE
        elif any(word in message_lower for word in ['compare', 'difference', 'similar', 'contrast']):
            return ChatIntent.COMPARE
        elif any(word in message_lower for word in ['discuss', 'tell me about', 'philosophy']):
            return ChatIntent.DISCUSS
        else:
            return ChatIntent.GENERAL
    
    def _find_relevant_verses(self, query: str, text_id: Optional[str] = None, limit: int = 3) -> List[TextReference]:
        """Find verses relevant to the query."""
        references = []
        
        try:
            if text_id:
                # Search in specific text
                units = self.text_service.search_text(text_id, query)
            else:
                # Search across all texts (just Ramayana for now)
                text_id = "ramayana"
                units = self.text_service.search_text(text_id, query)
            
            # Convert to references
            for unit in units[:limit]:
                reference = TextReference(
                    text_id=text_id,
                    unit_id=unit.id,
                    hierarchy_path=unit.get_hierarchy_path(),
                    excerpt=unit.get_primary_translation()[:200] + "..." if len(unit.get_primary_translation() or "") > 200 else unit.get_primary_translation() or "",
                    relevance_score=0.8  # Placeholder, would use proper scoring in production
                )
                references.append(reference)
        
        except Exception as e:
            self.logger.error(f"Error finding relevant verses: {e}")
        
        return references
    
    def _get_context_for_ai(self, conversation_id: str, user_message: str) -> Tuple[str, List[TextReference]]:
        """Get context and references for AI response."""
        # Get conversation history
        history = self.get_conversation(conversation_id)
        
        # Find relevant verses
        references = self._find_relevant_verses(user_message)
        
        # Build context string
        context_parts = []
        
        if references:
            context_parts.append("Relevant verses found:")
            for ref in references:
                context_parts.append(f"[{ref.text_id.title()}:{ref.hierarchy_path}] {ref.excerpt}")
        
        # Add conversation context
        if history:
            recent_messages = history[-3:]  # Last 3 messages for context
            context_parts.append("\nRecent conversation:")
            for msg in recent_messages:
                context_parts.append(f"{msg.role}: {msg.content[:100]}...")
        
        return "\n".join(context_parts), references
    
    def _generate_ai_response(self, user_message: str, context: str, intent: ChatIntent) -> str:
        """Generate AI response based on provider."""
        if self.provider == AIProvider.MOCK:
            return self._generate_mock_response(user_message, context, intent)
        
        # Choose system prompt based on intent
        system_prompt = self.system_prompts.get(intent.value, self.system_prompts["general"])
        
        if self.provider == AIProvider.OPENAI:
            return self._generate_openai_response(user_message, context, system_prompt)
        elif self.provider == AIProvider.ANTHROPIC:
            return self._generate_anthropic_response(user_message, context, system_prompt)
        
        return "I apologize, but I'm unable to generate a response at the moment."
    
    def _generate_openai_response(self, user_message: str, context: str, system_prompt: str) -> str:
        """Generate response using OpenAI."""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nUser Question: {user_message}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    def _generate_anthropic_response(self, user_message: str, context: str, system_prompt: str) -> str:
        """Generate response using Anthropic."""
        try:
            prompt = f"{system_prompt}\n\nContext:\n{context}\n\nUser Question: {user_message}\n\nResponse:"
            
            response = self.client.completions.create(
                model="claude-3-sonnet-20240229",
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.completion
        
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    def _generate_mock_response(self, user_message: str, context: str, intent: ChatIntent) -> str:
        """Generate a mock response for testing."""
        responses = {
            ChatIntent.SEARCH: f"I understand you're looking for information about '{user_message}'. Based on the available texts, I would suggest searching for related terms in the Ramayana or other scriptures.",
            
            ChatIntent.ANALYZE: f"To analyze '{user_message}', I would examine the text in its cultural and philosophical context. The meaning often operates on multiple levels - literal, metaphorical, and spiritual.",
            
            ChatIntent.COMPARE: f"When comparing different aspects of '{user_message}', it's important to consider the various traditions and interpretations found across different texts.",
            
            ChatIntent.DISCUSS: f"'{user_message}' is a fascinating topic in Hindu philosophy. The ancient texts offer profound insights that remain relevant today.",
            
            ChatIntent.GENERAL: f"Thank you for your question about '{user_message}'. I'm here to help you explore the wisdom of ancient sacred texts."
        }
        
        base_response = responses.get(intent, responses[ChatIntent.GENERAL])
        
        if context:
            base_response += f"\n\nBased on the relevant verses found, there are several passages that address this topic directly."
        
        return base_response
    
    def send_message(self, conversation_id: str, user_message: str, text_id: Optional[str] = None) -> ChatMessage:
        """Process user message and generate AI response."""
        try:
            # Create user message
            user_msg = ChatMessage(
                message_id=f"{conversation_id}_{len(self.get_conversation(conversation_id)) + 1}",
                role="user",
                content=user_message,
                timestamp=datetime.now()
            )
            
            # Add user message to conversation
            self.add_message(conversation_id, user_msg)
            
            # Detect intent
            intent = self._detect_intent(user_message)
            
            # Get context and references
            context, references = self._get_context_for_ai(conversation_id, user_message)
            
            # Generate AI response
            ai_content = self._generate_ai_response(user_message, context, intent)
            
            # Create AI message
            ai_context = ChatContext(
                active_text=text_id,
                user_intent=intent,
                referenced_units=[ref.unit_id for ref in references]
            )
            
            ai_msg = ChatMessage(
                message_id=f"{conversation_id}_{len(self.get_conversation(conversation_id)) + 1}",
                role="assistant",
                content=ai_content,
                timestamp=datetime.now(),
                references=references,
                context=ai_context
            )
            
            # Add AI message to conversation
            self.add_message(conversation_id, ai_msg)
            
            return ai_msg
        
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            
            # Return error message
            error_msg = ChatMessage(
                message_id=f"{conversation_id}_error",
                role="assistant",
                content="I apologize, but I encountered an error processing your message. Please try again.",
                timestamp=datetime.now()
            )
            
            self.add_message(conversation_id, error_msg)
            return error_msg
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary of a conversation."""
        messages = self.get_conversation(conversation_id)
        
        if not messages:
            return {"message_count": 0, "topics": [], "texts_discussed": []}
        
        # Count messages by role
        user_messages = [msg for msg in messages if msg.role == "user"]
        assistant_messages = [msg for msg in messages if msg.role == "assistant"]
        
        # Extract topics and texts
        topics = set()
        texts_discussed = set()
        
        for msg in assistant_messages:
            if msg.context:
                if msg.context.discussion_topic:
                    topics.add(msg.context.discussion_topic)
                if msg.context.active_text:
                    texts_discussed.add(msg.context.active_text)
        
        return {
            "message_count": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "topics": list(topics),
            "texts_discussed": list(texts_discussed),
            "start_time": messages[0].timestamp.isoformat() if messages else None,
            "last_activity": messages[-1].timestamp.isoformat() if messages else None
        }


# Global chat service instance
_chat_service = None


def get_chat_service(provider: AIProvider = AIProvider.OPENAI) -> ChatService:
    """Get the global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(provider)
    return _chat_service