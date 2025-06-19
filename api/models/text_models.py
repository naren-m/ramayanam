"""
Generic text models for supporting multiple sacred texts.
Replaces the hardcoded Ramayana structure with flexible, configurable models.
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class TextType(Enum):
    """Types of supported sacred texts."""
    EPIC = "epic"              # Ramayana, Mahabharata
    PHILOSOPHICAL = "philosophical"  # Bhagavad Gita, Upanishads
    PURANA = "purana"         # Bhagavata, Vishnu, Shiva Puranas
    DHARMA_SHASTRA = "dharma_shastra"  # Manusmriti, etc.
    VEDIC = "vedic"           # Vedas and Vedic literature


class TranslationStyle(Enum):
    """Translation styles for different approaches."""
    LITERAL = "literal"
    POETIC = "poetic"
    INTERPRETIVE = "interpretive"
    SCHOLARLY = "scholarly"


@dataclass
class HierarchyLevel:
    """Defines a level in the text hierarchy (e.g., Kanda, Parva, Chapter)."""
    name: str               # "Kanda", "Parva", "Chapter", etc.
    display_name: str       # "Book", "Section", etc.
    order: int             # 0-based ordering in hierarchy
    parent_level: Optional[str] = None  # Parent level name if nested


@dataclass
class Translation:
    """A translation of a text unit in a specific language."""
    language: str
    text: str
    translator: Optional[str] = None
    style: TranslationStyle = TranslationStyle.LITERAL
    version: int = 1


@dataclass
class UnitMetadata:
    """Metadata for a text unit (verse, passage, etc.)."""
    themes: List[str] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    difficulty_level: Optional[str] = None
    historical_context: Optional[str] = None
    commentary_notes: List[str] = field(default_factory=list)


@dataclass
class TextStructure:
    """Defines the hierarchical structure of a text."""
    hierarchy_levels: List[HierarchyLevel]
    max_depth: int
    
    def get_level_by_name(self, name: str) -> Optional[HierarchyLevel]:
        """Get hierarchy level by name."""
        return next((level for level in self.hierarchy_levels if level.name == name), None)
    
    def get_level_by_order(self, order: int) -> Optional[HierarchyLevel]:
        """Get hierarchy level by order."""
        return next((level for level in self.hierarchy_levels if level.order == order), None)


@dataclass
class TextMetadata:
    """Metadata for an entire text."""
    author: Optional[str] = None
    estimated_date: Optional[str] = None
    region: Optional[str] = None
    tradition: Optional[str] = None
    description: str = ""
    total_units: int = 0
    languages_available: List[str] = field(default_factory=list)


class TextUnit:
    """
    Generic text unit (verse, passage, etc.) that can represent any hierarchical text structure.
    Replaces the specific Sloka class with a flexible alternative.
    """
    
    def __init__(self, 
                 unit_id: str,
                 hierarchy: Dict[str, str],  # e.g., {"kanda": "1", "sarga": "2", "sloka": "3"}
                 original_text: str,
                 transliteration: Optional[str] = None,
                 meaning: Optional[str] = None,
                 metadata: Optional[UnitMetadata] = None):
        self.id = unit_id
        self.hierarchy = hierarchy
        self.original_text = original_text
        self.transliteration = transliteration
        self.meaning = meaning
        self.metadata = metadata or UnitMetadata()
        self.translations: List[Translation] = []
    
    def add_translation(self, translation: Translation) -> None:
        """Add a translation for this unit."""
        self.translations.append(translation)
    
    def get_translation(self, language: str, style: Optional[TranslationStyle] = None) -> Optional[Translation]:
        """Get translation by language and optionally by style."""
        for trans in self.translations:
            if trans.language == language:
                if style is None or trans.style == style:
                    return trans
        return None
    
    def get_primary_translation(self, language: str = "en") -> Optional[str]:
        """Get the primary translation text for a language."""
        translation = self.get_translation(language)
        return translation.text if translation else None
    
    def get_hierarchy_path(self) -> str:
        """Get a dot-separated hierarchy path (e.g., '1.2.3')."""
        return ".".join(str(v) for v in self.hierarchy.values())
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize unit for API responses."""
        primary_translation = self.get_primary_translation()
        return {
            "unit_id": self.id,
            "hierarchy": self.hierarchy,
            "hierarchy_path": self.get_hierarchy_path(),
            "original_text": self.original_text,
            "transliteration": self.transliteration,
            "meaning": self.meaning,
            "translation": primary_translation,
            "translations": [
                {
                    "language": t.language,
                    "text": t.text,
                    "translator": t.translator,
                    "style": t.style.value
                } for t in self.translations
            ],
            "metadata": {
                "themes": self.metadata.themes,
                "characters": self.metadata.characters,
                "concepts": self.metadata.concepts
            }
        }


class TextCollection:
    """
    A collection of text units organized by hierarchy.
    Replaces the Kanda/Sarga structure with flexible organization.
    """
    
    def __init__(self, level_name: str, level_value: str, parent: Optional['TextCollection'] = None):
        self.level_name = level_name  # e.g., "kanda", "sarga"
        self.level_value = level_value  # e.g., "1", "2"
        self.parent = parent
        self.children: Dict[str, 'TextCollection'] = {}
        self.units: Dict[str, TextUnit] = {}
    
    def add_child(self, child: 'TextCollection') -> None:
        """Add a child collection."""
        self.children[child.level_value] = child
        child.parent = self
    
    def add_unit(self, unit: TextUnit) -> None:
        """Add a text unit to this collection."""
        self.units[unit.id] = unit
    
    def get_child(self, level_value: str) -> Optional['TextCollection']:
        """Get child collection by level value."""
        return self.children.get(level_value)
    
    def get_unit(self, unit_id: str) -> Optional[TextUnit]:
        """Get text unit by ID."""
        return self.units.get(unit_id)
    
    def get_all_units(self) -> List[TextUnit]:
        """Get all units from this collection and all child collections."""
        units = list(self.units.values())
        for child in self.children.values():
            units.extend(child.get_all_units())
        return units
    
    def get_path(self) -> List[str]:
        """Get the full hierarchy path to this collection."""
        path = []
        current = self
        while current:
            path.insert(0, f"{current.level_name}:{current.level_value}")
            current = current.parent
        return path


class Text:
    """
    Main text class representing an entire sacred text.
    Replaces the Ramayanam class with a generic implementation.
    """
    
    def __init__(self,
                 text_id: str,
                 name: str,
                 language: str,
                 text_type: TextType,
                 structure: TextStructure,
                 metadata: Optional[TextMetadata] = None):
        self.id = text_id
        self.name = name
        self.language = language
        self.type = text_type
        self.structure = structure
        self.metadata = metadata or TextMetadata()
        self.root_collections: Dict[str, TextCollection] = {}
        self.units_by_id: Dict[str, TextUnit] = {}
        self.logger = logging.getLogger(__name__)
    
    def add_root_collection(self, collection: TextCollection) -> None:
        """Add a root-level collection (e.g., Kanda, Parva)."""
        self.root_collections[collection.level_value] = collection
    
    def get_collection(self, *path: str) -> Optional[TextCollection]:
        """
        Get a collection by hierarchical path.
        Example: get_collection("1", "2") for Kanda 1, Sarga 2
        """
        if not path:
            return None
        
        current = self.root_collections.get(path[0])
        for level_value in path[1:]:
            if not current:
                return None
            current = current.get_child(level_value)
        
        return current
    
    def get_unit(self, unit_id: str) -> Optional[TextUnit]:
        """Get a text unit by ID."""
        return self.units_by_id.get(unit_id)
    
    def get_unit_by_hierarchy(self, **hierarchy) -> Optional[TextUnit]:
        """
        Get a unit by hierarchy values.
        Example: get_unit_by_hierarchy(kanda="1", sarga="2", sloka="3")
        """
        for unit in self.units_by_id.values():
            if all(unit.hierarchy.get(k) == str(v) for k, v in hierarchy.items()):
                return unit
        return None
    
    def add_unit(self, unit: TextUnit) -> None:
        """Add a text unit and index it."""
        self.units_by_id[unit.id] = unit
        
        # Add to appropriate collection
        hierarchy_values = list(unit.hierarchy.values())
        if hierarchy_values:
            collection = self.get_collection(*hierarchy_values[:-1])
            if collection:
                collection.add_unit(unit)
    
    def get_all_units(self) -> List[TextUnit]:
        """Get all text units."""
        return list(self.units_by_id.values())
    
    def search_units(self, query: str, language: str = "en") -> List[TextUnit]:
        """Basic text search across all units."""
        query_lower = query.lower()
        results = []
        
        for unit in self.units_by_id.values():
            # Search in original text
            if query_lower in unit.original_text.lower():
                results.append(unit)
                continue
            
            # Search in meaning
            if unit.meaning and query_lower in unit.meaning.lower():
                results.append(unit)
                continue
            
            # Search in translations
            translation = unit.get_primary_translation(language)
            if translation and query_lower in translation.lower():
                results.append(unit)
                continue
        
        return results
    
    def get_structure_info(self) -> Dict[str, Any]:
        """Get information about the text structure."""
        return {
            "hierarchy_levels": [
                {
                    "name": level.name,
                    "display_name": level.display_name,
                    "order": level.order
                } for level in self.structure.hierarchy_levels
            ],
            "max_depth": self.structure.max_depth,
            "total_units": len(self.units_by_id),
            "root_collections": list(self.root_collections.keys())
        }
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize text metadata for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "type": self.type.value,
            "structure": self.get_structure_info(),
            "metadata": {
                "author": self.metadata.author,
                "estimated_date": self.metadata.estimated_date,
                "description": self.metadata.description,
                "total_units": self.metadata.total_units,
                "languages_available": self.metadata.languages_available
            }
        }


# Backward compatibility classes for existing Ramayana data
class LegacySloka(TextUnit):
    """Backward compatibility wrapper for existing Sloka usage."""
    
    def __init__(self, sarga, number, text, meaning, translation):
        # Convert to new format
        unit_id = f"{sarga.kanda.id}.{sarga.id}.{number}"
        hierarchy = {
            "kanda": str(sarga.kanda.number),
            "sarga": str(sarga.number),
            "sloka": str(number)
        }
        
        super().__init__(
            unit_id=unit_id,
            hierarchy=hierarchy,
            original_text=text or "",
            meaning=meaning
        )
        
        # Add English translation
        if translation:
            english_translation = Translation(
                language="en",
                text=translation,
                style=TranslationStyle.LITERAL
            )
            self.add_translation(english_translation)
        
        # Legacy properties for backward compatibility
        self.number = number
        self.sarga = sarga
        self._text = text
        self._meaning = meaning
        self._translation = translation
    
    @property
    def text(self):
        return self._text
    
    @property
    def translation(self):
        return self._translation
    
    @property
    def kanda(self):
        return self.sarga.kanda


def create_ramayana_structure() -> TextStructure:
    """Create the standard Ramayana text structure."""
    hierarchy_levels = [
        HierarchyLevel(name="kanda", display_name="Book", order=0),
        HierarchyLevel(name="sarga", display_name="Canto", order=1, parent_level="kanda"),
        HierarchyLevel(name="sloka", display_name="Verse", order=2, parent_level="sarga")
    ]
    
    return TextStructure(hierarchy_levels=hierarchy_levels, max_depth=3)


def create_bhagavad_gita_structure() -> TextStructure:
    """Create the Bhagavad Gita text structure."""
    hierarchy_levels = [
        HierarchyLevel(name="chapter", display_name="Chapter", order=0),
        HierarchyLevel(name="verse", display_name="Verse", order=1, parent_level="chapter")
    ]
    
    return TextStructure(hierarchy_levels=hierarchy_levels, max_depth=2)


def create_mahabharata_structure() -> TextStructure:
    """Create the Mahabharata text structure."""
    hierarchy_levels = [
        HierarchyLevel(name="parva", display_name="Book", order=0),
        HierarchyLevel(name="adhyaya", display_name="Chapter", order=1, parent_level="parva"),
        HierarchyLevel(name="sloka", display_name="Verse", order=2, parent_level="adhyaya")
    ]
    
    return TextStructure(hierarchy_levels=hierarchy_levels, max_depth=3)