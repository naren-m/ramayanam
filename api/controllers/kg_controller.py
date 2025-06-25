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
        # Handle URL encoding - entity_id might be http://example.org/entity/rama
        if not entity_id.startswith('http'):
            entity_id = f"http://example.org/entity/{entity_id}"
        
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
        stats = kg_service.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
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
            entity_id = f"http://example.org/entity/{entity_id}"
        
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
        
        # This might take a while, so we should ideally run it async
        # For now, keep it simple
        stats = run_automated_extraction_and_store()
        
        return jsonify({
            'success': True,
            'message': 'Extraction completed',
            'statistics': stats
        })
    
    except Exception as e:
        logger.error(f"Error running extraction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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