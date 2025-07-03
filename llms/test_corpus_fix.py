#!/usr/bin/env python3
"""
Test the fixed corpus loading
"""

import sys
sys.path.append('.')

from ramayanam_rag_system import RamayanamCorpusLoader
from pathlib import Path

def test_corpus_loading():
    """Test the fixed corpus loading"""
    print("🧪 Testing fixed corpus loading...")
    
    # Test with BalaKanda
    data_path = Path("../data/slokas/Slokas")
    if not data_path.exists():
        print(f"❌ Data path not found: {data_path}")
        return False
    
    loader = RamayanamCorpusLoader(str(data_path))
    
    # Test loading BalaKanda
    print("\n📖 Loading BalaKanda...")
    slokas = loader.load_kanda("BalaKanda")
    
    print(f"✅ Loaded {len(slokas)} slokas from BalaKanda")
    
    if slokas:
        # Show first few slokas
        print("\n📝 First 5 slokas:")
        for i, sloka in enumerate(slokas[:5], 1):
            print(f"{i}. {sloka.get_full_reference()}")
            print(f"   Sanskrit: {sloka.sanskrit_text[:80]}...")
            print(f"   Translation: {sloka.translation[:80]}..." if sloka.translation else "   Translation: Not available")
            print()
        
        return True
    else:
        print("❌ No slokas loaded")
        return False

if __name__ == "__main__":
    test_corpus_loading()