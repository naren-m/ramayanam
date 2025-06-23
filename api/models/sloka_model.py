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
    
    def __repr__(self):
        return f"Sloka(id={self.sloka_id}, text='{self.sloka_text[:50]}...')"
    
    def __eq__(self, other):
        if not isinstance(other, Sloka):
            return False
        return (self.sloka_id == other.sloka_id and 
                self.sloka_text == other.sloka_text and
                self.meaning == other.meaning and
                self.translation == other.translation)
    
    def __hash__(self):
        return hash((self.sloka_id, self.sloka_text, self.meaning, self.translation))
