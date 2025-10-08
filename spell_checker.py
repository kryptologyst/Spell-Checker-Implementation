import re
import string
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict, Counter
import sqlite3

# Try to import optional dependencies, fall back to basic implementations
try:
    import Levenshtein
    HAS_LEVENSHTEIN = True
except ImportError:
    HAS_LEVENSHTEIN = False

try:
    from phonetics import metaphone, soundex
    HAS_PHONETICS = True
except ImportError:
    HAS_PHONETICS = False

try:
    import textdistance
    HAS_TEXTDISTANCE = True
except ImportError:
    HAS_TEXTDISTANCE = False

from database import MockWordDatabase

def simple_levenshtein_distance(s1: str, s2: str) -> int:
    """Simple Levenshtein distance implementation"""
    if len(s1) < len(s2):
        return simple_levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def simple_metaphone(word: str) -> str:
    """Simple phonetic representation"""
    # Basic phonetic mapping
    phonetic_map = {
        'ph': 'f', 'ch': 'x', 'sh': 'x', 'th': '0',
        'ck': 'k', 'qu': 'kw', 'x': 'ks'
    }
    
    result = word.lower()
    for pattern, replacement in phonetic_map.items():
        result = result.replace(pattern, replacement)
    
    return result

def simple_soundex(word: str) -> str:
    """Simple Soundex implementation"""
    if not word:
        return "0000"
    
    word = word.upper()
    first_char = word[0]
    
    # Remove vowels and similar consonants
    word = word.replace('A', '').replace('E', '').replace('I', '').replace('O', '').replace('U', '')
    word = word.replace('H', '').replace('W', '').replace('Y', '')
    
    # Map consonants to numbers
    soundex_map = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    
    result = first_char
    for char in word[1:]:
        if char in soundex_map:
            result += soundex_map[char]
    
    # Pad with zeros
    result = result.ljust(4, '0')[:4]
    return result

class AdvancedSpellChecker:
    """Advanced spell checker with multiple algorithms and techniques"""
    
    def __init__(self, db_path: str = "word_database.db"):
        self.db = MockWordDatabase(db_path)
        self.dictionary = set(self.db.get_all_words())
        self.max_distance = 2
        self.min_word_length = 2
        
    def clean_word(self, word: str) -> str:
        """Clean and normalize a word"""
        # Remove punctuation and convert to lowercase
        cleaned = re.sub(r'[^\w\s]', '', word.lower())
        return cleaned.strip()
    
    def is_valid_word(self, word: str) -> bool:
        """Check if word is valid (exists in dictionary or custom words)"""
        cleaned = self.clean_word(word)
        if len(cleaned) < self.min_word_length:
            return True  # Skip very short words
        
        return (cleaned in self.dictionary or 
                self.db.is_custom_word(cleaned))
    
    def get_edit_distance_suggestions(self, word: str, max_distance: int = 2) -> List[Tuple[str, int, int]]:
        """Get suggestions using Levenshtein distance"""
        suggestions = []
        cleaned_word = self.clean_word(word)
        
        for dict_word in self.dictionary:
            if HAS_LEVENSHTEIN:
                distance = Levenshtein.distance(cleaned_word, dict_word)
            else:
                distance = simple_levenshtein_distance(cleaned_word, dict_word)
            
            if distance <= max_distance and distance > 0:
                frequency = self.db.get_word_frequency(dict_word)
                suggestions.append((dict_word, distance, frequency))
        
        # Sort by distance first, then by frequency
        suggestions.sort(key=lambda x: (x[1], -x[2]))
        return suggestions[:10]  # Return top 10 suggestions
    
    def get_phonetic_suggestions(self, word: str) -> List[str]:
        """Get suggestions using phonetic matching"""
        cleaned_word = self.clean_word(word)
        
        if HAS_PHONETICS:
            word_metaphone = metaphone(cleaned_word)
            word_soundex = soundex(cleaned_word)
        else:
            word_metaphone = simple_metaphone(cleaned_word)
            word_soundex = simple_soundex(cleaned_word)
        
        suggestions = []
        for dict_word in self.dictionary:
            if HAS_PHONETICS:
                dict_metaphone = metaphone(dict_word)
                dict_soundex = soundex(dict_word)
            else:
                dict_metaphone = simple_metaphone(dict_word)
                dict_soundex = simple_soundex(dict_word)
            
            # Check if phonetic codes match
            if (word_metaphone == dict_metaphone or 
                word_soundex == dict_soundex):
                suggestions.append(dict_word)
        
        return suggestions[:5]
    
    def get_context_suggestions(self, word: str, context_words: List[str]) -> List[Tuple[str, float]]:
        """Get context-aware suggestions based on surrounding words"""
        cleaned_word = self.clean_word(word)
        suggestions = []
        
        # Simple context analysis - look for words that commonly appear together
        for dict_word in self.dictionary:
            if HAS_LEVENSHTEIN:
                distance = Levenshtein.distance(cleaned_word, dict_word)
            else:
                distance = simple_levenshtein_distance(cleaned_word, dict_word)
            
            if distance <= 2:
                # Calculate context score based on co-occurrence
                context_score = 0
                for context_word in context_words:
                    if context_word in self.dictionary:
                        # Simple co-occurrence scoring (in real implementation, 
                        # you'd use pre-computed co-occurrence matrices)
                        context_score += 0.1
                
                if context_score > 0:
                    suggestions.append((dict_word, context_score))
        
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:5]
    
    def generate_candidates(self, word: str) -> Set[str]:
        """Generate candidate words using various techniques"""
        candidates = set()
        cleaned_word = self.clean_word(word)
        
        # 1. Character deletion
        for i in range(len(cleaned_word)):
            candidate = cleaned_word[:i] + cleaned_word[i+1:]
            if len(candidate) >= self.min_word_length:
                candidates.add(candidate)
        
        # 2. Character insertion
        for i in range(len(cleaned_word) + 1):
            for char in 'abcdefghijklmnopqrstuvwxyz':
                candidate = cleaned_word[:i] + char + cleaned_word[i:]
                candidates.add(candidate)
        
        # 3. Character substitution
        for i in range(len(cleaned_word)):
            for char in 'abcdefghijklmnopqrstuvwxyz':
                candidate = cleaned_word[:i] + char + cleaned_word[i+1:]
                candidates.add(candidate)
        
        # 4. Character transposition
        for i in range(len(cleaned_word) - 1):
            candidate = (cleaned_word[:i] + 
                        cleaned_word[i+1] + 
                        cleaned_word[i] + 
                        cleaned_word[i+2:])
            candidates.add(candidate)
        
        return candidates
    
    def get_suggestions(self, word: str, context: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """Get comprehensive suggestions for a misspelled word"""
        if self.is_valid_word(word):
            return {"exact_match": [word]}
        
        suggestions = {
            "edit_distance": [],
            "phonetic": [],
            "context": [],
            "candidates": []
        }
        
        # Edit distance suggestions
        edit_suggestions = self.get_edit_distance_suggestions(word)
        suggestions["edit_distance"] = [s[0] for s in edit_suggestions]
        
        # Phonetic suggestions
        phonetic_suggestions = self.get_phonetic_suggestions(word)
        suggestions["phonetic"] = phonetic_suggestions
        
        # Context suggestions
        if context:
            context_suggestions = self.get_context_suggestions(word, context)
            suggestions["context"] = [s[0] for s in context_suggestions]
        
        # Candidate generation
        candidates = self.generate_candidates(word)
        valid_candidates = [c for c in candidates if c in self.dictionary]
        suggestions["candidates"] = valid_candidates[:5]
        
        return suggestions
    
    def correct_text(self, text: str) -> Dict[str, any]:
        """Correct spelling errors in text and return detailed results"""
        words = re.findall(r'\b\w+\b', text)
        corrections = []
        corrected_text = text
        
        for i, word in enumerate(words):
            if not self.is_valid_word(word):
                # Get context (previous and next words)
                context = []
                if i > 0:
                    context.append(words[i-1])
                if i < len(words) - 1:
                    context.append(words[i+1])
                
                suggestions = self.get_suggestions(word, context)
                
                # Choose best suggestion (prioritize edit distance)
                best_suggestion = None
                if suggestions["edit_distance"]:
                    best_suggestion = suggestions["edit_distance"][0]
                elif suggestions["phonetic"]:
                    best_suggestion = suggestions["phonetic"][0]
                elif suggestions["candidates"]:
                    best_suggestion = suggestions["candidates"][0]
                
                if best_suggestion:
                    corrections.append({
                        "original": word,
                        "corrected": best_suggestion,
                        "suggestions": suggestions,
                        "position": i
                    })
                    
                    # Replace in corrected text
                    corrected_text = corrected_text.replace(word, best_suggestion, 1)
        
        # Log the spell check activity
        self.db.log_spell_check(text, corrected_text, len(corrections))
        
        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "corrections": corrections,
            "corrections_count": len(corrections),
            "confidence": self._calculate_confidence(corrections)
        }
    
    def _calculate_confidence(self, corrections: List[Dict]) -> float:
        """Calculate confidence score for corrections"""
        if not corrections:
            return 1.0
        
        total_confidence = 0
        for correction in corrections:
            # Simple confidence based on edit distance
            suggestions = correction["suggestions"]
            if suggestions["edit_distance"]:
                # Higher confidence for shorter edit distances
                if HAS_LEVENSHTEIN:
                    distance = Levenshtein.distance(
                        correction["original"], 
                        correction["corrected"]
                    )
                else:
                    distance = simple_levenshtein_distance(
                        correction["original"], 
                        correction["corrected"]
                    )
                confidence = max(0.1, 1.0 - (distance * 0.3))
            else:
                confidence = 0.5  # Lower confidence for phonetic/candidate matches
            
            total_confidence += confidence
        
        return total_confidence / len(corrections)
    
    def add_custom_word(self, word: str, user_id: str = "default"):
        """Add a word to custom dictionary"""
        self.db.add_custom_word(word, user_id)
        self.dictionary.add(self.clean_word(word))
    
    def get_statistics(self) -> Dict[str, any]:
        """Get spell checker statistics"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get word count
        cursor.execute("SELECT COUNT(*) FROM words")
        word_count = cursor.fetchone()[0]
        
        # Get custom word count
        cursor.execute("SELECT COUNT(*) FROM custom_words")
        custom_word_count = cursor.fetchone()[0]
        
        # Get spell check history count
        cursor.execute("SELECT COUNT(*) FROM spell_check_history")
        history_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "dictionary_size": word_count,
            "custom_words": custom_word_count,
            "total_checks": history_count,
            "max_edit_distance": self.max_distance
        }
