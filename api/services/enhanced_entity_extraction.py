"""
Enhanced Entity Extraction for Phase 1 Scale-Up
Optimized for processing the full Ramayana corpus with improved patterns and performance
"""

import re
import sqlite3
import logging
import json
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from api.models.kg_models import KGEntity, KGRelationship, EntityType, SemanticAnnotation


@dataclass
class EnhancedEntityPattern:
    """Enhanced pattern for entity identification with confidence scoring"""
    entity_id: str
    entity_type: EntityType
    primary_names: List[str]  # Most common names
    alternative_names: List[str]  # Alternative spellings/forms
    sanskrit_patterns: List[str]  # Sanskrit regex patterns
    english_patterns: List[str]  # English regex patterns
    epithets: List[str]  # Known epithets
    context_words: List[str]  # Words that boost confidence when found nearby
    confidence_base: float = 0.8
    min_confidence: float = 0.6
    
    def __post_init__(self):
        if not self.epithets:
            self.epithets = []
        if not self.context_words:
            self.context_words = []


class ScalableEntityExtractor:
    """Enhanced entity extractor optimized for large-scale processing"""
    
    def __init__(self, db_path: str = "data/db/ramayanam.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.entity_patterns = self._load_enhanced_patterns()
        self.processed_cache = set()  # Cache to avoid reprocessing
        self.extraction_stats = {
            'total_processed': 0,
            'entities_found': 0,
            'new_entities': 0,
            'processing_time': 0
        }
        self._lock = threading.Lock()
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _load_enhanced_patterns(self) -> List[EnhancedEntityPattern]:
        """Load comprehensive entity patterns for the Ramayana"""
        patterns = [
            # Major Characters - Enhanced patterns
            EnhancedEntityPattern(
                entity_id="rama",
                entity_type=EntityType.PERSON,
                primary_names=["राम", "राम:", "रामम्", "रामस्य", "रामो", "रामे"],
                alternative_names=["राघव", "दशरथि", "कोसलेन्द्र", "रघुनन्दन"],
                sanskrit_patterns=[
                    r"राम[ःम्ं।]?",
                    r"राघव[ःम्ं।]?", 
                    r"दशरथि[ःम्ं।]?",
                    r"रघु(?:नन्दन|पति|वीर)[ःम्ं।]?",
                    r"कोसल(?:राज|पति|नाथ)[ःम्ं।]?"
                ],
                english_patterns=[
                    r"\brama\b", r"\braghava\b", r"\bdasharathi\b"
                ],
                epithets=["राघव", "दशरथि", "कोसलेन्द्र", "रघुनन्दन", "रघुपति"],
                context_words=["राजा", "प्रिन्स", "धनुष", "सीता", "अयोध्या"],
                confidence_base=0.95
            ),
            
            EnhancedEntityPattern(
                entity_id="sita",
                entity_type=EntityType.PERSON,
                primary_names=["सीता", "सीते", "सीताम्", "सीतया"],
                alternative_names=["जानकी", "वैदेही", "मिथिलेशी"],
                sanskrit_patterns=[
                    r"सीत[ाे ाम्या ासम्।ः]?",
                    r"जानकी[म्ं।]?",
                    r"वैदेही[म्ं।]?",
                    r"मिथिलेश[ीः][म्ं।]?"
                ],
                english_patterns=[
                    r"\bsita\b", r"\bjanaki\b", r"\bvaidehi\b"
                ],
                epithets=["जानकी", "वैदेही", "मिथिलेशी"],
                context_words=["पत्नी", "राम", "रानी", "वन", "अग्नि"],
                confidence_base=0.95
            ),
            
            EnhancedEntityPattern(
                entity_id="lakshmana", 
                entity_type=EntityType.PERSON,
                primary_names=["लक्ष्मण", "लक्ष्मणस्य", "लक्ष्मणम्"],
                alternative_names=["सौमित्रि", "शेषावतार"],
                sanskrit_patterns=[
                    r"लक्ष्मण[ःम्ं।स्य]?",
                    r"सौमित्रि[ःम्ं।]?",
                    r"शेषावतार[ःम्ं।]?"
                ],
                english_patterns=[
                    r"\blakshmana\b", r"\blakshman\b", r"\bsaumitri\b"
                ],
                epithets=["सौमित्रि", "शेषावतार"],
                context_words=["भाई", "राम", "धनुष", "वन"],
                confidence_base=0.9
            ),
            
            EnhancedEntityPattern(
                entity_id="ravana",
                entity_type=EntityType.PERSON,
                primary_names=["रावण", "रावणस्य", "रावणम्"],
                alternative_names=["दशानन", "लंकेश", "राक्षसराज"],
                sanskrit_patterns=[
                    r"रावण[ःम्ं।स्य]?",
                    r"दशानन[ःम्ं।]?",
                    r"लंकेश[ःम्ं।]?",
                    r"राक्षस(?:राज|पति)[ःम्ं।]?"
                ],
                english_patterns=[
                    r"\bravana\b", r"\bdashanan\b", r"\blankesh\b"
                ],
                epithets=["दशानन", "लंकेश", "राक्षसराज"],
                context_words=["राक्षस", "लंका", "शत्रु", "युद्ध"],
                confidence_base=0.9
            ),
            
            EnhancedEntityPattern(
                entity_id="hanuman",
                entity_type=EntityType.PERSON, 
                primary_names=["हनुमान्", "हनुमत्", "हनुमान"],
                alternative_names=["मारुति", "पवनपुत्र", "वायुपुत्र", "अंजनेय"],
                sanskrit_patterns=[
                    r"हनुम[ाान्त्][न्तः।ं]?",
                    r"मारुति[ःम्ं।]?",
                    r"पवन(?:पुत्र|सुत)[ःम्ं।]?",
                    r"वायु(?:पुत्र|सुत)[ःम्ं।]?",
                    r"अंजनेय[ःम्ं।]?"
                ],
                english_patterns=[
                    r"\bhanuman\b", r"\bmaruti\b", r"\banjaneya\b"
                ],
                epithets=["मारुति", "पवनपुत्र", "वायुपुत्र", "अंजनेय"],
                context_words=["वानर", "राम", "सेवक", "उड़ना"],
                confidence_base=0.9
            ),
            
            # Places - Enhanced patterns
            EnhancedEntityPattern(
                entity_id="ayodhya",
                entity_type=EntityType.PLACE,
                primary_names=["अयोध्या", "अयोध्याम्", "अयोध्यायाम्"],
                alternative_names=["कोसल", "साकेत"],
                sanskrit_patterns=[
                    r"अयोध्या[म्यांः।]?",
                    r"कोसल[ेम्ं।]?",
                    r"साकेत[म्ं।]?"
                ],
                english_patterns=[
                    r"\bayodhya\b", r"\bkosala\b", r"\bsaketa\b"
                ],
                epithets=["कोसल", "साकेत"],
                context_words=["नगर", "राज्य", "राजधानी", "राम"],
                confidence_base=0.85
            ),
            
            EnhancedEntityPattern(
                entity_id="lanka",
                entity_type=EntityType.PLACE,
                primary_names=["लंका", "लंकाम्", "लंकायाम्"],
                alternative_names=["रावणपुरी", "राक्षसपुरी"],
                sanskrit_patterns=[
                    r"लंका[म्यांः।]?",
                    r"रावणपुरी[म्ं।]?",
                    r"राक्षसपुरी[म्ं।]?"
                ],
                english_patterns=[
                    r"\blanka\b", r"\bravanapur\b"
                ],
                epithets=["रावणपुरी", "राक्षसपुरी"],
                context_words=["द्वीप", "सागर", "रावण", "राक्षस"],
                confidence_base=0.85
            ),
            
            EnhancedEntityPattern(
                entity_id="dandaka",
                entity_type=EntityType.PLACE,
                primary_names=["दण्डक", "दण्डकारण्य"],
                alternative_names=["वन", "अरण्य"],
                sanskrit_patterns=[
                    r"दण्डक[ःम्ं।]?",
                    r"दण्डकारण्य[म्ं।]?"
                ],
                english_patterns=[
                    r"\bdandaka\b", r"\bdandakaranya\b"
                ],
                epithets=["दण्डकारण्य"],
                context_words=["वन", "अरण्य", "निर्वासन", "तपस्या"],
                confidence_base=0.8
            ),
            
            # Concepts - Enhanced patterns  
            EnhancedEntityPattern(
                entity_id="dharma",
                entity_type=EntityType.CONCEPT,
                primary_names=["धर्म", "धर्मस्य", "धर्मम्"],
                alternative_names=["न्याय", "सत्य", "कर्तव्य"],
                sanskrit_patterns=[
                    r"धर्म[ःम्ेस्य।]?",
                    r"न्याय[ःम्ं।]?",
                    r"सत्य[ःम्ं।]?",
                    r"कर्तव्य[ःम्ं।]?"
                ],
                english_patterns=[
                    r"\bdharma\b", r"\brighteousness\b", r"\bduty\b"
                ],
                epithets=["न्याय", "सत्य", "कर्तव्य"],
                context_words=["राज्य", "न्याय", "शासन", "आचार"],
                confidence_base=0.75
            ),
            
            EnhancedEntityPattern(
                entity_id="karma",
                entity_type=EntityType.CONCEPT,
                primary_names=["कर्म", "कर्मणः", "कर्मणा"],
                alternative_names=["कृत्य", "क्रिया"],
                sanskrit_patterns=[
                    r"कर्म[णःनाम्।]?",
                    r"कृत्य[ःम्ं।]?",
                    r"क्रिया[म्ं।]?"
                ],
                english_patterns=[
                    r"\bkarma\b", r"\baction\b", r"\bdeed\b"
                ],
                epithets=["कृत्य", "क्रिया"],
                context_words=["फल", "परिणाम", "कर्ता"],
                confidence_base=0.7
            )
        ]
        
        self.logger.info(f"Loaded {len(patterns)} enhanced entity patterns")
        return patterns
    
    def extract_entities_from_sloka(self, sloka_row) -> List[Dict[str, Any]]:
        """Extract entities from a single sloka with enhanced matching"""
        text_unit_id = f"{sloka_row['kanda_id']}.{sloka_row['sarga_id']}.{sloka_row['sloka_id']}"
        
        # Skip if already processed (for incremental processing)
        if text_unit_id in self.processed_cache:
            return []
        
        extractions = []
        
        # Process different text fields
        texts_to_process = [
            (sloka_row['sloka'], 'sanskrit'),
            (sloka_row['translation'], 'translation'), 
            (sloka_row['meaning'], 'meaning')
        ]
        
        for text, source_type in texts_to_process:
            if not text:
                continue
                
            text = str(text).lower()
            
            for pattern in self.entity_patterns:
                entity_mentions = self._find_entity_mentions(text, pattern, source_type)
                
                for mention in entity_mentions:
                    extraction = {
                        'entity_id': pattern.entity_id,
                        'entity_type': pattern.entity_type.value,
                        'text_unit_id': text_unit_id,
                        'span_start': mention['start'],
                        'span_end': mention['end'],
                        'confidence': mention['confidence'],
                        'source_type': source_type,
                        'matched_text': mention['matched_text'],
                        'pattern_type': mention['pattern_type']
                    }
                    extractions.append(extraction)
        
        return extractions
    
    def _find_entity_mentions(self, text: str, pattern: EnhancedEntityPattern, source_type: str) -> List[Dict[str, Any]]:
        """Find all mentions of an entity in text using enhanced patterns"""
        mentions = []
        
        # Choose appropriate patterns based on source type
        if source_type == 'sanskrit':
            patterns_to_use = pattern.sanskrit_patterns
        else:
            patterns_to_use = pattern.english_patterns
        
        for regex_pattern in patterns_to_use:
            for match in re.finditer(regex_pattern, text, re.IGNORECASE):
                confidence = self._calculate_confidence(
                    text, match, pattern, source_type
                )
                
                if confidence >= pattern.min_confidence:
                    mentions.append({
                        'start': match.start(),
                        'end': match.end(), 
                        'confidence': confidence,
                        'matched_text': match.group(),
                        'pattern_type': regex_pattern
                    })
        
        return mentions
    
    def _calculate_confidence(self, text: str, match, pattern: EnhancedEntityPattern, source_type: str) -> float:
        """Calculate confidence score for an entity match"""
        base_confidence = pattern.confidence_base
        
        # Boost confidence based on source type
        source_multipliers = {
            'sanskrit': 1.0,
            'translation': 0.9,
            'meaning': 0.8
        }
        confidence = base_confidence * source_multipliers.get(source_type, 0.7)
        
        # Context boost - check for related words nearby
        context_window = text[max(0, match.start()-50):match.end()+50]
        context_boost = 0
        for context_word in pattern.context_words:
            if context_word.lower() in context_window.lower():
                context_boost += 0.05
        
        # Epithet boost
        for epithet in pattern.epithets:
            if epithet.lower() in context_window.lower():
                context_boost += 0.1
        
        # Apply boosts but cap at 1.0
        final_confidence = min(1.0, confidence + context_boost)
        
        return final_confidence
    
    def process_corpus_batch(self, batch_size: int = 1000, max_workers: int = 4) -> Dict[str, Any]:
        """Process the entire corpus in batches with parallel processing"""
        start_time = time.time()
        
        self.logger.info(f"Starting large-scale entity extraction with {max_workers} workers")
        
        with self.get_connection() as conn:
            # Get total count for progress tracking
            total_slokas = conn.execute("SELECT COUNT(*) as count FROM slokas").fetchone()['count']
            
            # Load already processed slokas to skip them
            processed_units = conn.execute("""
                SELECT DISTINCT text_unit_id FROM text_entity_mentions
            """).fetchall()
            
            self.processed_cache = {row['text_unit_id'] for row in processed_units}
            
            self.logger.info(f"Found {len(self.processed_cache)} already processed slokas")
            
            # Process in batches
            results = {
                'entities': {},
                'mentions': [],
                'statistics': {
                    'total_slokas': total_slokas,
                    'processed_slokas': 0,
                    'entities_found': 0,
                    'new_entities': 0,
                    'processing_time': 0
                }
            }
            
            offset = 0
            while offset < total_slokas:
                batch_start = time.time()
                
                # Get batch of slokas
                slokas = conn.execute("""
                    SELECT kanda_id, sarga_id, sloka_id, sloka, translation, meaning
                    FROM slokas 
                    ORDER BY kanda_id, sarga_id, sloka_id
                    LIMIT ? OFFSET ?
                """, (batch_size, offset)).fetchall()
                
                if not slokas:
                    break
                
                # Process batch with parallel workers
                batch_results = self._process_batch_parallel(slokas, max_workers)
                
                # Store results in database
                self._store_batch_results(batch_results)
                
                # Update statistics
                batch_time = time.time() - batch_start
                results['statistics']['processed_slokas'] += len(slokas)
                results['statistics']['entities_found'] += len(batch_results)
                
                # Progress logging
                progress = (offset + len(slokas)) / total_slokas * 100
                self.logger.info(f"Progress: {progress:.1f}% ({offset + len(slokas)}/{total_slokas}) - "
                               f"Batch time: {batch_time:.2f}s - Found: {len(batch_results)} entities")
                
                offset += batch_size
        
        total_time = time.time() - start_time
        results['statistics']['processing_time'] = total_time
        
        self.logger.info(f"Completed corpus processing in {total_time:.2f}s")
        return results
    
    def _process_batch_parallel(self, slokas: List, max_workers: int) -> List[Dict[str, Any]]:
        """Process a batch of slokas in parallel"""
        all_extractions = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all slokas for processing
            future_to_sloka = {
                executor.submit(self.extract_entities_from_sloka, sloka): sloka 
                for sloka in slokas
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_sloka):
                try:
                    extractions = future.result()
                    all_extractions.extend(extractions)
                except Exception as e:
                    sloka = future_to_sloka[future]
                    self.logger.error(f"Error processing sloka {sloka.get('sloka_id', 'unknown')}: {e}")
        
        return all_extractions
    
    def _store_batch_results(self, extractions: List[Dict[str, Any]]):
        """Store extraction results in database efficiently"""
        if not extractions:
            return
        
        with self.get_connection() as conn:
            # Group extractions by entity for efficient storage
            entities_data = defaultdict(list)
            mentions_data = []
            
            for extraction in extractions:
                entity_id = extraction['entity_id']
                entities_data[entity_id].append(extraction)
                
                # Prepare mention data
                mentions_data.append((
                    extraction['text_unit_id'],
                    entity_id, 
                    extraction['span_start'],
                    extraction['span_end'],
                    extraction['confidence'],
                    extraction['source_type']
                ))
            
            # Store/update entities
            for entity_id, entity_extractions in entities_data.items():
                self._store_or_update_entity(conn, entity_id, entity_extractions)
            
            # Batch insert mentions
            conn.executemany("""
                INSERT OR IGNORE INTO text_entity_mentions 
                (text_unit_id, entity_id, span_start, span_end, confidence, source_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, mentions_data)
            
            conn.commit()
            self.logger.debug(f"Stored {len(entities_data)} entities and {len(mentions_data)} mentions")
    
    def _store_or_update_entity(self, conn, entity_id: str, extractions: List[Dict[str, Any]]):
        """Store or update entity information"""
        if not extractions:
            return
        
        first_extraction = extractions[0]
        entity_type = first_extraction['entity_type']
        
        # Find corresponding pattern for labels and properties
        pattern = next((p for p in self.entity_patterns if p.entity_id == entity_id), None)
        if not pattern:
            return
        
        # Calculate aggregated confidence and occurrence count
        total_confidence = sum(e['confidence'] for e in extractions)
        avg_confidence = total_confidence / len(extractions)
        occurrence_count = len(extractions)
        
        # Prepare labels
        labels = {
            'en': pattern.primary_names[0] if pattern.primary_names else entity_id,
            'sa': pattern.primary_names[0] if pattern.primary_names else entity_id
        }
        
        # Prepare properties  
        properties = {
            'epithets': pattern.epithets,
            'confidence_score': avg_confidence,
            'occurrence_count': occurrence_count,
            'extraction_confidence': avg_confidence,
            'alternative_names': pattern.alternative_names,
            'context_words': pattern.context_words
        }
        
        # Store/update entity
        kg_id = f"http://ramayanam.hanuma.com/entity/{entity_id}"
        
        conn.execute("""
            INSERT OR REPLACE INTO kg_entities 
            (kg_id, entity_type, labels, properties, extraction_method, extraction_confidence, updated_at)
            VALUES (?, ?, ?, ?, 'automated', ?, CURRENT_TIMESTAMP)
        """, (
            kg_id,
            entity_type,
            json.dumps(labels),
            json.dumps(properties),
            avg_confidence
        ))
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        with self.get_connection() as conn:
            stats = {
                'total_entities': conn.execute("SELECT COUNT(*) as count FROM kg_entities").fetchone()['count'],
                'total_mentions': conn.execute("SELECT COUNT(*) as count FROM text_entity_mentions").fetchone()['count'],
                'processed_slokas': conn.execute("SELECT COUNT(DISTINCT text_unit_id) as count FROM text_entity_mentions").fetchone()['count'],
                'total_slokas': conn.execute("SELECT COUNT(*) as count FROM slokas").fetchone()['count']
            }
            
            stats['completion_percentage'] = (stats['processed_slokas'] / stats['total_slokas']) * 100
            
            return stats


def run_scaled_extraction():
    """Main function to run scaled entity extraction"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    extractor = ScalableEntityExtractor()
    
    print("🚀 Starting Phase 1: Scaled Entity Discovery")
    print("=" * 60)
    
    # Get initial statistics
    initial_stats = extractor.get_processing_statistics()
    print(f"Initial state: {initial_stats['total_entities']} entities, "
          f"{initial_stats['processed_slokas']}/{initial_stats['total_slokas']} slokas processed "
          f"({initial_stats['completion_percentage']:.1f}%)")
    
    # Run scaled extraction
    results = extractor.process_corpus_batch(batch_size=500, max_workers=4)
    
    # Get final statistics
    final_stats = extractor.get_processing_statistics()
    
    print("\n📊 Extraction Complete!")
    print(f"Final state: {final_stats['total_entities']} entities (+{final_stats['total_entities'] - initial_stats['total_entities']})")
    print(f"Processed: {final_stats['processed_slokas']}/{final_stats['total_slokas']} slokas ({final_stats['completion_percentage']:.1f}%)")
    print(f"Total mentions: {final_stats['total_mentions']:,}")
    print(f"Processing time: {results['statistics']['processing_time']:.2f} seconds")
    
    return results


if __name__ == "__main__":
    run_scaled_extraction()