import unittest
import tempfile
import os
import sqlite3
import sys
sys.path.append('..')
from spell_checker import AdvancedSpellChecker
from database import MockWordDatabase

class TestMockWordDatabase(unittest.TestCase):
    """Test cases for MockWordDatabase"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = MockWordDatabase(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization"""
        self.assertTrue(os.path.exists(self.temp_db.name))
        
        # Check if tables exist
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('words', tables)
        self.assertIn('custom_words', tables)
        self.assertIn('spell_check_history', tables)
        
        conn.close()
    
    def test_word_frequency(self):
        """Test word frequency retrieval"""
        freq = self.db.get_word_frequency('the')
        self.assertGreater(freq, 0)
        
        freq = self.db.get_word_frequency('nonexistentword')
        self.assertEqual(freq, 0)
    
    def test_custom_words(self):
        """Test custom word functionality"""
        # Add custom word
        self.db.add_custom_word('testword')
        
        # Check if it exists
        self.assertTrue(self.db.is_custom_word('testword'))
        self.assertFalse(self.db.is_custom_word('notacustomword'))
    
    def test_get_all_words(self):
        """Test getting all words"""
        words = self.db.get_all_words()
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 0)
        self.assertIn('the', words)
    
    def test_log_spell_check(self):
        """Test spell check logging"""
        self.db.log_spell_check('test text', 'corrected text', 2)
        
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM spell_check_history")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, 1)
        conn.close()

class TestAdvancedSpellChecker(unittest.TestCase):
    """Test cases for AdvancedSpellChecker"""
    
    def setUp(self):
        """Set up test spell checker"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.spell_checker = AdvancedSpellChecker(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_db.name)
    
    def test_clean_word(self):
        """Test word cleaning"""
        self.assertEqual(self.spell_checker.clean_word('Hello!'), 'hello')
        self.assertEqual(self.spell_checker.clean_word('  Test  '), 'test')
        self.assertEqual(self.spell_checker.clean_word('UPPERCASE'), 'uppercase')
    
    def test_is_valid_word(self):
        """Test word validation"""
        self.assertTrue(self.spell_checker.is_valid_word('the'))
        self.assertTrue(self.spell_checker.is_valid_word('a'))
        self.assertFalse(self.spell_checker.is_valid_word('nonexistentword'))
        self.assertTrue(self.spell_checker.is_valid_word('x'))  # Short words are valid
    
    def test_edit_distance_suggestions(self):
        """Test edit distance suggestions"""
        suggestions = self.spell_checker.get_edit_distance_suggestions('teh')
        self.assertIsInstance(suggestions, list)
        
        # Should find 'the' as a suggestion
        suggestion_words = [s[0] for s in suggestions]
        self.assertIn('the', suggestion_words)
    
    def test_phonetic_suggestions(self):
        """Test phonetic suggestions"""
        suggestions = self.spell_checker.get_phonetic_suggestions('rite')
        self.assertIsInstance(suggestions, list)
    
    def test_generate_candidates(self):
        """Test candidate generation"""
        candidates = self.spell_checker.generate_candidates('test')
        self.assertIsInstance(candidates, set)
        self.assertGreater(len(candidates), 0)
        
        # Should include common variations
        self.assertIn('est', candidates)  # deletion
        self.assertIn('tests', candidates)  # insertion
    
    def test_correct_text(self):
        """Test text correction"""
        result = self.spell_checker.correct_text('I realy like this librarry.')
        
        self.assertIsInstance(result, dict)
        self.assertIn('original_text', result)
        self.assertIn('corrected_text', result)
        self.assertIn('corrections', result)
        self.assertIn('corrections_count', result)
        self.assertIn('confidence', result)
        
        self.assertGreater(result['corrections_count'], 0)
        self.assertGreater(result['confidence'], 0)
    
    def test_add_custom_word(self):
        """Test adding custom words"""
        self.spell_checker.add_custom_word('customword')
        self.assertTrue(self.spell_checker.is_valid_word('customword'))
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        stats = self.spell_checker.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('dictionary_size', stats)
        self.assertIn('custom_words', stats)
        self.assertIn('total_checks', stats)
        self.assertIn('max_edit_distance', stats)
        
        self.assertGreater(stats['dictionary_size'], 0)

class TestSpellCheckerIntegration(unittest.TestCase):
    """Integration tests for the complete spell checker system"""
    
    def setUp(self):
        """Set up integration test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.spell_checker = AdvancedSpellChecker(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_db.name)
    
    def test_complete_spell_check_workflow(self):
        """Test complete spell check workflow"""
        test_text = "I realy like this librarry. Ths projct is relly amzing!"
        
        result = self.spell_checker.correct_text(test_text)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result['original_text'], test_text)
        self.assertNotEqual(result['corrected_text'], test_text)
        self.assertGreater(result['corrections_count'], 0)
        
        # Verify corrections
        corrections = result['corrections']
        self.assertIsInstance(corrections, list)
        
        for correction in corrections:
            self.assertIn('original', correction)
            self.assertIn('corrected', correction)
            self.assertIn('suggestions', correction)
            self.assertIn('position', correction)
    
    def test_multiple_suggestions(self):
        """Test getting multiple types of suggestions"""
        word = 'teh'
        suggestions = self.spell_checker.get_suggestions(word)
        
        self.assertIsInstance(suggestions, dict)
        self.assertIn('edit_distance', suggestions)
        self.assertIn('phonetic', suggestions)
        self.assertIn('context', suggestions)
        self.assertIn('candidates', suggestions)
    
    def test_confidence_calculation(self):
        """Test confidence calculation"""
        # Test with perfect text (no corrections)
        result = self.spell_checker.correct_text('This is a perfect sentence.')
        self.assertEqual(result['confidence'], 1.0)
        
        # Test with corrections
        result = self.spell_checker.correct_text('I realy like this.')
        self.assertGreater(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1.0)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMockWordDatabase))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAdvancedSpellChecker))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSpellCheckerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
