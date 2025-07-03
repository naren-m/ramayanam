"""
Entity Discovery API Controller

Separate controller for entity discovery endpoints to avoid route conflicts.
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
discovery_blueprint = Blueprint('entity_discovery', __name__)

# Initialize service
kg_service = KGDatabaseService()
logger = logging.getLogger(__name__)


@discovery_blueprint.route('/status', methods=['GET'])
def get_discovery_status():
    """Get current entity discovery status"""
    try:
        status = kg_service.get_discovery_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting discovery status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discovery_blueprint.route('/start', methods=['POST'])
def start_discovery():
    """Start entity discovery process"""
    try:
        config = request.json or {}
        # Build settings dictionary as expected by the service
        settings = {
            'confidence_threshold': config.get('confidence_threshold', 0.7),
            'max_entities_per_sloka': config.get('max_entities_per_sloka', 10),
            'process_all_kandas': config.get('processAllKandas', True)
        }
        session_id = kg_service.start_discovery_session(settings)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Entity discovery started'
        })
    except Exception as e:
        logger.error(f"Error starting discovery: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discovery_blueprint.route('/pending', methods=['GET'])
def get_pending_entities():
    """Get entities pending validation"""
    try:
        limit = int(request.args.get('limit', 100))
        entities = kg_service.get_pending_entities(limit=limit)
        
        return jsonify({
            'success': True,
            'entities': entities,
            'count': len(entities)
        })
    except Exception as e:
        logger.error(f"Error getting pending entities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discovery_blueprint.route('/validate', methods=['POST'])
def validate_entities():
    """Validate or reject entities"""
    try:
        data = request.json
        entity_ids = data.get('entity_ids', [])
        action = data.get('action')  # 'approve' or 'reject'
        corrections = data.get('corrections', {})
        
        if not entity_ids or not action:
            return jsonify({
                'success': False,
                'error': 'entity_ids and action are required'
            }), 400
        
        # If corrections are provided, apply them first
        if corrections and entity_ids:
            entity_id = entity_ids[0]  # For single entity editing
            kg_service.apply_entity_corrections(entity_id, corrections)
        
        result = kg_service.bulk_validate_entities(entity_ids, action, validated_by='api_user')
        
        return jsonify({
            'success': True,
            'processed': result['processed'],
            'message': f"{action.title()}d {result['processed']} entities"
        })
    except Exception as e:
        logger.error(f"Error validating entities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discovery_blueprint.route('/metrics', methods=['GET'])
def get_discovery_metrics():
    """Get entity discovery metrics"""
    try:
        metrics = kg_service.get_discovery_metrics()
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error getting discovery metrics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Error handlers
@discovery_blueprint.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Discovery endpoint not found'
    }), 404


@discovery_blueprint.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error in discovery service'
    }), 500