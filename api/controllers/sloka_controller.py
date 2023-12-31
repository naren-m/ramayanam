from flask import Blueprint, jsonify, request
from api.models.sloka_model import Sloka
# from api.services.fuzzy_search_service import fuzzy_search_slokas
from api.services.sloka_reader import SlokaReader

sloka_blueprint = Blueprint('sloka', __name__)


# Assuming the SlokaReader is correctly implemented in sloka_reader.py
sloka_reader = SlokaReader('ramayanam_data/Slokas')

# Define Kanda enumeration
KANDA = {
    1: 'BalaKanda',
    2: 'AyodhyaKanda',
    3: 'AranyaKanda',
    4: 'SundaraKanda',
    5: 'YudhaKanda',
}

@sloka_blueprint.route('/kanda/<int:kanda_number>', methods=['GET'])
def get_kanda_name(kanda_number):
    kanda_name = KANDA.get(kanda_number)
    if kanda_name:
        return jsonify({'kanda_name': kanda_name})
    else:
        return jsonify({'error': 'Invalid Kanda number'}), 404

@sloka_blueprint.route('/kandas/<kanda_name>/sargas/<int:sarga_number>/slokas', methods=['GET'])
def get_slokas_by_kanda_sarga(kanda_name, sarga_number):
    # Use the sloka_reader to fetch slokas, meanings, and translations
    sloka_text = sloka_reader.read_sloka(kanda_name, sarga_number)
    meaning = sloka_reader.read_meaning(kanda_name, sarga_number)
    translation = sloka_reader.read_translation(kanda_name, sarga_number)

    # Create a Sloka instance
    sloka = Sloka(sloka_id=f'{kanda_name}_{sarga_number}', sloka_text=sloka_text, meaning=meaning, translation=translation)

    # Serialize the Sloka instance and return as JSON
    return jsonify(sloka.serialize())

@sloka_blueprint.route('/slokas/fuzzy-search', methods=['GET'])
def fuzzy_search():
    # Get the search query from the request parameters
    query = request.args.get('query')

    # Perform fuzzy search on slokas
    results = fuzzy_search_slokas(query, sample_slokas)  # Replace with actual search logic

    return jsonify(results)


# Add more endpoints as needed (e.g., get_sloka_by_id, add_sloka, etc.)
