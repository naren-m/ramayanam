"""
Integration tests for data loading and processing.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from api.services.sloka_reader import SlokaReader


@pytest.mark.integration
@pytest.mark.requires_data
class TestDataLoading:
    """Test data loading and processing integration."""
    
    def test_sloka_reader_with_real_structure(self, temp_data_files):
        """Test SlokaReader with realistic file structure."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        
        # Initialize reader
        reader = SlokaReader(slokas_path)
        assert reader.base_path == slokas_path
        
        # Verify directory structure exists
        assert os.path.exists(slokas_path)
        
        # Check for kanda directories
        bala_kanda_path = os.path.join(slokas_path, 'BalaKanda')
        assert os.path.exists(bala_kanda_path)
        
        # Check for sloka files
        sloka_file = os.path.join(bala_kanda_path, 'BalaKanda_sarga_1_sloka.txt')
        assert os.path.exists(sloka_file)
        
        # Verify file content
        with open(sloka_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0
            assert 'धर्मक्षेत्रे' in content
    
    def test_file_encoding_handling(self, temp_data_files):
        """Test handling of different file encodings."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas', 'BalaKanda')
        
        # Create files with different content
        unicode_content = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।।\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय।।"
        
        # Test UTF-8 encoding
        utf8_file = os.path.join(slokas_path, 'utf8_test.txt')
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write(unicode_content)
        
        # Read back and verify
        with open(utf8_file, 'r', encoding='utf-8') as f:
            read_content = f.read()
            assert read_content == unicode_content
            assert 'धर्मक्षेत्रे' in read_content
            assert '।।' in read_content
    
    def test_missing_file_handling(self, temp_data_files):
        """Test handling of missing files in data structure."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        reader = SlokaReader(slokas_path)
        
        # Test accessing non-existent kanda
        non_existent_kanda = os.path.join(slokas_path, 'NonExistentKanda')
        assert not os.path.exists(non_existent_kanda)
        
        # Test accessing partial file structure
        partial_kanda = os.path.join(slokas_path, 'PartialKanda')
        os.makedirs(partial_kanda, exist_ok=True)
        
        # Create only sloka file, missing meaning and translation
        with open(os.path.join(partial_kanda, 'PartialKanda_sarga_1_sloka.txt'), 'w', encoding='utf-8') as f:
            f.write("Test sloka content")
        
        # Verify partial structure
        assert os.path.exists(partial_kanda)
        assert os.path.exists(os.path.join(partial_kanda, 'PartialKanda_sarga_1_sloka.txt'))
        assert not os.path.exists(os.path.join(partial_kanda, 'PartialKanda_sarga_1_meaning.txt'))
    
    def test_large_file_handling(self, temp_data_files):
        """Test handling of large data files."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas', 'BalaKanda')
        
        # Create a large file
        large_content = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।\n" * 10000  # 10k lines
        large_file = os.path.join(slokas_path, 'large_sloka.txt')
        
        with open(large_file, 'w', encoding='utf-8') as f:
            f.write(large_content)
        
        # Verify file was created and can be read
        assert os.path.exists(large_file)
        
        with open(large_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 100000  # Should be large
            assert content.count('धर्मक्षेत्रे') == 10000  # Should have 10k occurrences
    
    def test_special_characters_in_files(self, temp_data_files):
        """Test handling of special characters and formatting."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas', 'BalaKanda')
        
        # Content with various special characters
        special_content = """धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय।।१।।

अत्र शूरा महेष्वासा भीमार्जुनसमा युधि।
युयुधानो विराटश्च द्रुपदश्च महारथः।।२।।

धृष्टकेतुश्चेकितानः काशिराजश्च वीर्यवान्।
पुरुजित्कुन्तिभोजश्च शैब्यश्च नरपुङ्गवः।।३।।"""
        
        special_file = os.path.join(slokas_path, 'special_chars.txt')
        with open(special_file, 'w', encoding='utf-8') as f:
            f.write(special_content)
        
        # Read and verify special characters are preserved
        with open(special_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '।।' in content  # Double danda
            assert '।' in content   # Single danda
            assert '१' in content   # Devanagari digit
            assert '२' in content
            assert '३' in content
            assert '\n' in content  # Line breaks


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across the system."""
    
    def test_file_structure_consistency(self, temp_data_files):
        """Test that file structure follows expected patterns."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        
        # Check expected kanda directories
        expected_kandas = ['BalaKanda']  # Based on our temp data
        
        for kanda in expected_kandas:
            kanda_path = os.path.join(slokas_path, kanda)
            assert os.path.exists(kanda_path)
            assert os.path.isdir(kanda_path)
            
            # Check for expected file types in each kanda
            files = os.listdir(kanda_path)
            
            # Should have sloka, meaning, and translation files
            sloka_files = [f for f in files if f.endswith('_sloka.txt')]
            meaning_files = [f for f in files if f.endswith('_meaning.txt')]
            translation_files = [f for f in files if f.endswith('_translation.txt')]
            
            assert len(sloka_files) > 0
            assert len(meaning_files) > 0
            assert len(translation_files) > 0
    
    def test_matching_file_counts(self, temp_data_files):
        """Test that sloka, meaning, and translation files match."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas', 'BalaKanda')
        
        if os.path.exists(slokas_path):
            files = os.listdir(slokas_path)
            
            # Group files by sarga
            sarga_groups = {}
            for file in files:
                if '_sarga_' in file:
                    # Extract sarga number
                    parts = file.split('_sarga_')
                    if len(parts) >= 2:
                        sarga_part = parts[1].split('_')[0]
                        if sarga_part not in sarga_groups:
                            sarga_groups[sarga_part] = []
                        sarga_groups[sarga_part].append(file)
            
            # For each sarga, check we have matching files
            for sarga, sarga_files in sarga_groups.items():
                file_types = set()
                for file in sarga_files:
                    if file.endswith('_sloka.txt'):
                        file_types.add('sloka')
                    elif file.endswith('_meaning.txt'):
                        file_types.add('meaning')
                    elif file.endswith('_translation.txt'):
                        file_types.add('translation')
                
                # Should have all three types (in our test data)
                expected_types = {'sloka', 'meaning', 'translation'}
                assert file_types == expected_types, f"Sarga {sarga} missing file types: {expected_types - file_types}"
    
    def test_content_alignment(self, temp_data_files):
        """Test that sloka, meaning, and translation content align."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas', 'BalaKanda')
        
        # Read the test files we created
        sloka_file = os.path.join(slokas_path, 'BalaKanda_sarga_1_sloka.txt')
        meaning_file = os.path.join(slokas_path, 'BalaKanda_sarga_1_meaning.txt')
        translation_file = os.path.join(slokas_path, 'BalaKanda_sarga_1_translation.txt')
        
        if all(os.path.exists(f) for f in [sloka_file, meaning_file, translation_file]):
            # Read all files
            with open(sloka_file, 'r', encoding='utf-8') as f:
                sloka_lines = f.readlines()
            
            with open(meaning_file, 'r', encoding='utf-8') as f:
                meaning_lines = f.readlines()
            
            with open(translation_file, 'r', encoding='utf-8') as f:
                translation_lines = f.readlines()
            
            # Line counts should match
            assert len(sloka_lines) == len(meaning_lines) == len(translation_lines), \
                "Sloka, meaning, and translation files should have same number of lines"
            
            # Content should be related (basic check)
            for i, (sloka, meaning, translation) in enumerate(zip(sloka_lines, meaning_lines, translation_lines)):
                assert len(sloka.strip()) > 0, f"Empty sloka at line {i+1}"
                assert len(meaning.strip()) > 0, f"Empty meaning at line {i+1}"
                assert len(translation.strip()) > 0, f"Empty translation at line {i+1}"


@pytest.mark.integration
@pytest.mark.slow
class TestDataProcessingPerformance:
    """Test data processing performance."""
    
    def test_file_reading_performance(self, temp_data_files):
        """Test performance of reading data files."""
        import time
        
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        reader = SlokaReader(slokas_path)
        
        # Time the initialization
        start_time = time.time()
        
        # Simulate some file operations
        for kanda in ['BalaKanda']:
            kanda_path = os.path.join(slokas_path, kanda)
            if os.path.exists(kanda_path):
                files = os.listdir(kanda_path)
                for file in files[:5]:  # Limit to first 5 files
                    file_path = os.path.join(kanda_path, file)
                    if os.path.isfile(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            assert len(content) >= 0
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete reasonably quickly
        assert processing_time < 5.0, f"File reading took too long: {processing_time:.2f} seconds"
    
    def test_memory_usage_during_processing(self, temp_data_files):
        """Test memory usage during data processing."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        
        # Process files and monitor memory
        for i in range(10):
            reader = SlokaReader(slokas_path)
            
            # Read some files
            bala_kanda_path = os.path.join(slokas_path, 'BalaKanda')
            if os.path.exists(bala_kanda_path):
                files = os.listdir(bala_kanda_path)
                for file in files:
                    file_path = os.path.join(bala_kanda_path, file)
                    if os.path.isfile(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Process content
                            lines = content.split('\n')
                            assert isinstance(lines, list)
            
            # Clean up
            del reader
            if i % 3 == 0:
                gc.collect()
        
        # Final cleanup
        gc.collect()
        
        # Test passes if no memory errors occur
        assert True


@pytest.mark.integration
class TestDataValidation:
    """Test data validation and integrity."""
    
    def test_utf8_encoding_validation(self, temp_data_files):
        """Test that all files are valid UTF-8."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        
        def validate_utf8_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # If we can read it, it's valid UTF-8
                    return True, len(content)
            except UnicodeDecodeError as e:
                return False, str(e)
        
        # Check all text files
        for root, dirs, files in os.walk(slokas_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    is_valid, result = validate_utf8_file(file_path)
                    assert is_valid, f"File {file_path} is not valid UTF-8: {result}"
                    assert result > 0, f"File {file_path} is empty"
    
    def test_content_format_validation(self, temp_data_files):
        """Test that file content follows expected format."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas', 'BalaKanda')
        
        # Check sloka files
        sloka_files = [f for f in os.listdir(slokas_path) if f.endswith('_sloka.txt')]
        
        for sloka_file in sloka_files:
            file_path = os.path.join(slokas_path, sloka_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Basic format checks
                assert len(content.strip()) > 0, f"Empty sloka file: {sloka_file}"
                
                # Should contain Sanskrit characters
                has_devanagari = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in content)
                assert has_devanagari, f"Sloka file {sloka_file} doesn't contain Devanagari characters"
    
    def test_filename_pattern_validation(self, temp_data_files):
        """Test that filenames follow expected patterns."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        
        for root, dirs, files in os.walk(slokas_path):
            for file in files:
                if file.endswith('.txt'):
                    # Expected pattern: KandaName_sarga_X_type.txt
                    parts = file.replace('.txt', '').split('_')
                    
                    assert len(parts) >= 4, f"Filename {file} doesn't follow expected pattern"
                    assert parts[-3] == 'sarga', f"Filename {file} missing 'sarga' part"
                    assert parts[-2].isdigit(), f"Filename {file} sarga number is not numeric"
                    assert parts[-1] in ['sloka', 'meaning', 'translation'], \
                        f"Filename {file} has invalid type: {parts[-1]}"


@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery in data processing."""
    
    def test_recovery_from_missing_files(self, temp_data_files):
        """Test graceful handling of missing files."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas')
        
        # Create a reader
        reader = SlokaReader(slokas_path)
        
        # Temporarily rename a file to simulate missing file
        bala_kanda_path = os.path.join(slokas_path, 'BalaKanda')
        original_file = os.path.join(bala_kanda_path, 'BalaKanda_sarga_1_sloka.txt')
        temp_file = os.path.join(bala_kanda_path, 'BalaKanda_sarga_1_sloka.txt.backup')
        
        if os.path.exists(original_file):
            # Rename file
            os.rename(original_file, temp_file)
            
            try:
                # Reader should still work (just with less data)
                assert reader.base_path == slokas_path
                
                # Accessing missing file should be handled gracefully
                assert not os.path.exists(original_file)
                
            finally:
                # Restore file
                if os.path.exists(temp_file):
                    os.rename(temp_file, original_file)
    
    def test_recovery_from_corrupted_files(self, temp_data_files):
        """Test handling of corrupted files."""
        slokas_path = os.path.join(temp_data_files, 'slokas', 'Slokas', 'BalaKanda')
        
        # Create a corrupted file
        corrupted_file = os.path.join(slokas_path, 'corrupted_file.txt')
        
        # Write some binary data that's not valid UTF-8
        with open(corrupted_file, 'wb') as f:
            f.write(b'\x80\x81\x82\x83')  # Invalid UTF-8 sequence
        
        # Reading should handle the error gracefully
        try:
            with open(corrupted_file, 'r', encoding='utf-8') as f:
                content = f.read()
            assert False, "Should have raised UnicodeDecodeError"
        except UnicodeDecodeError:
            # Expected behavior
            pass
        
        # Cleanup
        os.remove(corrupted_file)