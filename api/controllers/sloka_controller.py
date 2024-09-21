from flask import Blueprint, jsonify, request, Response
from api.models.sloka_model import Sloka
from api.services.fuzzy_search_service import FuzzySearchService
from api.services.sloka_reader import SlokaReader
import logging
from ramayanam import Ramayanam


sloka_blueprint = Blueprint("sloka", __name__)
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sloka_path = "/app/data/slokas/Slokas"
sloka_reader = SlokaReader(sloka_path)

# Load Ramayanam`` instance on app start
ramayanam_data = Ramayanam.load()
fuzzy_search_service = FuzzySearchService(ramayanam_data)

logging.info("Loaded Ramayanam data")


@sloka_blueprint.route("/kandas/<int:kanda_number>", methods=["GET"])
def get_kanda_name(kanda_number):
    logger.debug("Request %d", kanda_number)
    kanda_name = ramayanam_data.kandaDetails.get(kanda_number, {}).get("name")
    if kanda_name:
        return jsonify({"kanda_name": kanda_name})
    else:
        return jsonify({"error": "Invalid Kanda number"}), 404


@sloka_blueprint.route(
    "/kandas/<int:kanda_number>/sargas/<int:sarga_number>/slokas/<int:sloka_number>",
    methods=["GET"],
)
def get_slokas_by_kanda_sarga(kanda_number, sarga_number, sloka_number):
    try:
        # Use the ramayanam_instance to fetch slokas, meanings, and translations
        kanda = ramayanam_data.kandas[kanda_number]
        logger.debug("Processing for kanda %s, sarga %s", kanda_number, sarga_number)
        if not kanda:
            logger.error(
                "Unable to get %s kanda details from the corpus ", kanda_number
            )
            return jsonify({"error": f"Kanda '{kanda_number}' not found"}), 404

        sarga = kanda.sargas.get(sarga_number)
        if not sarga:
            return (
                jsonify(
                    {
                        "error": f"Sarga '{sarga_number}' not found for Kanda '{kanda_number}'"
                    }
                ),
                404,
            )

        logger.debug("sarga %s, sloka number %d", sarga, sloka_number)
        # Access sloka data using ramayanam_instance
        sloka = sarga.slokas[sloka_number]
        sloka_text = sarga.slokas[sloka_number].text
        meaning = sarga.slokas[
            sloka_number
        ].meaning  # Replace with your logic to get the meaning
        translation = sarga.slokas[
            sloka_number
        ].translation  # Replace with your logic to get the translation

        kanda_name = ramayanam_data.kandaDetails.get(kanda_number, {}).get("name")
        if not kanda_name:
            return jsonify({"error": "Invalid Kanda number"}), 404

        logger.debug("Kanda name %s", kanda_name)
        # Create a Sloka instance
        sloka = Sloka(
            sloka_id=f"{sloka.id}",
            sloka_text=sloka_text,
            meaning=meaning,
            translation=translation,
        )

        # Serialize the Sloka instance and return as JSON
        return jsonify(sloka.serialize())

    except (KeyError, IndexError) as e:
        # Log any exceptions
        logger.exception(
            "Error processing request for kanda %s, sarga %s: %s", kanda_name, sarga_number, str(e)
        )
        return jsonify({"error": "Internal Server Error"}), 500


@sloka_blueprint.route("/slokas/fuzzy-search", methods=["GET"])
def fuzzy_search_slokas():
    """
    Fuzzy search for slokas based on a query and an optional kanda.

    This function retrieves the search query and kanda from the request arguments.
    It performs a fuzzy search for translations of slokas. If the kanda is specified
    and is not zero, it searches within that specific kanda; otherwise, it searches
    across all kandas.

    Returns:
        JSON response containing the search results.
    """
    query = request.args.get("query", "")
    kanda = request.args.get("kanda", "")
    # search_translation_in_kanda_fuzzy
    logger.debug("Query: %s, Kanda: %s", query, kanda)
    kanda = int(kanda)
    if kanda == 0:
        results = fuzzy_search_service.search_translation_fuzzy(query)
    else:
        results = fuzzy_search_service.search_translation_in_kanda_fuzzy(kanda, query, 70)
    return jsonify(results)


@sloka_blueprint.route("/slokas/fuzzy-search-sanskrit", methods=["GET"])
def fuzzy_search_slokas_sanskrit():
    """
    Fuzzy search for slokas in Sanskrit based on a query and optional kanda.

    This function retrieves a search query and kanda from the request arguments,
    performs a fuzzy search for slokas in Sanskrit, and returns the results as JSON.

    Parameters:
        query (str): The search term to look for in the slokas.
        kanda (int): The specific kanda to limit the search to. If 0, searches all kandas.

    Returns:
        Response: A JSON response containing the search results.
    """
    query = request.args.get("query", "")
    kanda = request.args.get("kanda", "")
    # search_translation_in_kanda_fuzzy
    logger.debug("Query: %s, Kanda: %s", query, kanda)
    kanda = int(kanda)
    if kanda == 0:
        results = fuzzy_search_service.search_sloka_sanskrit_fuzzy(query)
    else:
        results = fuzzy_search_service.search_sloka_sanskrit_in_kanda_fuzzy(kanda, query, 70)
    return jsonify(results)


@sloka_blueprint.route("/slokas/fuzzy-search-stream", methods=["GET"])
def fuzzy_search_slokas_stream():
    query = request.args.get("query", "")

    def generate_results():
        # Perform fuzzy search on slokas
        for result in fuzzy_search_service.search_translation_fuzzy(query):
            yield jsonify(result) + "\n"

    return Response(generate_results(), content_type="application/json; charset=utf-8")
