import logging


class Sloka:
    def __init__(self, sloka_id, sloka_text, meaning, translation):
        self.sloka_id = sloka_id
        self.sloka_text = sloka_text
        self.meaning = meaning
        self.translation = translation

    def serialize(self):
        return {
            'sloka_id': self.sloka_id,
            'sloka_text': self.sloka_text,
            'meaning': self.meaning,
            'translation': self.translation
        }
