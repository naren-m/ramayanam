#!/usr/bin/env python3
"""
Export Validated Entities Script
Exports all validated, pending, and rejected entities to different formats
"""

import sqlite3
import json
import csv
from datetime import datetime
from pathlib import Path

DB_PATH = "data/db/ramayanam.db"
OUTPUT_DIR = "exports"

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def export_validated_entities():
    """Export validated entities to JSON and CSV"""
    print("📥 Exporting validated entities...")
    
    with get_connection() as conn:
        validated = conn.execute("""
            SELECT kg_id, entity_type, labels, validation_status, validated_by, 
                   validated_at, properties, validation_notes
            FROM kg_entities 
            WHERE validation_status = 'validated'
            ORDER BY validated_at DESC
        """).fetchall()
        
        # Convert to list of dicts for JSON export
        entities_data = []
        for row in validated:
            labels = json.loads(row['labels'])
            properties = json.loads(row['properties'])
            
            entity = {
                'id': row['kg_id'],
                'entity_type': row['entity_type'],
                'english_name': labels.get('en', ''),
                'sanskrit_name': labels.get('sa', ''),
                'validation_status': row['validation_status'],
                'validated_by': row['validated_by'],
                'validated_at': row['validated_at'],
                'mention_count': properties.get('occurrence_count', 0),
                'confidence_score': properties.get('confidence_score', 0),
                'epithets': properties.get('epithets', []),
                'correction_notes': properties.get('correction_notes', ''),
                'extraction_method': properties.get('extraction_method', 'automated')
            }
            entities_data.append(entity)
        
        # Export to JSON
        json_file = f"{OUTPUT_DIR}/validated_entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'export_timestamp': datetime.now().isoformat(),
                'total_count': len(entities_data),
                'entities': entities_data
            }, f, indent=2, ensure_ascii=False)
        
        # Export to CSV
        csv_file = f"{OUTPUT_DIR}/validated_entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if entities_data:
                writer = csv.DictWriter(f, fieldnames=entities_data[0].keys())
                writer.writeheader()
                writer.writerows(entities_data)
        
        print(f"  ✅ Exported {len(entities_data)} validated entities")
        print(f"     JSON: {json_file}")
        print(f"     CSV: {csv_file}")
        
        return len(entities_data)

def export_pending_entities():
    """Export pending entities for external validation"""
    print("📥 Exporting pending entities...")
    
    with get_connection() as conn:
        pending = conn.execute("""
            SELECT kg_id, entity_type, labels, properties
            FROM kg_entities 
            WHERE validation_status = 'pending'
            ORDER BY CAST(JSON_EXTRACT(properties, '$.occurrence_count') AS INTEGER) DESC
        """).fetchall()
        
        entities_data = []
        for row in pending:
            labels = json.loads(row['labels'])
            properties = json.loads(row['properties'])
            
            entity = {
                'id': row['kg_id'],
                'entity_type': row['entity_type'],
                'english_name': labels.get('en', ''),
                'sanskrit_name': labels.get('sa', ''),
                'mention_count': properties.get('occurrence_count', 0),
                'confidence_score': properties.get('confidence_score', 0),
                'epithets': ', '.join(properties.get('epithets', [])),
                'needs_validation': True
            }
            entities_data.append(entity)
        
        # Export to CSV for manual validation
        csv_file = f"{OUTPUT_DIR}/pending_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if entities_data:
                # Add validation columns
                fieldnames = list(entities_data[0].keys()) + ['validation_decision', 'validation_notes', 'corrected_name', 'corrected_type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for entity in entities_data:
                    # Add empty validation fields
                    entity.update({
                        'validation_decision': '',  # approve/reject
                        'validation_notes': '',
                        'corrected_name': '',
                        'corrected_type': ''
                    })
                    writer.writerow(entity)
        
        print(f"  ✅ Exported {len(entities_data)} pending entities")
        print(f"     CSV: {csv_file}")
        
        return len(entities_data)

def export_entity_mentions():
    """Export entity mentions for analysis"""
    print("📥 Exporting entity mentions...")
    
    with get_connection() as conn:
        mentions = conn.execute("""
            SELECT 
                tem.entity_id,
                tem.text_unit_id,
                tem.span_start,
                tem.span_end,
                tem.confidence,
                e.entity_type,
                JSON_EXTRACT(e.labels, '$.en') as english_name,
                e.validation_status
            FROM text_entity_mentions tem
            JOIN kg_entities e ON tem.entity_id = e.kg_id
            ORDER BY tem.entity_id, tem.text_unit_id
            LIMIT 1000
        """).fetchall()
        
        mentions_data = []
        for row in mentions:
            mention = {
                'entity_id': row['entity_id'],
                'entity_name': row['english_name'],
                'entity_type': row['entity_type'],
                'validation_status': row['validation_status'],
                'text_unit_id': row['text_unit_id'],
                'span_start': row['span_start'],
                'span_end': row['span_end'],
                'confidence': row['confidence']
            }
            mentions_data.append(mention)
        
        csv_file = f"{OUTPUT_DIR}/entity_mentions_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if mentions_data:
                writer = csv.DictWriter(f, fieldnames=mentions_data[0].keys())
                writer.writeheader()
                writer.writerows(mentions_data)
        
        print(f"  ✅ Exported {len(mentions_data)} entity mentions (sample)")
        print(f"     CSV: {csv_file}")
        
        return len(mentions_data)

def export_discovery_summary():
    """Export discovery session summary"""
    print("📥 Exporting discovery summary...")
    
    with get_connection() as conn:
        # Get overall statistics
        stats = conn.execute("""
            SELECT 
                validation_status,
                entity_type,
                COUNT(*) as count,
                AVG(CAST(JSON_EXTRACT(properties, '$.occurrence_count') AS REAL)) as avg_mentions,
                SUM(CAST(JSON_EXTRACT(properties, '$.occurrence_count') AS INTEGER)) as total_mentions
            FROM kg_entities
            GROUP BY validation_status, entity_type
        """).fetchall()
        
        summary_data = {
            'export_timestamp': datetime.now().isoformat(),
            'database_location': str(Path(DB_PATH).absolute()),
            'summary_statistics': [dict(row) for row in stats],
            'total_entities': conn.execute("SELECT COUNT(*) as count FROM kg_entities").fetchone()['count'],
            'total_mentions': conn.execute("SELECT COUNT(*) as count FROM text_entity_mentions").fetchone()['count']
        }
        
        json_file = f"{OUTPUT_DIR}/discovery_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Exported discovery summary")
        print(f"     JSON: {json_file}")

def main():
    """Run all exports"""
    print("📦 ENTITY STORAGE EXPORT UTILITY")
    print("=" * 50)
    
    ensure_output_dir()
    
    try:
        validated_count = export_validated_entities()
        pending_count = export_pending_entities() 
        mentions_count = export_entity_mentions()
        export_discovery_summary()
        
        print(f"\n📊 EXPORT SUMMARY")
        print(f"  Validated entities: {validated_count}")
        print(f"  Pending validation: {pending_count}")
        print(f"  Entity mentions: {mentions_count}")
        print(f"  Output directory: {Path(OUTPUT_DIR).absolute()}")
        print("✅ Export complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()