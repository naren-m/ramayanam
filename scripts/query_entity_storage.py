#!/usr/bin/env python3
"""
Entity Storage Query Script
Demonstrates how to access validated/unvalidated entries and their storage details
"""

import sqlite3
import json
from typing import Dict, List, Any
from pathlib import Path

DB_PATH = "data/db/ramayanam.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_validation_summary():
    """Get validation status summary"""
    print("📊 VALIDATION STATUS SUMMARY")
    print("=" * 50)
    
    with get_connection() as conn:
        # Validation status counts
        status_counts = conn.execute("""
            SELECT validation_status, COUNT(*) as count 
            FROM kg_entities 
            GROUP BY validation_status
        """).fetchall()
        
        for row in status_counts:
            print(f"  {row['validation_status'].upper()}: {row['count']} entities")
        
        # Entity type breakdown
        print("\n📈 ENTITY TYPE BREAKDOWN")
        type_counts = conn.execute("""
            SELECT entity_type, COUNT(*) as count 
            FROM kg_entities 
            GROUP BY entity_type 
            ORDER BY count DESC
        """).fetchall()
        
        for row in type_counts:
            print(f"  {row['entity_type']}: {row['count']} entities")

def query_validated_entities():
    """Show all validated entities with details"""
    print("\n✅ VALIDATED ENTITIES")
    print("=" * 50)
    
    with get_connection() as conn:
        validated = conn.execute("""
            SELECT kg_id, entity_type, labels, validation_status, validated_by, 
                   validated_at, properties
            FROM kg_entities 
            WHERE validation_status = 'validated'
            ORDER BY validated_at DESC
        """).fetchall()
        
        if not validated:
            print("  No validated entities yet.")
            return
            
        for row in validated:
            labels = json.loads(row['labels'])
            properties = json.loads(row['properties'])
            
            print(f"\n  🔹 {labels.get('en', 'Unknown')} ({row['entity_type']})")
            print(f"     ID: {row['kg_id']}")
            print(f"     Validated by: {row['validated_by']} at {row['validated_at']}")
            print(f"     Mentions: {properties.get('occurrence_count', 'N/A')}")
            
            if 'correction_notes' in properties:
                print(f"     Corrections: {properties['correction_notes']}")

def query_pending_entities():
    """Show pending entities awaiting validation"""
    print("\n⏳ PENDING VALIDATION")
    print("=" * 50)
    
    with get_connection() as conn:
        pending = conn.execute("""
            SELECT kg_id, entity_type, labels, properties,
                   (SELECT COUNT(*) FROM text_entity_mentions WHERE entity_id = kg_id) as mention_count
            FROM kg_entities 
            WHERE validation_status = 'pending'
            ORDER BY 
                CAST(JSON_EXTRACT(properties, '$.occurrence_count') AS INTEGER) DESC
            LIMIT 10
        """).fetchall()
        
        print(f"  Showing top 10 by mention count (total pending: {len(pending)})")
        
        for i, row in enumerate(pending, 1):
            labels = json.loads(row['labels'])
            properties = json.loads(row['properties'])
            
            print(f"\n  {i}. 🔸 {labels.get('en', 'Unknown')} ({row['entity_type']})")
            print(f"     Mentions: {properties.get('occurrence_count', 0):,}")
            print(f"     Confidence: {properties.get('confidence_score', 0):.2f}")

def query_rejected_entities():
    """Show rejected entities"""
    print("\n❌ REJECTED ENTITIES")
    print("=" * 50)
    
    with get_connection() as conn:
        rejected = conn.execute("""
            SELECT kg_id, entity_type, labels, validation_status, validated_by, 
                   validated_at, validation_notes
            FROM kg_entities 
            WHERE validation_status = 'rejected'
            ORDER BY validated_at DESC
        """).fetchall()
        
        if not rejected:
            print("  No rejected entities yet.")
            return
            
        for row in rejected:
            labels = json.loads(row['labels'])
            
            print(f"\n  🔹 {labels.get('en', 'Unknown')} ({row['entity_type']})")
            print(f"     Rejected by: {row['validated_by']} at {row['validated_at']}")
            if row['validation_notes']:
                print(f"     Reason: {row['validation_notes']}")

def query_entity_mentions():
    """Show entity mention statistics"""
    print("\n📝 ENTITY MENTIONS IN TEXT")
    print("=" * 50)
    
    with get_connection() as conn:
        total_mentions = conn.execute("""
            SELECT COUNT(*) as count FROM text_entity_mentions
        """).fetchone()['count']
        
        print(f"  Total entity mentions in corpus: {total_mentions:,}")
        
        # Top mentioned entities
        top_mentioned = conn.execute("""
            SELECT entity_id, COUNT(*) as mention_count
            FROM text_entity_mentions 
            GROUP BY entity_id 
            ORDER BY mention_count DESC 
            LIMIT 5
        """).fetchall()
        
        print("\n  Top 5 most mentioned entities:")
        for row in top_mentioned:
            print(f"    {row['entity_id']}: {row['mention_count']:,} mentions")

def query_discovery_sessions():
    """Show discovery session history"""
    print("\n🔍 DISCOVERY SESSIONS")
    print("=" * 50)
    
    with get_connection() as conn:
        sessions = conn.execute("""
            SELECT session_id, status, entities_found, start_time, end_time, settings
            FROM entity_discovery_sessions 
            ORDER BY created_at DESC 
            LIMIT 5
        """).fetchall()
        
        for row in sessions:
            settings = json.loads(row['settings'])
            duration = "Running..." if not row['end_time'] else "Completed"
            
            print(f"\n  📋 Session: {row['session_id'][:8]}...")
            print(f"     Status: {row['status']} ({duration})")
            print(f"     Started: {row['start_time']}")
            print(f"     Settings: confidence≥{settings.get('confidence_threshold', 0.7)}")

def main():
    """Run all queries"""
    print("🗃️  RAMAYANAM ENTITY STORAGE ANALYSIS")
    print("=" * 60)
    
    try:
        query_validation_summary()
        query_validated_entities()
        query_pending_entities() 
        query_rejected_entities()
        query_entity_mentions()
        query_discovery_sessions()
        
        print(f"\n💾 Database location: {Path(DB_PATH).absolute()}")
        print("✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()