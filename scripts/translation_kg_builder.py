#!/usr/bin/env python3
"""
Translation-based Knowledge Graph Builder for Ramayana

This script processes English and Sanskrit translations from the data directory,
identifies entities mentioned in each sloka, and builds a comprehensive knowledge graph.
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EntityType(Enum):
    PERSON = "Person"
    PLACE = "Place"
    EVENT = "Event"
    OBJECT = "Object"
    CONCEPT = "Concept"

@dataclass
class KGEntity:
    kg_id: str
    entity_type: EntityType
    labels: Dict[str, str]
    properties: Dict[str, Any] = field(default_factory=dict)
    mentions: List[Tuple[str, int, int]] = field(default_factory=list)  # (text_unit_id, start, end)

@dataclass
class KGRelationship:
    subject_id: str
    predicate: str
    object_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class TranslationKGBuilder:
    """Builds knowledge graph from translation texts in the data directory"""
    
    def __init__(self, data_path: str = "data", db_path: str = "ramayanam.db"):
        self.data_path = Path(data_path)
        self.db_path = db_path
        self.entities: Dict[str, KGEntity] = {}
        self.relationships: List[KGRelationship] = []
        
        # Initialize entity patterns for both English and Sanskrit
        self.entity_patterns = self._define_entity_patterns()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with KG tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Read and execute the KG table creation script
        script_path = Path("scripts/add_kg_tables.sql")
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
                cursor.executescript(script)
        else:
            # Create tables inline if script not found
            self._create_kg_tables(cursor)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized with KG tables")
    
    def _create_kg_tables(self, cursor):
        """Create KG tables if script file not available"""
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS kg_entities (
            kg_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            labels TEXT NOT NULL,
            properties TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS kg_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object_id TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES kg_entities(kg_id),
            FOREIGN KEY (object_id) REFERENCES kg_entities(kg_id)
        );
        
        CREATE TABLE IF NOT EXISTS text_entity_mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_unit_id TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            span_start INTEGER NOT NULL,
            span_end INTEGER NOT NULL,
            confidence REAL DEFAULT 1.0,
            source_type TEXT DEFAULT 'automated',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES kg_entities(kg_id)
        );
        """)
    
    def _define_entity_patterns(self) -> Dict[EntityType, List[Dict[str, Any]]]:
        """Define comprehensive patterns for entity recognition in translations"""
        return {
            EntityType.PERSON: [
                # Core characters
                {"pattern": r"\b(Rama|Lord Rama|Shri Rama|राम|रामः|राघव|दाशरथि)\b", "canonical": "rama", "epithets": ["राघव", "दाशरथि", "कोसलेन्द्र"]},
                {"pattern": r"\b(Sita|Seetha|Janaki|सीता|सीतः|जानकी|मैथिली|वैदेही)\b", "canonical": "sita", "epithets": ["जानकी", "मैथिली", "वैदेही"]},
                {"pattern": r"\b(Hanuman|Anjaneya|हनुमान्|हनुमत्|आञ्जनेय|पवनात्मज|मारुति)\b", "canonical": "hanuman", "epithets": ["आञ्जनेय", "पवनात्मज", "मारुति"]},
                {"pattern": r"\b(Lakshmana|Lakshman|लक्ष्मण|लक्ष्मणः|सौमित्रि)\b", "canonical": "lakshmana", "epithets": ["सौमित्रि"]},
                {"pattern": r"\b(Bharata|Bharat|भरत|भरतः)\b", "canonical": "bharata", "epithets": []},
                {"pattern": r"\b(Shatrughna|Satrughna|शत्रुघ्न|शत्रुघ्नः)\b", "canonical": "shatrughna", "epithets": []},
                {"pattern": r"\b(Dasharatha|Dasaratha|दशरथ|दशरथः)\b", "canonical": "dasharatha", "epithets": []},
                {"pattern": r"\b(Kaushalya|Kausalya|कौशल्या)\b", "canonical": "kaushalya", "epithets": []},
                {"pattern": r"\b(Kaikeyi|कैकेयी)\b", "canonical": "kaikeyi", "epithets": []},
                {"pattern": r"\b(Sumitra|सुमित्रा)\b", "canonical": "sumitra", "epithets": []},
                {"pattern": r"\b(Ravana|Ravan|रावण|रावणः|दशानन|लङ्केश)\b", "canonical": "ravana", "epithets": ["दशानन", "लङ्केश"]},
                {"pattern": r"\b(Vibhishana|Vibhishan|विभीषण|विभीषणः)\b", "canonical": "vibhishana", "epithets": []},
                {"pattern": r"\b(Sugriva|Sugreeva|सुग्रीव|सुग्रीवः)\b", "canonical": "sugriva", "epithets": []},
                {"pattern": r"\b(Vali|Bali|वाली|बली)\b", "canonical": "vali", "epithets": []},
                {"pattern": r"\b(Jatayu|जटायु|जटायुः)\b", "canonical": "jatayu", "epithets": []},
                {"pattern": r"\b(Sampati|सम्पाति)\b", "canonical": "sampati", "epithets": []},
                {"pattern": r"\b(Angada|अङ्गद|अङ्गदः)\b", "canonical": "angada", "epithets": []},
                {"pattern": r"\b(Jambavan|Jambavant|जाम्बवान्|जाम्बवत्)\b", "canonical": "jambavan", "epithets": []},
                {"pattern": r"\b(Surpanakha|शूर्पणखा)\b", "canonical": "surpanakha", "epithets": []},
                {"pattern": r"\b(Khara|खर|खरः)\b", "canonical": "khara", "epithets": []},
                {"pattern": r"\b(Dushana|दूषण|दूषणः)\b", "canonical": "dushana", "epithets": []},
                {"pattern": r"\b(Trijata|त्रिजटा)\b", "canonical": "trijata", "epithets": []},
                {"pattern": r"\b(Mandodari|मन्दोदरी)\b", "canonical": "mandodari", "epithets": []},
            ],
            
            EntityType.PLACE: [
                {"pattern": r"\b(Ayodhya|Ayodhya|अयोध्या)\b", "canonical": "ayodhya", "type": "city"},
                {"pattern": r"\b(Lanka|Lankapuri|लङ्का|लङ्कापुरी)\b", "canonical": "lanka", "type": "city"},
                {"pattern": r"\b(Mithila|मिथिला)\b", "canonical": "mithila", "type": "city"},
                {"pattern": r"\b(Kishkindha|Kishkindhya|किष्किन्धा)\b", "canonical": "kishkindha", "type": "city"},
                {"pattern": r"\b(Dandaka|Dandakaranya|दण्डक|दण्डकारण्य)\b", "canonical": "dandaka", "type": "forest"},
                {"pattern": r"\b(Chitrakuta|Chitrakoot|चित्रकूट)\b", "canonical": "chitrakuta", "type": "mountain"},
                {"pattern": r"\b(Panchavati|पञ्चवटी)\b", "canonical": "panchavati", "type": "hermitage"},
                {"pattern": r"\b(Rishyamukha|ऋष्यमूक)\b", "canonical": "rishyamukha", "type": "mountain"},
                {"pattern": r"\b(Vindhya|विन्ध्य)\b", "canonical": "vindhya", "type": "mountain"},
                {"pattern": r"\b(Godavari|गोदावरी)\b", "canonical": "godavari", "type": "river"},
                {"pattern": r"\b(Ganga|Ganges|गङ्गा)\b", "canonical": "ganga", "type": "river"},
                {"pattern": r"\b(Sarayu|सरयू)\b", "canonical": "sarayu", "type": "river"},
                {"pattern": r"\b(Kosala|कोसल)\b", "canonical": "kosala", "type": "kingdom"},
                {"pattern": r"\b(Ashoka Vatika|अशोक वाटिका)\b", "canonical": "ashoka_vatika", "type": "garden"},
            ],
            
            EntityType.OBJECT: [
                {"pattern": r"\b(bow|धनुष|धनुः|Shiva's bow|शिव धनुष)\b", "canonical": "bow", "significance": "divine_weapon"},
                {"pattern": r"\b(chariot|रथ|रथः)\b", "canonical": "chariot", "significance": "vehicle"},
                {"pattern": r"\b(crown|मुकुट|किरीट)\b", "canonical": "crown", "significance": "royal_insignia"},
                {"pattern": r"\b(ring|अङ्गुलीयक|मुद्रिका)\b", "canonical": "ring", "significance": "token"},
                {"pattern": r"\b(arrow|बाण|शर|इषु)\b", "canonical": "arrow", "significance": "weapon"},
                {"pattern": r"\b(sword|खड्ग|असि)\b", "canonical": "sword", "significance": "weapon"},
                {"pattern": r"\b(mace|गदा)\b", "canonical": "mace", "significance": "weapon"},
                {"pattern": r"\b(ornament|आभूषण|अलङ्कार)\b", "canonical": "ornament", "significance": "decoration"},
            ],
            
            EntityType.CONCEPT: [
                {"pattern": r"\b(dharma|righteousness|धर्म|धर्मः)\b", "canonical": "dharma", "category": "ethics"},
                {"pattern": r"\b(karma|action|कर्म|कर्मन्)\b", "canonical": "karma", "category": "action"},
                {"pattern": r"\b(devotion|भक्ति|भक्तिः)\b", "canonical": "devotion", "category": "spiritual"},
                {"pattern": r"\b(duty|कर्तव्य)\b", "canonical": "duty", "category": "ethics"},
                {"pattern": r"\b(exile|वनवास|अरण्यवास)\b", "canonical": "exile", "category": "circumstance"},
                {"pattern": r"\b(sacrifice|यज्ञ|यागः)\b", "canonical": "sacrifice", "category": "ritual"},
                {"pattern": r"\b(meditation|ध्यान|समाधि)\b", "canonical": "meditation", "category": "spiritual"},
                {"pattern": r"\b(knowledge|ज्ञान|विद्या)\b", "canonical": "knowledge", "category": "wisdom"},
                {"pattern": r"\b(truth|सत्य|सत्यम्)\b", "canonical": "truth", "category": "virtue"},
                {"pattern": r"\b(compassion|करुणा|दया)\b", "canonical": "compassion", "category": "virtue"},
            ],
            
            EntityType.EVENT: [
                {"pattern": r"\b(coronation|राज्याभिषेक|पट्टाभिषेक)\b", "canonical": "coronation", "type": "ceremony"},
                {"pattern": r"\b(exile|वनवास|प्रवास)\b", "canonical": "exile", "type": "journey"},
                {"pattern": r"\b(abduction|हरण|अपहरण)\b", "canonical": "abduction", "type": "conflict"},
                {"pattern": r"\b(war|युद्ध|संग्राम|रण)\b", "canonical": "war", "type": "conflict"},
                {"pattern": r"\b(marriage|विवाह|पाणिग्रहण)\b", "canonical": "marriage", "type": "ceremony"},
                {"pattern": r"\b(swayamvara|स्वयंवर)\b", "canonical": "swayamvara", "type": "ceremony"},
                {"pattern": r"\b(funeral|अन्त्येष्टि|दाह)\b", "canonical": "funeral", "type": "ceremony"},
                {"pattern": r"\b(sacrifice|यज्ञ|होम)\b", "canonical": "sacrifice", "type": "ritual"},
                {"pattern": r"\b(blessing|आशीर्वाद|वरदान)\b", "canonical": "blessing", "type": "divine_act"},
                {"pattern": r"\b(curse|शाप|श्राप)\b", "canonical": "curse", "type": "divine_act"},
            ]
        }
    
    def extract_entities_from_text(self, text: str, text_unit_id: str) -> List[KGEntity]:
        """Extract entities from a single text passage"""
        found_entities = []
        text_lower = text.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                canonical = pattern_info["canonical"]
                
                # Find all matches
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    start, end = match.span()
                    matched_text = match.group()
                    
                    # Create entity ID
                    entity_id = f"http://ramayanam.hanuma.com/entity/{canonical}"
                    
                    # Check if entity already exists
                    if entity_id in self.entities:
                        entity = self.entities[entity_id]
                        entity.mentions.append((text_unit_id, start, end))
                    else:
                        # Create new entity
                        labels = {"en": canonical.replace("_", " ").title()}
                        
                        # Add Sanskrit label if available in pattern
                        properties = {}
                        for key, value in pattern_info.items():
                            if key not in ["pattern", "canonical"]:
                                properties[key] = value
                        
                        entity = KGEntity(
                            kg_id=entity_id,
                            entity_type=entity_type,
                            labels=labels,
                            properties=properties,
                            mentions=[(text_unit_id, start, end)]
                        )
                        
                        self.entities[entity_id] = entity
                        found_entities.append(entity)
        
        return found_entities
    
    def process_translation_files(self) -> Dict[str, Any]:
        """Process all translation files in the data directory"""
        results = {
            "processed_files": 0,
            "total_slokas": 0,
            "entities_found": 0,
            "error_files": []
        }
        
        # Look for translation files - updated for actual data structure
        base_path = self.data_path / "slokas" / "Slokas"
        
        if not base_path.exists():
            logger.error(f"Data path does not exist: {base_path}")
            return results
                
        logger.info(f"Processing translations from: {base_path}")
        
        # Process each kanda directory
        for kanda_dir in base_path.iterdir():
            if not kanda_dir.is_dir():
                continue
            
            kanda_name = kanda_dir.name
            logger.info(f"Processing Kanda: {kanda_name}")
            
            # Group files by sarga
            sarga_files = {}
            for file_path in kanda_dir.iterdir():
                if not file_path.is_file() or not file_path.name.endswith('.txt'):
                    continue
                
                # Parse filename: KandaName_sarga_X_type.txt
                parts = file_path.stem.split('_')
                if len(parts) >= 4 and parts[1] == 'sarga':
                    sarga_num = parts[2]
                    file_type = parts[3]  # meaning, sloka, translation
                    
                    if sarga_num not in sarga_files:
                        sarga_files[sarga_num] = {}
                    sarga_files[sarga_num][file_type] = file_path
            
            # Process each sarga
            for sarga_num, files in sarga_files.items():
                try:
                    results["processed_files"] += 1
                    sloka_count = 0
                    
                    # Process each file type for this sarga
                    for file_type, file_path in files.items():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read().strip()
                            
                            if not content:
                                continue
                            
                            # Split content into individual slokas/verses
                            # Content is typically separated by double newlines or sloka numbers
                            verses = re.split(r'\n\s*\n|(?=\d+\.)', content)
                            
                            for i, verse in enumerate(verses):
                                if not verse.strip():
                                    continue
                                
                                sloka_count += 1
                                # Generate text unit ID
                                sloka_id = f"{kanda_name}.{sarga_num}.{i+1}"
                                
                                # Extract entities from the verse text
                                entities = self.extract_entities_from_text(verse.strip(), sloka_id)
                                results["entities_found"] += len(entities)
                                
                                # Log sample findings for debugging
                                if entities and len(entities) > 0:
                                    logger.debug(f"Found {len(entities)} entities in {sloka_id}: {[e.labels['en'] for e in entities]}")
                        
                        except Exception as e:
                            logger.error(f"Error processing file {file_path}: {e}")
                            results["error_files"].append(str(file_path))
                    
                    results["total_slokas"] += sloka_count
                    logger.info(f"Processed sarga {sarga_num}: {sloka_count} verses, {results['entities_found']} total entities found so far")
                
                except Exception as e:
                    logger.error(f"Error processing sarga {sarga_num} in {kanda_name}: {e}")
                    results["error_files"].append(f"{kanda_name}/sarga_{sarga_num}")
        
        return results
    
    def infer_relationships(self):
        """Infer relationships between entities based on co-occurrence and semantic rules"""
        logger.info("Inferring relationships between entities...")
        
        # Relationship inference rules
        relationship_rules = [
            # Family relationships
            {"subjects": ["rama", "bharata", "lakshmana", "shatrughna"], "predicate": "hasSibling"},
            {"subject": "rama", "predicate": "hasSpouse", "object": "sita"},
            {"subject": "dasharatha", "predicate": "hasChild", "objects": ["rama", "bharata", "lakshmana", "shatrughna"]},
            {"subject": "kaushalya", "predicate": "hasChild", "object": "rama"},
            {"subject": "kaikeyi", "predicate": "hasChild", "object": "bharata"},
            {"subject": "sumitra", "predicate": "hasChild", "objects": ["lakshmana", "shatrughna"]},
            
            # Devotional relationships
            {"subject": "hanuman", "predicate": "devoteeOf", "object": "rama"},
            {"subject": "jambavan", "predicate": "devoteeOf", "object": "rama"},
            {"subject": "angada", "predicate": "devoteeOf", "object": "rama"},
            {"subject": "vibhishana", "predicate": "devoteeOf", "object": "rama"},
            
            # Ruling relationships
            {"subject": "dasharatha", "predicate": "rules", "object": "ayodhya"},
            {"subject": "rama", "predicate": "rules", "object": "ayodhya"},
            {"subject": "ravana", "predicate": "rules", "object": "lanka"},
            {"subject": "sugriva", "predicate": "rules", "object": "kishkindha"},
            
            # Conceptual embodiment
            {"subject": "rama", "predicate": "embodies", "objects": ["dharma", "truth", "duty"]},
            {"subject": "sita", "predicate": "embodies", "objects": ["devotion", "dharma"]},
            {"subject": "hanuman", "predicate": "embodies", "objects": ["devotion", "duty"]},
            {"subject": "ravana", "predicate": "opposes", "object": "dharma"},
        ]
        
        # Apply relationship rules
        for rule in relationship_rules:
            subject_canonical = rule.get("subject")
            subjects_canonical = rule.get("subjects", [])
            predicate = rule["predicate"]
            object_canonical = rule.get("object")
            objects_canonical = rule.get("objects", [])
            
            # Handle single subject rules
            if subject_canonical:
                subject_id = f"http://ramayanam.hanuma.com/entity/{subject_canonical}"
                if subject_id in self.entities:
                    
                    # Single object
                    if object_canonical:
                        object_id = f"http://ramayanam.hanuma.com/entity/{object_canonical}"
                        if object_id in self.entities:
                            self.relationships.append(KGRelationship(
                                subject_id=subject_id,
                                predicate=predicate,
                                object_id=object_id,
                                metadata={"confidence": 0.95, "source": "rule_inference"}
                            ))
                    
                    # Multiple objects
                    for obj_canonical in objects_canonical:
                        object_id = f"http://ramayanam.hanuma.com/entity/{obj_canonical}"
                        if object_id in self.entities:
                            self.relationships.append(KGRelationship(
                                subject_id=subject_id,
                                predicate=predicate,
                                object_id=object_id,
                                metadata={"confidence": 0.95, "source": "rule_inference"}
                            ))
            
            # Handle multiple subject rules (e.g., siblings)
            if subjects_canonical and predicate == "hasSibling":
                for i, subj1 in enumerate(subjects_canonical):
                    for j, subj2 in enumerate(subjects_canonical):
                        if i != j:
                            subj1_id = f"http://ramayanam.hanuma.com/entity/{subj1}"
                            subj2_id = f"http://ramayanam.hanuma.com/entity/{subj2}"
                            if subj1_id in self.entities and subj2_id in self.entities:
                                self.relationships.append(KGRelationship(
                                    subject_id=subj1_id,
                                    predicate=predicate,
                                    object_id=subj2_id,
                                    metadata={"confidence": 0.95, "source": "rule_inference"}
                                ))
        
        logger.info(f"Inferred {len(self.relationships)} relationships")
    
    def save_to_database(self):
        """Save entities and relationships to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM text_entity_mentions")
        cursor.execute("DELETE FROM kg_relationships") 
        cursor.execute("DELETE FROM kg_entities")
        
        # Insert entities
        for entity in self.entities.values():
            cursor.execute("""
                INSERT INTO kg_entities (kg_id, entity_type, labels, properties)
                VALUES (?, ?, ?, ?)
            """, (
                entity.kg_id,
                entity.entity_type.value,
                json.dumps(entity.labels),
                json.dumps(entity.properties)
            ))
            
            # Insert mentions
            for text_unit_id, start, end in entity.mentions:
                cursor.execute("""
                    INSERT INTO text_entity_mentions 
                    (text_unit_id, entity_id, span_start, span_end, confidence, source_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (text_unit_id, entity.kg_id, start, end, 0.9, 'automated'))
        
        # Insert relationships
        for rel in self.relationships:
            cursor.execute("""
                INSERT INTO kg_relationships (subject_id, predicate, object_id, metadata)
                VALUES (?, ?, ?, ?)
            """, (rel.subject_id, rel.predicate, rel.object_id, json.dumps(rel.metadata)))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(self.entities)} entities and {len(self.relationships)} relationships to database")
    
    def build_knowledge_graph(self) -> Dict[str, Any]:
        """Main method to build the complete knowledge graph"""
        logger.info("Starting knowledge graph construction from translations...")
        
        # Process translation files
        processing_results = self.process_translation_files()
        
        # Infer relationships
        self.infer_relationships()
        
        # Save to database
        self.save_to_database()
        
        # Return summary
        return {
            "success": True,
            "summary": {
                "files_processed": processing_results["processed_files"],
                "slokas_processed": processing_results["total_slokas"],
                "entities_extracted": len(self.entities),
                "relationships_inferred": len(self.relationships),
                "error_files": processing_results["error_files"]
            },
            "entities": {eid: {"type": e.entity_type.value, "labels": e.labels, "mention_count": len(e.mentions)} 
                       for eid, e in self.entities.items()},
            "top_entities": sorted(
                [(eid, len(e.mentions)) for eid, e in self.entities.items()], 
                key=lambda x: x[1], reverse=True
            )[:10]
        }

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Knowledge Graph from Ramayana translations")
    parser.add_argument("--data-path", default="data", help="Path to data directory")
    parser.add_argument("--db-path", default="ramayanam.db", help="Path to database file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Build knowledge graph
    builder = TranslationKGBuilder(args.data_path, args.db_path)
    results = builder.build_knowledge_graph()
    
    # Print results
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    exit(main())