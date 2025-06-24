"""
Text configuration system for managing multiple sacred texts.
Defines the structure and metadata for each supported text.
"""
from typing import Dict, Any
from api.models.text_models import (
    TextType, TextStructure, TextMetadata, HierarchyLevel,
    create_ramayana_structure, create_bhagavad_gita_structure, create_mahabharata_structure
)


class TextConfig:
    """Configuration for a specific text."""
    
    def __init__(self,
                 text_id: str,
                 name: str,
                 language: str,
                 text_type: TextType,
                 structure: TextStructure,
                 metadata: TextMetadata,
                 data_path: str,
                 file_pattern: str):
        self.text_id = text_id
        self.name = name
        self.language = language
        self.type = text_type
        self.structure = structure
        self.metadata = metadata
        self.data_path = data_path
        self.file_pattern = file_pattern
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "id": self.text_id,
            "name": self.name,
            "language": self.language,
            "type": self.type.value,
            "data_path": self.data_path,
            "file_pattern": self.file_pattern,
            "structure": {
                "hierarchy_levels": [
                    {
                        "name": level.name,
                        "display_name": level.display_name,
                        "order": level.order,
                        "parent_level": level.parent_level
                    } for level in self.structure.hierarchy_levels
                ],
                "max_depth": self.structure.max_depth
            },
            "metadata": {
                "author": self.metadata.author,
                "estimated_date": self.metadata.estimated_date,
                "region": self.metadata.region,
                "tradition": self.metadata.tradition,
                "description": self.metadata.description,
                "total_units": self.metadata.total_units,
                "languages_available": self.metadata.languages_available
            }
        }


# Predefined text configurations
TEXT_CONFIGS: Dict[str, TextConfig] = {
    "ramayana": TextConfig(
        text_id="ramayana",
        name="Valmiki Ramayana",
        language="sanskrit",
        text_type=TextType.EPIC,
        structure=create_ramayana_structure(),
        metadata=TextMetadata(
            author="Maharshi Valmiki",
            estimated_date="5th-4th century BCE",
            region="Ancient India",
            tradition="Hindu",
            description="The first Sanskrit epic poem attributed to the sage Valmiki, telling the story of Rama's journey.",
            total_units=24000,  # Approximate number of slokas
            languages_available=["sanskrit", "en", "hi"]
        ),
        data_path="data/slokas/Slokas",
        file_pattern="{kanda}Kanda/{kanda}Kanda_sarga_{sarga}_{type}.txt"
    ),
    
    "bhagavad_gita": TextConfig(
        text_id="bhagavad_gita",
        name="Bhagavad Gita",
        language="sanskrit",
        text_type=TextType.PHILOSOPHICAL,
        structure=create_bhagavad_gita_structure(),
        metadata=TextMetadata(
            author="Attributed to Vyasa",
            estimated_date="5th-2nd century BCE",
            region="Ancient India",
            tradition="Hindu",
            description="A 700-verse dialogue between Prince Arjuna and Krishna, part of the Mahabharata.",
            total_units=700,
            languages_available=["sanskrit", "en", "hi"]
        ),
        data_path="data/bhagavad_gita",
        file_pattern="chapter_{chapter}/verse_{verse}_{type}.txt"
    ),
    
    "mahabharata": TextConfig(
        text_id="mahabharata",
        name="Mahabharata",
        language="sanskrit",
        text_type=TextType.EPIC,
        structure=create_mahabharata_structure(),
        metadata=TextMetadata(
            author="Attributed to Vyasa",
            estimated_date="8th-9th century BCE to 4th century CE",
            region="Ancient India",
            tradition="Hindu",
            description="The longest Sanskrit epic, containing over 100,000 verses including the Bhagavad Gita.",
            total_units=100000,
            languages_available=["sanskrit", "en", "hi"]
        ),
        data_path="data/mahabharata",
        file_pattern="{parva}_parva/{parva}_adhyaya_{adhyaya}_{type}.txt"
    )
}


def get_text_config(text_id: str) -> TextConfig:
    """Get configuration for a specific text."""
    if text_id not in TEXT_CONFIGS:
        raise ValueError(f"Text '{text_id}' not found. Available texts: {list(TEXT_CONFIGS.keys())}")
    return TEXT_CONFIGS[text_id]


def get_available_texts() -> Dict[str, Dict[str, Any]]:
    """Get list of all available texts with their metadata."""
    return {text_id: config.to_dict() for text_id, config in TEXT_CONFIGS.items()}


def add_text_config(config: TextConfig) -> None:
    """Add a new text configuration."""
    TEXT_CONFIGS[config.text_id] = config


def get_text_by_type(text_type: TextType) -> Dict[str, TextConfig]:
    """Get all texts of a specific type."""
    return {
        text_id: config 
        for text_id, config in TEXT_CONFIGS.items() 
        if config.type == text_type
    }


# Kanda details for backward compatibility with existing Ramayana code
RAMAYANA_KANDA_DETAILS = {
    1: {"id": 1, "name": "BalaKanda", "sargas": 77},
    2: {"id": 2, "name": "AyodhyaKanda", "sargas": 119},
    3: {"id": 3, "name": "AranyaKanda", "sargas": 75},
    4: {"id": 4, "name": "KishkindaKanda", "sargas": 67},
    5: {"id": 5, "name": "SundaraKanda", "sargas": 68},
    6: {"id": 6, "name": "YuddhaKanda", "sargas": 128}  # Added missing Yuddha Kanda
}


def get_ramayana_kanda_details() -> Dict[int, Dict[str, Any]]:
    """Get Ramayana Kanda details for backward compatibility."""
    return RAMAYANA_KANDA_DETAILS.copy()


# Example configurations for future texts
FUTURE_TEXT_CONFIGS = {
    "bhagavata_purana": {
        "name": "Bhagavata Purana",
        "type": TextType.PURANA,
        "hierarchy": ["skandha", "adhyaya", "sloka"],
        "total_books": 12,
        "description": "One of the eighteen Mahapuranas, focusing on devotion to Krishna."
    },
    
    "vishnu_purana": {
        "name": "Vishnu Purana",
        "type": TextType.PURANA,
        "hierarchy": ["amsha", "adhyaya", "sloka"],
        "total_books": 6,
        "description": "One of the eighteen Mahapuranas, dedicated to Vishnu."
    },
    
    "upanishads": {
        "name": "Principal Upanishads",
        "type": TextType.PHILOSOPHICAL,
        "hierarchy": ["upanishad", "section", "mantra"],
        "total_texts": 13,
        "description": "The principal Upanishads containing the philosophical essence of the Vedas."
    },
    
    "manusmriti": {
        "name": "Manusmriti",
        "type": TextType.DHARMA_SHASTRA,
        "hierarchy": ["adhyaya", "sloka"],
        "total_chapters": 12,
        "description": "Ancient legal text and dharma shastra."
    }
}