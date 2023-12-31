from flask import Flask
from api.controllers.sloka_controller import sloka_blueprint

app = Flask(__name__)

# Register the sloka_blueprint
app.register_blueprint(sloka_blueprint, url_prefix='/api/ramayanam')
