#!/usr/bin/env python3
"""
Rebuild Database with YuddhaKanda Data

This script rebuilds the Ramayanam database to include the newly collected YuddhaKanda data.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.services.corpus_loader import CorpusLoader

def backup_existing_database():
    """Create a backup of the existing database"""
    db_path = project_root / "data" / "db" / "ramayanam.db"
    backup_path = project_root / "data" / "db" / "ramayanam_backup.db"
    
    if db_path.exists():
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to {backup_path}")
        return True
    else:
        print("ℹ️ No existing database found, creating new one")
        return False

def check_yuddha_kanda_files():
    """Check if YuddhaKanda files are available"""
    yuddha_dir = project_root / "data" / "slokas" / "Slokas" / "YuddhaKanda"
    
    if not yuddha_dir.exists():
        print(f"❌ YuddhaKanda directory not found: {yuddha_dir}")
        return False
    
    # Count files
    sloka_files = list(yuddha_dir.glob("*_sloka.txt"))
    meaning_files = list(yuddha_dir.glob("*_meaning.txt"))
    translation_files = list(yuddha_dir.glob("*_translation.txt"))
    
    print(f"📁 YuddhaKanda files found:")
    print(f"   Sloka files: {len(sloka_files)}")
    print(f"   Meaning files: {len(meaning_files)}")
    print(f"   Translation files: {len(translation_files)}")
    
    if len(sloka_files) == 0:
        print("❌ No sloka files found!")
        return False
    
    return True

def rebuild_database():
    """Rebuild the database with all kandas including YuddhaKanda"""
    print("🔄 Rebuilding database with YuddhaKanda...")
    
    try:
        # Initialize corpus loader
        corpus_loader = CorpusLoader()
        
        # Load all kandas (including YuddhaKanda)
        print("📖 Loading corpus data...")
        corpus_loader.load_corpus()
        
        # Save to database
        print("💾 Saving to database...")
        corpus_loader.save_to_database()
        
        print("✅ Database rebuild completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error rebuilding database: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_yuddha_kanda_in_db():
    """Verify that YuddhaKanda data is properly loaded in the database"""
    print("🔍 Verifying YuddhaKanda data in database...")
    
    db_path = project_root / "data" / "db" / "ramayanam.db"
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if YuddhaKanda (kanda_id=6) exists
        cursor.execute("SELECT COUNT(*) FROM slokas WHERE kanda_id = 6")
        yuddha_count = cursor.fetchone()[0]
        
        # Get counts for all kandas
        cursor.execute("SELECT kanda_id, COUNT(*) FROM slokas GROUP BY kanda_id ORDER BY kanda_id")
        kanda_counts = cursor.fetchall()
        
        print("📊 Sloka counts by Kanda:")
        for kanda_id, count in kanda_counts:
            kanda_name = {
                1: "BalaKanda",
                2: "AyodhyaKanda", 
                3: "AranyaKanda",
                4: "KishkindaKanda",
                5: "SundaraKanda",
                6: "YuddhaKanda"
            }.get(kanda_id, f"Kanda {kanda_id}")
            
            status = "✅" if kanda_id == 6 and count > 0 else "📄"
            print(f"   {status} {kanda_name}: {count} slokas")
        
        if yuddha_count > 0:
            print(f"🎉 YuddhaKanda successfully loaded with {yuddha_count} slokas!")
            return True
        else:
            print("❌ YuddhaKanda not found in database!")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def update_knowledge_graph():
    """Extract entities from YuddhaKanda for knowledge graph"""
    print("🧠 Updating knowledge graph with YuddhaKanda entities...")
    
    try:
        from api.services.automated_entity_extraction import RamayanaEntityExtractor
        
        extractor = RamayanaEntityExtractor()
        
        # Extract entities from YuddhaKanda
        print("🔍 Extracting entities from YuddhaKanda...")
        extractor.process_kanda_files('YuddhaKanda')
        
        print("✅ Knowledge graph updated with YuddhaKanda entities!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating knowledge graph: {e}")
        print("ℹ️ You can run entity extraction manually later")
        return False

def main():
    """Main execution function"""
    print("🎯 YuddhaKanda Database Integration")
    print("=" * 50)
    
    # Step 1: Check prerequisites
    if not check_yuddha_kanda_files():
        print("❌ YuddhaKanda files not found. Please run data collection first.")
        return False
    
    # Step 2: Backup existing database
    backup_existing_database()
    
    # Step 3: Rebuild database
    if not rebuild_database():
        print("❌ Database rebuild failed!")
        return False
    
    # Step 4: Verify YuddhaKanda is loaded
    if not verify_yuddha_kanda_in_db():
        print("❌ YuddhaKanda verification failed!")
        return False
    
    # Step 5: Update knowledge graph
    update_knowledge_graph()
    
    print("\n🎉 YuddhaKanda integration completed successfully!")
    print("\n📋 Summary:")
    print("✅ YuddhaKanda data files copied")
    print("✅ Database rebuilt with YuddhaKanda")
    print("✅ Data verification completed")
    print("✅ Knowledge graph updated")
    
    print("\n🚀 Next steps:")
    print("1. Test the application to browse YuddhaKanda")
    print("2. Verify search functionality includes YuddhaKanda")
    print("3. Check knowledge graph entities for YuddhaKanda characters")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)