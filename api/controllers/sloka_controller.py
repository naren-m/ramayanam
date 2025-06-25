from flask import Blueprint, jsonify, request, Response
from api.models.sloka_model import Sloka
from api.services.optimized_fuzzy_search_service import OptimizedFuzzySearchService
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
    fuzzy_search_service = OptimizedFuzzySearchService(ramayanam_data)
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


@sloka_blueprint.route("/kandas/<int:kanda_number>/sargas/<int:sarga_number>", methods=["GET"])
def get_sarga_slokas(kanda_number, sarga_number):
    """Get all slokas in a specific sarga."""
    try:
        logger.debug("Getting sarga for kanda: %d, sarga: %d", kanda_number, sarga_number)
        
        # Get kanda
        kanda = ramayanam_data.kandas.get(kanda_number)
        if not kanda:
            raise KandaNotFoundError(kanda_number)

        # Get sarga
        sarga = kanda.sargas.get(sarga_number)
        if not sarga:
            raise SargaNotFoundError(sarga_number, kanda_number)

        # Get all slokas in the sarga
        slokas = []
        for sloka_number, sloka_obj in sarga.slokas.items():
            response_sloka = Sloka(
                sloka_id=sloka_obj.id,
                sloka_text=sloka_obj.text,
                meaning=sloka_obj.meaning,
                translation=sloka_obj.translation,
            )
            slokas.append(response_sloka.serialize())

        # Get kanda and sarga metadata
        kanda_info = ramayanam_data.kandaDetails.get(kanda_number, {})
        
        response = {
            "kanda": {
                "number": kanda_number,
                "name": kanda_info.get("name", f"Kanda {kanda_number}")
            },
            "sarga": {
                "number": sarga_number,
                "total_slokas": len(slokas)
            },
            "slokas": slokas
        }

        return jsonify(response)

    except RamayanamAPIException as e:
        logger.warning(f"API error in get_sarga_slokas: {e.message}")
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error in get_sarga_slokas: {e}")
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
    Fuzzy search for slokas based on English translation query with pagination.
    
    Query parameters:
        - query (str): Search query for English translations
        - kanda (int, optional): Specific kanda to search in (0 for all kandas)
        - threshold (int, optional): Minimum similarity threshold (default: 70)
        - page (int, optional): Page number (1-based, default: 1)
        - page_size (int, optional): Number of results per page (default: 10, max: 50)
    """
    try:
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        kanda = request.args.get("kanda", "0")
        threshold = int(request.args.get("threshold", Config.DEFAULT_FUZZY_THRESHOLD))
        page = int(request.args.get("page", 1))
        page_size = min(int(request.args.get("page_size", Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE)
        
        try:
            kanda_num = int(kanda) if kanda else 0
        except ValueError:
            return jsonify({"error": "Invalid kanda parameter"}), 400
            
        if page < 1:
            return jsonify({"error": "Page number must be >= 1"}), 400
            
        logger.debug("Fuzzy search - Query: %s, Kanda: %s, Threshold: %d, Page: %d, Size: %d", 
                    query, kanda_num, threshold, page, page_size)
        
        # Get all results first - use optimized search with result limit
        max_total_results = page_size * 100  # Limit total results to avoid memory issues
        if kanda_num == 0:
            all_results = fuzzy_search_service.search_translation_fuzzy(query, max_total_results)
        else:
            all_results = fuzzy_search_service.search_translation_in_kanda_fuzzy(kanda_num, query, threshold)
            
        # Calculate pagination
        total_results = len(all_results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page results
        page_results = all_results[start_idx:end_idx]
        
        # Calculate pagination metadata
        total_pages = (total_results + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        response = {
            "results": page_results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_results": total_results,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in fuzzy_search_slokas: {e}")
        raise SearchError("Failed to perform translation search")


@sloka_blueprint.route("/slokas/fuzzy-search-sanskrit", methods=["GET"])
def fuzzy_search_slokas_sanskrit():
    """
    Fuzzy search for slokas in Sanskrit text and meaning with pagination.
    
    Query parameters:
        - query (str): Search query for Sanskrit text
        - kanda (int, optional): Specific kanda to search in (0 for all kandas)
        - threshold (int, optional): Minimum similarity threshold (default: 70)
        - page (int, optional): Page number (1-based, default: 1)
        - page_size (int, optional): Number of results per page (default: 10, max: 50)
    """
    try:
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        kanda = request.args.get("kanda", "0")
        threshold = int(request.args.get("threshold", Config.DEFAULT_FUZZY_THRESHOLD))
        page = int(request.args.get("page", 1))
        page_size = min(int(request.args.get("page_size", Config.DEFAULT_PAGE_SIZE)), Config.MAX_PAGE_SIZE)
        
        try:
            kanda_num = int(kanda) if kanda else 0
        except ValueError:
            return jsonify({"error": "Invalid kanda parameter"}), 400
            
        if page < 1:
            return jsonify({"error": "Page number must be >= 1"}), 400
            
        logger.debug("Sanskrit fuzzy search - Query: %s, Kanda: %s, Threshold: %d, Page: %d, Size: %d", 
                    query, kanda_num, threshold, page, page_size)
        
        # Get all results first - use optimized search with result limit
        max_total_results = page_size * 100  # Limit total results to avoid memory issues
        if kanda_num == 0:
            all_results = fuzzy_search_service.search_sloka_sanskrit_fuzzy(query, threshold, max_total_results)
        else:
            all_results = fuzzy_search_service.search_sloka_sanskrit_in_kanda_fuzzy(kanda_num, query, threshold)
            
        # Calculate pagination
        total_results = len(all_results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page results
        page_results = all_results[start_idx:end_idx]
        
        # Calculate pagination metadata
        total_pages = (total_results + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        response = {
            "results": page_results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_results": total_results,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in fuzzy_search_slokas_sanskrit: {e}")
        raise SearchError("Failed to perform Sanskrit search")


@sloka_blueprint.route("/slokas/fuzzy-search-stream", methods=["GET"])
def fuzzy_search_slokas_stream():
    """Enhanced streaming fuzzy search for progressive loading of results."""
    try:
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        kanda = request.args.get("kanda", "0")
        threshold = int(request.args.get("threshold", Config.DEFAULT_FUZZY_THRESHOLD))
        batch_size = int(request.args.get("batch_size", Config.STREAM_BATCH_SIZE))
        search_type = request.args.get("search_type", "translation")  # translation or sanskrit
        
        try:
            kanda_num = int(kanda) if kanda else 0
        except ValueError:
            return jsonify({"error": "Invalid kanda parameter"}), 400
            
        if search_type not in ["translation", "sanskrit"]:
            return jsonify({"error": "Invalid search_type. Must be 'translation' or 'sanskrit'"}), 400
            
        def generate_results():
            try:
                import json
                import time
                
                # Send initial metadata
                start_time = time.time()
                yield f'data: {json.dumps({"type": "start", "query": query, "search_type": search_type, "timestamp": start_time})}\n\n'
                
                # Use streaming search if kanda_num is 0 (all kandas)
                if kanda_num == 0 and hasattr(fuzzy_search_service, 'search_stream'):
                    batch_count = 0
                    total_results = 0
                    
                    # Use the new streaming search method
                    for batch_results in fuzzy_search_service.search_stream(query, search_type, threshold, batch_size):
                        if batch_results:
                            batch_count += 1
                            total_results += len(batch_results)
                            
                            batch_data = {
                                "type": "batch",
                                "results": batch_results,
                                "batch_number": batch_count,
                                "batch_size": len(batch_results),
                                "total_so_far": total_results,
                                "processing_time": time.time() - start_time
                            }
                            yield f'data: {json.dumps(batch_data)}\n\n'
                    
                    # Send completion with final stats
                    completion_data = {
                        "type": "complete",
                        "total_results": total_results,
                        "total_batches": batch_count,
                        "total_time": time.time() - start_time,
                        "cache_stats": fuzzy_search_service.get_cache_stats() if hasattr(fuzzy_search_service, 'get_cache_stats') else None
                    }
                    yield f'data: {json.dumps(completion_data)}\n\n'
                    
                else:
                    # Fallback to regular search for specific kandas
                    if search_type == "translation":
                        if kanda_num == 0:
                            all_results = fuzzy_search_service.search_translation_fuzzy(query)
                        else:
                            all_results = fuzzy_search_service.search_translation_in_kanda_fuzzy(kanda_num, query, threshold)
                    else:  # sanskrit
                        if kanda_num == 0:
                            all_results = fuzzy_search_service.search_sloka_sanskrit_fuzzy(query, threshold)
                        else:
                            all_results = fuzzy_search_service.search_sloka_sanskrit_in_kanda_fuzzy(kanda_num, query, threshold)
                    
                    # Send total count
                    total_count = len(all_results)
                    yield f'data: {json.dumps({"type": "total", "count": total_count})}\n\n'
                    
                    # Send results in batches
                    batch_count = 0
                    for i in range(0, len(all_results), batch_size):
                        batch = all_results[i:i + batch_size]
                        batch_count += 1
                        
                        batch_data = {
                            "type": "batch",
                            "results": batch,
                            "batch_number": batch_count,
                            "batch_size": len(batch),
                            "has_more": i + batch_size < len(all_results),
                            "progress": min(100, int((i + batch_size) / total_count * 100))
                        }
                        yield f'data: {json.dumps(batch_data)}\n\n'
                        
                        # Small delay to prevent overwhelming the client
                        time.sleep(0.01)
                    
                    # Send completion signal
                    completion_data = {
                        "type": "complete",
                        "total_results": total_count,
                        "total_batches": batch_count,
                        "total_time": time.time() - start_time
                    }
                    yield f'data: {json.dumps(completion_data)}\n\n'
                
            except Exception as e:
                import json
                logger.error(f"Error in streaming search: {e}")
                error_data = {
                    "type": "error", 
                    "message": "Search failed",
                    "error_details": str(e) if Config.DEBUG else None
                }
                yield f'data: {json.dumps(error_data)}\n\n'

        return Response(generate_results(), 
                       content_type="text/event-stream; charset=utf-8",
                       headers={
                           "Cache-Control": "no-cache",
                           "Connection": "keep-alive",
                           "Access-Control-Allow-Origin": "*",
                           "Access-Control-Allow-Headers": "Cache-Control"
                       })
        
    except Exception as e:
        logger.error(f"Error in fuzzy_search_slokas_stream: {e}")
        return jsonify({"error": "Failed to initialize streaming search"}), 500


@sloka_blueprint.route("/search/stats", methods=["GET"])
def get_search_stats():
    """Get search performance statistics."""
    try:
        if hasattr(fuzzy_search_service, 'get_cache_stats'):
            stats = fuzzy_search_service.get_cache_stats()
            return jsonify(stats)
        else:
            return jsonify({"message": "Statistics not available for this search service"})
    except Exception as e:
        logger.error(f"Error getting search stats: {e}")
        return jsonify({"error": "Failed to retrieve statistics"}), 500


@sloka_blueprint.errorhandler(RamayanamAPIException)
def handle_api_exception(e):
    """Handle custom API exceptions."""
    return jsonify({"error": e.message}), e.status_code


@sloka_blueprint.errorhandler(Exception)
def handle_general_exception(e):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "Internal server error"}), 500
