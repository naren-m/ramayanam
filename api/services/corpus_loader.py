# services/corpus_loader.py

import os

def load_slokas_from_corpus(corpus_path):
    slokas_data = {}

    for kanda_name in os.listdir(corpus_path):
        kanda_path = os.path.join(corpus_path, kanda_name)

        if os.path.isdir(kanda_path):
            slokas_data[kanda_name] = {}

            for sarga_name in os.listdir(kanda_path):
                sarga_path = os.path.join(kanda_path, sarga_name)

                if os.path.isdir(sarga_path):
                    slokas_data[kanda_name][sarga_name] = {
                        'slokas': {}
                    }

                    sloka_files = os.listdir(sarga_path)

                    for sloka_file in sloka_files:
                        if sloka_file.endswith('_sloka.txt'):
                            sloka_number = sloka_file.split('_')[2]
                            sloka_id = f'{kanda_name}_{sarga_name}_{sloka_number}'

                            with open(os.path.join(sarga_path, sloka_file), 'r', encoding='utf-8') as sloka_file:
                                sloka_text = sloka_file.read().strip()

                            slokas_data[kanda_name][sarga_name]['slokas'][sloka_id] = sloka_text

    return slokas_data
