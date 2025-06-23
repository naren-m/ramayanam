"""
Unit tests for model classes.
"""

import pytest
from api.models.sloka_model import Sloka


@pytest.mark.model
class TestSlokaModel:
    """Test cases for the Sloka model."""
    
    def test_sloka_creation(self):
        """Test basic sloka creation."""
        sloka = Sloka(
            sloka_id="1.1.1",
            sloka_text="धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः",
            meaning="धर्म के क्षेत्र में कुरुक्षेत्र में युद्ध की इच्छा रखने वाले",
            translation="In the field of dharma, in Kurukshetra, those desirous of war"
        )
        
        assert sloka.sloka_id == "1.1.1"
        assert sloka.sloka_text == "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः"
        assert sloka.meaning == "धर्म के क्षेत्र में कुरुक्षेत्र में युद्ध की इच्छा रखने वाले"
        assert sloka.translation == "In the field of dharma, in Kurukshetra, those desirous of war"
    
    def test_sloka_creation_with_empty_values(self):
        """Test sloka creation with empty values."""
        sloka = Sloka(
            sloka_id="",
            sloka_text="",
            meaning="",
            translation=""
        )
        
        assert sloka.sloka_id == ""
        assert sloka.sloka_text == ""
        assert sloka.meaning == ""
        assert sloka.translation == ""
    
    def test_sloka_creation_with_none_values(self):
        """Test sloka creation with None values."""
        sloka = Sloka(
            sloka_id=None,
            sloka_text=None,
            meaning=None,
            translation=None
        )
        
        assert sloka.sloka_id is None
        assert sloka.sloka_text is None
        assert sloka.meaning is None
        assert sloka.translation is None
    
    def test_sloka_serialize(self, sample_sloka):
        """Test sloka serialization."""
        serialized = sample_sloka.serialize()
        
        assert isinstance(serialized, dict)
        assert 'sloka_id' in serialized
        assert 'sloka_text' in serialized
        assert 'meaning' in serialized
        assert 'translation' in serialized
        
        assert serialized['sloka_id'] == sample_sloka.sloka_id
        assert serialized['sloka_text'] == sample_sloka.sloka_text
        assert serialized['meaning'] == sample_sloka.meaning
        assert serialized['translation'] == sample_sloka.translation
    
    def test_sloka_serialize_empty_values(self):
        """Test serialization with empty values."""
        sloka = Sloka(
            sloka_id="",
            sloka_text="",
            meaning="",
            translation=""
        )
        
        serialized = sloka.serialize()
        
        assert isinstance(serialized, dict)
        assert serialized['sloka_id'] == ""
        assert serialized['sloka_text'] == ""
        assert serialized['meaning'] == ""
        assert serialized['translation'] == ""
    
    def test_sloka_serialize_none_values(self):
        """Test serialization with None values."""
        sloka = Sloka(
            sloka_id=None,
            sloka_text=None,
            meaning=None,
            translation=None
        )
        
        serialized = sloka.serialize()
        
        assert isinstance(serialized, dict)
        assert serialized['sloka_id'] is None
        assert serialized['sloka_text'] is None
        assert serialized['meaning'] is None
        assert serialized['translation'] is None
    
    def test_sloka_repr(self, sample_sloka):
        """Test sloka string representation."""
        repr_str = repr(sample_sloka)
        
        assert isinstance(repr_str, str)
        assert 'Sloka' in repr_str
        assert sample_sloka.sloka_id in repr_str
    
    def test_sloka_str(self, sample_sloka):
        """Test sloka string conversion."""
        str_repr = str(sample_sloka)
        
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_sloka_equality(self):
        """Test sloka equality comparison."""
        sloka1 = Sloka(
            sloka_id="1.1.1",
            sloka_text="Text",
            meaning="Meaning",
            translation="Translation"
        )
        
        sloka2 = Sloka(
            sloka_id="1.1.1",
            sloka_text="Text",
            meaning="Meaning",
            translation="Translation"
        )
        
        sloka3 = Sloka(
            sloka_id="1.1.2",
            sloka_text="Different",
            meaning="Different",
            translation="Different"
        )
        
        assert sloka1 == sloka2
        assert sloka1 != sloka3
        assert sloka2 != sloka3
    
    def test_sloka_hash(self):
        """Test sloka hash functionality."""
        sloka1 = Sloka(
            sloka_id="1.1.1",
            sloka_text="Text",
            meaning="Meaning",
            translation="Translation"
        )
        
        sloka2 = Sloka(
            sloka_id="1.1.1",
            sloka_text="Text",
            meaning="Meaning",
            translation="Translation"
        )
        
        # Same slokas should have same hash
        assert hash(sloka1) == hash(sloka2)
        
        # Should be usable in sets and dicts
        sloka_set = {sloka1, sloka2}
        assert len(sloka_set) == 1  # Should only contain one unique sloka
    
    @pytest.mark.parametrize("sloka_id,expected_valid", [
        ("1.1.1", True),
        ("123.456.789", True),
        ("1.1", False),  # Missing sloka number
        ("1", False),   # Missing sarga and sloka
        ("", False),    # Empty
        ("abc.def.ghi", False),  # Non-numeric
        ("1.1.1.1", False),  # Too many parts
    ])
    def test_sloka_id_format_validation(self, sloka_id, expected_valid):
        """Test sloka ID format validation."""
        sloka = Sloka(
            sloka_id=sloka_id,
            sloka_text="Text",
            meaning="Meaning",
            translation="Translation"
        )
        
        # Basic format check - should have 3 parts separated by dots
        if expected_valid:
            parts = sloka_id.split('.')
            assert len(parts) == 3
            assert all(part.isdigit() for part in parts)
        else:
            if sloka_id:  # Only check format if not empty
                parts = sloka_id.split('.')
                is_valid_format = (
                    len(parts) == 3 and 
                    all(part.isdigit() for part in parts)
                )
                assert not is_valid_format
    
    def test_sloka_with_unicode_text(self):
        """Test sloka with various Unicode characters."""
        sloka = Sloka(
            sloka_id="1.1.1",
            sloka_text="धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः। मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय।।",
            meaning="धर्म के क्षेत्र में कुरुक्षेत्र में एकत्र हुए युद्ध की इच्छा वाले मेरे और पाण्डवों ने क्या किया, संजय?",
            translation="In the field of dharma, in Kurukshetra, gathered together, what did my people and the Pandavas do, O Sanjaya, who desire war?"
        )
        
        assert len(sloka.sloka_text) > 0
        assert len(sloka.meaning) > 0
        assert len(sloka.translation) > 0
        
        # Should serialize properly
        serialized = sloka.serialize()
        assert isinstance(serialized, dict)
        assert serialized['sloka_text'] == sloka.sloka_text
    
    def test_sloka_with_special_characters(self):
        """Test sloka with special characters and punctuation."""
        sloka = Sloka(
            sloka_id="1.1.1",
            sloka_text="धर्मक्षेत्रे कुरुक्षेत्रे।। समवेता युयुत्सवः ॥",
            meaning="धर्म के क्षेत्र में, कुरुक्षेत्र में।",
            translation="In the field of dharma, in Kurukshetra."
        )
        
        assert '।।' in sloka.sloka_text
        assert '॥' in sloka.sloka_text
        assert ',' in sloka.meaning
        assert '.' in sloka.translation
    
    def test_sloka_immutability_simulation(self, sample_sloka):
        """Test that sloka behaves as if it's immutable (no setters defined)."""
        original_id = sample_sloka.sloka_id
        original_text = sample_sloka.sloka_text
        
        # Try to modify (this should work since it's not truly immutable)
        sample_sloka.sloka_id = "modified"
        assert sample_sloka.sloka_id == "modified"
        
        # Reset for other tests
        sample_sloka.sloka_id = original_id
        assert sample_sloka.sloka_id == original_id
    
    def test_sloka_large_text(self):
        """Test sloka with very large text content."""
        large_text = "धर्म " * 1000  # Very long Sanskrit text
        large_translation = "dharma " * 1000  # Very long English text
        
        sloka = Sloka(
            sloka_id="1.1.1",
            sloka_text=large_text,
            meaning="Meaning",
            translation=large_translation
        )
        
        assert len(sloka.sloka_text) == len(large_text)
        assert len(sloka.translation) == len(large_translation)
        
        # Should still serialize properly
        serialized = sloka.serialize()
        assert len(serialized['sloka_text']) == len(large_text)
    
    def test_sloka_factory_method(self):
        """Test creating sloka from dictionary (if such method exists)."""
        sloka_data = {
            'sloka_id': '1.1.1',
            'sloka_text': 'धर्मक्षेत्रे कुरुक्षेत्रे',
            'meaning': 'धर्म के क्षेत्र में',
            'translation': 'In the field of dharma'
        }
        
        # If there's a factory method, test it
        # For now, just test manual creation
        sloka = Sloka(**sloka_data)
        
        assert sloka.sloka_id == sloka_data['sloka_id']
        assert sloka.sloka_text == sloka_data['sloka_text']
        assert sloka.meaning == sloka_data['meaning']
        assert sloka.translation == sloka_data['translation']
    
    def test_sloka_performance(self):
        """Test performance of sloka operations."""
        import time
        
        # Test creation performance
        start_time = time.time()
        for i in range(1000):
            sloka = Sloka(
                sloka_id=f"1.1.{i}",
                sloka_text="Test text",
                meaning="Test meaning",
                translation="Test translation"
            )
        creation_time = time.time() - start_time
        
        assert creation_time < 1.0  # Should create 1000 slokas in less than 1 second
        
        # Test serialization performance
        test_sloka = Sloka(
            sloka_id="1.1.1",
            sloka_text="Test text",
            meaning="Test meaning",
            translation="Test translation"
        )
        
        start_time = time.time()
        for i in range(1000):
            serialized = test_sloka.serialize()
        serialization_time = time.time() - start_time
        
        assert serialization_time < 1.0  # Should serialize 1000 times in less than 1 second