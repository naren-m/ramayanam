"""
Automated Entity Extraction Pipeline for Ramayana Knowledge Graph

This module provides automated extraction of entities from the existing Ramayana text corpus
rather than manual creation. It processes Sanskrit slokas, English translations, and 
word-by-word meanings to identify characters, places, concepts, and relationships.
"""

import re
import os
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
from pathlib import Path

from api.models.kg_models import KGEntity, KGRelationship, EntityType, SemanticAnnotation
from api.models.text_models import TextUnit


@dataclass
class EntityPattern:
    """Pattern for identifying entities in text"""
    entity_id: str
    entity_type: EntityType
    sanskrit_patterns: List[str]
    english_patterns: List[str]
    epithets: List[str] = None
    confidence_boost: float = 1.0
    
    def __post_init__(self):
        if self.epithets is None:
            self.epithets = []


@dataclass
class ExtractionResult:
    """Result of entity extraction from a text unit"""
    entity_id: str
    entity_type: EntityType
    mentions: List[Tuple[int, int]]  # (start, end) positions
    confidence: float
    source_type: str  # 'sanskrit', 'translation', 'meaning'


class RamayanaEntityExtractor:
    """Automated entity extractor for Ramayana corpus"""
    
    def __init__(self, data_path: str = "data/slokas/Slokas"):
        self.data_path = data_path
        self.logger = logging.getLogger(__name__)
        
        # Define entity patterns based on text analysis
        self.entity_patterns = self._define_entity_patterns()
        
        # Statistics tracking
        self.extraction_stats = {
            'processed_slokas': 0,
            'entities_found': defaultdict(int),
            'confidence_scores': [],
            'patterns_matched': defaultdict(int)
        }
    
    def _define_entity_patterns(self) -> List[EntityPattern]:
        """Define patterns for major Ramayana entities"""
        patterns = [
            # Major Characters
            EntityPattern(
                entity_id="rama",
                entity_type=EntityType.PERSON,
                sanskrit_patterns=[
                    r'राम[ःोम्स्य]?', r'रामस्य', r'रामम्', r'रामेण', 
                    r'राघव[ःोम्स्य]?', r'राघवस्य', r'राघवम्',
                    r'दाशरथि[ःस्य]?', r'काकुत्स्थ[ःस्य]?'
                ],
                english_patterns=[
                    r'\bRama\b', r'\bRaama\b', r'\bRāma\b', r'\bRaghava\b', 
                    r'\bDasarathi\b', r'\bKakutstha\b'
                ],
                epithets=['राघव', 'दाशरथि', 'काकुत्स्थ'],
                confidence_boost=1.2
            ),
            
            EntityPattern(
                entity_id="sita",
                entity_type=EntityType.PERSON,
                sanskrit_patterns=[
                    r'सीता[म्ं]?', r'सीतायाः', r'सीतया', 
                    r'मैथिली[म्ं]?', r'वैदेही[म्ं]?', r'जानकी[म्ं]?'
                ],
                english_patterns=[
                    r'\bSita\b', r'\bSītā\b', r'\bMaithili\b', 
                    r'\bVaidehi\b', r'\bJanaki\b'
                ],
                epithets=['मैथिली', 'वैदेही', 'जानकी']
            ),
            
            EntityPattern(
                entity_id="hanuman",
                entity_type=EntityType.PERSON,
                sanskrit_patterns=[
                    r'हनुमा[न्त्]?', r'हनुमतः', r'हनुमते',
                    r'पवनात्मज[ःस्य]?', r'वायुपुत्र[ःस्य]?', r'मारुतिः?'
                ],
                english_patterns=[
                    r'\bHanuman\b', r'\bHanumat\b', r'\bMaruti\b',
                    r'\bson of the Windgod\b', r'\bson of Vayu\b'
                ],
                epithets=['पवनात्मज', 'वायुपुत्र', 'मारुति']
            ),
            
            EntityPattern(
                entity_id="ravana",
                entity_type=EntityType.PERSON,
                sanskrit_patterns=[
                    r'रावण[ःम्स्य]?', r'रावणेन', r'रावणस्य',
                    r'दशग्रीव[ःस्य]?', r'लङ्केश[ःस्य]?'
                ],
                english_patterns=[
                    r'\bRavana\b', r'\bRāvaṇa\b', r'\bDashagriva\b',
                    r'\bLankesa\b', r'\bten-headed\b'
                ],
                epithets=['दशग्रीव', 'लङ्केश']
            ),
            
            EntityPattern(
                entity_id="lakshmana",
                entity_type=EntityType.PERSON,
                sanskrit_patterns=[
                    r'लक्ष्मण[ःम्स्य]?', r'लक्ष्मणेन', r'लक्ष्मणस्य',
                    r'सौमित्रि[ःस्य]?'
                ],
                english_patterns=[
                    r'\bLakshmana\b', r'\bLakṣmaṇa\b', r'\bSaumitri\b'
                ],
                epithets=['सौमित्रि']
            ),
            
            # Places
            EntityPattern(
                entity_id="ayodhya",
                entity_type=EntityType.PLACE,
                sanskrit_patterns=[
                    r'अयोध्या[म्ं]?', r'अयोध्यायाम्', r'अयोध्यायाः'
                ],
                english_patterns=[
                    r'\bAyodhya\b', r'\bAyodhyā\b'
                ]
            ),
            
            EntityPattern(
                entity_id="lanka",
                entity_type=EntityType.PLACE,
                sanskrit_patterns=[
                    r'लङ्का[म्ं]?', r'लङ्कायाम्', r'लङ्कायाः'
                ],
                english_patterns=[
                    r'\bLanka\b', r'\bLaṅkā\b', r'\bCeylon\b'
                ]
            ),
            
            EntityPattern(
                entity_id="dandaka",
                entity_type=EntityType.PLACE,
                sanskrit_patterns=[
                    r'दण्डक[ःम्]?', r'दण्डकारण्य[म्]?'
                ],
                english_patterns=[
                    r'\bDandaka\b', r'\bDandaka forest\b'
                ]
            ),
            
            # Concepts
            EntityPattern(
                entity_id="dharma",
                entity_type=EntityType.CONCEPT,
                sanskrit_patterns=[
                    r'धर्म[ःम्स्य]?', r'धर्मेण', r'धर्मज्ञ[ःस्य]?'
                ],
                english_patterns=[
                    r'\bdharma\b', r'\bduty\b', r'\brighteous\b', r'\bvirtue\b'
                ]
            ),
            
            EntityPattern(
                entity_id="karma",
                entity_type=EntityType.CONCEPT,
                sanskrit_patterns=[
                    r'कर्म[न्ाः]?', r'कार्य[म्]?'
                ],
                english_patterns=[
                    r'\bkarma\b', r'\baction\b', r'\bdeeds\b'
                ]
            )
        ]
        
        return patterns
    
    def extract_entities_from_corpus(self) -> Dict[str, Any]:
        """Extract entities from the entire Ramayana corpus"""
        self.logger.info("Starting automated entity extraction from corpus")
        
        entities = {}
        relationships = []
        text_annotations = []
        
        # Process each kanda
        for kanda_path in self._get_kanda_directories():
            kanda_name = kanda_path.name
            self.logger.info(f"Processing {kanda_name}")
            
            kanda_results = self._process_kanda(kanda_path)
            
            # Merge results
            entities.update(kanda_results['entities'])
            relationships.extend(kanda_results['relationships'])
            text_annotations.extend(kanda_results['annotations'])
        
        # Post-process and validate
        validated_entities = self._validate_and_enhance_entities(entities)
        relationship_network = self._build_relationship_network(relationships)
        
        self._log_extraction_statistics()
        
        return {
            'entities': validated_entities,
            'relationships': relationship_network,
            'annotations': text_annotations,
            'statistics': self.extraction_stats
        }
    
    def _get_kanda_directories(self) -> List[Path]:
        """Get all kanda directories"""
        data_dir = Path(self.data_path)
        return [d for d in data_dir.iterdir() if d.is_dir()]
    
    def _process_kanda(self, kanda_path: Path) -> Dict[str, Any]:
        """Process all sargas in a kanda"""
        entities = {}
        relationships = []
        annotations = []
        
        # Get all sarga files
        sarga_files = self._group_sarga_files(kanda_path)
        
        for sarga_id, files in sarga_files.items():
            if len(files) == 3:  # Ensure we have sloka, translation, meaning
                sarga_results = self._process_sarga(kanda_path.name, sarga_id, files)
                
                # Merge sarga results
                entities.update(sarga_results['entities'])
                relationships.extend(sarga_results['relationships'])
                annotations.extend(sarga_results['annotations'])
        
        return {
            'entities': entities,
            'relationships': relationships,
            'annotations': annotations
        }
    
    def _group_sarga_files(self, kanda_path: Path) -> Dict[str, Dict[str, Path]]:
        """Group sarga files by sarga number"""
        sarga_files = defaultdict(dict)
        
        for file_path in kanda_path.glob("*.txt"):
            # Parse filename: KandaName_sarga_N_type.txt
            parts = file_path.stem.split('_')
            if len(parts) >= 4:
                sarga_num = parts[2]
                file_type = parts[3]
                sarga_files[sarga_num][file_type] = file_path
        
        return dict(sarga_files)
    
    def _process_sarga(self, kanda_name: str, sarga_id: str, files: Dict[str, Path]) -> Dict[str, Any]:
        """Process a single sarga (chapter)"""
        entities = {}
        relationships = []
        annotations = []
        
        # Read all three file types
        sanskrit_text = self._read_file_content(files.get('sloka'))
        translation_text = self._read_file_content(files.get('translation'))
        meaning_text = self._read_file_content(files.get('meaning'))
        
        if not sanskrit_text:
            return {'entities': {}, 'relationships': [], 'annotations': []}
        
        # Process each sloka
        for sloka_line in sanskrit_text:
            sloka_data = self._parse_sloka_line(sloka_line)
            if not sloka_data:
                continue
            
            kanda_num, sarga_num, sloka_num, content = sloka_data
            text_unit_id = f"{kanda_num}.{sarga_num}.{sloka_num}"
            
            # Find corresponding translation and meaning
            translation = self._find_corresponding_text(translation_text, kanda_num, sarga_num, sloka_num)
            meaning = self._find_corresponding_text(meaning_text, kanda_num, sarga_num, sloka_num)
            
            # Extract entities from this sloka
            sloka_entities = self._extract_entities_from_sloka(
                text_unit_id, content, translation, meaning
            )
            
            # Store entities and annotations
            for entity_result in sloka_entities:
                entity_id = entity_result.entity_id
                
                # Create or update entity
                if entity_id not in entities:
                    entities[entity_id] = self._create_entity_from_pattern(entity_id)
                
                # Add annotations
                for start, end in entity_result.mentions:
                    annotation = SemanticAnnotation(
                        text_unit_id=text_unit_id,
                        entity_id=entity_id,
                        span_start=start,
                        span_end=end,
                        confidence=entity_result.confidence
                    )
                    annotations.append(annotation)
                
                # Track statistics
                self.extraction_stats['entities_found'][entity_id] += len(entity_result.mentions)
                self.extraction_stats['confidence_scores'].append(entity_result.confidence)
            
            self.extraction_stats['processed_slokas'] += 1
        
        return {
            'entities': entities,
            'relationships': relationships,
            'annotations': annotations
        }
    
    def _read_file_content(self, file_path: Optional[Path]) -> List[str]:
        """Read file content as lines"""
        if not file_path or not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.logger.warning(f"Failed to read {file_path}: {e}")
            return []
    
    def _parse_sloka_line(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """Parse sloka line format: kanda::sarga::sloka::content"""
        if '::' not in line:
            return None
        
        parts = line.split('::', 3)
        if len(parts) != 4:
            return None
        
        return parts[0], parts[1], parts[2], parts[3]
    
    def _find_corresponding_text(self, text_lines: List[str], kanda: str, sarga: str, sloka: str) -> str:
        """Find corresponding translation/meaning for a sloka"""
        target_prefix = f"{kanda}::{sarga}::{sloka}::"
        
        for line in text_lines:
            if line.startswith(target_prefix):
                return line[len(target_prefix):]
        
        return ""
    
    def _extract_entities_from_sloka(self, text_unit_id: str, sanskrit: str, 
                                   translation: str, meaning: str) -> List[ExtractionResult]:
        """Extract entities from a single sloka across all text types"""
        results = []
        
        # Process Sanskrit text
        results.extend(self._extract_from_text(sanskrit, 'sanskrit'))
        
        # Process English translation
        results.extend(self._extract_from_text(translation, 'translation'))
        
        # Process word meanings (often contains character names)
        results.extend(self._extract_from_text(meaning, 'meaning'))
        
        return results
    
    def _extract_from_text(self, text: str, source_type: str) -> List[ExtractionResult]:
        """Extract entities from a single text"""
        results = []
        
        if not text:
            return results
        
        for pattern in self.entity_patterns:
            # Choose appropriate patterns based on source type
            if source_type == 'sanskrit':
                patterns_to_use = pattern.sanskrit_patterns
            else:
                patterns_to_use = pattern.english_patterns
            
            # Find matches
            mentions = []
            confidence = 0.7  # Base confidence
            
            for regex_pattern in patterns_to_use:
                for match in re.finditer(regex_pattern, text, re.IGNORECASE):
                    mentions.append((match.start(), match.end()))
                    confidence = min(0.95, confidence + 0.1)  # Increase confidence for matches
                    
                    # Track pattern usage
                    self.extraction_stats['patterns_matched'][regex_pattern] += 1
            
            if mentions:
                # Apply confidence boost
                confidence *= pattern.confidence_boost
                confidence = min(0.99, confidence)  # Cap at 99%
                
                results.append(ExtractionResult(
                    entity_id=pattern.entity_id,
                    entity_type=pattern.entity_type,
                    mentions=mentions,
                    confidence=confidence,
                    source_type=source_type
                ))
        
        return results
    
    def _create_entity_from_pattern(self, entity_id: str) -> KGEntity:
        """Create KG entity from pattern definition"""
        pattern = next((p for p in self.entity_patterns if p.entity_id == entity_id), None)
        if not pattern:
            return None
        
        # Extract name from first English pattern (simplified)
        english_name = pattern.english_patterns[0].replace(r'\b', '').replace('\\', '')
        
        # Create labels
        labels = {'en': english_name}
        
        # Add Sanskrit name if available
        if pattern.sanskrit_patterns:
            sanskrit_name = pattern.sanskrit_patterns[0]
            labels['sa'] = sanskrit_name
        
        return KGEntity(
            kg_id=f"http://example.org/entity/{entity_id}",
            entity_type=pattern.entity_type,
            labels=labels,
            properties={
                'epithets': pattern.epithets,
                'confidence_score': pattern.confidence_boost
            }
        )
    
    def _validate_and_enhance_entities(self, entities: Dict[str, KGEntity]) -> Dict[str, KGEntity]:
        """Validate and enhance extracted entities"""
        enhanced_entities = {}
        
        for entity_id, entity in entities.items():
            # Validate minimum occurrences
            occurrence_count = self.extraction_stats['entities_found'][entity_id]
            if occurrence_count >= 2:  # Minimum threshold
                # Enhance with corpus statistics
                entity.properties['occurrence_count'] = occurrence_count
                entity.properties['extraction_confidence'] = min(0.99, 0.5 + (occurrence_count * 0.05))
                
                enhanced_entities[entity_id] = entity
            else:
                self.logger.debug(f"Filtered out {entity_id} due to low occurrence: {occurrence_count}")
        
        return enhanced_entities
    
    def _build_relationship_network(self, relationships: List[KGRelationship]) -> List[KGRelationship]:
        """Build relationships based on co-occurrence patterns"""
        # This is a simplified version - could be enhanced with more sophisticated analysis
        co_occurrence_network = []
        
        # For now, return empty - relationships can be built in a separate phase
        return co_occurrence_network
    
    def _log_extraction_statistics(self):
        """Log extraction statistics"""
        stats = self.extraction_stats
        
        self.logger.info(f"Entity Extraction Complete:")
        self.logger.info(f"  Processed slokas: {stats['processed_slokas']}")
        self.logger.info(f"  Unique entities found: {len(stats['entities_found'])}")
        self.logger.info(f"  Total entity mentions: {sum(stats['entities_found'].values())}")
        
        if stats['confidence_scores']:
            avg_confidence = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
            self.logger.info(f"  Average confidence: {avg_confidence:.2f}")
        
        # Top entities
        top_entities = sorted(stats['entities_found'].items(), key=lambda x: x[1], reverse=True)[:10]
        self.logger.info("  Top entities by mentions:")
        for entity, count in top_entities:
            self.logger.info(f"    {entity}: {count}")


# Utility functions for integration with existing codebase

def extract_entities_for_text_service(text_service, force_refresh: bool = False) -> Dict[str, Any]:
    """Extract entities and integrate with existing text service"""
    extractor = RamayanaEntityExtractor()
    
    # Check if extraction already done
    cache_file = Path("data/extracted_entities.pkl")
    if cache_file.exists() and not force_refresh:
        import pickle
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Perform extraction
    results = extractor.extract_entities_from_corpus()
    
    # Cache results
    import pickle
    with open(cache_file, 'wb') as f:
        pickle.dump(results, f)
    
    return results


def create_sample_kg_data(num_entities: int = 20) -> Dict[str, Any]:
    """Create sample KG data for testing/development"""
    extractor = RamayanaEntityExtractor()
    
    # Process just BalaKanda for quick sample
    bala_path = Path("data/slokas/Slokas/BalaKanda")
    if bala_path.exists():
        results = extractor._process_kanda(bala_path)
        
        # Limit to requested number of entities
        entities = dict(list(results['entities'].items())[:num_entities])
        
        return {
            'entities': entities,
            'relationships': results['relationships'][:10],  # Sample relationships
            'annotations': results['annotations'][:50],  # Sample annotations
            'statistics': {'sample_data': True}
        }
    
    return {'entities': {}, 'relationships': [], 'annotations': []}


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    extractor = RamayanaEntityExtractor()
    
    # Test on a small sample
    sample_results = create_sample_kg_data(10)
    print(f"Extracted {len(sample_results['entities'])} entities")
    print(f"Sample entities: {list(sample_results['entities'].keys())}")