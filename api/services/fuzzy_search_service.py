from fuzzywuzzy import fuzz
# fuzzy_search_service.py
import logging

class FuzzySearchService:
    def __init__(self, ramayanam_data):
        self.ramayanam_data = ramayanam_data
        self.logger = logging.getLogger(__name__)

    def search_sloka_fuzzy(self, query):
        query = query.lower()  # Convert query to lowercase

        results = []
        for kanda_number, kanda in self.ramayanam_data.kandas.items():
            self.logger.debug("Kadna %s", kanda)
            for sarga_number, sarga in kanda.sargas.items():
                if not sarga:
                    self.logger.error(f"Sarga '{sarga_number}' not found for Kanda '{kanda_number}'")
                    continue

                for sloka_number, sloka in sarga.slokas.items():
                    if sloka is None or sloka.translation is None:
                        self.logger.debug("Kanda %s, Sarga %s, Sloka %s", kanda, sarga, sloka)
                        continue
                    text = sloka.translation.lower()  # Convert sloka text to lowercase
                    # ratio = fuzz.ratio(text, query)
                    ratio = fuzz.partial_ratio(text, query)
                    self.logger.debug(f"Checking sloka {kanda_number}.{sarga_number}.{sloka_number} - Ratio: {ratio}")
                    if ratio > 50:  # Adjust the threshold as needed
                        results.append({"sloka_number": sloka.id, "sloka":sloka.text, "translation":sloka.translation, "meaning":sloka.meaning, "ratio": ratio})

        results.sort(key=lambda x: x["ratio"], reverse=True)
        # self.logger.debug(f"Fuzzy search results: {results}")
        return results

