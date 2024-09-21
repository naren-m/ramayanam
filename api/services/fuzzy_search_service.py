from fuzzywuzzy import fuzz

# fuzzy_search_service.py
import logging
from difflib import SequenceMatcher
import re


class FuzzySearchService:
    """
    FuzzySearchService is a class that provides methods for performing fuzzy searches
    on the Ramayanam data, allowing for similarity matching of translations and slokas.

    Attributes:
        ramayanam_data (object): An object containing the Ramayanam data structured
        into Kandas, Sargas, and Slokas.
        logger (Logger): A logger instance for logging information and errors.

    Methods:
        __init__(ramayanam_data): Initializes the FuzzySearchService with the provided
        Ramayanam data and sets up the logger.

        tokenize(text): Splits the input text into tokens based on spaces, pipes,
        and newlines.

        similarity(a, b): Computes the similarity ratio between two strings using
        the SequenceMatcher.

        search_and_highlight(text, query, threshold=0.7): Searches for the query
        in the provided text and highlights matching tokens based on the similarity
        threshold.

        search_translation_fuzzy(query): Searches for translations across all Kandas
        using fuzzy matching and returns a list of results.

        search_translation_in_kanda_fuzzy(kanda_number, query, threshold=70):
        Searches for translations in a specific Kanda using fuzzy matching, returning
        a list of matching slokas with details.

        search_sloka_sanskrit_fuzzy(query, threshold=70): Searches for slokas in
        Sanskrit using fuzzy matching and returns a list of results.

        search_sloka_sanskrit_in_kanda_fuzzy(kanda_number, query, threshold=70):
        Searches for slokas in a specified Kanda using fuzzy matching, returning
        a list of matched slokas with details.
    """

    def __init__(self, ramayanam_data):
        self.ramayanam_data = ramayanam_data
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def tokenize(self, text):
        """
        Tokenizes the input text into a list of tokens.

        This method splits the input text based on spaces, single pipes ('|'), 
        double pipes ('||'), and newline characters. It returns a list of non-empty 
        tokens.

        Parameters:
            text (str): The input string to be tokenized.

        Returns:
            List[str]: A list of tokens extracted from the input text.
        """
        # Splitting based on spaces, |, and ||
        tokens = re.split(r"\s+|\|\|?|\n", text)
        return [token for token in tokens if token]

    def similarity(self, a, b):
        """
        Calculates the similarity ratio between two strings using the SequenceMatcher.

        Args:
            a (str): The first string to compare.
            b (str): The second string to compare.

        Returns:
            float: A float value representing the similarity ratio between the two strings,
                   ranging from 0.0 (no similarity) to 1.0 (identical strings).
        """
        # Using SequenceMatcher to get similarity ratio
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def search_and_highlight(self, text, query, threshold=0.7):
        """
        Searches for a query within a given text and highlights matching tokens.

        Parameters:
            text (str): The text in which to search for the query.
            query (str): The query string to search for in the text.
            threshold (float, optional): The similarity threshold for highlighting. 
                                          Defaults to 0.7.

        Returns:
            str: The text with matching tokens highlighted using HTML span elements.
        """
        tokens = self.tokenize(text)
        highlighted_tokens = []

        for _, token in enumerate(tokens):
            if query.lower() == token.lower():
                highlighted_tokens.append(
                    '<span class="highlight">' + token + "</span>"
                )
            elif self.similarity(query, token) >= threshold:
                highlighted_tokens.append(
                    '<span class="highlight">' + token + "</span>"
                )
            else:
                highlighted_tokens.append(token)

        # Joining tokens to recreate sentences/phrases for output
        highlighted_text = " ".join(highlighted_tokens)
        return highlighted_text

    def search_translation_fuzzy(self, query):
        """
        Search for fuzzy translations of a given query across all Kandas in the Ramayanam data.

        Parameters:
            query (str): The search term to find translations for. This will be converted to lowercase for case-insensitive matching.

        Returns:
            list: A list of results containing fuzzy matches for the provided query from all Kandas.
        """
        query = query.lower()  # Convert query to lowercase
        self.logger.info("Searching for query %s", query)
        results = []
        for kanda_number, kanda in self.ramayanam_data.kandas.items():
            self.logger.info("Kadna %s", kanda)
            r = self.search_translation_in_kanda_fuzzy(kanda_number, query, 70)
            results.extend(r)
        return results

    def search_translation_in_kanda_fuzzy(self, kanda_number, query, threshold=70):
        """
        Searches for translations in a specific Kanda of the Ramayanam using fuzzy matching.

        Parameters:
            kanda_number (int): The number of the Kanda to search within.
            query (str): The search query to match against the translations.
            threshold (int, optional): The minimum similarity ratio for a match to be considered valid. Defaults to 70.

        Returns:
            list: A list of dictionaries containing details of matching slokas, including:
                - sloka_number (int): The ID of the sloka.
                - sloka (str): The text of the sloka.
                - translation (str): The highlighted translation of the sloka.
                - meaning (str): The meaning of the sloka.
                - ratio (int): The similarity ratio of the translation to the query.
        """
        kanda = self.ramayanam_data.kandas.get(kanda_number)
        results = []
        if not kanda:
            self.logger.error("Kanda '%s' not found", kanda_number)
            return results
        for sarga_number, sarga in kanda.sargas.items():
            if not sarga:
                self.logger.error(
                    "Sarga '%s' not found for Kanda '%s'", sarga_number, kanda_number
                )
                continue

            for sloka_number, sloka in sarga.slokas.items():
                if sloka is None or sloka.translation is None:
                    self.logger.debug(
                        "Kanda %s, Sarga %s, Sloka %s", kanda, sarga, sloka
                    )
                    continue
                text = sloka.translation.lower()  # Convert sloka text to lowercase
                highlighted_text = self.search_and_highlight(text, query)

                ratio = fuzz.partial_ratio(text, query)
                self.logger.debug(
                    "Checking sloka %s.%s.%s - Ratio: %s",
                    kanda_number,
                    sarga_number,
                    sloka_number,
                    ratio,
                )
                if ratio > threshold:  # Adjust the threshold as needed
                    results.append(
                        {
                            "sloka_number": sloka.id,
                            "sloka": sloka.text,
                            "translation": highlighted_text,
                            "meaning": sloka.meaning,
                            "ratio": ratio,
                        }
                    )

        results.sort(key=lambda x: x["ratio"], reverse=True)
        return results

    def search_sloka_sanskrit_fuzzy(self, query, threshold=70):
        """
        Search for slokas in Sanskrit using a fuzzy matching algorithm.

        Parameters:
            query (str): The search query in Sanskrit to be matched.
            threshold (int, optional): The minimum similarity threshold for fuzzy matching. Defaults to 70.

        Returns:
            list: A list of slokas that match the query based on the fuzzy search criteria.

        Logs:
            - Logs the search query and each kanda being searched.
        """
        query = query.lower()  # Convert query to lowercase
        self.logger.info("Searching for query %s", query)
        results = []
        for kanda_number, kanda in self.ramayanam_data.kandas.items():
            self.logger.info("Kadna %s", kanda)
            r = self.search_sloka_sanskrit_in_kanda_fuzzy(
                kanda_number, query, threshold
            )
            results.extend(r)
        return results

    def search_sloka_sanskrit_in_kanda_fuzzy(self, kanda_number, query, threshold=70):
        """
        Search for slokas in a specified kanda using a fuzzy matching algorithm.

        Parameters:
            kanda_number (int): The number of the kanda to search within.
            query (str): The search term to match against sloka text and meaning.
            threshold (int, optional): The minimum similarity ratio (default is 70) for a match to be considered valid.

        Returns:
            list: A list of dictionaries containing the matched slokas, each with the following keys:
                - sloka_number (int): The ID of the sloka.
                - sloka (str): The text of the sloka with highlighted matches.
                - translation (str): The translation of the sloka.
                - meaning (str): The meaning of the sloka with highlighted matches.
                - ratio (int): The similarity ratio of the match.

        Logs:
            Errors if the specified kanda or sarga is not found.
            Debug information about the matching process and ratios.
        """
        results = []
        kanda = self.ramayanam_data.kandas.get(kanda_number)
        if not kanda:
            self.logger.error("Kanda '%s' not found", kanda_number)
            return results
        for sarga_number, sarga in kanda.sargas.items():
            if not sarga:
                self.logger.error(
                    "Sarga '%s' not found for Kanda '%s'", sarga_number, kanda_number
                )
                continue

            for sloka_number, sloka in sarga.slokas.items():
                if sloka is None or sloka.text is None or sloka.meaning is None:
                    self.logger.debug(
                        "Kanda %s, Sarga %s, Sloka %s", kanda, sarga, sloka
                    )
                    continue
                text = sloka.text.lower()  # Convert sloka text to lowercase
                highlighted_text = self.search_and_highlight(text, query)
                highlighted_meaning = self.search_and_highlight(
                    sloka.meaning.lower(), query
                )

                ratio = fuzz.partial_ratio(text, query)
                self.logger.debug(
                    "Checking sloka %s.%s.%s - Ratio: %s",
                    kanda_number,
                    sarga_number,
                    sloka_number,
                    ratio,
                )
                if ratio > threshold:  # Adjust the threshold as needed
                    results.append(
                        {
                            "sloka_number": sloka.id,
                            "sloka": highlighted_text,
                            "translation": sloka.translation,
                            "meaning": highlighted_meaning,
                            "ratio": ratio,
                        }
                    )

        results.sort(key=lambda x: x["ratio"], reverse=True)
        return results
