"""
Enhanced Entity Extraction with Proper NLP Strategy for Sanskrit Texts

This module implements a comprehensive approach for extracting entities from Sanskrit texts
using multiple strategies suitable for ancient Indian texts and proper names.
"""

import re
import logging
import requests
import json
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
from pathlib import Path

# For NLP processing
try:
    import spacy
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from api.models.kg_models import KGEntity, KGRelationship, EntityType, SemanticAnnotation


@dataclass
class EntityCandidate:
    """Candidate entity from various extraction methods"""
    text: str
    start: int
    end: int
    entity_type: str
    confidence: float
    extraction_method: str
    context: str
    transliterated_form: Optional[str] = None
    english_translation: Optional[str] = None


class SanskritEntityExtractor:
    """
    Multi-strategy entity extractor specifically designed for Sanskrit texts
    Combines pattern-based, NLP-based, and knowledge-based approaches
    """
    
    def __init__(self, use_external_apis: bool = False):
        self.logger = logging.getLogger(__name__)
        self.use_external_apis = use_external_apis
        
        # Initialize NLP models if available
        self.nlp_model = None
        self.ner_pipeline = None
        self._initialize_nlp_models()
        
        # Sanskrit-specific patterns and knowledge
        self.sanskrit_patterns = self._load_sanskrit_patterns()
        self.transliteration_map = self._load_transliteration_map()
        self.known_epithets = self._load_known_epithets()
        
        # Statistics
        self.extraction_stats = {
            'total_processed': 0,
            'entities_found': defaultdict(int),
            'methods_used': defaultdict(int),
            'confidence_distribution': defaultdict(int)
        }
    
    def _initialize_nlp_models(self):
        """Initialize NLP models for entity extraction"""
        if not SPACY_AVAILABLE:
            self.logger.warning("spaCy not available. Using pattern-based extraction only.")
            return
        
        try:
            # Load English NLP model for translation processing
            self.nlp_model = spacy.load("en_core_web_sm")
            self.logger.info("Loaded spaCy English model")
        except OSError:
            self.logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
        
        try:
            # Load transformer-based NER model
            self.ner_pipeline = pipeline(
                "ner", 
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            self.logger.info("Loaded transformer NER model")
        except Exception as e:
            self.logger.warning(f"Could not load transformer model: {e}")
    
    def _load_sanskrit_patterns(self) -> Dict[str, List[str]]:
        """Load Sanskrit patterns for major entity types"""
        return {
            'person_patterns': [
                # General person indicators
                r'[A-Za-z]*राम[A-Za-z]*',  # Any word containing 'राम'
                r'[A-Za-z]*सीता[A-Za-z]*',  # Any word containing 'सीता'
                r'[A-Za-z]*हनुमा[न्त्][A-Za-z]*',  # Hanuman variants
                r'[A-Za-z]*लक्ष्मण[A-Za-z]*',  # Lakshmana variants
                r'[A-Za-z]*भरत[A-Za-z]*',   # Bharata variants
                r'[A-Za-z]*शत्रुघ्न[A-Za-z]*',  # Shatrughna variants
                r'[A-Za-z]*रावण[A-Za-z]*',  # Ravana variants
                r'[A-Za-z]*विभीषण[A-Za-z]*',  # Vibhishana variants
                r'[A-Za-z]*सुग्रीव[A-Za-z]*',  # Sugriva variants
                r'[A-Za-z]*अङ्गद[A-Za-z]*',  # Angada variants
                r'[A-Za-z]*जामवन्त्[A-Za-z]*',  # Jambavan variants
                r'[A-Za-z]*दशरथ[A-Za-z]*',  # Dasharatha variants
                r'[A-Za-z]*जनक[A-Za-z]*',   # Janaka variants
                r'[A-Za-z]*कैकेयी[A-Za-z]*',  # Kaikeyi variants
                r'[A-Za-z]*कौशल्या[A-Za-z]*',  # Kausalya variants
                r'[A-Za-z]*सुमित्रा[A-Za-z]*',  # Sumitra variants
                
                # Pattern for compound names ending in common suffixes
                r'\b\w*[ःम्य]\b',  # Sanskrit case endings
                r'\b\w*पुत्र[ःम्स्य]?\b',  # Son of X
                r'\b\w*आत्मज[ःम्स्य]?\b',  # Soul-born of X
                r'\b\w*नन्दन[ःम्स्य]?\b',  # Joy of X
            ],
            
            'place_patterns': [
                r'[A-Za-z]*अयोध्या[A-Za-z]*',  # Ayodhya variants
                r'[A-Za-z]*लङ्का[A-Za-z]*',   # Lanka variants
                r'[A-Za-z]*मिथिला[A-Za-z]*',  # Mithila variants
                r'[A-Za-z]*किष्किन्धा[A-Za-z]*',  # Kishkindha variants
                r'[A-Za-z]*दण्डक[A-Za-z]*',   # Dandaka variants
                r'[A-Za-z]*चित्रकूट[A-Za-z]*',  # Chitrakoot variants
                r'[A-Za-z]*पञ्चवटी[A-Za-z]*',  # Panchavati variants
                
                # Pattern for place suffixes
                r'\b\w*पुर[ःम्ी]?\b',  # City
                r'\b\w*नगर[ःम्ी]?\b',  # City
                r'\b\w*आश्रम[ःम्े]?\b',  # Hermitage
                r'\b\w*वन[ःम्े]?\b',   # Forest
                r'\b\w*गिरि[ःम्]?\b',  # Mountain
                r'\b\w*सागर[ःम्]?\b',  # Ocean
            ],
            
            'concept_patterns': [
                r'धर्म[ःम्स्य]?',  # Dharma
                r'अर्थ[ःम्स्य]?',  # Artha
                r'काम[ःम्स्य]?',   # Kama
                r'मोक्ष[ःम्स्य]?', # Moksha
                r'यज्ञ[ःम्स्य]?',  # Yajna
                r'तप[ःम्स्य]?',    # Tapas
                r'भक्ति[ःम्स्य]?', # Bhakti
                r'करुणा[ःम्स्य]?', # Compassion
                r'दया[ःम्स्य]?',   # Mercy
                r'अहिंसा[ःम्स्य]?', # Non-violence
            ]
        }
    
    def _load_transliteration_map(self) -> Dict[str, str]:
        """Load Devanagari to Roman transliteration mappings"""
        return {
            'राम': 'Rama',
            'सीता': 'Sita',
            'हनुमान्': 'Hanuman',
            'लक्ष्मण': 'Lakshmana',
            'भरत': 'Bharata',
            'शत्रुघ्न': 'Shatrughna',
            'रावण': 'Ravana',
            'विभीषण': 'Vibhishana',
            'सुग्रीव': 'Sugriva',
            'अयोध्या': 'Ayodhya',
            'लङ्का': 'Lanka',
            'मिथिला': 'Mithila',
            'धर्म': 'Dharma',
            'अर्थ': 'Artha',
            'काम': 'Kama',
            'मोक्ष': 'Moksha'
        }
    
    def _load_known_epithets(self) -> Dict[str, List[str]]:
        """Load known epithets for major characters"""
        return {
            'rama': ['राघव', 'दाशरथि', 'काकुत्स्थ', 'कोसलेन्द्र', 'रघुनन्दन'],
            'sita': ['मैथिली', 'वैदेही', 'जानकी', 'भूमिजा'],
            'hanuman': ['पवनात्मज', 'वायुपुत्र', 'मारुति', 'अञ्जनेय', 'महावीर'],
            'ravana': ['दशग्रीव', 'लङ्केश', 'दशमुख', 'रावणेश्वर'],
            'lakshmana': ['सौमित्रि', 'लक्ष्मण'],
            'bharata': ['भरत', 'कैकेयीनन्दन'],
            'sugriva': ['सुग्रीव', 'वानरराज', 'किष्किन्धेश']
        }
    
    def extract_entities_from_corpus(self, corpus_path: str = "data/slokas/Slokas") -> Dict[str, Any]:
        """
        Extract entities using multiple strategies:
        1. Pattern-based Sanskrit extraction
        2. NLP-based English extraction  
        3. Knowledge-based epithet recognition
        4. External API verification (optional)
        """
        self.logger.info("Starting enhanced multi-strategy entity extraction")
        
        all_candidates = []
        entities = {}
        
        # Process each text unit
        for kanda_path in self._get_kanda_directories(corpus_path):
            self.logger.info(f"Processing {kanda_path.name}")
            kanda_candidates = self._process_kanda_enhanced(kanda_path)
            all_candidates.extend(kanda_candidates)
        
        # Consolidate and rank candidates
        entities = self._consolidate_candidates(all_candidates)
        
        # Post-process with external verification if enabled
        if self.use_external_apis:
            entities = self._verify_with_external_apis(entities)
        
        self._log_extraction_statistics()
        
        return {
            'entities': entities,
            'candidates': all_candidates,
            'statistics': self.extraction_stats
        }
    
    def _process_kanda_enhanced(self, kanda_path: Path) -> List[EntityCandidate]:
        """Process a kanda with enhanced extraction strategies"""
        candidates = []
        
        sarga_files = self._group_sarga_files(kanda_path)
        
        for sarga_id, files in sarga_files.items():
            if len(files) == 3:  # sloka, translation, meaning
                sarga_candidates = self._extract_from_sarga_enhanced(
                    kanda_path.name, sarga_id, files
                )
                candidates.extend(sarga_candidates)
        
        return candidates
    
    def _extract_from_sarga_enhanced(self, kanda_name: str, sarga_id: str, 
                                   files: Dict[str, Path]) -> List[EntityCandidate]:
        """Enhanced extraction from a single sarga"""
        candidates = []
        
        # Read all three file types
        sanskrit_text = self._read_file_content(files.get('sloka'))
        translation_text = self._read_file_content(files.get('translation'))
        meaning_text = self._read_file_content(files.get('meaning'))
        
        for i, sloka_line in enumerate(sanskrit_text):
            sloka_data = self._parse_sloka_line(sloka_line)
            if not sloka_data:
                continue
            
            kanda_num, sarga_num, sloka_num, sanskrit_content = sloka_data
            text_unit_id = f"{kanda_num}.{sarga_num}.{sloka_num}"
            
            # Find corresponding texts
            translation = self._find_corresponding_text(translation_text, kanda_num, sarga_num, sloka_num)
            meaning = self._find_corresponding_text(meaning_text, kanda_num, sarga_num, sloka_num)
            
            # Strategy 1: Sanskrit pattern extraction
            sanskrit_candidates = self._extract_sanskrit_patterns(
                sanskrit_content, text_unit_id, 'sanskrit'
            )
            candidates.extend(sanskrit_candidates)
            
            # Strategy 2: English NLP extraction  
            if translation:
                english_candidates = self._extract_english_nlp(
                    translation, text_unit_id, 'translation'
                )
                candidates.extend(english_candidates)
            
            # Strategy 3: Meaning-based extraction
            if meaning:
                meaning_candidates = self._extract_meaning_based(
                    meaning, text_unit_id, 'meaning'
                )
                candidates.extend(meaning_candidates)
            
            # Strategy 4: Context-based epithet recognition
            context_candidates = self._extract_context_epithets(
                sanskrit_content, translation, meaning, text_unit_id
            )
            candidates.extend(context_candidates)
            
            self.extraction_stats['total_processed'] += 1
        
        return candidates
    
    def _extract_sanskrit_patterns(self, text: str, text_unit_id: str, 
                                 source_type: str) -> List[EntityCandidate]:
        """Extract entities using Sanskrit patterns"""
        candidates = []
        
        if not text:
            return candidates
        
        # Try each entity type pattern
        for entity_type, patterns in self.sanskrit_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    candidate = EntityCandidate(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        entity_type=entity_type.replace('_patterns', ''),
                        confidence=0.7,
                        extraction_method='sanskrit_pattern',
                        context=text[max(0, match.start()-50):match.end()+50],
                        transliterated_form=self._transliterate(match.group())
                    )
                    candidates.append(candidate)
                    self.extraction_stats['methods_used']['sanskrit_pattern'] += 1
        
        return candidates
    
    def _extract_english_nlp(self, text: str, text_unit_id: str, 
                           source_type: str) -> List[EntityCandidate]:
        """Extract entities using English NLP models"""
        candidates = []
        
        if not text or not self.nlp_model:
            return candidates
        
        # Use spaCy NER
        doc = self.nlp_model(text)
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'GPE', 'LOC', 'ORG']:  # Relevant entity types
                candidate = EntityCandidate(
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    entity_type=self._map_spacy_label(ent.label_),
                    confidence=0.8,
                    extraction_method='spacy_ner',
                    context=text[max(0, ent.start_char-50):ent.end_char+50],
                    english_translation=ent.text
                )
                candidates.append(candidate)
                self.extraction_stats['methods_used']['spacy_ner'] += 1
        
        # Use transformer NER if available
        if self.ner_pipeline:
            try:
                ner_results = self.ner_pipeline(text)
                for result in ner_results:
                    if result['entity_group'] in ['PER', 'LOC', 'ORG']:
                        candidate = EntityCandidate(
                            text=result['word'],
                            start=result['start'],
                            end=result['end'],
                            entity_type=self._map_transformer_label(result['entity_group']),
                            confidence=result['score'],
                            extraction_method='transformer_ner',
                            context=text[max(0, result['start']-50):result['end']+50],
                            english_translation=result['word']
                        )
                        candidates.append(candidate)
                        self.extraction_stats['methods_used']['transformer_ner'] += 1
            except Exception as e:
                self.logger.warning(f"Transformer NER failed: {e}")
        
        return candidates
    
    def _extract_meaning_based(self, text: str, text_unit_id: str, 
                             source_type: str) -> List[EntityCandidate]:
        """Extract entities from word-by-word meanings"""
        candidates = []
        
        if not text:
            return candidates
        
        # Look for Sanskrit words in meanings (often formatted as "word = meaning")
        meaning_patterns = [
            r'([^\s=]+)\s*=\s*([^,;]+)',  # word = meaning
            r'([^\s\-]+)\s*\-\s*([^,;]+)',  # word - meaning  
            r'\b([A-Za-z]+)\s*:\s*([^,;]+)',  # word: meaning
        ]
        
        for pattern in meaning_patterns:
            for match in re.finditer(pattern, text):
                sanskrit_word = match.group(1).strip()
                english_meaning = match.group(2).strip()
                
                # Check if this looks like a proper noun
                if self._is_likely_proper_noun(sanskrit_word, english_meaning):
                    candidate = EntityCandidate(
                        text=sanskrit_word,
                        start=match.start(1),
                        end=match.end(1),
                        entity_type=self._classify_from_meaning(english_meaning),
                        confidence=0.6,
                        extraction_method='meaning_analysis',
                        context=match.group(0),
                        english_translation=english_meaning
                    )
                    candidates.append(candidate)
                    self.extraction_stats['methods_used']['meaning_analysis'] += 1
        
        return candidates
    
    def _extract_context_epithets(self, sanskrit: str, translation: str, 
                                 meaning: str, text_unit_id: str) -> List[EntityCandidate]:
        """Extract entities based on known epithets and context"""
        candidates = []
        
        # Check for known epithets in Sanskrit text
        for character, epithets in self.known_epithets.items():
            for epithet in epithets:
                for text, source_type in [(sanskrit, 'sanskrit'), (translation, 'translation'), (meaning, 'meaning')]:
                    if not text:
                        continue
                    
                    for match in re.finditer(re.escape(epithet), text):
                        candidate = EntityCandidate(
                            text=match.group(),
                            start=match.start(),
                            end=match.end(),
                            entity_type='person',
                            confidence=0.9,  # High confidence for known epithets
                            extraction_method='epithet_recognition',
                            context=text[max(0, match.start()-50):match.end()+50],
                            transliterated_form=character.title()
                        )
                        candidates.append(candidate)
                        self.extraction_stats['methods_used']['epithet_recognition'] += 1
        
        return candidates
    
    def _consolidate_candidates(self, candidates: List[EntityCandidate]) -> Dict[str, KGEntity]:
        """Consolidate overlapping candidates and create final entities"""
        entities = {}
        
        # Group candidates by normalized text
        candidate_groups = defaultdict(list)
        for candidate in candidates:
            # Normalize the text for grouping
            normalized = self._normalize_entity_text(candidate.text)
            candidate_groups[normalized].append(candidate)
        
        # Process each group
        for normalized_text, group in candidate_groups.items():
            if len(group) < 2:  # Skip entities with only one mention
                continue
            
            # Calculate aggregate confidence
            confidence = self._calculate_aggregate_confidence(group)
            
            # Determine best entity type
            entity_type = self._determine_entity_type(group)
            
            # Create entity
            entity_id = f"entity_{len(entities) + 1}"
            
            # Get best translations
            english_name = self._get_best_english_name(group)
            sanskrit_name = self._get_best_sanskrit_name(group)
            
            entity = KGEntity(
                kg_id=f"http://ramayanam.hanuma.com/entity/{entity_id}",
                entity_type=EntityType(entity_type.upper()),
                labels={
                    'en': english_name,
                    'sa': sanskrit_name
                },
                properties={
                    'extraction_confidence': confidence,
                    'mention_count': len(group),
                    'extraction_methods': list(set(c.extraction_method for c in group)),
                    'validation_status': 'pending'
                }
            )
            
            entities[entity_id] = entity
            self.extraction_stats['entities_found'][entity_type] += 1
        
        return entities
    
    # Helper methods
    def _get_kanda_directories(self, corpus_path: str) -> List[Path]:
        """Get all kanda directories"""
        data_dir = Path(corpus_path)
        return [d for d in data_dir.iterdir() if d.is_dir()]
    
    def _group_sarga_files(self, kanda_path: Path) -> Dict[str, Dict[str, Path]]:
        """Group sarga files by sarga number"""
        sarga_files = defaultdict(dict)
        
        for file_path in kanda_path.glob("*.txt"):
            parts = file_path.stem.split('_')
            if len(parts) >= 4:
                sarga_num = parts[2]
                file_type = parts[3]
                sarga_files[sarga_num][file_type] = file_path
        
        return dict(sarga_files)
    
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
    
    def _transliterate(self, sanskrit_text: str) -> str:
        """Simple transliteration of Sanskrit to Roman"""
        return self.transliteration_map.get(sanskrit_text, sanskrit_text)
    
    def _map_spacy_label(self, label: str) -> str:
        """Map spaCy entity labels to our types"""
        mapping = {
            'PERSON': 'person',
            'GPE': 'place',
            'LOC': 'place',
            'ORG': 'organization'
        }
        return mapping.get(label, 'other')
    
    def _map_transformer_label(self, label: str) -> str:
        """Map transformer entity labels to our types"""
        mapping = {
            'PER': 'person',
            'LOC': 'place',
            'ORG': 'organization'
        }
        return mapping.get(label, 'other')
    
    def _is_likely_proper_noun(self, word: str, meaning: str) -> bool:
        """Check if word is likely a proper noun based on meaning"""
        proper_noun_indicators = [
            'name of', 'called', 'known as', 'son of', 'daughter of',
            'king', 'queen', 'prince', 'princess', 'sage', 'demon',
            'city', 'mountain', 'river', 'forest', 'place'
        ]
        
        return any(indicator in meaning.lower() for indicator in proper_noun_indicators)
    
    def _classify_from_meaning(self, meaning: str) -> str:
        """Classify entity type from English meaning"""
        if any(word in meaning.lower() for word in ['king', 'queen', 'prince', 'princess', 'sage', 'demon', 'son', 'daughter']):
            return 'person'
        elif any(word in meaning.lower() for word in ['city', 'place', 'mountain', 'river', 'forest']):
            return 'place'
        elif any(word in meaning.lower() for word in ['dharma', 'duty', 'virtue', 'concept']):
            return 'concept'
        else:
            return 'other'
    
    def _normalize_entity_text(self, text: str) -> str:
        """Normalize entity text for grouping"""
        # Remove common Sanskrit case endings
        normalized = re.sub(r'[ःं]$|म्$|स्य$', '', text)
        return normalized.lower().strip()
    
    def _calculate_aggregate_confidence(self, candidates: List[EntityCandidate]) -> float:
        """Calculate aggregate confidence from multiple candidates"""
        if not candidates:
            return 0.0
        
        # Weight by extraction method reliability
        method_weights = {
            'epithet_recognition': 1.0,
            'sanskrit_pattern': 0.8,
            'spacy_ner': 0.9,
            'transformer_ner': 0.95,
            'meaning_analysis': 0.6
        }
        
        weighted_sum = sum(
            c.confidence * method_weights.get(c.extraction_method, 0.5) 
            for c in candidates
        )
        total_weight = sum(method_weights.get(c.extraction_method, 0.5) for c in candidates)
        
        return min(0.99, weighted_sum / total_weight if total_weight > 0 else 0.5)
    
    def _determine_entity_type(self, candidates: List[EntityCandidate]) -> str:
        """Determine entity type from candidates"""
        type_counts = Counter(c.entity_type for c in candidates)
        return type_counts.most_common(1)[0][0] if type_counts else 'other'
    
    def _get_best_english_name(self, candidates: List[EntityCandidate]) -> str:
        """Get best English name from candidates"""
        english_names = [c.english_translation for c in candidates if c.english_translation]
        if english_names:
            return Counter(english_names).most_common(1)[0][0]
        
        # Fallback to transliterated form
        transliterations = [c.transliterated_form for c in candidates if c.transliterated_form]
        if transliterations:
            return transliterations[0]
        
        return candidates[0].text if candidates else 'Unknown'
    
    def _get_best_sanskrit_name(self, candidates: List[EntityCandidate]) -> str:
        """Get best Sanskrit name from candidates"""
        sanskrit_names = [c.text for c in candidates if self._is_sanskrit_text(c.text)]
        if sanskrit_names:
            return Counter(sanskrit_names).most_common(1)[0][0]
        
        return candidates[0].text if candidates else 'Unknown'
    
    def _is_sanskrit_text(self, text: str) -> bool:
        """Check if text contains Sanskrit (Devanagari) characters"""
        return bool(re.search(r'[\u0900-\u097F]', text))
    
    def _verify_with_external_apis(self, entities: Dict[str, KGEntity]) -> Dict[str, KGEntity]:
        """Verify entities using external APIs (Google, Wikipedia, etc.)"""
        # This would implement external API calls for verification
        # For now, just return the entities as-is
        self.logger.info("External API verification not implemented yet")
        return entities
    
    def _log_extraction_statistics(self):
        """Log extraction statistics"""
        stats = self.extraction_stats
        
        self.logger.info(f"Enhanced Entity Extraction Complete:")
        self.logger.info(f"  Total processed: {stats['total_processed']}")
        self.logger.info(f"  Entities found by type: {dict(stats['entities_found'])}")
        self.logger.info(f"  Methods used: {dict(stats['methods_used'])}")


if __name__ == "__main__":
    # Test the enhanced extractor
    logging.basicConfig(level=logging.INFO)
    
    extractor = SanskritEntityExtractor(use_external_apis=False)
    results = extractor.extract_entities_from_corpus()
    
    print(f"Enhanced extraction found {len(results['entities'])} entities")
    print(f"Candidates generated: {len(results['candidates'])}")
    print(f"Statistics: {results['statistics']}")