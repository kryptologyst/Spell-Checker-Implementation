from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from spell_checker import AdvancedSpellChecker
import sqlite3

app = Flask(__name__)
CORS(app)

# Initialize spell checker
spell_checker = AdvancedSpellChecker()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/spell-check', methods=['POST'])
def spell_check():
    """API endpoint for spell checking"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({
                'error': 'No text provided'
            }), 400
        
        result = spell_checker.correct_text(text)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': f'Spell check failed: {str(e)}'
        }), 500

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    """API endpoint for getting suggestions for a specific word"""
    try:
        data = request.get_json()
        word = data.get('word', '')
        context = data.get('context', [])
        
        if not word.strip():
            return jsonify({
                'error': 'No word provided'
            }), 400
        
        suggestions = spell_checker.get_suggestions(word, context)
        return jsonify(suggestions)
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to get suggestions: {str(e)}'
        }), 500

@app.route('/api/add-word', methods=['POST'])
def add_custom_word():
    """API endpoint for adding custom words"""
    try:
        data = request.get_json()
        word = data.get('word', '')
        user_id = data.get('user_id', 'default')
        
        if not word.strip():
            return jsonify({
                'error': 'No word provided'
            }), 400
        
        spell_checker.add_custom_word(word, user_id)
        return jsonify({
            'message': f'Word "{word}" added successfully'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to add word: {str(e)}'
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """API endpoint for getting spell checker statistics"""
    try:
        stats = spell_checker.get_statistics()
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to get statistics: {str(e)}'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """API endpoint for getting spell check history"""
    try:
        conn = sqlite3.connect(spell_checker.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original_text, corrected_text, corrections_count, timestamp 
            FROM spell_check_history 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'original': row[0],
                'corrected': row[1],
                'corrections_count': row[2],
                'timestamp': row[3]
            })
        
        conn.close()
        return jsonify(history)
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to get history: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
