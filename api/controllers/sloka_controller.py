from flask import Blueprint, jsonify, request, Response
from api.models.sloka_model import Sloka
from api.services.fuzzy_search_service import FuzzySearchService
from api.services.sloka_reader import SlokaReader
from api.config import Config
from api.exceptions import (
    KandaNotFoundError, 
    SargaNotFoundError, 
    SlokaNotFoundError, 
    SearchError,
    RamayanamAPIException
)
import logging
from ramayanam import Ramayanam


sloka_blueprint = Blueprint("sloka", __name__)
logger = logging.getLogger(__name__)

# Initialize services
sloka_reader = SlokaReader(Config.SLOKAS_PATH)

# Load Ramayanam instance on app start
try:
    ramayanam_data = Ramayanam.load()
    fuzzy_search_service = FuzzySearchService(ramayanam_data)
    logger.info("Successfully loaded Ramayanam data")
except Exception as e:
    logger.error(f"Failed to load Ramayanam data: {e}")
    raise


@sloka_blueprint.route("/kandas/<int:kanda_number>", methods=["GET"])
def get_kanda_name(kanda_number):
    """Get the name of a specific Kanda."""
    try:
        logger.debug("Getting kanda name for kanda: %d", kanda_number)
        kanda_name = ramayanam_data.kandaDetails.get(kanda_number, {}).get("name")
        if not kanda_name:
            raise KandaNotFoundError(kanda_number)
        
        return jsonify({"kanda_name": kanda_name})
    
    except RamayanamAPIException as e:
        logger.warning(f"Kanda not found: {e.message}")
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error in get_kanda_name: {e}")
        return jsonify({"error": "Internal server error"}), 500


@sloka_blueprint.route(
    "/kandas/<int:kanda_number>/sargas/<int:sarga_number>/slokas/<int:sloka_number>",
    methods=["GET"],
)
def get_slokas_by_kanda_sarga(kanda_number, sarga_number, sloka_number):
    """Get a specific sloka by Kanda, Sarga, and Sloka number."""
    try:
        logger.debug(
            "Getting sloka for kanda: %d, sarga: %d, sloka: %d", 
            kanda_number, sarga_number, sloka_number
        )
        
        # Get kanda
        kanda = ramayanam_data.kandas.get(kanda_number)
        if not kanda:
            raise KandaNotFoundError(kanda_number)

        # Get sarga
        sarga = kanda.sargas.get(sarga_number)
        if not sarga:
            raise SargaNotFoundError(sarga_number, kanda_number)

        # Get sloka
        sloka_obj = sarga.slokas.get(sloka_number)
        if not sloka_obj:
            raise SlokaNotFoundError(sloka_number, sarga_number, kanda_number)

        # Create API response sloka
        response_sloka = Sloka(
            sloka_id=sloka_obj.id,
            sloka_text=sloka_obj.text,
            meaning=sloka_obj.meaning,
            translation=sloka_obj.translation,
        )

        return jsonify(response_sloka.serialize())

    except RamayanamAPIException as e:
        logger.warning(f"API error in get_slokas_by_kanda_sarga: {e.message}")
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error in get_slokas_by_kanda_sarga: {e}")
        return jsonify({"error": "Internal server error"}), 500


@sloka_blueprint.route("/slokas/fuzzy-search", methods=["GET"])
def fuzzy_search_slokas():
    """
    Fuzzy search for slokas based on English translation query.
    
    Query parameters:
        - query (str): Search query for English translations
        - kanda (int, optional): Specific kanda to search in (0 for all kandas)
        - threshold (int, optional): Minimum similarity threshold (default: 70)
    """
    try:
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        kanda = request.args.get("kanda", "0")
        threshold = int(request.args.get("threshold", Config.DEFAULT_FUZZY_THRESHOLD))
        
        try:
            kanda_num = int(kanda) if kanda else 0
        except ValueError:
            return jsonify({"error": "Invalid kanda parameter"}), 400
            
        logger.debug("Fuzzy search - Query: %s, Kanda: %s, Threshold: %d", query, kanda_num, threshold)
        
        if kanda_num == 0:
            results = fuzzy_search_service.search_translation_fuzzy(query)
        else:
            results = fuzzy_search_service.search_translation_in_kanda_fuzzy(kanda_num, query, threshold)
            
        # Limit results for performance
        limited_results = results[:Config.MAX_SEARCH_RESULTS]
        
        return jsonify(limited_results)
        
    except Exception as e:
        logger.error(f"Error in fuzzy_search_slokas: {e}")
        raise SearchError("Failed to perform translation search")


@sloka_blueprint.route("/slokas/fuzzy-search-sanskrit", methods=["GET"])
def fuzzy_search_slokas_sanskrit():
    """
    Fuzzy search for slokas in Sanskrit text and meaning.
    
    Query parameters:
        - query (str): Search query for Sanskrit text
        - kanda (int, optional): Specific kanda to search in (0 for all kandas)
        - threshold (int, optional): Minimum similarity threshold (default: 70)
    """
    try:
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        kanda = request.args.get("kanda", "0")
        threshold = int(request.args.get("threshold", Config.DEFAULT_FUZZY_THRESHOLD))
        
        try:
            kanda_num = int(kanda) if kanda else 0
        except ValueError:
            return jsonify({"error": "Invalid kanda parameter"}), 400
            
        logger.debug("Sanskrit fuzzy search - Query: %s, Kanda: %s, Threshold: %d", query, kanda_num, threshold)
        
        if kanda_num == 0:
            results = fuzzy_search_service.search_sloka_sanskrit_fuzzy(query, threshold)
        else:
            results = fuzzy_search_service.search_sloka_sanskrit_in_kanda_fuzzy(kanda_num, query, threshold)
            
        # Limit results for performance
        limited_results = results[:Config.MAX_SEARCH_RESULTS]
        
        return jsonify(limited_results)
        
    except Exception as e:
        logger.error(f"Error in fuzzy_search_slokas_sanskrit: {e}")
        raise SearchError("Failed to perform Sanskrit search")


@sloka_blueprint.route("/slokas/fuzzy-search-stream", methods=["GET"])
def fuzzy_search_slokas_stream():
    """Streaming fuzzy search for real-time results."""
    try:
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        def generate_results():
            try:
                for result in fuzzy_search_service.search_translation_fuzzy(query):
                    yield f"{jsonify(result).get_data(as_text=True)}\n"
            except Exception as e:
                logger.error(f"Error in streaming search: {e}")
                yield f'{jsonify({"error": "Search failed"}).get_data(as_text=True)}\n'

        return Response(generate_results(), content_type="application/json; charset=utf-8")
        
    except Exception as e:
        logger.error(f"Error in fuzzy_search_slokas_stream: {e}")
        return jsonify({"error": "Failed to initialize streaming search"}), 500


@sloka_blueprint.errorhandler(RamayanamAPIException)
def handle_api_exception(e):
    """Handle custom API exceptions."""
    return jsonify({"error": e.message}), e.status_code


@sloka_blueprint.errorhandler(Exception)
def handle_general_exception(e):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "Internal server error"}), 500
