from fuzzywuzzy import fuzz
# fuzzy_search_service.py
import logging
from difflib import SequenceMatcher
import re



class FuzzySearchService:
    def __init__(self, ramayanam_data):
        self.ramayanam_data = ramayanam_data
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def tokenize(self, text):
        # Splitting based on spaces, |, and ||
        tokens = re.split(r'\s+|\|\|?|\n', text)
        return [token for token in tokens if token]

    def similarity(self, a, b):
        # Using SequenceMatcher to get similarity ratio
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def search_and_highlight(self, text, query, threshold=0.7):
        tokens = self.tokenize(text)
        highlighted_tokens = []

        for i, token in enumerate(tokens):
            if query.lower() == token.lower():
                highlighted_tokens.append('<span class="highlight">' + token + '</span>')
            elif self.similarity(query, token) >= threshold:
                highlighted_tokens.append('<span class="highlight">' + token + '</span>')
            else:
                highlighted_tokens.append(token)

        # Joining tokens to recreate sentences/phrases for output
        highlighted_text = ' '.join(highlighted_tokens)
        return highlighted_text

    def search_translation_fuzzy(self, query):
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
                    highlighted_text = self.search_and_highlight(text, query)

                    # ratio = fuzz.ratio(text, query)
                    ratio = fuzz.partial_ratio(text, query)
                    self.logger.debug(f"Checking sloka {kanda_number}.{sarga_number}.{sloka_number} - Ratio: {ratio}")
                    if ratio > 70:  # Adjust the threshold as needed
                        results.append({"sloka_number": sloka.id, "sloka":sloka.text, "translation":highlighted_text, "meaning":sloka.meaning, "ratio": ratio})

        results.sort(key=lambda x: x["ratio"], reverse=True)

        return results


    def search_sloka_sanskrit_fuzzy(self, query, threshold=70):
        query = query.lower()  # Convert query to lowercase

        results = []
        for kanda_number, kanda in self.ramayanam_data.kandas.items():

            for sarga_number, sarga in kanda.sargas.items():
                if not sarga:
                    self.logger.error(f"Sarga '{sarga_number}' not found for Kanda '{kanda_number}'")
                    continue

                for sloka_number, sloka in sarga.slokas.items():
                    if sloka is None or sloka.text is None or sloka.meaning is None:
                        self.logger.debug("Kanda %s, Sarga %s, Sloka %s", kanda, sarga, sloka)
                        continue
                    text = sloka.text.lower()  # Convert sloka text to lowercase
                    highlighted_text = self.search_and_highlight(text, query)
                    highlighted_meaning = self.search_and_highlight(sloka.meaning.lower(), query)

                    ratio = fuzz.partial_ratio(text, query)
                    self.logger.debug(f"Checking sloka {kanda_number}.{sarga_number}.{sloka_number} - Ratio: {ratio}")
                    if ratio > threshold:  # Adjust the threshold as needed
                        results.append({"sloka_number": sloka.id, "sloka": highlighted_text, "translation": sloka.translation, "meaning": highlighted_meaning, "ratio": ratio})

        results.sort(key=lambda x: x["ratio"], reverse=True)
        return results