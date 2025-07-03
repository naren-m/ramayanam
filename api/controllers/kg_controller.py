"""
Knowledge Graph API Controller

This controller provides REST API endpoints for querying the knowledge graph,
including entities, relationships, and text annotations.
"""

from flask import Blueprint, request, jsonify
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.services.kg_database_service import KGDatabaseService

# Create blueprint
kg_blueprint = Blueprint('kg', __name__)

# Initialize service
kg_service = KGDatabaseService()
logger = logging.getLogger(__name__)


@kg_blueprint.route('/entities', methods=['GET'])
def get_entities():
    """Get all entities with optional filtering"""
    try:
        entity_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        
        entities = kg_service.get_all_entities(entity_type=entity_type, limit=limit)
        
        return jsonify({
            'success': True,
            'entities': entities,
            'count': len(entities),
            'filters': {
                'type': entity_type,
                'limit': limit
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting entities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/entities/<path:entity_id>', methods=['GET'])
def get_entity(entity_id: str):
    """Get specific entity with relationships and mentions"""
    try:
        # Handle URL encoding - entity_id might be http://ramayanam.hanuma.com/entity/rama
        if not entity_id.startswith('http'):
            entity_id = f"http://ramayanam.hanuma.com/entity/{entity_id}"
        
        entity = kg_service.get_entity_by_id(entity_id)
        if not entity:
            return jsonify({
                'success': False,
                'error': 'Entity not found'
            }), 404
        
        # Get relationships and mentions
        relationships = kg_service.get_entity_relationships(entity_id)
        mentions = kg_service.get_entity_mentions(entity_id)
        
        return jsonify({
            'success': True,
            'entity': entity,
            'relationships': relationships,
            'mentions': mentions,
            'stats': {
                'relationship_count': len(relationships),
                'mention_count': len(mentions)
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting entity {entity_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/search', methods=['GET'])
def search_entities():
    """Search entities by name/label"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        entity_type = request.args.get('type')
        limit = int(request.args.get('limit', 20))
        
        entities = kg_service.search_entities(
            query=query,
            entity_type=entity_type,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'entities': entities,
            'count': len(entities)
        })
    
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/text-units/<text_unit_id>/entities', methods=['GET'])
def get_entities_in_text_unit(text_unit_id: str):
    """Get all entities mentioned in a specific text unit (sloka)"""
    try:
        entities = kg_service.get_entities_in_text_unit(text_unit_id)
        
        return jsonify({
            'success': True,
            'text_unit_id': text_unit_id,
            'entities': entities,
            'count': len(entities)
        })
    
    except Exception as e:
        logger.error(f"Error getting entities for text unit {text_unit_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/statistics', methods=['GET'])
def get_statistics():
    """Get knowledge graph statistics"""
    try:
        # Use enhanced statistics from the service
        enhanced_stats = kg_service.get_enhanced_statistics()
        
        return jsonify({
            'success': True,
            'statistics': enhanced_stats
        })
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/relationships/<entity_id>', methods=['GET'])
def get_entity_relationships_endpoint(entity_id: str):
    """Get relationships for a specific entity"""
    try:
        if not entity_id.startswith('http'):
            entity_id = f"http://ramayanam.hanuma.com/entity/{entity_id}"
        
        relationships = kg_service.get_entity_relationships(entity_id)
        
        return jsonify({
            'success': True,
            'entity_id': entity_id,
            'relationships': relationships,
            'count': len(relationships)
        })
    
    except Exception as e:
        logger.error(f"Error getting relationships for {entity_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/extract', methods=['POST'])
def run_extraction():
    """Trigger automated entity extraction (for admin use)"""
    try:
        # Import here to avoid circular imports
        from api.services.kg_database_service import run_automated_extraction_and_store
        
        # Get settings from request
        settings = request.json or {}
        confidence_threshold = settings.get('confidence_threshold', 0.7)
        max_entities_per_sloka = settings.get('max_entities_per_sloka', 10)
        
        # This might take a while, so we should ideally run it async
        # For now, keep it simple
        stats = run_automated_extraction_and_store()
        
        return jsonify({
            'success': True,
            'message': 'Extraction completed',
            'statistics': stats,
            'totalSlokas': 24000  # Approximate total for progress tracking
        })
    
    except Exception as e:
        logger.error(f"Error running extraction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/entities/pending', methods=['GET'])
def get_kg_pending_entities():
    """Get entities pending validation"""
    try:
        limit = int(request.args.get('limit', 100))
        pending_entities = kg_service.get_pending_entities(limit=limit)
        
        return jsonify({
            'success': True,
            'entities': pending_entities,
            'count': len(pending_entities)
        })
    
    except Exception as e:
        logger.error(f"Error getting pending entities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/entities/validate', methods=['POST'])
def validate_kg_entity():
    """Validate discovered entity"""
    try:
        entity_id = request.json.get('entity_id')
        validation = request.json.get('validation')
        
        if not entity_id or not validation:
            return jsonify({
                'success': False,
                'error': 'entity_id and validation are required'
            }), 400
        
        # Use the service to validate the entity
        kg_service.validate_entity(entity_id, validation, validated_by='api_user')
        
        return jsonify({
            'success': True,
            'message': f"Entity {entity_id} validated successfully"
        })
    
    except Exception as e:
        logger.error(f"Error validating entity: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/conflicts', methods=['GET'])
def get_entity_conflicts():
    """Get entity conflicts that need resolution"""
    try:
        limit = int(request.args.get('limit', 50))
        conflicts = kg_service.get_entity_conflicts(limit=limit)
        
        return jsonify({
            'success': True,
            'conflicts': conflicts,
            'count': len(conflicts)
        })
    
    except Exception as e:
        logger.error(f"Error getting conflicts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_blueprint.route('/conflicts/resolve', methods=['POST'])
def resolve_conflict():
    """Resolve entity conflict"""
    try:
        conflict_id = request.json.get('conflict_id')
        resolution = request.json.get('resolution')
        
        if not conflict_id or not resolution:
            return jsonify({
                'success': False,
                'error': 'conflict_id and resolution are required'
            }), 400
        
        # Use the service to resolve the conflict
        kg_service.resolve_entity_conflict(conflict_id, resolution, resolved_by='api_user')
        
        return jsonify({
            'success': True,
            'message': f"Conflict {conflict_id} resolved successfully"
        })
    
    except Exception as e:
        logger.error(f"Error resolving conflict: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Test endpoint
@kg_blueprint.route('/test', methods=['GET'])
def test_route():
    """Test route to verify KG endpoints are working"""
    return jsonify({'message': 'KG routes are loaded', 'success': True})


# Error handlers
@kg_blueprint.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@kg_blueprint.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500