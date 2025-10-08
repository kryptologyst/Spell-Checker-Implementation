# Advanced Spell Checker - Development Setup

This document provides detailed setup instructions for developers and contributors.

## 🛠️ Development Environment Setup

### Prerequisites
- Python 3.8+ (recommended: Python 3.11)
- Git
- Virtual environment tool (venv, conda, or virtualenv)

### Initial Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/advanced-spell-checker.git
cd advanced-spell-checker
```

2. **Create virtual environment**
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n spell-checker python=3.11
conda activate spell-checker
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

## 🧪 Running Tests

### Test Suite
```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=spell_checker --cov=database --cov-report=html

# Run specific test file
python -m pytest tests/test_spell_checker.py

# Run specific test class
python -m pytest tests/test_spell_checker.py::TestAdvancedSpellChecker
```

### Test Coverage
- Target: 95%+ code coverage
- Current coverage: Check with `--cov-report=html`
- Coverage report: `htmlcov/index.html`

## 🚀 Running the Application

### Command Line Interface
```bash
python 0171.py
```

### Web Interface
```bash
python app.py
```
Then visit: `http://localhost:5000`

### Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

## 📁 Project Structure

```
advanced-spell-checker/
├── 0171.py                 # Main demo script
├── app.py                  # Flask web application
├── spell_checker.py        # Core spell checking logic
├── database.py            # SQLite database management
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── tests/                 # Test suite
│   └── test_spell_checker.py
├── templates/             # HTML templates
│   └── index.html
├── static/               # Static files (CSS, JS, images)
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── .gitignore            # Git ignore rules
├── .github/              # GitHub workflows
│   └── workflows/
│       ├── ci.yml        # Continuous Integration
│       └── deploy.yml    # Deployment
├── README.md             # Main documentation
├── LICENSE               # MIT License
└── CHANGELOG.md          # Version history
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
export SPELL_CHECKER_DB_PATH="word_database.db"

# Flask
export FLASK_ENV="development"
export FLASK_DEBUG="True"
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"

# Spell Checker
export MAX_EDIT_DISTANCE="2"
export MIN_WORD_LENGTH="2"
```

### Configuration Files
- `config.py`: Application configuration
- `.env`: Environment variables (not committed)
- `requirements.txt`: Production dependencies
- `requirements-dev.txt`: Development dependencies

## 📊 Database Management

### Database Schema
```sql
-- Words table
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 1,
    word_type TEXT DEFAULT 'common',
    phonetic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custom words table
CREATE TABLE custom_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL,
    user_id TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spell check history
CREATE TABLE spell_check_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_text TEXT NOT NULL,
    corrected_text TEXT NOT NULL,
    corrections_count INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Operations
```python
# Initialize database
from database import MockWordDatabase
db = MockWordDatabase("custom_path.db")

# Add custom words
db.add_custom_word("GitHub", "user123")

# Get statistics
stats = db.get_statistics()
```

## 🧪 Testing Guidelines

### Test Categories
1. **Unit Tests**: Individual function testing
2. **Integration Tests**: Component interaction testing
3. **API Tests**: Endpoint testing
4. **UI Tests**: Frontend testing (future)

### Test Naming Convention
- `test_<function_name>`: Unit tests
- `test_<class_name>`: Class tests
- `test_<module_name>_integration`: Integration tests

### Mocking
```python
import unittest.mock as mock

@mock.patch('spell_checker.MockWordDatabase')
def test_spell_checker_with_mock_db(mock_db):
    # Test implementation
    pass
```

## 🚀 Deployment

### Local Deployment
```bash
# Production mode
export FLASK_ENV=production
export FLASK_DEBUG=False
python app.py
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Cloud Deployment
- **Heroku**: Use Procfile and requirements.txt
- **AWS**: Use Elastic Beanstalk or Lambda
- **Google Cloud**: Use App Engine or Cloud Run
- **Azure**: Use App Service or Container Instances

## 🔍 Debugging

### Common Issues
1. **Database not found**: Check file permissions and path
2. **Import errors**: Verify virtual environment activation
3. **Port conflicts**: Change FLASK_PORT environment variable
4. **Memory issues**: Reduce dictionary size or optimize algorithms

### Debug Tools
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use Python debugger
import pdb
pdb.set_trace()

# Profile performance
import cProfile
cProfile.run('spell_checker.correct_text("test")')
```

## 📝 Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Use meaningful variable names

### Code Formatting
```bash
# Install formatting tools
pip install black flake8 isort

# Format code
black .
isort .

# Check style
flake8 .
```

## 🤝 Contributing

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

### Code Review Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance impact considered

## 📚 Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Algorithms
- [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Soundex Algorithm](https://en.wikipedia.org/wiki/Soundex)
- [Metaphone Algorithm](https://en.wikipedia.org/wiki/Metaphone)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
