import json
import sqlite3
import os
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import re
import string

class MockWordDatabase:
    """Mock database for storing word frequency and dictionary data"""
    
    def __init__(self, db_path: str = "word_database.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_sample_data()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Words table with frequency data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                frequency INTEGER DEFAULT 1,
                word_type TEXT DEFAULT 'common',
                phonetic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User custom dictionary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                user_id TEXT DEFAULT 'default',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Spell check history for analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spell_check_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                corrected_text TEXT NOT NULL,
                corrections_count INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Populate database with sample word frequency data"""
        # Common English words with estimated frequencies
        common_words = [
            ("the", 1000000, "article"),
            ("be", 800000, "verb"),
            ("to", 700000, "preposition"),
            ("of", 600000, "preposition"),
            ("and", 500000, "conjunction"),
            ("a", 450000, "article"),
            ("in", 400000, "preposition"),
            ("that", 350000, "pronoun"),
            ("have", 300000, "verb"),
            ("i", 280000, "pronoun"),
            ("it", 260000, "pronoun"),
            ("for", 240000, "preposition"),
            ("not", 220000, "adverb"),
            ("on", 200000, "preposition"),
            ("with", 180000, "preposition"),
            ("he", 160000, "pronoun"),
            ("as", 140000, "conjunction"),
            ("you", 120000, "pronoun"),
            ("do", 100000, "verb"),
            ("at", 90000, "preposition"),
            ("this", 80000, "pronoun"),
            ("but", 70000, "conjunction"),
            ("his", 60000, "pronoun"),
            ("by", 50000, "preposition"),
            ("from", 45000, "preposition"),
            ("they", 40000, "pronoun"),
            ("she", 35000, "pronoun"),
            ("or", 30000, "conjunction"),
            ("an", 25000, "article"),
            ("will", 20000, "verb"),
            ("my", 18000, "pronoun"),
            ("one", 16000, "number"),
            ("all", 14000, "determiner"),
            ("would", 12000, "verb"),
            ("there", 10000, "pronoun"),
            ("their", 8000, "pronoun"),
            ("what", 7000, "pronoun"),
            ("so", 6000, "adverb"),
            ("up", 5000, "preposition"),
            ("out", 4500, "preposition"),
            ("if", 4000, "conjunction"),
            ("about", 3500, "preposition"),
            ("who", 3000, "pronoun"),
            ("get", 2500, "verb"),
            ("which", 2000, "pronoun"),
            ("go", 1800, "verb"),
            ("me", 1600, "pronoun"),
            ("when", 1400, "adverb"),
            ("make", 1200, "verb"),
            ("can", 1000, "verb"),
            ("like", 900, "verb"),
            ("time", 800, "noun"),
            ("no", 700, "determiner"),
            ("just", 600, "adverb"),
            ("him", 500, "pronoun"),
            ("know", 450, "verb"),
            ("take", 400, "verb"),
            ("people", 350, "noun"),
            ("into", 300, "preposition"),
            ("year", 250, "noun"),
            ("your", 200, "pronoun"),
            ("good", 180, "adjective"),
            ("some", 160, "determiner"),
            ("could", 140, "verb"),
            ("them", 120, "pronoun"),
            ("see", 100, "verb"),
            ("other", 90, "adjective"),
            ("than", 80, "conjunction"),
            ("then", 70, "adverb"),
            ("now", 60, "adverb"),
            ("look", 50, "verb"),
            ("only", 45, "adverb"),
            ("come", 40, "verb"),
            ("its", 35, "pronoun"),
            ("over", 30, "preposition"),
            ("think", 25, "verb"),
            ("also", 20, "adverb"),
            ("back", 18, "adverb"),
            ("after", 16, "preposition"),
            ("use", 14, "verb"),
            ("two", 12, "number"),
            ("how", 10, "adverb"),
            ("our", 8, "pronoun"),
            ("work", 6, "noun"),
            ("first", 5, "adjective"),
            ("well", 4, "adverb"),
            ("way", 3, "noun"),
            ("even", 2, "adverb"),
            ("new", 1, "adjective"),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for word, freq, word_type in common_words:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO words (word, frequency, word_type) VALUES (?, ?, ?)",
                    (word, freq, word_type)
                )
            except sqlite3.IntegrityError:
                pass  # Word already exists
        
        conn.commit()
        conn.close()
    
    def get_word_frequency(self, word: str) -> int:
        """Get frequency of a word from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT frequency FROM words WHERE word = ?", (word.lower(),))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else 0
    
    def add_custom_word(self, word: str, user_id: str = "default"):
        """Add a word to custom dictionary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR IGNORE INTO custom_words (word, user_id) VALUES (?, ?)",
            (word.lower(), user_id)
        )
        
        conn.commit()
        conn.close()
    
    def is_custom_word(self, word: str, user_id: str = "default") -> bool:
        """Check if word exists in custom dictionary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM custom_words WHERE word = ? AND user_id = ?",
            (word.lower(), user_id)
        )
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def get_all_words(self) -> List[str]:
        """Get all words from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT word FROM words")
        words = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return words
    
    def log_spell_check(self, original: str, corrected: str, corrections_count: int):
        """Log spell check activity for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO spell_check_history (original_text, corrected_text, corrections_count) VALUES (?, ?, ?)",
            (original, corrected, corrections_count)
        )
        
        conn.commit()
        conn.close()
