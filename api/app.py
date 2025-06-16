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

# Register the sloka_blueprint
app.register_blueprint(sloka_blueprint, url_prefix='/api/ramayanam')

# Serve React app
@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path=''):
    """
    Serve the React application.
    In production, serves built files from dist/.
    In development, falls back to old frontend if dist/ doesn't exist.
    """
    # Check if we have the built React app
    dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist')
    if os.path.exists(dist_path):
        if path and os.path.exists(os.path.join(dist_path, path)):
            return send_from_directory(dist_path, path)
        return send_file(os.path.join(dist_path, 'index.html'))
    else:
        # Fallback to old frontend for development
        logging.warning("dist/ not found, serving old frontend")
        return send_file('../slokas-frontend/index.html')
