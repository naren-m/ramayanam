"""
Text management service for loading and managing multiple sacred texts.
Provides a unified interface for working with different text structures.
"""
import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from api.models.text_models import (
    Text, TextUnit, TextCollection, Translation, TranslationStyle,
    UnitMetadata, LegacySloka
)
from api.config.text_configs import TextConfig, get_text_config, get_available_texts
from api.services.sloka_reader import SlokaReader
from ramayanam import Ramayanam  # For backward compatibility


class TextService:
    """Service for managing multiple sacred texts."""
    
    def __init__(self, base_data_path: str = "data"):
        self.base_data_path = base_data_path
        self.loaded_texts: Dict[str, Text] = {}
        self.legacy_ramayana: Optional[Ramayanam] = None
        self.logger = logging.getLogger(__name__)
    
    def get_available_texts(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all available texts."""
        return get_available_texts()
    
    def load_text(self, text_id: str, force_reload: bool = False) -> Text:
        """Load a specific text by ID."""
        if not force_reload and text_id in self.loaded_texts:
            return self.loaded_texts[text_id]
        
        config = get_text_config(text_id)
        
        if text_id == "ramayana":
            # Special handling for Ramayana with backward compatibility
            text = self._load_ramayana(config)
        else:
            # Generic loading for other texts
            text = self._load_generic_text(config)
        
        self.loaded_texts[text_id] = text
        self.logger.info(f"Loaded text '{text_id}' with {len(text.get_all_units())} units")
        return text
    
    def get_text(self, text_id: str) -> Optional[Text]:
        """Get a loaded text by ID."""
        return self.loaded_texts.get(text_id)
    
    def get_or_load_text(self, text_id: str) -> Text:
        """Get text if loaded, otherwise load it."""
        text = self.get_text(text_id)
        if text is None:
            text = self.load_text(text_id)
        return text
    
    def _load_ramayana(self, config: TextConfig) -> Text:
        """Load Ramayana with backward compatibility."""
        try:
            # Load using existing Ramayana loader for compatibility
            if self.legacy_ramayana is None:
                self.legacy_ramayana = Ramayanam.load()
            
            # Create new Text object
            text = Text(
                text_id=config.text_id,
                name=config.name,
                language=config.language,
                text_type=config.type,
                structure=config.structure,
                metadata=config.metadata
            )
            
            # Convert legacy data to new format
            for kanda_num, kanda in self.legacy_ramayana.kandas.items():
                # Create kanda collection
                kanda_collection = TextCollection(
                    level_name="kanda",
                    level_value=str(kanda_num)
                )
                text.add_root_collection(kanda_collection)
                
                for sarga_num, sarga in kanda.sargas.items():
                    # Create sarga collection
                    sarga_collection = TextCollection(
                        level_name="sarga",
                        level_value=str(sarga_num),
                        parent=kanda_collection
                    )
                    kanda_collection.add_child(sarga_collection)
                    
                    for sloka_num, sloka in sarga.slokas.items():
                        # Create text unit from legacy sloka
                        unit_id = f"{kanda_num}.{sarga_num}.{sloka_num}"
                        hierarchy = {
                            "kanda": str(kanda_num),
                            "sarga": str(sarga_num),
                            "sloka": str(sloka_num)
                        }
                        
                        unit = TextUnit(
                            unit_id=unit_id,
                            hierarchy=hierarchy,
                            original_text=sloka.text or "",
                            meaning=sloka.meaning
                        )
                        
                        # Add English translation
                        if sloka.translation:
                            translation = Translation(
                                language="en",
                                text=sloka.translation,
                                style=TranslationStyle.LITERAL
                            )
                            unit.add_translation(translation)
                        
                        # Add to collections and text
                        sarga_collection.add_unit(unit)
                        text.add_unit(unit)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Failed to load Ramayana: {e}")
            raise
    
    def _load_generic_text(self, config: TextConfig) -> Text:
        """Load a generic text from file system."""
        # This is a placeholder for future implementation
        # When we add other texts, we'll implement specific loaders
        
        text = Text(
            text_id=config.text_id,
            name=config.name,
            language=config.language,
            text_type=config.type,
            structure=config.structure,
            metadata=config.metadata
        )
        
        self.logger.info(f"Generic text loading not yet implemented for {config.text_id}")
        return text
    
    def search_text(self, text_id: str, query: str, language: str = "en") -> List[TextUnit]:
        """Search within a specific text."""
        text = self.get_or_load_text(text_id)
        return text.search_units(query, language)
    
    def search_all_texts(self, query: str, language: str = "en") -> Dict[str, List[TextUnit]]:
        """Search across all loaded texts."""
        results = {}
        for text_id, text in self.loaded_texts.items():
            text_results = text.search_units(query, language)
            if text_results:
                results[text_id] = text_results
        return results
    
    def get_text_unit(self, text_id: str, unit_id: str) -> Optional[TextUnit]:
        """Get a specific text unit."""
        text = self.get_text(text_id)
        if text:
            return text.get_unit(unit_id)
        return None
    
    def get_text_unit_by_hierarchy(self, text_id: str, **hierarchy) -> Optional[TextUnit]:
        """Get a text unit by hierarchy values."""
        text = self.get_text(text_id)
        if text:
            return text.get_unit_by_hierarchy(**hierarchy)
        return None
    
    def get_collection(self, text_id: str, *path: str) -> Optional[TextCollection]:
        """Get a collection within a text."""
        text = self.get_text(text_id)
        if text:
            return text.get_collection(*path)
        return None
    
    def get_text_structure(self, text_id: str) -> Optional[Dict[str, Any]]:
        """Get the structure information for a text."""
        text = self.get_text(text_id)
        if text:
            return text.get_structure_info()
        return None
    
    def get_legacy_ramayana(self) -> Optional[Ramayanam]:
        """Get the legacy Ramayana object for backward compatibility."""
        if self.legacy_ramayana is None:
            try:
                self.load_text("ramayana")
            except Exception as e:
                self.logger.error(f"Failed to load legacy Ramayana: {e}")
        return self.legacy_ramayana
    
    def validate_text_data(self, text_id: str) -> Tuple[bool, List[str]]:
        """Validate the data integrity of a text."""
        errors = []
        
        try:
            text = self.get_or_load_text(text_id)
            
            # Check if text has units
            if not text.get_all_units():
                errors.append("No text units found")
            
            # Check for units with missing data
            for unit in text.get_all_units():
                if not unit.original_text:
                    errors.append(f"Unit {unit.id} missing original text")
                
                if not unit.get_primary_translation():
                    errors.append(f"Unit {unit.id} missing primary translation")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Failed to load text: {e}")
            return False, errors
    
    def get_text_statistics(self, text_id: str) -> Dict[str, Any]:
        """Get statistics about a text."""
        text = self.get_or_load_text(text_id)
        
        all_units = text.get_all_units()
        
        # Count units by hierarchy level
        hierarchy_counts = {}
        for level in text.structure.hierarchy_levels:
            hierarchy_counts[level.name] = len(set(
                unit.hierarchy.get(level.name) 
                for unit in all_units 
                if level.name in unit.hierarchy
            ))
        
        # Count translations by language
        translation_counts = {}
        for unit in all_units:
            for translation in unit.translations:
                lang = translation.language
                translation_counts[lang] = translation_counts.get(lang, 0) + 1
        
        return {
            "total_units": len(all_units),
            "hierarchy_counts": hierarchy_counts,
            "translation_counts": translation_counts,
            "structure": text.get_structure_info()
        }


# Global text service instance
_text_service = None


def get_text_service(base_data_path: str = "data") -> TextService:
    """Get the global text service instance."""
    global _text_service
    if _text_service is None:
        _text_service = TextService(base_data_path)
    return _text_service