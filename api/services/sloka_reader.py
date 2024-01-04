import os


class SlokaReader:

    def __init__(self, base_path):
        self.base_path = base_path
        self.corpus_path = base_path

    def read_sloka(self, kanda_name, sarga_number):
        sloka_path = os.path.join(
            self.base_path, kanda_name,
            f"{kanda_name}_sarga_{sarga_number}_sloka.txt")
        return self._read_file_contents(sloka_path)

    def read_meaning(self, kanda_name, sarga_number):
        meaning_path = os.path.join(
            self.base_path, kanda_name,
            f"{kanda_name}_sarga_{sarga_number}_meaning.txt")
        return self._read_file_contents(meaning_path)

    def read_translation(self, kanda_name, sarga_number):
        translation_path = os.path.join(
            self.base_path, kanda_name,
            f"{kanda_name}_sarga_{sarga_number}_translation.txt")
        return self._read_file_contents(translation_path)

    def _read_file_contents(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            return None

    def load_slokas_from_corpus(self):
        slokas_data = {}

        for kanda_name in os.listdir(self.corpus_path):
            kanda_path = os.path.join(self.corpus_path, kanda_name)

            if os.path.isdir(kanda_path):
                slokas_data[kanda_name] = {}

                for sarga_name in os.listdir(kanda_path):
                    sarga_path = os.path.join(kanda_path, sarga_name)

                    if os.path.isdir(sarga_path):
                        slokas_data[kanda_name][sarga_name] = {'slokas': {}}

                        sloka_files = os.listdir(sarga_path)

                        for sloka_file in sloka_files:
                            if sloka_file.endswith('_sloka.txt'):
                                sloka_number = sloka_file.split('_')[2]
                                sloka_id = f'{kanda_name}_{sarga_name}_{sloka_number}'

                                with open(os.path.join(sarga_path, sloka_file),
                                          'r',
                                          encoding='utf-8') as sloka_file:
                                    sloka_text = sloka_file.read().strip()

                                slokas_data[kanda_name][sarga_name]['slokas'][
                                    sloka_id] = sloka_text

        return slokas_data
