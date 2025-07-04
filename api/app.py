from flask import Flask, send_file, send_from_directory
from flask_cors import CORS
from api.controllers.sloka_controller import sloka_blueprint
from api.config import Config
import logging
import tracemalloc
import os

tracemalloc.start()

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=Config.CORS_ORIGINS)

# Add this for testing
test_client = app.test_client

# Register blueprints
app.register_blueprint(sloka_blueprint, url_prefix='/api/ramayanam')

# Register chat blueprint
from api.controllers.chat_controller import chat_blueprint
app.register_blueprint(chat_blueprint, url_prefix='/api/chat')

# Register knowledge graph blueprint
from api.controllers.kg_controller import kg_blueprint
app.register_blueprint(kg_blueprint, url_prefix='/api/kg')

# Register entity discovery blueprint
from api.controllers.entity_discovery_controller import discovery_blueprint
app.register_blueprint(discovery_blueprint, url_prefix='/api/entity-discovery')

# Health check endpoint for testing - MUST be before catch-all route
@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration and testing."""
    return {'status': 'healthy', 'service': 'ramayanam-api'}, 200

# Serve React app - MUST be last (catch-all route)
@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path=''):
    """
    Serve the React application.
    In production, serves built files from dist/.
    In development, falls back to old frontend if dist/ doesn't exist.
    """
    # Don't serve frontend for API routes that don't exist - let Flask return 404
    if path and path.startswith('api/'):
        from flask import abort
        abort(404)
    
    # Check if we have the built React app
    dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist')
    if os.path.exists(dist_path):
        if path and os.path.exists(os.path.join(dist_path, path)):
            return send_from_directory(dist_path, path)
        return send_file(os.path.join(dist_path, 'index.html'))
    else:
        # In test environment, don't try to serve frontend files that don't exist
        if app.config.get('TESTING') or not os.path.exists('../slokas-frontend/index.html'):
            from flask import abort
            abort(404)
        # Fallback to old frontend for development
        logging.warning("dist/ not found, serving old frontend")
        return send_file('../slokas-frontend/index.html')
