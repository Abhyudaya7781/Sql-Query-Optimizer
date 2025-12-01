# SQL Complete Platform 🚀

A comprehensive web-based SQL practice platform, real-time query execution, AI-powered optimization, and 20+ practice questions.

## Features ✨


### 💻 SQL Compiler
- Execute SQL queries with custom schemas
- Real-time query execution using SQLite
- View all database tables and their contents
- Support for CREATE, INSERT, SELECT, UPDATE, DELETE operations
- Visual results display with formatted tables
- Sample schema loader for quick testing

### ⚡ Query Optimizer
- **AI-Powered Analysis**: Using Groq (Llama 3.3 70B Versatile)
- Detect syntax, logical, and performance issues
- Generate optimized query versions
- Detailed explanations of what changed and why
- Multiple SQL Dialects: PostgreSQL, MySQL, SQLite, SQL Server, Oracle
- Performance gain estimations

### 📚 Practice Questions
- **20 Real SQL Interview Questions**
- Difficulty levels: Easy, Medium, Hard
- Complete database schemas with sample data
- Run and test your solutions in real-time
- Hints and detailed solutions provided
- Topics: JOINs, Subqueries, Aggregations, Window Functions, CTEs
- Filter by difficulty level


## Prerequisites 📋

- Python 3.8 or higher
- pip (Python package manager)
- Groq API Key (FREE - get from https://console.groq.com)

## Installation Steps 🛠️

### 1. Get Your Groq API Key (FREE)

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it in step 4)

### 2. Clone the Repository

```bash
git clone https://github.com/Abhyudaya7781/Sql-Query-Optimizer
cd sql-query-optimizer
```

### 3. Install Dependencies

#### On Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### On Mac/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure API Key

Create a file named `.env` in the root directory:

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
```

**Important:**
- Replace `your_actual_groq_api_key_here` with your actual Groq API key
- No spaces before or after the `=` sign
- No blank lines in the file
- Save the file

**Your .env file should look EXACTLY like this:**
```
GROQ_API_KEY=gsk_abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
```
(Just one line, nothing else)

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

Open your browser and navigate to: `http://localhost:5000`

## Project Structure 📁

```
sql-complete-platform/
├── app.py                 # Main Flask application with all routes
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API key)
├── .gitignore            # Git ignore file
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Complete styling (with learning module styles)
│   └── js/
│       └── script.js     # Frontend logic (all features)
└── templates/
    └── index.html        # Main HTML page (4 tabs)
```

## Usage Guide 📖

### 1. SQL Compiler Tab 💻

**Execute Custom Queries:**
1. Write or load a sample database schema
2. Add your SQL query
3. Click "Execute" to run the query
4. View results in formatted tables
5. See all database tables and their data

**Use Cases:**
- Test query syntax
- Prototype database designs
- Learn by experimentation
- Debug SQL queries

### 2. Query Optimizer Tab ⚡

**Optimize Your Queries:**
1. Select your SQL dialect
2. Paste your SQL query
3. Click "Analyze Query"
4. Review detected issues
5. Click "Generate Optimization"
6. View optimized query with changes
7. Read detailed explanations

**Benefits:**
- Improve query performance
- Learn optimization techniques
- Understand best practices
- Fix syntax and logical errors

### 3. Practice Questions Tab 📚

**Solve Real Interview Questions:**
1. Filter questions by difficulty (Easy/Medium/Hard)
2. Read the question description
3. Click "View Tables" to see schema and data
4. Write your SQL solution
5. Run your query to test
6. Compare with hints and solutions

**Topics Covered:**
- Basic SELECT queries
- JOINs (INNER, LEFT, Self-joins)
- Aggregate functions
- GROUP BY and HAVING
- Subqueries and CTEs
- Window functions
- Complex analytical queries


## Technologies Used 💻

- **Backend**: Flask (Python)
- **Database**: SQLite (in-memory for execution)
- **AI Model**: Groq API (Llama 3.3 70B Versatile)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **API**: REST API architecture

## API Endpoints 🌐

### Main Routes
- `GET /` - Main application page


### Compiler
- `POST /compile-sql` - Execute SQL with schema

### Optimizer
- `POST /analyze` - Analyze SQL query
- `POST /optimize` - Generate optimized queries
- `POST /explain` - Explain optimizations

### Practice Questions
- `GET /get-practice-questions` - Get all 20 questions
- `POST /get-question-schema` - Get question database schema
- `POST /execute-question` - Execute solution for a question



## Testing Your Setup ✅

Create `test_setup.py`:

```python
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Test 1: Check API Key
api_key = os.getenv('GROQ_API_KEY')
print(f"✓ API Key loaded: {api_key[:20]}..." if api_key else "✗ API Key not found")

# Test 2: Test Groq Connection
try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'Connected!'"}],
        max_tokens=10
    )
    print(f"✓ Groq API works: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ Groq API error: {e}")

# Test 3: Check Flask
try:
    from flask import Flask
    print("✓ Flask installed")
except:
    print("✗ Flask not installed")

# Test 4: Check SQLite
try:
    import sqlite3
    conn = sqlite3.connect(':memory:')
    print("✓ SQLite works")
    conn.close()
except:
    print("✗ SQLite error")

print("\n✅ All checks passed!" if all else "⚠️ Fix errors above")
```

Run: `python test_setup.py`

## Security Best Practices 🔒

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Never share API keys** - Keep them private
3. **Use environment variables** - Don't hardcode secrets
4. **Update dependencies regularly** - Run `pip install --upgrade`
5. **Set debug=False in production** - For security

## .gitignore Template 

Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Flask
instance/
.webassets-cache
```

## Performance Tips 💡

1. **Compiler**: Runs queries in-memory for speed
2. **Optimizer**: Uses efficient Groq API (fast responses)
3. **Practice**: Questions load once and cache locally

## Learning Path Recommendation 🎯

**Complete Beginner:**
1. Start with "Learn SQL" tab → Introduction module
2. Complete all beginner lessons (3 lessons)
3. Move to "Practice Questions" → Easy questions
4. Try "SQL Compiler" to experiment

**Intermediate:**
1. "Learn SQL" → Intermediate modules
2. "Practice Questions" → Medium questions
3. Use "Query Optimizer" to improve your queries

**Advanced:**
1. "Learn SQL" → Advanced modules
2. "Practice Questions" → Hard questions
3. Experiment with window functions and CTEs


## Browser Compatibility 🌐

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+


## Future Enhancements 🚧
- [ ] SQL Learning Module
- [ ] User authentication and progress tracking
- [ ] Save queries and solutions
- [ ] More SQL dialects support
- [ ] Advanced visualization of query execution plans
- [ ] Code collaboration features
- [ ] Mobile app version
- [ ] More practice questions (50+)
- [ ] Leaderboard for practice questions


## Acknowledgments 🙏

- **Groq** for providing free, fast AI API
- **Flask** for the excellent web framework
- **SQLite** for lightweight database
- **LeetCode** for SQL question inspiration




**Happy SQL Learning! 🎉🚀**