#!/usr/bin/env python3
"""
Test script for automated entity extraction pipeline

This script demonstrates how to automatically extract entities from the Ramayana corpus
instead of creating them manually. It processes the existing text files and identifies
characters, places, concepts, and their relationships.

Usage:
    python scripts/test_entity_extraction.py [--sample] [--full] [--kanda BalaKanda]
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.services.automated_entity_extraction import (
    RamayanaEntityExtractor, 
    create_sample_kg_data,
    extract_entities_for_text_service
)


def setup_logging(level=logging.INFO):
    """Set up logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('entity_extraction.log')
        ]
    )


def test_sample_extraction():
    """Test extraction on a small sample"""
    print("Testing automated entity extraction on sample data...")
    
    # Create sample data from BalaKanda
    results = create_sample_kg_data(15)
    
    print(f"\n📊 Sample Extraction Results:")
    print(f"   Entities found: {len(results['entities'])}")
    print(f"   Annotations: {len(results['annotations'])}")
    print(f"   Relationships: {len(results['relationships'])}")
    
    print(f"\n🔍 Extracted Entities:")
    for entity_id, entity in results['entities'].items():
        labels = entity.labels
        entity_type = entity.entity_type.value
        confidence = entity.properties.get('extraction_confidence', 'N/A')
        
        print(f"   • {entity_id} ({entity_type})")
        print(f"     Labels: {labels}")
        print(f"     Confidence: {confidence}")
        print()
    
    return results


def test_pattern_matching():
    """Test specific pattern matching"""
    print("Testing pattern matching on known text...")
    
    extractor = RamayanaEntityExtractor()
    
    # Test texts with known entities
    test_texts = [
        "रामो नाम जनैश्श्रुत: राघवो धर्मज्ञ:",  # Sanskrit
        "Rama, the son of Dasharatha, went to the forest with Sita and Lakshmana",  # English
        "हनुमान् पवनात्मजः लङ्कां गत्वा सीताम् अपश्यत्"  # Sanskrit with multiple entities
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest Text {i}: {text}")
        
        results = extractor._extract_from_text(text, 'sanskrit' if i != 2 else 'translation')
        
        for result in results:
            print(f"   Found: {result.entity_id} ({result.entity_type.value})")
            print(f"   Mentions: {result.mentions}")
            print(f"   Confidence: {result.confidence:.2f}")


def test_full_extraction():
    """Test extraction on full corpus (takes longer)"""
    print("Running full corpus extraction...")
    print("⚠️  This may take several minutes for the complete corpus")
    
    # Run full extraction
    results = extract_entities_for_text_service(None, force_refresh=True)
    
    print(f"\n📊 Full Extraction Results:")
    print(f"   Entities found: {len(results['entities'])}")
    print(f"   Annotations: {len(results['annotations'])}")
    print(f"   Relationships: {len(results['relationships'])}")
    
    # Show statistics
    stats = results.get('statistics', {})
    print(f"   Processed slokas: {stats.get('processed_slokas', 'N/A')}")
    
    # Top entities by frequency
    entities_by_frequency = sorted(
        stats.get('entities_found', {}).items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    print(f"\n🏆 Top Entities by Mentions:")
    for entity_id, count in entities_by_frequency:
        print(f"   {entity_id}: {count} mentions")
    
    return results


def test_kanda_extraction(kanda_name: str):
    """Test extraction on a specific kanda"""
    print(f"Testing extraction on {kanda_name}...")
    
    extractor = RamayanaEntityExtractor()
    kanda_path = Path(f"data/slokas/Slokas/{kanda_name}")
    
    if not kanda_path.exists():
        print(f"❌ Kanda directory not found: {kanda_path}")
        return
    
    results = extractor._process_kanda(kanda_path)
    
    print(f"\n📊 {kanda_name} Extraction Results:")
    print(f"   Entities found: {len(results['entities'])}")
    print(f"   Annotations: {len(results['annotations'])}")
    
    # Show entities found
    print(f"\n📝 Entities in {kanda_name}:")
    for entity_id, entity in results['entities'].items():
        occurrence_count = entity.properties.get('occurrence_count', 'N/A')
        print(f"   • {entity_id}: {occurrence_count} mentions")


def demonstrate_vs_manual_approach():
    """Demonstrate why automated approach is better than manual"""
    print("\n" + "="*60)
    print("🔄 AUTOMATED vs MANUAL ENTITY CREATION")
    print("="*60)
    
    print("\n❌ Manual Approach Problems:")
    print("   • Time-consuming: ~100+ hours for 13,102 slokas")
    print("   • Error-prone: Human mistakes in entity identification")
    print("   • Inconsistent: Different people might identify differently")
    print("   • Not scalable: What about other texts (Mahabharata, etc.)?")
    print("   • No confidence scores: No way to measure accuracy")
    print("   • Misses variants: Won't catch all name variations/epithets")
    
    print("\n✅ Automated Approach Benefits:")
    print("   • Fast: Processes entire corpus in minutes")
    print("   • Consistent: Same rules applied everywhere")
    print("   • Scalable: Easy to extend to other texts")
    print("   • Comprehensive: Catches all pattern variations")
    print("   • Measurable: Provides confidence scores")
    print("   • Maintainable: Can improve patterns over time")
    print("   • Traceable: Know exactly why entity was identified")
    
    # Show example of what automated approach finds
    sample_results = create_sample_kg_data(5)
    
    print(f"\n📊 Quick Demo - Found {len(sample_results['entities'])} entities automatically:")
    for entity_id, entity in list(sample_results['entities'].items())[:3]:
        print(f"   • {entity_id}: {entity.labels}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test automated entity extraction')
    parser.add_argument('--sample', action='store_true', 
                       help='Run sample extraction (quick test)')
    parser.add_argument('--full', action='store_true', 
                       help='Run full corpus extraction (takes time)')
    parser.add_argument('--kanda', type=str, 
                       help='Extract from specific kanda (e.g., BalaKanda)')
    parser.add_argument('--patterns', action='store_true',
                       help='Test pattern matching')
    parser.add_argument('--demo', action='store_true',
                       help='Demonstrate automated vs manual approach')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    print("🔮 Ramayana Automated Entity Extraction Test")
    print("=" * 50)
    
    try:
        if args.demo:
            demonstrate_vs_manual_approach()
        
        if args.patterns:
            test_pattern_matching()
        
        if args.sample:
            test_sample_extraction()
        
        if args.kanda:
            test_kanda_extraction(args.kanda)
        
        if args.full:
            test_full_extraction()
        
        # Default action if no specific test chosen
        if not any([args.sample, args.full, args.kanda, args.patterns, args.demo]):
            print("Running default sample test...")
            demonstrate_vs_manual_approach()
            test_sample_extraction()
        
        print("\n✅ Entity extraction testing completed!")
        print("\n💡 Next steps:")
        print("   1. Review extracted entities for accuracy")
        print("   2. Adjust patterns based on results")
        print("   3. Create JSON-LD schema for entities")
        print("   4. Integrate with knowledge graph database")
        
    except Exception as e:
        logging.error(f"Error during extraction: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())