"""
Comprehensive tests for entity extraction systems
Tests both pattern-based and enhanced NLP approaches
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.services.automated_entity_extraction import RamayanaEntityExtractor, EntityPattern, ExtractionResult
from api.models.kg_models import EntityType


class TestPatternBasedExtraction(unittest.TestCase):
    """Test the current pattern-based entity extraction"""
    
    def setUp(self):
        """Set up test environment"""
        self.extractor = RamayanaEntityExtractor()
        
        # Create temporary test data directory
        self.test_data_dir = tempfile.mkdtemp()
        self.test_kanda_dir = Path(self.test_data_dir) / "TestKanda"
        self.test_kanda_dir.mkdir()
        
        # Create test files
        self._create_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_data_dir)
    
    def _create_test_files(self):
        """Create test sloka files"""
        # Test sloka file
        sloka_file = self.test_kanda_dir / "TestKanda_sarga_1_sloka.txt"
        sloka_content = [
            "1::1::1::राम नाम सत्य है धर्म के साथ।",
            "1::1::2::सीता माता वैदेही जानकी नाम से।",
            "1::1::3::हनुमान पवनात्मज वायुपुत्र महावीर।",
            "1::1::4::अयोध्या नगर में राजा दशरथ राज्य।",
            "1::1::5::रावण दशग्रीव लङ्केश लङ्का में।"
        ]
        with open(sloka_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sloka_content))
        
        # Test translation file
        translation_file = self.test_kanda_dir / "TestKanda_sarga_1_translation.txt"
        translation_content = [
            "1::1::1::Rama's name is truth with dharma.",
            "1::1::2::Sita mother called Vaidehi and Janaki.",
            "1::1::3::Hanuman son of wind god, great hero Maruti.",
            "1::1::4::In Ayodhya city, king Dasharatha rules.",
            "1::1::5::Ravana ten-headed, Lankesa in Lanka."
        ]
        with open(translation_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(translation_content))
        
        # Test meaning file
        meaning_file = self.test_kanda_dir / "TestKanda_sarga_1_meaning.txt"
        meaning_content = [
            "1::1::1::राम = name of prince, नाम = name, सत्य = truth, धर्म = duty",
            "1::1::2::सीता = name of princess, माता = mother, वैदेही = daughter of Videha, जानकी = daughter of Janaka",
            "1::1::3::हनुमान = name of monkey hero, पवनात्मज = son of wind god, वायुपुत्र = son of Vayu",
            "1::1::4::अयोध्या = name of city, नगर = city, दशरथ = name of king, राज्य = kingdom",
            "1::1::5::रावण = name of demon king, दशग्रीव = ten-headed, लङ्का = name of island"
        ]
        with open(meaning_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(meaning_content))
    
    def test_entity_pattern_creation(self):
        """Test EntityPattern creation"""
        pattern = EntityPattern(
            entity_id="test_rama",
            entity_type=EntityType.PERSON,
            sanskrit_patterns=[r'राम[ःोम्स्य]?'],
            english_patterns=[r'\bRama\b'],
            epithets=['राघव']
        )
        
        self.assertEqual(pattern.entity_id, "test_rama")
        self.assertEqual(pattern.entity_type, EntityType.PERSON)
        self.assertEqual(len(pattern.sanskrit_patterns), 1)
        self.assertEqual(len(pattern.english_patterns), 1)
        self.assertEqual(pattern.epithets, ['राघव'])
    
    def test_pattern_definitions(self):
        """Test that all required patterns are defined"""
        patterns = self.extractor._define_entity_patterns()
        
        # Check that major characters are included
        entity_ids = [p.entity_id for p in patterns]
        expected_entities = ['rama', 'sita', 'hanuman', 'ravana', 'lakshmana']
        
        for entity in expected_entities:
            self.assertIn(entity, entity_ids, f"Missing entity: {entity}")
        
        # Check pattern structure
        for pattern in patterns:
            self.assertIsInstance(pattern.entity_id, str)
            self.assertIsInstance(pattern.entity_type, EntityType)
            self.assertIsInstance(pattern.sanskrit_patterns, list)
            self.assertIsInstance(pattern.english_patterns, list)
            self.assertTrue(len(pattern.sanskrit_patterns) > 0 or len(pattern.english_patterns) > 0)
    
    def test_sanskrit_pattern_matching(self):
        """Test Sanskrit pattern matching"""
        test_text = "राम नाम सत्य है और राघव महान्"
        results = self.extractor._extract_from_text(test_text, 'sanskrit')
        
        # Should find Rama entities
        rama_results = [r for r in results if r.entity_id == 'rama']
        self.assertTrue(len(rama_results) > 0, "Should find Rama in Sanskrit text")
        
        # Check result structure
        for result in rama_results:
            self.assertIsInstance(result, ExtractionResult)
            self.assertEqual(result.source_type, 'sanskrit')
            self.assertGreater(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)
    
    def test_english_pattern_matching(self):
        """Test English pattern matching"""
        test_text = "Rama and Sita went to the forest with Lakshmana"
        results = self.extractor._extract_from_text(test_text, 'translation')
        
        # Should find multiple entities
        entity_ids = [r.entity_id for r in results]
        expected_entities = ['rama', 'sita', 'lakshmana']
        
        for entity in expected_entities:
            self.assertIn(entity, entity_ids, f"Should find {entity} in English text")
    
    def test_confidence_scoring(self):
        """Test confidence scoring mechanism"""
        # Text with multiple matches should have higher confidence
        high_match_text = "राम राम राम"
        results_high = self.extractor._extract_from_text(high_match_text, 'sanskrit')
        
        # Text with single match
        low_match_text = "राम"
        results_low = self.extractor._extract_from_text(low_match_text, 'sanskrit')
        
        if results_high and results_low:
            self.assertGreaterEqual(
                results_high[0].confidence, 
                results_low[0].confidence,
                "Multiple matches should have higher confidence"
            )
    
    def test_file_reading(self):
        """Test file reading functionality"""
        # Test existing file
        content = self.extractor._read_file_content(
            self.test_kanda_dir / "TestKanda_sarga_1_sloka.txt"
        )
        self.assertTrue(len(content) > 0, "Should read content from existing file")
        
        # Test non-existent file
        content_empty = self.extractor._read_file_content(
            self.test_kanda_dir / "nonexistent.txt"
        )
        self.assertEqual(len(content_empty), 0, "Should return empty list for non-existent file")
    
    def test_sloka_parsing(self):
        """Test sloka line parsing"""
        # Valid sloka line
        valid_line = "1::2::3::राम नाम सत्य है"
        result = self.extractor._parse_sloka_line(valid_line)
        self.assertIsNotNone(result)
        self.assertEqual(result, ("1", "2", "3", "राम नाम सत्य है"))
        
        # Invalid sloka line
        invalid_line = "invalid format"
        result_invalid = self.extractor._parse_sloka_line(invalid_line)
        self.assertIsNone(result_invalid)
    
    def test_text_correspondence(self):
        """Test finding corresponding text across files"""
        # Create test translation lines
        translation_lines = [
            "1::1::1::Rama's name is truth",
            "1::1::2::Sita is mother"
        ]
        
        # Test finding existing correspondence
        result = self.extractor._find_corresponding_text(translation_lines, "1", "1", "1")
        self.assertEqual(result, "Rama's name is truth")
        
        # Test missing correspondence
        result_missing = self.extractor._find_corresponding_text(translation_lines, "1", "1", "99")
        self.assertEqual(result_missing, "")
    
    def test_entity_creation_from_pattern(self):
        """Test entity creation from patterns"""
        entity = self.extractor._create_entity_from_pattern("rama")
        
        self.assertIsNotNone(entity)
        self.assertEqual(entity.entity_type, EntityType.PERSON)
        self.assertIn('en', entity.labels)
        self.assertIn('sa', entity.labels)
        self.assertIn('epithets', entity.properties)
    
    def test_entity_validation_and_enhancement(self):
        """Test entity validation logic"""
        # Create test entities with different occurrence counts
        rama_entity = Mock()
        rama_entity.properties = {}
        rare_entity = Mock()
        rare_entity.properties = {}
        
        test_entities = {
            'rama': rama_entity,
            'rare_entity': rare_entity
        }
        
        # Mock statistics for testing
        self.extractor.extraction_stats['entities_found'] = {
            'rama': 10,  # Above threshold
            'rare_entity': 1  # Below threshold
        }
        
        enhanced = self.extractor._validate_and_enhance_entities(test_entities)
        
        # Should keep high-occurrence entities
        self.assertIn('rama', enhanced)
        # Should filter out low-occurrence entities
        self.assertNotIn('rare_entity', enhanced)
    
    def test_extraction_statistics(self):
        """Test statistics tracking"""
        # Reset stats with defaultdict
        self.extractor.extraction_stats = {
            'processed_slokas': 0,
            'entities_found': defaultdict(int),
            'confidence_scores': [],
            'patterns_matched': defaultdict(int)
        }
        
        # Process test text
        test_text = "राम और सीता"
        self.extractor._extract_from_text(test_text, 'sanskrit')
        
        # Check that statistics are updated
        self.assertGreater(len(self.extractor.extraction_stats['patterns_matched']), 0)
    
    def test_full_extraction_workflow(self):
        """Test the complete extraction workflow"""
        # Override the data path to use our test directory
        self.extractor.data_path = self.test_data_dir
        
        # Run extraction
        results = self.extractor.extract_entities_from_corpus()
        
        # Verify results structure
        self.assertIn('entities', results)
        self.assertIn('relationships', results)
        self.assertIn('annotations', results)
        self.assertIn('statistics', results)
        
        # Check that entities were found
        entities = results['entities']
        self.assertGreater(len(entities), 0, "Should find some entities")
        
        # Check annotations were created
        annotations = results['annotations']
        self.assertGreater(len(annotations), 0, "Should create annotations")
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with empty text
        results_empty = self.extractor._extract_from_text("", 'sanskrit')
        self.assertEqual(len(results_empty), 0)
        
        # Test with None text
        results_none = self.extractor._extract_from_text(None, 'sanskrit')
        self.assertEqual(len(results_none), 0)
        
        # Test with malformed patterns (should not crash)
        try:
            invalid_extractor = RamayanaEntityExtractor()
            # This should handle gracefully
            invalid_extractor._extract_from_text("test", 'sanskrit')
        except Exception as e:
            self.fail(f"Should handle errors gracefully: {e}")


class TestEnhancedEntityExtraction(unittest.TestCase):
    """Test the enhanced NLP-based entity extraction"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock NLP dependencies to avoid requiring actual installations
        self.mock_spacy = MagicMock()
        self.mock_transformers = MagicMock()
        
        # Create test data
        self.test_data_dir = tempfile.mkdtemp()
        self._create_test_files()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_data_dir)
    
    def _create_test_files(self):
        """Create enhanced test files with more complex data"""
        test_kanda_dir = Path(self.test_data_dir) / "TestKanda"
        test_kanda_dir.mkdir()
        
        # More complex test data
        sloka_file = test_kanda_dir / "TestKanda_sarga_1_sloka.txt"
        sloka_content = [
            "1::1::1::श्री रामचन्द्र राघव दाशरथि काकुत्स्थ कोसलेन्द्र।",
            "1::1::2::सीता मैथिली वैदेही जानकी भूमिजा देवी।",
            "1::1::3::हनुमान् पवनात्मज वायुपुत्र मारुति अञ्जनेय महावीर।",
            "1::1::4::लक्ष्मण सौमित्रि भ्राता रामस्य सहचर।",
            "1::1::5::रावण दशग्रीव लङ्केश रक्षसराज असुर।"
        ]
        with open(sloka_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sloka_content))
        
        # Enhanced translations with proper nouns
        translation_file = test_kanda_dir / "TestKanda_sarga_1_translation.txt"
        translation_content = [
            "1::1::1::Lord Ramachandra, Raghava, son of Dasharatha, of Kakutstha lineage, lord of Kosala.",
            "1::1::2::Sita, princess of Mithila, daughter of Videha king, Janaki, earth-born goddess.",
            "1::1::3::Hanuman, son of wind god Pavana, Vayu's son Maruti, son of Anjana, great hero.",
            "1::1::4::Lakshmana, son of Sumitra, brother of Rama, his companion.",
            "1::1::5::Ravana, the ten-headed demon king, lord of Lanka, king of Rakshasas."
        ]
        with open(translation_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(translation_content))
        
        # Enhanced meanings with clear entity definitions
        meaning_file = test_kanda_dir / "TestKanda_sarga_1_meaning.txt"
        meaning_content = [
            "1::1::1::रामचन्द्र = name of prince of Ayodhya, राघव = descendant of Raghu, दाशरथि = son of Dasharatha",
            "1::1::2::सीता = name of princess, wife of Rama, मैथिली = princess of Mithila, जानकी = daughter of king Janaka",
            "1::1::3::हनुमान् = name of monkey hero, devotee of Rama, पवनात्मज = son of wind god, मारुति = name of Hanuman",
            "1::1::4::लक्ष्मण = name of prince, brother of Rama, सौमित्रि = son of queen Sumitra",
            "1::1::5::रावण = name of demon king of Lanka, दशग्रीव = having ten heads, लङ्केश = lord of Lanka"
        ]
        with open(meaning_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(meaning_content))
    
    @patch('api.services.enhanced_entity_extraction.spacy')
    def test_enhanced_extractor_initialization(self, mock_spacy):
        """Test enhanced extractor initialization"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        # Mock spacy.load to avoid requiring actual model
        mock_nlp = MagicMock()
        mock_spacy.load.return_value = mock_nlp
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        
        # Should initialize properly
        self.assertIsNotNone(extractor.sanskrit_patterns)
        self.assertIsNotNone(extractor.transliteration_map)
        self.assertIsNotNone(extractor.known_epithets)
    
    def test_sanskrit_pattern_loading(self):
        """Test Sanskrit pattern definitions"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        patterns = extractor._load_sanskrit_patterns()
        
        # Should have all entity type patterns
        expected_types = ['person_patterns', 'place_patterns', 'concept_patterns']
        for pattern_type in expected_types:
            self.assertIn(pattern_type, patterns)
            self.assertIsInstance(patterns[pattern_type], list)
            self.assertGreater(len(patterns[pattern_type]), 0)
    
    def test_transliteration_mapping(self):
        """Test transliteration functionality"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        
        # Test known transliterations
        self.assertEqual(extractor._transliterate('राम'), 'Rama')
        self.assertEqual(extractor._transliterate('सीता'), 'Sita')
        
        # Test unknown word (should return as-is)
        unknown_word = 'अज्ञात'
        self.assertEqual(extractor._transliterate(unknown_word), unknown_word)
    
    def test_epithet_recognition(self):
        """Test epithet recognition system"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        epithets = extractor._load_known_epithets()
        
        # Should have epithets for major characters
        self.assertIn('rama', epithets)
        self.assertIn('राघव', epithets['rama'])
        self.assertIn('दाशरथि', epithets['rama'])
        
        self.assertIn('hanuman', epithets)
        self.assertIn('पवनात्मज', epithets['hanuman'])
    
    def test_sanskrit_text_detection(self):
        """Test Sanskrit text detection"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        
        # Sanskrit text should be detected
        self.assertTrue(extractor._is_sanskrit_text('राम नाम सत्य'))
        
        # English text should not be detected as Sanskrit
        self.assertFalse(extractor._is_sanskrit_text('Rama name truth'))
        
        # Mixed text should be detected as Sanskrit
        self.assertTrue(extractor._is_sanskrit_text('राम and Sita'))
    
    def test_proper_noun_detection(self):
        """Test proper noun detection from meanings"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        
        # Should detect proper nouns
        self.assertTrue(extractor._is_likely_proper_noun('राम', 'name of prince'))
        self.assertTrue(extractor._is_likely_proper_noun('अयोध्या', 'name of city'))
        
        # Should not detect common words
        self.assertFalse(extractor._is_likely_proper_noun('जल', 'water'))
        self.assertFalse(extractor._is_likely_proper_noun('वृक्ष', 'tree'))
    
    def test_entity_type_classification(self):
        """Test entity type classification from meanings"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        
        # Test person classification
        self.assertEqual(extractor._classify_from_meaning('name of king'), 'person')
        self.assertEqual(extractor._classify_from_meaning('son of Dasharatha'), 'person')
        
        # Test place classification
        self.assertEqual(extractor._classify_from_meaning('name of city'), 'place')
        self.assertEqual(extractor._classify_from_meaning('holy mountain'), 'place')
        
        # Test concept classification
        self.assertEqual(extractor._classify_from_meaning('dharma and duty'), 'concept')
    
    def test_text_normalization(self):
        """Test entity text normalization"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        
        # Should normalize Sanskrit case endings
        self.assertEqual(extractor._normalize_entity_text('रामः'), 'राम')
        self.assertEqual(extractor._normalize_entity_text('रामम्'), 'राम')
        self.assertEqual(extractor._normalize_entity_text('रामस्य'), 'राम')
        
        # Should handle lowercase
        self.assertEqual(extractor._normalize_entity_text('RAMA'), 'rama')
    
    def test_confidence_calculation(self):
        """Test aggregate confidence calculation"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor, EntityCandidate
        
        extractor = SanskritEntityExtractor(use_external_apis=False)
        
        # Create test candidates with different methods and confidences
        candidates = [
            EntityCandidate(
                text='राम', start=0, end=3, entity_type='person',
                confidence=0.9, extraction_method='epithet_recognition', context='test'
            ),
            EntityCandidate(
                text='Rama', start=0, end=4, entity_type='person',
                confidence=0.8, extraction_method='spacy_ner', context='test'
            ),
            EntityCandidate(
                text='राम', start=0, end=3, entity_type='person',
                confidence=0.7, extraction_method='sanskrit_pattern', context='test'
            )
        ]
        
        confidence = extractor._calculate_aggregate_confidence(candidates)
        
        # Should be weighted average with higher confidence
        self.assertGreater(confidence, 0.7)
        self.assertLessEqual(confidence, 1.0)
    
    @patch('api.services.enhanced_entity_extraction.spacy')
    @patch('api.services.enhanced_entity_extraction.pipeline')
    def test_mock_nlp_extraction(self, mock_pipeline, mock_spacy):
        """Test NLP extraction with mocked models"""
        from api.services.enhanced_entity_extraction import SanskritEntityExtractor, EntityCandidate
        
        # Mock spaCy NER
        mock_ent = MagicMock()
        mock_ent.text = 'Rama'
        mock_ent.start_char = 0
        mock_ent.end_char = 4
        mock_ent.label_ = 'PERSON'
        
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]
        
        mock_nlp = MagicMock()
        mock_nlp.return_value = mock_doc
        mock_spacy.load.return_value = mock_nlp
        
        # Mock transformer pipeline
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.return_value = [
            {
                'word': 'Sita',
                'start': 5,
                'end': 9,
                'entity_group': 'PER',
                'score': 0.95
            }
        ]
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Test extraction
        extractor = SanskritEntityExtractor(use_external_apis=False)
        candidates = extractor._extract_english_nlp('Rama and Sita', 'test_id', 'translation')
        
        # Should find entities from both models
        self.assertGreater(len(candidates), 0)
        
        # Check candidate structure
        for candidate in candidates:
            self.assertIsInstance(candidate, EntityCandidate)
            self.assertIn(candidate.extraction_method, ['spacy_ner', 'transformer_ner'])


class TestEntityExtractionIntegration(unittest.TestCase):
    """Integration tests for entity extraction with database"""
    
    def setUp(self):
        """Set up integration test environment"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        # Create test data directory
        self.test_data_dir = tempfile.mkdtemp()
        self._create_realistic_test_data()
    
    def tearDown(self):
        """Clean up integration test environment"""
        os.unlink(self.temp_db.name)
        shutil.rmtree(self.test_data_dir)
    
    def _create_realistic_test_data(self):
        """Create realistic test data with real Sanskrit content"""
        test_kanda_dir = Path(self.test_data_dir) / "BalaKanda"
        test_kanda_dir.mkdir()
        
        # Real-looking Sanskrit content
        sloka_file = test_kanda_dir / "BalaKanda_sarga_1_sloka.txt"
        sloka_content = [
            "1::1::1::तपस्स्वाध्यायनिरतं तपस्वी वाग्विदां वरम्।",
            "1::1::2::नारदं परिपप्रच्छ वाल्मीकिर्मुनिपुङ्गवम्॥",
            "1::1::3::को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्।",
            "1::1::4::धर्मज्ञश्च कृतज्ञश्च सत्यवाक्यो दृढव्रतः॥",
            "1::1::5::चारित्रेण च को युक्तः सर्वभूतेषु को हितः।"
        ]
        with open(sloka_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sloka_content))
        
        # Corresponding translations
        translation_file = test_kanda_dir / "BalaKanda_sarga_1_translation.txt"
        translation_content = [
            "1::1::1::To Narada, who was absorbed in penance and study, the best among eloquent speakers,",
            "1::1::2::Valmiki, the foremost among sages, respectfully asked:",
            "1::1::3::Who in this world at present is virtuous and powerful?",
            "1::1::4::Who knows dharma, is grateful, truthful, and steadfast in vows?",
            "1::1::5::Who is endowed with good character and beneficial to all beings?"
        ]
        with open(translation_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(translation_content))
        
        # Word meanings
        meaning_file = test_kanda_dir / "BalaKanda_sarga_1_meaning.txt"
        meaning_content = [
            "1::1::1::तपस् = penance, स्वाध्याय = study, निरतं = absorbed, नारदं = to sage Narada",
            "1::1::2::परिपप्रच्छ = asked respectfully, वाल्मीकिः = sage Valmiki, मुनिपुङ्गवम् = best among sages",
            "1::1::3::कः = who, साम्प्रतं = at present, लोके = in world, गुणवान् = virtuous, वीर्यवान् = powerful",
            "1::1::4::धर्मज्ञः = knower of dharma, कृतज्ञः = grateful, सत्यवाक्यः = truthful, दृढव्रतः = firm in vows",
            "1::1::5::चारित्रेण = by character, युक्तः = endowed, सर्वभूतेषु = in all beings, हितः = beneficial"
        ]
        with open(meaning_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(meaning_content))
    
    def test_integration_with_database_service(self):
        """Test integration with KG database service"""
        from api.services.kg_database_service import KGDatabaseService
        
        # Create database service with temp database
        db_service = KGDatabaseService(db_path=self.temp_db.name)
        
        # Initialize database tables (would need actual schema)
        # This would require running the SQL schema first
        
        # For now, just test that the service can be created
        self.assertIsNotNone(db_service)
    
    def test_extraction_performance(self):
        """Test extraction performance with larger dataset"""
        extractor = RamayanaEntityExtractor(data_path=self.test_data_dir)
        
        import time
        start_time = time.time()
        
        # Run extraction on test data
        results = extractor.extract_entities_from_corpus()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(processing_time, 10.0, "Extraction should complete within 10 seconds")
        
        # Should produce valid results
        self.assertIn('entities', results)
        self.assertIn('statistics', results)
    
    def test_extraction_consistency(self):
        """Test that extraction produces consistent results"""
        extractor = RamayanaEntityExtractor(data_path=self.test_data_dir)
        
        # Run extraction twice
        results1 = extractor.extract_entities_from_corpus()
        results2 = extractor.extract_entities_from_corpus()
        
        # Should produce same number of entities
        self.assertEqual(
            len(results1['entities']), 
            len(results2['entities']),
            "Should produce consistent entity counts"
        )


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)