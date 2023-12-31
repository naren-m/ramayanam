import os

class SlokaReader:
    def __init__(self, base_path):
        self.base_path = base_path

    def read_sloka(self, kanda_name, sarga_number):
        sloka_path = os.path.join(self.base_path, kanda_name, f"{kanda_name}_sarga_{sarga_number}_sloka.txt")
        return self._read_file_contents(sloka_path)

    def read_meaning(self, kanda_name, sarga_number):
        meaning_path = os.path.join(self.base_path, kanda_name, f"{kanda_name}_sarga_{sarga_number}_meaning.txt")
        return self._read_file_contents(meaning_path)

    def read_translation(self, kanda_name, sarga_number):
        translation_path = os.path.join(self.base_path, kanda_name, f"{kanda_name}_sarga_{sarga_number}_translation.txt")
        return self._read_file_contents(translation_path)

    def _read_file_contents(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            return None
