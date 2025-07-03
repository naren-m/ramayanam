"""
Bulk Validation Tools for Entity Discovery
Provides efficient tools for validating large numbers of discovered entities
"""

import sqlite3
import json
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from pathlib import Path
import csv
import time

@dataclass
class ValidationBatch:
    """A batch of entities for validation"""
    batch_id: str
    entities: List[Dict[str, Any]]
    batch_size: int
    created_at: str
    validation_criteria: Dict[str, Any]

@dataclass
class ValidationRule:
    """Rule for automatic validation"""
    rule_id: str
    rule_type: str  # 'confidence', 'occurrence', 'pattern', 'context'
    criteria: Dict[str, Any]
    action: str  # 'validate', 'reject', 'flag'
    confidence_threshold: float

@dataclass
class ValidationResult:
    """Result of validation operation"""
    entity_id: str
    action: str  # 'validated', 'rejected', 'flagged'
    confidence: float
    reason: str
    applied_rules: List[str]
    manual_review: bool = False

class BulkValidationService:
    """Service for bulk validation of discovered entities"""
    
    def __init__(self, db_path: str = "data/db/ramayanam.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Default validation rules
        self.validation_rules = self._load_default_validation_rules()
        
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _load_default_validation_rules(self) -> List[ValidationRule]:
        """Load default validation rules"""
        return [
            # High confidence + high occurrence = auto-validate
            ValidationRule(
                rule_id="high_confidence_high_occurrence",
                rule_type="combined",
                criteria={
                    "min_confidence": 0.85,
                    "min_occurrences": 10
                },
                action="validate",
                confidence_threshold=0.9
            ),
            
            # Very high confidence = auto-validate
            ValidationRule(
                rule_id="very_high_confidence",
                rule_type="confidence",
                criteria={
                    "min_confidence": 0.95
                },
                action="validate",
                confidence_threshold=0.95
            ),
            
            # Low confidence + low occurrence = auto-reject
            ValidationRule(
                rule_id="low_confidence_low_occurrence",
                rule_type="combined",
                criteria={
                    "max_confidence": 0.6,
                    "max_occurrences": 2
                },
                action="reject",
                confidence_threshold=0.3
            ),
            
            # Medium confidence = flag for manual review
            ValidationRule(
                rule_id="medium_confidence_review",
                rule_type="confidence",
                criteria={
                    "min_confidence": 0.7,
                    "max_confidence": 0.84
                },
                action="flag",
                confidence_threshold=0.75
            ),
            
            # High occurrence regardless of confidence = validate
            ValidationRule(
                rule_id="high_occurrence_validate",
                rule_type="occurrence",
                criteria={
                    "min_occurrences": 20
                },
                action="validate",
                confidence_threshold=0.8
            ),
            
            # Pattern-based validation for known entities
            ValidationRule(
                rule_id="known_entity_patterns",
                rule_type="pattern",
                criteria={
                    "known_entities": ["rama", "sita", "hanuman", "ravana", "lakshmana"]
                },
                action="validate",
                confidence_threshold=0.85
            )
        ]
    
    def get_pending_entities(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get entities pending validation"""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    kg_id,
                    entity_type,
                    labels,
                    properties,
                    extraction_confidence,
                    created_at,
                    (SELECT COUNT(*) FROM text_entity_mentions tem 
                     WHERE tem.entity_id = REPLACE(kg_entities.kg_id, 'http://ramayanam.hanuma.com/entity/', '')) as mention_count
                FROM kg_entities 
                WHERE JSON_EXTRACT(properties, '$.validation_status') = 'pending'
                ORDER BY extraction_confidence DESC, mention_count DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            rows = conn.execute(query).fetchall()
            
            entities = []
            for row in rows:
                entity = {
                    'entity_id': row['kg_id'].split('/')[-1],
                    'kg_id': row['kg_id'],
                    'entity_type': row['entity_type'],
                    'labels': json.loads(row['labels']),
                    'properties': json.loads(row['properties']),
                    'extraction_confidence': row['extraction_confidence'],
                    'mention_count': row['mention_count'],
                    'created_at': row['created_at']
                }
                entities.append(entity)
            
            return entities
    
    def create_validation_batch(self, batch_size: int = 100, 
                              criteria: Optional[Dict[str, Any]] = None) -> ValidationBatch:
        """Create a batch of entities for validation"""
        entities = self.get_pending_entities(limit=batch_size)
        
        batch_id = f"batch_{int(time.time())}"
        
        return ValidationBatch(
            batch_id=batch_id,
            entities=entities,
            batch_size=len(entities),
            created_at=time.strftime('%Y-%m-%d %H:%M:%S'),
            validation_criteria=criteria or {}
        )
    
    def apply_validation_rules(self, entities: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Apply validation rules to a list of entities"""
        results = []
        
        for entity in entities:
            result = self._validate_single_entity(entity)
            results.append(result)
        
        return results
    
    def _validate_single_entity(self, entity: Dict[str, Any]) -> ValidationResult:
        """Validate a single entity against all rules"""
        entity_id = entity['entity_id']
        applied_rules = []
        best_action = "flag"  # Default to manual review
        best_confidence = 0.5
        best_reason = "No rules matched"
        
        # Extract key metrics
        confidence = entity.get('extraction_confidence', 0.0)
        occurrences = entity.get('mention_count', 0)
        
        # Apply each rule
        for rule in self.validation_rules:
            if self._rule_matches_entity(rule, entity):
                applied_rules.append(rule.rule_id)
                
                # Use the rule with highest confidence
                if rule.confidence_threshold > best_confidence:
                    best_action = rule.action
                    best_confidence = rule.confidence_threshold
                    best_reason = f"Rule: {rule.rule_id}"
        
        # Determine if manual review is needed
        manual_review = (
            best_action == "flag" or 
            (best_action == "validate" and best_confidence < 0.8) or
            (best_action == "reject" and best_confidence < 0.7)
        )
        
        return ValidationResult(
            entity_id=entity_id,
            action=best_action,
            confidence=best_confidence,
            reason=best_reason,
            applied_rules=applied_rules,
            manual_review=manual_review
        )
    
    def _rule_matches_entity(self, rule: ValidationRule, entity: Dict[str, Any]) -> bool:
        """Check if a validation rule matches an entity"""
        confidence = entity.get('extraction_confidence', 0.0)
        occurrences = entity.get('mention_count', 0)
        entity_id = entity['entity_id']
        
        if rule.rule_type == "confidence":
            min_conf = rule.criteria.get('min_confidence', 0.0)
            max_conf = rule.criteria.get('max_confidence', 1.0)
            return min_conf <= confidence <= max_conf
        
        elif rule.rule_type == "occurrence":
            min_occ = rule.criteria.get('min_occurrences', 0)
            max_occ = rule.criteria.get('max_occurrences', float('inf'))
            return min_occ <= occurrences <= max_occ
        
        elif rule.rule_type == "combined":
            # Both confidence and occurrence criteria must match
            conf_match = True
            occ_match = True
            
            if 'min_confidence' in rule.criteria:
                conf_match = confidence >= rule.criteria['min_confidence']
            if 'max_confidence' in rule.criteria:
                conf_match = conf_match and confidence <= rule.criteria['max_confidence']
            
            if 'min_occurrences' in rule.criteria:
                occ_match = occurrences >= rule.criteria['min_occurrences']
            if 'max_occurrences' in rule.criteria:
                occ_match = occ_match and occurrences <= rule.criteria['max_occurrences']
            
            return conf_match and occ_match
        
        elif rule.rule_type == "pattern":
            known_entities = rule.criteria.get('known_entities', [])
            return entity_id in known_entities
        
        return False
    
    def execute_bulk_validation(self, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Execute bulk validation results"""
        stats = {
            'validated': 0,
            'rejected': 0,
            'flagged': 0,
            'manual_review': 0,
            'errors': 0
        }
        
        with self.get_connection() as conn:
            for result in validation_results:
                try:
                    # Update entity validation status
                    kg_id = f"http://ramayanam.hanuma.com/entity/{result.entity_id}"
                    
                    # Get current properties
                    row = conn.execute(
                        "SELECT properties FROM kg_entities WHERE kg_id = ?", 
                        (kg_id,)
                    ).fetchone()
                    
                    if row:
                        properties = json.loads(row['properties'])
                        
                        # Update validation status
                        if result.action == "validate":
                            properties['validation_status'] = 'validated'
                            stats['validated'] += 1
                        elif result.action == "reject":
                            properties['validation_status'] = 'rejected'
                            stats['rejected'] += 1
                        else:  # flag
                            properties['validation_status'] = 'flagged'
                            stats['flagged'] += 1
                        
                        # Add validation metadata
                        properties['validation_confidence'] = result.confidence
                        properties['validation_reason'] = result.reason
                        properties['validation_rules'] = result.applied_rules
                        properties['validation_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        if result.manual_review:
                            properties['needs_manual_review'] = True
                            stats['manual_review'] += 1
                        
                        # Update database
                        conn.execute("""
                            UPDATE kg_entities 
                            SET properties = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE kg_id = ?
                        """, (json.dumps(properties), kg_id))
                        
                except Exception as e:
                    self.logger.error(f"Error validating entity {result.entity_id}: {e}")
                    stats['errors'] += 1
            
            conn.commit()
        
        return stats
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        with self.get_connection() as conn:
            # Overall statistics
            total_entities = conn.execute("SELECT COUNT(*) as count FROM kg_entities").fetchone()['count']
            
            # Status breakdown
            status_stats = conn.execute("""
                SELECT 
                    JSON_EXTRACT(properties, '$.validation_status') as status,
                    COUNT(*) as count
                FROM kg_entities
                GROUP BY JSON_EXTRACT(properties, '$.validation_status')
            """).fetchall()
            
            status_counts = {row['status']: row['count'] for row in status_stats}
            
            # Entities needing manual review
            manual_review_count = conn.execute("""
                SELECT COUNT(*) as count FROM kg_entities
                WHERE JSON_EXTRACT(properties, '$.needs_manual_review') = 1
            """).fetchone()['count']
            
            # Average confidence by status
            confidence_stats = conn.execute("""
                SELECT 
                    JSON_EXTRACT(properties, '$.validation_status') as status,
                    AVG(JSON_EXTRACT(properties, '$.validation_confidence')) as avg_confidence,
                    COUNT(*) as count
                FROM kg_entities
                WHERE JSON_EXTRACT(properties, '$.validation_confidence') IS NOT NULL
                GROUP BY JSON_EXTRACT(properties, '$.validation_status')
            """).fetchall()
            
            confidence_by_status = {
                row['status']: {
                    'avg_confidence': row['avg_confidence'],
                    'count': row['count']
                } for row in confidence_stats
            }
            
            return {
                'total_entities': total_entities,
                'status_counts': status_counts,
                'manual_review_needed': manual_review_count,
                'confidence_by_status': confidence_by_status,
                'completion_rate': (status_counts.get('validated', 0) + status_counts.get('rejected', 0)) / total_entities * 100
            }
    
    def export_validation_report(self, output_path: str = "exports/validation_report.csv"):
        """Export validation report to CSV"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            entities = conn.execute("""
                SELECT 
                    kg_id,
                    entity_type,
                    labels,
                    properties,
                    extraction_confidence,
                    created_at,
                    (SELECT COUNT(*) FROM text_entity_mentions tem 
                     WHERE tem.entity_id = REPLACE(kg_entities.kg_id, 'http://ramayanam.hanuma.com/entity/', '')) as mention_count
                FROM kg_entities 
                ORDER BY JSON_EXTRACT(properties, '$.validation_status'), extraction_confidence DESC
            """).fetchall()
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow([
                    'Entity ID', 'Type', 'English Name', 'Sanskrit Name',
                    'Validation Status', 'Extraction Confidence', 'Validation Confidence',
                    'Mention Count', 'Validation Reason', 'Needs Manual Review',
                    'Created At', 'Validation Timestamp'
                ])
                
                # Data rows
                for entity in entities:
                    entity_id = entity['kg_id'].split('/')[-1]
                    labels = json.loads(entity['labels'])
                    properties = json.loads(entity['properties'])
                    
                    writer.writerow([
                        entity_id,
                        entity['entity_type'],
                        labels.get('en', ''),
                        labels.get('sa', ''),
                        properties.get('validation_status', 'pending'),
                        entity['extraction_confidence'],
                        properties.get('validation_confidence', ''),
                        entity['mention_count'],
                        properties.get('validation_reason', ''),
                        properties.get('needs_manual_review', False),
                        entity['created_at'],
                        properties.get('validation_timestamp', '')
                    ])
        
        self.logger.info(f"Validation report exported to {output_path}")
        return output_path
    
    def run_bulk_validation(self, batch_size: int = 100, auto_execute: bool = True) -> Dict[str, Any]:
        """Run the complete bulk validation process"""
        self.logger.info("Starting bulk validation process")
        
        # Create validation batch
        batch = self.create_validation_batch(batch_size)
        
        if not batch.entities:
            self.logger.info("No entities pending validation")
            return {'message': 'No entities to validate'}
        
        # Apply validation rules
        validation_results = self.apply_validation_rules(batch.entities)
        
        # Execute validation if requested
        execution_stats = {}
        if auto_execute:
            execution_stats = self.execute_bulk_validation(validation_results)
        
        # Get updated statistics
        validation_stats = self.get_validation_statistics()
        
        results = {
            'batch_info': asdict(batch),
            'validation_results': [asdict(r) for r in validation_results],
            'execution_stats': execution_stats,
            'validation_stats': validation_stats
        }
        
        self.logger.info(f"Bulk validation complete: processed {len(batch.entities)} entities")
        return results

def run_bulk_validation():
    """Main function to run bulk validation"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    service = BulkValidationService()
    
    print("🔍 Starting Bulk Entity Validation")
    print("=" * 50)
    
    # Get initial statistics
    initial_stats = service.get_validation_statistics()
    print(f"Total entities: {initial_stats['total_entities']}")
    print(f"Status breakdown: {initial_stats['status_counts']}")
    
    # Run bulk validation
    results = service.run_bulk_validation(batch_size=50)
    
    if 'message' in results:
        print(results['message'])
        return results
    
    # Print results
    exec_stats = results['execution_stats']
    print(f"\n📊 Validation Results:")
    print(f"  Validated: {exec_stats['validated']}")
    print(f"  Rejected: {exec_stats['rejected']}")
    print(f"  Flagged: {exec_stats['flagged']}")
    print(f"  Manual review needed: {exec_stats['manual_review']}")
    print(f"  Errors: {exec_stats['errors']}")
    
    # Export report
    report_path = service.export_validation_report()
    print(f"\n📄 Validation report exported to: {report_path}")
    
    return results

if __name__ == "__main__":
    run_bulk_validation()