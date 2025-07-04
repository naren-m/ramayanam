#!/usr/bin/env python3
"""
Test enhanced sloka referencing directly with the RAG system
"""

import sys
sys.path.append('.')

from ramayanam_rag_system import RamayanamRAGSystem

def test_direct_referencing():
    """Test the enhanced referencing system directly"""
    print("🧪 Testing Enhanced Sloka Referencing (Direct)")
    print("=" * 60)
    
    # Initialize system
    print("\n1. Initializing RAG system...")
    rag_system = RamayanamRAGSystem(
        data_path="../data/slokas/Slokas",
        db_path="./test_referencing_chroma_db"
    )
    
    # Load a smaller subset for testing
    print("\n2. Loading BalaKanda for testing...")
    rag_system.load_corpus(kandas=["BalaKanda"])
    
    print(f"Loaded {len(rag_system.slokas)} slokas")
    
    # Index the corpus
    print("\n3. Indexing corpus...")
    rag_system.index_corpus()
    
    # Test reference lookup
    print("\n4. Testing sloka reference lookup...")
    test_refs = ["BalaKanda.1.1", "BalaKanda.1.2", "BalaKanda.2.1"]
    
    for ref in test_refs:
        sloka = rag_system.get_sloka_by_reference(ref)
        if sloka:
            print(f"✅ Found {ref}:")
            print(f"   Sanskrit: {sloka.sanskrit_text[:80]}...")
            print(f"   Translation: {sloka.translation[:80] if sloka.translation else 'Not available'}...")
        else:
            print(f"❌ Could not find {ref}")
    
    # Test enhanced context
    print("\n5. Testing enhanced context generation...")
    query = "Who is Rama?"
    context = rag_system.get_context(query, top_k=3)
    
    print("Generated context:")
    print("-" * 40)
    print(context[:500] + "..." if len(context) > 500 else context)
    print("-" * 40)
    
    # Check if context includes clear references
    if "SLOKA REFERENCE" in context:
        print("✅ Context includes clear sloka references!")
    else:
        print("⚠️  Context may not have clear reference format")
    
    # Test search results
    print("\n6. Testing search with reference information...")
    results = rag_system.search(query, top_k=3)
    
    for i, sloka in enumerate(results, 1):
        ref = sloka.get_full_reference()
        print(f"{i}. {ref}: {sloka.sanskrit_text[:60]}...")
    
    print("\n" + "=" * 60)
    print("✅ Direct testing completed!")

if __name__ == "__main__":
    test_direct_referencing()