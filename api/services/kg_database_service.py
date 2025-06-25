"""
Knowledge Graph Database Service

This service handles storing and retrieving entities from the database,
integrating the automated extraction with the existing SQLite database.
"""

import json
import sqlite3
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from api.models.kg_models import KGEntity, KGRelationship, EntityType, SemanticAnnotation
from api.services.automated_entity_extraction import RamayanaEntityExtractor


class KGDatabaseService:
    """Service for managing knowledge graph data in SQLite database"""
    
    def __init__(self, db_path: str = "data/db/ramayanam.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def store_extraction_results(self, extraction_results: Dict[str, Any]) -> Dict[str, int]:
        """Store automated extraction results in database"""
        self.logger.info("Storing extraction results in database")
        
        entities = extraction_results.get('entities', {})
        relationships = extraction_results.get('relationships', [])
        annotations = extraction_results.get('annotations', [])
        
        stats = {
            'entities_stored': 0,
            'relationships_stored': 0,
            'annotations_stored': 0
        }
        
        with self.get_connection() as conn:
            # Store entities
            for entity_id, entity in entities.items():
                self._store_entity(conn, entity)
                stats['entities_stored'] += 1
            
            # Store relationships
            for relationship in relationships:
                self._store_relationship(conn, relationship)
                stats['relationships_stored'] += 1
            
            # Store annotations
            for annotation in annotations:
                self._store_annotation(conn, annotation)
                stats['annotations_stored'] += 1
            
            conn.commit()
        
        self.logger.info(f"Stored: {stats}")
        return stats
    
    def _store_entity(self, conn: sqlite3.Connection, entity: KGEntity):
        """Store a single entity"""
        try:
            conn.execute("""
                INSERT OR REPLACE INTO kg_entities 
                (kg_id, entity_type, labels, properties, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                entity.kg_id,
                entity.entity_type.value,
                json.dumps(entity.labels),
                json.dumps(entity.properties)
            ))
        except Exception as e:
            self.logger.error(f"Error storing entity {entity.kg_id}: {e}")
    
    def _store_relationship(self, conn: sqlite3.Connection, relationship: KGRelationship):
        """Store a single relationship"""
        try:
            conn.execute("""
                INSERT OR REPLACE INTO kg_relationships 
                (subject_id, predicate, object_id, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                relationship.subject_id,
                relationship.predicate,
                relationship.object_id,
                json.dumps(relationship.metadata)
            ))
        except Exception as e:
            self.logger.error(f"Error storing relationship: {e}")
    
    def _store_annotation(self, conn: sqlite3.Connection, annotation: SemanticAnnotation):
        """Store a single annotation"""
        try:
            conn.execute("""
                INSERT OR REPLACE INTO text_entity_mentions 
                (text_unit_id, entity_id, span_start, span_end, confidence, source_type)
                VALUES (?, ?, ?, ?, ?, 'automated')
            """, (
                annotation.text_unit_id,
                annotation.entity_id,
                annotation.span_start,
                annotation.span_end,
                annotation.confidence
            ))
        except Exception as e:
            self.logger.error(f"Error storing annotation: {e}")
    
    def get_all_entities(self, entity_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all entities, optionally filtered by type"""
        query = "SELECT * FROM kg_entities"
        params = []
        
        if entity_type:
            query += " WHERE entity_type = ?"
            params.append(entity_type)
        
        query += " ORDER BY kg_id LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            
            entities = []
            for row in rows:
                entity = {
                    'kg_id': row['kg_id'],
                    'entity_type': row['entity_type'],
                    'labels': json.loads(row['labels']),
                    'properties': json.loads(row['properties']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                entities.append(entity)
            
            return entities
    
    def get_entity_by_id(self, kg_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific entity by ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM kg_entities WHERE kg_id = ?", 
                (kg_id,)
            ).fetchone()
            
            if not row:
                return None
            
            return {
                'kg_id': row['kg_id'],
                'entity_type': row['entity_type'],
                'labels': json.loads(row['labels']),
                'properties': json.loads(row['properties']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
    
    def get_entity_relationships(self, kg_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for an entity"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM kg_relationships 
                WHERE subject_id = ? OR object_id = ?
                ORDER BY predicate
            """, (kg_id, kg_id)).fetchall()
            
            relationships = []
            for row in rows:
                relationship = {
                    'id': row['id'],
                    'subject_id': row['subject_id'],
                    'predicate': row['predicate'],
                    'object_id': row['object_id'],
                    'metadata': json.loads(row['metadata']),
                    'created_at': row['created_at']
                }
                relationships.append(relationship)
            
            return relationships
    
    def get_entity_mentions(self, kg_id: str) -> List[Dict[str, Any]]:
        """Get all text mentions for an entity"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM text_entity_mentions 
                WHERE entity_id = ?
                ORDER BY text_unit_id
            """, (kg_id,)).fetchall()
            
            mentions = []
            for row in rows:
                mention = {
                    'id': row['id'],
                    'text_unit_id': row['text_unit_id'],
                    'entity_id': row['entity_id'],
                    'span_start': row['span_start'],
                    'span_end': row['span_end'],
                    'confidence': row['confidence'],
                    'source_type': row['source_type'],
                    'created_at': row['created_at']
                }
                mentions.append(mention)
            
            return mentions
    
    def get_entities_in_text_unit(self, text_unit_id: str) -> List[Dict[str, Any]]:
        """Get all entities mentioned in a specific text unit"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT e.*, tem.span_start, tem.span_end, tem.confidence
                FROM kg_entities e
                JOIN text_entity_mentions tem ON e.kg_id = tem.entity_id
                WHERE tem.text_unit_id = ?
                ORDER BY tem.span_start
            """, (text_unit_id,)).fetchall()
            
            entities = []
            for row in rows:
                entity = {
                    'kg_id': row['kg_id'],
                    'entity_type': row['entity_type'],
                    'labels': json.loads(row['labels']),
                    'properties': json.loads(row['properties']),
                    'mention': {
                        'span_start': row['span_start'],
                        'span_end': row['span_end'],
                        'confidence': row['confidence']
                    }
                }
                entities.append(entity)
            
            return entities
    
    def search_entities(self, query: str, entity_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search entities by name/label"""
        sql_query = """
            SELECT * FROM kg_entities 
            WHERE (labels LIKE ? OR kg_id LIKE ?)
        """
        params = [f'%{query}%', f'%{query}%']
        
        if entity_type:
            sql_query += " AND entity_type = ?"
            params.append(entity_type)
        
        sql_query += " ORDER BY kg_id LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            rows = conn.execute(sql_query, params).fetchall()
            
            entities = []
            for row in rows:
                entity = {
                    'kg_id': row['kg_id'],
                    'entity_type': row['entity_type'],
                    'labels': json.loads(row['labels']),
                    'properties': json.loads(row['properties'])
                }
                entities.append(entity)
            
            return entities
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        with self.get_connection() as conn:
            # Entity counts by type
            entity_counts = {}
            rows = conn.execute("""
                SELECT entity_type, COUNT(*) as count 
                FROM kg_entities 
                GROUP BY entity_type
            """).fetchall()
            
            for row in rows:
                entity_counts[row['entity_type']] = row['count']
            
            # Total relationships
            relationship_count = conn.execute(
                "SELECT COUNT(*) as count FROM kg_relationships"
            ).fetchone()['count']
            
            # Total mentions
            mention_count = conn.execute(
                "SELECT COUNT(*) as count FROM text_entity_mentions"
            ).fetchone()['count']
            
            # Top entities by mentions
            top_entities = conn.execute("""
                SELECT e.kg_id, e.labels, COUNT(tem.id) as mention_count
                FROM kg_entities e
                LEFT JOIN text_entity_mentions tem ON e.kg_id = tem.entity_id
                GROUP BY e.kg_id
                ORDER BY mention_count DESC
                LIMIT 10
            """).fetchall()
            
            top_entities_list = []
            for row in top_entities:
                top_entities_list.append({
                    'kg_id': row['kg_id'],
                    'labels': json.loads(row['labels']),
                    'mention_count': row['mention_count']
                })
            
            return {
                'entity_counts': entity_counts,
                'total_entities': sum(entity_counts.values()),
                'total_relationships': relationship_count,
                'total_mentions': mention_count,
                'top_entities': top_entities_list
            }


def run_automated_extraction_and_store():
    """Run the automated extraction and store results in database"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting automated extraction and database storage")
    
    # Run extraction
    extractor = RamayanaEntityExtractor()
    results = extractor.extract_entities_from_corpus()
    
    # Store in database
    db_service = KGDatabaseService()
    stats = db_service.store_extraction_results(results)
    
    # Get final statistics
    final_stats = db_service.get_statistics()
    
    logger.info("Extraction and storage complete!")
    logger.info(f"Final statistics: {final_stats}")
    
    return final_stats


if __name__ == "__main__":
    # Quick test
    db_service = KGDatabaseService()
    
    # Test basic functionality
    entities = db_service.get_all_entities(limit=5)
    print(f"Sample entities: {len(entities)}")
    
    for entity in entities:
        print(f"  {entity['kg_id']}: {entity['labels']}")
    
    # Show statistics
    stats = db_service.get_statistics()
    print(f"\nDatabase statistics: {stats}")