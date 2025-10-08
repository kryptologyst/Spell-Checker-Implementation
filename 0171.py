# Project 171. Advanced Spell Checker Implementation
# Description:
# A comprehensive spell checker that automatically detects and suggests corrections for misspelled words.
# This implementation uses multiple algorithms including Levenshtein distance, phonetic matching,
# context-aware suggestions, and word frequency analysis. Features a modern web UI and database.

# Modern Implementation with Advanced Features:
# - Multiple spell checking algorithms (Levenshtein, phonetic, context-aware)
# - SQLite database with word frequency data
# - Flask web interface with real-time spell checking
# - Custom dictionary support
# - Comprehensive test suite
# - RESTful API endpoints

from spell_checker import AdvancedSpellChecker
import json

def main():
    """Main function demonstrating the advanced spell checker"""
    print("🔍 Advanced Spell Checker Demo\n")
    
    # Initialize the spell checker
    spell_checker = AdvancedSpellChecker()
    
    # Example sentences with spelling mistakes
    test_sentences = [
        "I realy like this librarry.",
        "Ths projct is relly amzing!",
        "Welcom to the wrld of NLP.",
        "The quik brown fox jumps over the lazy dog.",
        "Speling erors are commen in writen text."
    ]
    
    print("=" * 60)
    print("SPELL CHECKING RESULTS")
    print("=" * 60)
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n{i}. Testing: '{sentence}'")
        print("-" * 50)
        
        # Get comprehensive spell check results
        result = spell_checker.correct_text(sentence)
        
        print(f"❌ Original:  {result['original_text']}")
        print(f"✅ Corrected: {result['corrected_text']}")
        print(f"📊 Corrections: {result['corrections_count']}")
        print(f"🎯 Confidence: {result['confidence']:.2%}")
        
        # Show detailed corrections
        if result['corrections']:
            print("\n📝 Detailed Corrections:")
            for correction in result['corrections']:
                print(f"   • '{correction['original']}' → '{correction['corrected']}'")
                
                # Show suggestions
                suggestions = correction['suggestions']
                if suggestions['edit_distance']:
                    print(f"     Edit Distance: {', '.join(suggestions['edit_distance'][:3])}")
                if suggestions['phonetic']:
                    print(f"     Phonetic: {', '.join(suggestions['phonetic'][:3])}")
    
    # Show statistics
    print("\n" + "=" * 60)
    print("SPELL CHECKER STATISTICS")
    print("=" * 60)
    
    stats = spell_checker.get_statistics()
    print(f"📚 Dictionary Size: {stats['dictionary_size']:,} words")
    print(f"🔧 Custom Words: {stats['custom_words']:,}")
    print(f"🔍 Total Checks: {stats['total_checks']:,}")
    print(f"📏 Max Edit Distance: {stats['max_edit_distance']}")
    
    # Demonstrate custom word addition
    print("\n" + "=" * 60)
    print("CUSTOM DICTIONARY DEMO")
    print("=" * 60)
    
    custom_words = ["GitHub", "API", "NLP", "machine learning"]
    print("Adding custom words to dictionary...")
    
    for word in custom_words:
        spell_checker.add_custom_word(word)
        print(f"✅ Added: '{word}'")
    
    # Test with custom words
    test_with_custom = "I love GitHub and NLP APIs!"
    result = spell_checker.correct_text(test_with_custom)
    print(f"\nTesting with custom words: '{test_with_custom}'")
    print(f"Result: '{result['corrected_text']}'")
    print(f"Corrections needed: {result['corrections_count']}")
    
    print("\n" + "=" * 60)
    print("🚀 To run the web interface:")
    print("   python app.py")
    print("   Then visit: http://localhost:5001")
    print("=" * 60)

if __name__ == "__main__":
    main()