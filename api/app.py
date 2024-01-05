from flask import Flask, send_file
from api.controllers.sloka_controller import sloka_blueprint
import logging
import tracemalloc

tracemalloc.start()
# Configure logging
logging.basicConfig(level=logging.DEBUG)

# app = Flask(__name__)
app = Flask(__name__)


# Add this for testing
test_client = app.test_client

# Register the sloka_blueprint
app.register_blueprint(sloka_blueprint, url_prefix='/api/ramayanam')


@app.route('/')
def index():
    return send_file('../slokas-frontend/index.html')
