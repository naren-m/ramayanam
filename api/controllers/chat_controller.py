"""
Chat controller for handling AI-powered conversations about sacred texts.
Provides REST endpoints for chat functionality.
"""
from flask import Blueprint, request, jsonify, Response
import logging
import uuid
from datetime import datetime
from api.services.chat_service import get_chat_service, AIProvider
from api.exceptions import RamayanamAPIException


chat_blueprint = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)

# Initialize chat service
chat_service = get_chat_service()


@chat_blueprint.route("/conversations", methods=["POST"])
def create_conversation():
    """Create a new chat conversation."""
    try:
        data = request.get_json() or {}
        
        # Generate conversation ID
        conversation_id = data.get("conversation_id", str(uuid.uuid4()))
        
        # Initialize conversation
        chat_service.create_conversation(conversation_id)
        
        return jsonify({
            "conversation_id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return jsonify({"error": "Failed to create conversation"}), 500


@chat_blueprint.route("/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id: str):
    """Get conversation history."""
    try:
        messages = chat_service.get_conversation(conversation_id)
        
        return jsonify({
            "conversation_id": conversation_id,
            "messages": [msg.to_dict() for msg in messages],
            "message_count": len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        return jsonify({"error": "Failed to retrieve conversation"}), 500


@chat_blueprint.route("/conversations/<conversation_id>/messages", methods=["POST"])
def send_message(conversation_id: str):
    """Send a message and get AI response."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        text_id = data.get("text_id")  # Optional: specify which text to focus on
        
        # Process message and get response
        response_message = chat_service.send_message(
            conversation_id=conversation_id,
            user_message=user_message,
            text_id=text_id
        )
        
        return jsonify({
            "conversation_id": conversation_id,
            "response": response_message.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error processing message in conversation {conversation_id}: {e}")
        return jsonify({"error": "Failed to process message"}), 500


@chat_blueprint.route("/conversations/<conversation_id>/summary", methods=["GET"])
def get_conversation_summary(conversation_id: str):
    """Get conversation summary and statistics."""
    try:
        summary = chat_service.get_conversation_summary(conversation_id)
        
        return jsonify({
            "conversation_id": conversation_id,
            "summary": summary
        })
        
    except Exception as e:
        logger.error(f"Error getting summary for conversation {conversation_id}: {e}")
        return jsonify({"error": "Failed to get conversation summary"}), 500


@chat_blueprint.route("/ai/status", methods=["GET"])
def get_ai_status():
    """Get AI service status and capabilities."""
    try:
        provider = chat_service.provider
        client_available = chat_service.client is not None
        
        status = {
            "provider": provider.value,
            "available": client_available,
            "capabilities": {
                "text_analysis": True,
                "verse_search": True,
                "philosophical_discussion": True,
                "cross_text_comparison": False,  # Not yet implemented
                "multilingual": False  # Not yet implemented
            }
        }
        
        if provider == AIProvider.MOCK:
            status["note"] = "Running in mock mode for testing"
        elif not client_available:
            status["note"] = "API key not configured"
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        return jsonify({"error": "Failed to get AI status"}), 500


@chat_blueprint.route("/ai/providers", methods=["GET"])
def get_available_providers():
    """Get list of available AI providers."""
    try:
        providers = []
        
        # Check which providers are available
        try:
            import openai
            providers.append({
                "id": "openai",
                "name": "OpenAI GPT",
                "available": True,
                "models": ["gpt-3.5-turbo", "gpt-4"]
            })
        except ImportError:
            providers.append({
                "id": "openai",
                "name": "OpenAI GPT",
                "available": False,
                "reason": "Package not installed"
            })
        
        try:
            import anthropic
            providers.append({
                "id": "anthropic",
                "name": "Anthropic Claude",
                "available": True,
                "models": ["claude-3-sonnet", "claude-3-haiku"]
            })
        except ImportError:
            providers.append({
                "id": "anthropic",
                "name": "Anthropic Claude",
                "available": False,
                "reason": "Package not installed"
            })
        
        # Mock provider is always available
        providers.append({
            "id": "mock",
            "name": "Mock AI (Testing)",
            "available": True,
            "models": ["mock-v1"]
        })
        
        return jsonify({
            "providers": providers,
            "current": chat_service.provider.value
        })
        
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        return jsonify({"error": "Failed to get provider information"}), 500


@chat_blueprint.route("/suggestions", methods=["POST"])
def get_suggestions():
    """Get conversation suggestions based on context."""
    try:
        data = request.get_json() or {}
        text_id = data.get("text_id")
        topic = data.get("topic", "")
        
        # Generate contextual suggestions
        suggestions = []
        
        if text_id == "ramayana" or not text_id:
            suggestions.extend([
                "Tell me about Rama's exile",
                "What lessons does the Ramayana teach about dharma?",
                "Compare Rama and Ravana as characters",
                "Explain the significance of Hanuman's devotion",
                "What is the role of Sita in the story?"
            ])
        
        if topic.lower() in ["dharma", "duty", "righteousness"]:
            suggestions.extend([
                "How is dharma defined in ancient texts?",
                "What are the different types of dharma?",
                "How do characters struggle with dharmic choices?"
            ])
        
        # Default suggestions if no context
        if not suggestions:
            suggestions = [
                "What can I learn from the Ramayana?",
                "Explain a concept from Hindu philosophy",
                "Find verses about devotion",
                "Compare different characters' motivations",
                "What is the significance of specific events?"
            ]
        
        return jsonify({
            "suggestions": suggestions[:5],  # Limit to 5 suggestions
            "context": {
                "text_id": text_id,
                "topic": topic
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return jsonify({"error": "Failed to get suggestions"}), 500


@chat_blueprint.errorhandler(RamayanamAPIException)
def handle_api_exception(e):
    """Handle custom API exceptions."""
    return jsonify({"error": e.message}), e.status_code


@chat_blueprint.errorhandler(Exception)
def handle_general_exception(e):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception in chat controller: {e}")
    return jsonify({"error": "Internal server error"}), 500