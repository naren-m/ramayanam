from flask import Blueprint, jsonify, request, Response
from api.models.sloka_model import Sloka
from api.services.fuzzy_search_service import FuzzySearchService
from api.services.sloka_reader import SlokaReader
import logging
from ramayanam import Ramayanam

# Load Ramayanam instance on app start
ramayanam_data = Ramayanam.load()

sloka_blueprint = Blueprint('sloka', __name__)
# Set up logging
logger = logging.getLogger(__name__)

sloka_reader = SlokaReader('/home/narenuday/Projects/ramayanam_data/slokas/Slokas')
fuzzy_search_service = FuzzySearchService(ramayanam_data)


@sloka_blueprint.route('/kanda/<int:kanda_number>', methods=['GET'])
def get_kanda_name(kanda_number):
    kanda_name = ramayanam_data.kandaDetails.get(kanda_number, {}).get('name')
    if kanda_name:
        return jsonify({'kanda_name': kanda_name})
    else:
        return jsonify({'error': 'Invalid Kanda number'}), 404

@sloka_blueprint.route('/kandas/<int:kanda_number>/sargas/<int:sarga_number>/slokas/<int:sloka_number>', methods=['GET'])
def get_slokas_by_kanda_sarga(kanda_number, sarga_number, sloka_number):
    try:
        # Use the ramayanam_instance to fetch slokas, meanings, and translations
        kanda = ramayanam_data.kandas[kanda_number]
        logger.debug("Processing for kanda %s, sarga %s", kanda_number, sarga_number)
        if not kanda:
            logger.error("Unable to get %s kanda details from the corpus ", kanda_number)
            return jsonify({"error": f"Kanda '{kanda_number}' not found"}), 404

        sarga = kanda.sargas.get(sarga_number)
        if not sarga:
            return jsonify({"error": f"Sarga '{sarga_number}' not found for Kanda '{kanda_number}'"}), 404

        logger.debug("sarga %s, sloka number %d", sarga, sloka_number)
        # Access sloka data using ramayanam_instance
        sloka_text = sarga.slokas[sloka_number].text
        meaning = sarga.slokas[sloka_number].meaning  # Replace with your logic to get the meaning
        translation = sarga.slokas[sloka_number].translation  # Replace with your logic to get the translation

        kanda_name = ramayanam_data.kandaDetails.get(kanda_number, {}).get('name')
        if not kanda_name:
            return jsonify({'error': 'Invalid Kanda number'}), 404

        logger.debug("Kanda name %s", kanda_name)
        # Create a Sloka instance
        sloka = Sloka(sloka_id=f'{kanda_name}_{sarga_number}', sloka_text=sloka_text, meaning=meaning, translation=translation)

        # Serialize the Sloka instance and return as JSON
        return jsonify(sloka.serialize())

    except Exception as e:
        # Log any exceptions
        logger.exception(f"Error processing request for kanda {kanda_name}, sarga {sarga_number}: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@sloka_blueprint.route('/slokas/fuzzy-search', methods=['GET'])
def fuzzy_search_slokas():
    query = request.args.get('query', '')

    # Retrieve slokas data from the app's context

    # Perform fuzzy search on slokas
    results = fuzzy_search_service.search_translation_fuzzy(query)

    return jsonify(results)

@sloka_blueprint.route('/slokas/fuzzy-search-sanskrit', methods=['GET'])
def fuzzy_search_slokas_sanskrit():
    query = request.args.get('query', '')
    results = fuzzy_search_service.search_sloka_sanskrit_fuzzy(query)
    return jsonify(results)

@sloka_blueprint.route('/slokas/fuzzy-search-stream', methods=['GET'])
def fuzzy_search_slokas_stream():
    query = request.args.get('query', '')

    def generate_results():
        # Perform fuzzy search on slokas
        for result in fuzzy_search_service.search_translation_fuzzy(query):
            yield jsonify(result) + '\n'

    return Response(generate_results(), content_type='application/json; charset=utf-8')
