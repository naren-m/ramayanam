#!/usr/bin/env python3
"""
Debug script for Ramayanam parsing
"""

from pathlib import Path

def debug_parsing():
    """Debug the parsing logic"""
    
    # Sample line from the file
    sample_line = "     1→1::1::1::तपस्स्वाध्यायनिरतं तपस्वी वाग्विदां वरम् ।नारदं परिपप्रच्छ वाल्मीकिर्मुनिपुङ्गवम् ।।1.1.1।।"
    
    print("Original line:")
    print(repr(sample_line))
    print()
    
    # Clean line
    line = sample_line.strip()
    print("Cleaned line:")
    print(repr(line))
    print()
    
    # Check for arrow and colons
    if '→' in line and '::' in line:
        print("✓ Contains → and ::")
        
        # Split by arrow
        parts = line.split('→', 1)
        print(f"After splitting by →: {len(parts)} parts")
        print(f"Part 0 (sloka_num): {repr(parts[0])}")
        print(f"Part 1 (rest): {repr(parts[1])}")
        print()
        
        try:
            sloka_num = int(parts[0].strip())
            print(f"✓ Sloka number: {sloka_num}")
        except ValueError as e:
            print(f"❌ Error parsing sloka number: {e}")
        
        rest = parts[1]
        
        # Split by ::
        text_parts = rest.split('::', 3)
        print(f"After splitting by :: (max 3 splits): {len(text_parts)} parts")
        for i, part in enumerate(text_parts):
            print(f"Part {i}: {repr(part)}")
        print()
        
        if len(text_parts) >= 4:
            sanskrit_text = text_parts[3].strip()
            print(f"✓ Extracted Sanskrit text: {repr(sanskrit_text)}")
            
            # Clean up the text (remove verse markers)
            if '।।' in sanskrit_text:
                # Split by the verse marker and take the first part
                text_without_marker = sanskrit_text.split('।।')[0].strip()
                print(f"✓ Text without verse marker: {repr(text_without_marker)}")
        else:
            print(f"❌ Not enough parts after :: split (need 4, got {len(text_parts)})")
    else:
        print("❌ Missing → or ::")

def test_actual_file():
    """Test with actual file using new parsing logic"""
    print("\n" + "="*50)
    print("Testing with actual file (NEW LOGIC)")
    print("="*50)
    
    file_path = Path("../data/slokas/Slokas/BalaKanda/BalaKanda_sarga_1_sloka.txt")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✓ File loaded with {len(lines)} lines")
        
        slokas_found = 0
        for i, line in enumerate(lines[:10]):  # Test first 10 lines
            line = line.strip()
            if not line:
                continue
                
            print(f"\nLine {i+1}: {repr(line[:100])}...")
            
            # New parsing logic (no arrow needed)
            if '::' in line:
                try:
                    text_parts = line.split('::', 3)
                    if len(text_parts) >= 4:
                        sloka_num = int(text_parts[0])
                        sanskrit_text = text_parts[3].strip()
                        
                        # Clean up verse markers
                        if '।।' in sanskrit_text:
                            clean_text = sanskrit_text.split('।।')[0].strip()
                        else:
                            clean_text = sanskrit_text
                        
                        print(f"  ✓ Sloka {sloka_num}: {clean_text[:50]}...")
                        slokas_found += 1
                    else:
                        print(f"  ❌ Not enough parts: {len(text_parts)}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
            else:
                print(f"  → Missing ::")
        
        print(f"\nSlokas found in first 10 lines: {slokas_found}")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    debug_parsing()
    test_actual_file()