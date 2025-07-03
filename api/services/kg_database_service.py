"""
Knowledge Graph Database Service

This service handles storing and retrieving entities from the database,
integrating the automated extraction with the existing SQLite database.
"""

import json
import sqlite3
import logging
import uuid
from datetime import datetime
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
            # Extract validation status and confidence from properties
            properties = entity.properties or {}
            validation_status = properties.get('validation_status', 'pending')
            extraction_method = properties.get('extraction_method', 'automated')
            extraction_confidence = properties.get('confidence_score', 0.7)
            
            conn.execute("""
                INSERT OR REPLACE INTO kg_entities 
                (kg_id, entity_type, labels, properties, validation_status, 
                 extraction_method, extraction_confidence, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                entity.kg_id,
                entity.entity_type.value,
                json.dumps(entity.labels),
                json.dumps(entity.properties),
                validation_status,
                extraction_method,
                extraction_confidence
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
    
    # === Entity Discovery Methods ===
    
    def start_discovery_session(self, settings: Dict[str, Any]) -> str:
        """Start a new entity discovery session"""
        session_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO entity_discovery_sessions 
                (session_id, status, settings, total_slokas)
                VALUES (?, 'running', ?, ?)
            """, (
                session_id,
                json.dumps(settings),
                settings.get('total_slokas', 24000)
            ))
            conn.commit()
        
        self.logger.info(f"Started discovery session: {session_id}")
        return session_id
    
    def update_discovery_progress(self, session_id: str, progress_data: Dict[str, Any]):
        """Update discovery session progress"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE entity_discovery_sessions 
                SET progress_data = ?, 
                    processed_slokas = ?,
                    entities_found = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (
                json.dumps(progress_data),
                progress_data.get('processed_slokas', 0),
                progress_data.get('entities_found', 0),
                session_id
            ))
            conn.commit()
    
    def complete_discovery_session(self, session_id: str, status: str = 'completed'):
        """Mark discovery session as completed"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE entity_discovery_sessions 
                SET status = ?, end_time = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (status, session_id))
            conn.commit()
    
    def get_discovery_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get discovery session details"""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM entity_discovery_sessions 
                WHERE session_id = ?
            """, (session_id,)).fetchone()
            
            if not row:
                return None
            
            return {
                'session_id': row['session_id'],
                'status': row['status'],
                'settings': json.loads(row['settings']),
                'progress_data': json.loads(row['progress_data']),
                'total_slokas': row['total_slokas'],
                'processed_slokas': row['processed_slokas'],
                'entities_found': row['entities_found'],
                'start_time': row['start_time'],
                'end_time': row['end_time']
            }
    
    def get_pending_entities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get entities pending validation"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT e.*, COUNT(tem.id) as mention_count
                FROM kg_entities e
                LEFT JOIN text_entity_mentions tem ON e.kg_id = tem.entity_id
                WHERE e.validation_status = 'pending'
                GROUP BY e.kg_id
                ORDER BY e.extraction_confidence DESC, mention_count DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            entities = []
            for row in rows:
                # Get source references for this entity
                source_refs = self._get_entity_source_references(row['kg_id'])
                
                entity = {
                    'id': row['kg_id'],
                    'text': self._extract_original_text(row['labels']),
                    'normalizedForm': self._extract_english_name(row['labels']),
                    'type': row['entity_type'],
                    'confidence': row['extraction_confidence'] or 0.0,
                    'sourceReferences': source_refs,
                    'extractionMethod': row['extraction_method'] or 'automated',
                    'validationStatus': row['validation_status'],
                    'epithets': json.loads(row['properties']).get('epithets', []),
                    'alternativeNames': []
                }
                entities.append(entity)
            
            return entities
    
    def _get_entity_source_references(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get source references for an entity"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT tem.*, s.sloka, s.translation, s.meaning
                FROM text_entity_mentions tem
                LEFT JOIN slokas s ON (
                    CAST(s.kanda_id AS TEXT) || '.' || 
                    CAST(s.sarga_id AS TEXT) || '.' || 
                    CAST(s.sloka_id AS TEXT) = tem.text_unit_id
                )
                WHERE tem.entity_id = ?
                ORDER BY tem.confidence DESC
                LIMIT 5
            """, (entity_id,)).fetchall()
            
            references = []
            for row in rows:
                # Parse text_unit_id to get kanda/sarga/sloka
                parts = row['text_unit_id'].split('.')
                if len(parts) == 3:
                    kanda_id, sarga_id, sloka_id = parts
                    
                    # Get context from sloka text
                    context = row['sloka'] or row['translation'] or row['meaning'] or 'No context available'
                    if len(context) > 200:
                        context = context[:200] + '...'
                    
                    reference = {
                        'sloka_id': row['text_unit_id'],
                        'kanda': f'Kanda{kanda_id}',
                        'sarga': sarga_id,
                        'position': {
                            'start': row['span_start'],
                            'end': row['span_end']
                        },
                        'context': context
                    }
                    references.append(reference)
            
            return references
    
    def _extract_original_text(self, labels_json: str) -> str:
        """Extract original text from labels JSON"""
        try:
            labels = json.loads(labels_json)
            return labels.get('sa', labels.get('en', 'Unknown'))
        except:
            return 'Unknown'
    
    def _extract_english_name(self, labels_json: str) -> str:
        """Extract English name from labels JSON"""
        try:
            labels = json.loads(labels_json)
            return labels.get('en', 'Unknown')
        except:
            return 'Unknown'
    
    def validate_entity(self, entity_id: str, validation: Dict[str, Any], validated_by: str = 'user'):
        """Validate an entity"""
        status = validation.get('status', 'validated')
        notes = validation.get('notes', '')
        
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE kg_entities 
                SET validation_status = ?,
                    validation_notes = ?,
                    validated_by = ?,
                    validated_at = CURRENT_TIMESTAMP
                WHERE kg_id = ?
            """, (status, notes, validated_by, entity_id))
            
            # Update related mentions
            conn.execute("""
                UPDATE text_entity_mentions 
                SET validation_status = ?
                WHERE entity_id = ?
            """, (status, entity_id))
            
            conn.commit()
        
        self.logger.info(f"Entity {entity_id} validated with status: {status}")
    
    def create_entity_conflict(self, conflict_type: str, description: str, 
                             entity_ids: List[str], suggested_resolution: str = '') -> str:
        """Create a new entity conflict"""
        conflict_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO entity_conflicts 
                (id, conflict_type, description, entity_ids, suggested_resolution)
                VALUES (?, ?, ?, ?, ?)
            """, (
                conflict_id,
                conflict_type,
                description,
                json.dumps(entity_ids),
                suggested_resolution
            ))
            conn.commit()
        
        return conflict_id
    
    def get_entity_conflicts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get unresolved entity conflicts"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM entity_conflicts 
                WHERE status = 'pending'
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            conflicts = []
            for row in rows:
                entity_ids = json.loads(row['entity_ids'])
                entities = []
                
                # Get entity details for each ID
                for entity_id in entity_ids:
                    entity = self.get_entity_by_id(entity_id)
                    if entity:
                        entities.append({
                            'id': entity['kg_id'],
                            'normalizedForm': self._extract_english_name(entity['labels'])
                        })
                
                conflict = {
                    'id': row['id'],
                    'type': row['conflict_type'],
                    'description': row['description'],
                    'entities': entities,
                    'suggestedResolution': row['suggested_resolution']
                }
                conflicts.append(conflict)
            
            return conflicts
    
    def resolve_entity_conflict(self, conflict_id: str, resolution: Dict[str, Any], resolved_by: str = 'user'):
        """Resolve an entity conflict"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE entity_conflicts 
                SET status = 'resolved',
                    resolution_action = ?,
                    resolved_by = ?,
                    resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(resolution), resolved_by, conflict_id))
            conn.commit()
        
        self.logger.info(f"Conflict {conflict_id} resolved with action: {resolution.get('action')}")
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced statistics for Entity Discovery dashboard"""
        with self.get_connection() as conn:
            # Entity type counts by validation status
            entity_type_stats = {}
            rows = conn.execute("""
                SELECT entity_type, validation_status, COUNT(*) as count
                FROM kg_entities
                GROUP BY entity_type, validation_status
            """).fetchall()
            
            entity_counts = {}
            for row in rows:
                entity_type = row['entity_type']
                if entity_type not in entity_counts:
                    entity_counts[entity_type] = 0
                entity_counts[entity_type] += row['count']
            
            # Confidence distribution
            confidence_rows = conn.execute("""
                SELECT 
                    CASE 
                        WHEN extraction_confidence >= 0.9 THEN '90-100%'
                        WHEN extraction_confidence >= 0.8 THEN '80-89%'
                        WHEN extraction_confidence >= 0.7 THEN '70-79%'
                        WHEN extraction_confidence >= 0.6 THEN '60-69%'
                        ELSE '0-59%'
                    END as confidence_range,
                    COUNT(*) as count
                FROM kg_entities
                WHERE extraction_confidence > 0
                GROUP BY confidence_range
            """).fetchall()
            
            confidence_dist = {}
            for row in confidence_rows:
                confidence_dist[row['confidence_range']] = row['count']
            
            # Processing stats
            avg_confidence = conn.execute("""
                SELECT AVG(extraction_confidence) as avg_conf
                FROM kg_entities
                WHERE extraction_confidence > 0
            """).fetchone()['avg_conf'] or 0.0
            
            total_entities = sum(entity_counts.values())
            total_mentions = conn.execute("""
                SELECT COUNT(*) as count FROM text_entity_mentions
            """).fetchone()['count']
            
            # Recent activity (mock for now)
            recent_activity = [
                {
                    'type': 'discovery',
                    'message': f'Discovered {total_entities} entities from corpus',
                    'timestamp': '1 hour ago'
                },
                {
                    'type': 'validation', 
                    'message': 'Entity validation workflow initialized',
                    'timestamp': '2 hours ago'
                }
            ]
            
            return {
                'entityTypeCounts': entity_counts,
                'confidenceDistribution': confidence_dist,
                'processingStats': {
                    'totalProcessingTime': 30.0,  # minutes
                    'averageConfidence': avg_confidence,
                    'patternsMatched': total_mentions,
                    'uniqueEntitiesFound': total_entities
                },
                'recentActivity': recent_activity
            }
    
    def get_discovery_status(self) -> Dict[str, Any]:
        """Get current discovery status"""
        with self.get_connection() as conn:
            # Get latest session
            session_row = conn.execute("""
                SELECT * FROM entity_discovery_sessions 
                ORDER BY created_at DESC LIMIT 1
            """).fetchone()
            
            if not session_row:
                return {
                    'is_running': False,
                    'current_session': None,
                    'last_run': None
                }
            
            session = dict(session_row)
            
            return {
                'is_running': session['status'] == 'running',
                'current_session': session,
                'last_run': session['created_at'] if session['status'] != 'running' else None
            }
    
    def get_discovery_metrics(self) -> Dict[str, Any]:
        """Get discovery metrics for dashboard"""
        with self.get_connection() as conn:
            # Entity counts by validation status
            validation_stats = {}
            rows = conn.execute("""
                SELECT validation_status, COUNT(*) as count 
                FROM kg_entities 
                GROUP BY validation_status
            """).fetchall()
            
            for row in rows:
                validation_stats[row['validation_status']] = row['count']
            
            # Entity counts by type
            type_stats = {}
            rows = conn.execute("""
                SELECT entity_type, COUNT(*) as count 
                FROM kg_entities 
                GROUP BY entity_type
            """).fetchall()
            
            for row in rows:
                type_stats[row['entity_type']] = row['count']
            
            # Recent discovery sessions
            recent_sessions = conn.execute("""
                SELECT * FROM entity_discovery_sessions 
                ORDER BY created_at DESC LIMIT 5
            """).fetchall()
            
            return {
                'validation_stats': validation_stats,
                'type_stats': type_stats,
                'recent_sessions': [dict(row) for row in recent_sessions],
                'total_entities': sum(validation_stats.values()),
                'pending_validation': validation_stats.get('pending', 0)
            }
    
    def bulk_validate_entities(self, entity_ids: List[str], action: str, validated_by: str) -> Dict[str, Any]:
        """Bulk validate or reject entities"""
        if action not in ['approve', 'reject']:
            raise ValueError("Action must be 'approve' or 'reject'")
        
        status = 'validated' if action == 'approve' else 'rejected'
        
        with self.get_connection() as conn:
            # Update entities
            placeholders = ','.join(['?' for _ in entity_ids])
            conn.execute(f"""
                UPDATE kg_entities 
                SET validation_status = ?,
                    validated_by = ?,
                    validated_at = CURRENT_TIMESTAMP
                WHERE kg_id IN ({placeholders})
            """, [status, validated_by] + entity_ids)
            
            processed = conn.rowcount
            conn.commit()
        
        self.logger.info(f"Bulk {action}: {processed} entities processed")
        
        return {
            'processed': processed,
            'action': action,
            'status': status
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