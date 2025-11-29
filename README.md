# SQL Query Optimizer 🚀

A powerful web-based tool to analyze, optimize, and understand SQL queries using AI (Groq API with Llama 3.3 70B Versatile).

## Features ✨

- **Query Analysis**: Detect syntax, logical, and performance issues
- **Smart Optimization**: Generate 3 levels of optimized queries (Conservative, Balanced, Aggressive)
- **Detailed Explanations**: Understand what changed and why
- **Multiple SQL Dialects**: PostgreSQL, MySQL, SQLite, SQL Server, Oracle
- **Clean UI**: Simple and intuitive interface
- **Free AI Model**: Uses Groq's Llama 3.3 70B (completely FREE!)

## Prerequisites 📋

- Python 3.8 or higher
- Groq API Key (FREE - get from https://console.groq.com)

## Important Notes ⚠️

- **Model Update**: This project uses `llama-3.3-70b-versatile`. If you see "model decommissioned" errors, the model name needs to be updated in `app.py`
- **API Key Security**: Never share your API key publicly or commit it to GitHub
- **Rate Limits**: Groq free tier has usage limits - wait a few minutes if you hit them

## Installation Steps 🛠️

### 1. Get Your Groq API Key (FREE)

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it in step 4)

### 2. Clone/Download the Project

```bash
# Create project directory
mkdir sql-query-optimizer
cd sql-query-optimizer
```

### 3. Create Project Files

Create the following directory structure:

```
sql-query-optimizer/
├── app.py
├── requirements.txt
├── .env
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/
    └── index.html
```

**Copy all the code from the artifacts I provided above into their respective files.**

### 4. Setup Environment

#### On Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the content from .env.example and add your Groq API key
```

#### On Mac/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the content from .env.example and add your Groq API key
```

### 5. Configure API Key

Create a file named `.env` in the root directory and add your API key **on a single line with NO blank lines**:

```
GROQ_API_KEY=your_actual_groq_api_key_here
```

**Important:**
- Replace `your_actual_groq_api_key_here` with your actual Groq API key
- No spaces before or after the `=` sign
- No blank lines after the key
- Save the file with cursor at the end of the key

**Your .env file should look EXACTLY like this:**
```
GROQ_API_KEY=gsk_abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
```
(Just one line, nothing else)

### 6. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

Open your browser and navigate to: `http://localhost:5000`

## Usage Guide 📖

### Step 1: Enter Your Query
1. Select SQL dialect (PostgreSQL, MySQL, etc.)
2. Optionally add schema information
3. Paste or type your SQL query
4. Click "Analyze Query"

### Step 2: Review Analysis
- See syntax issues, logical problems, and performance bottlenecks
- Read the overall assessment
- Review hints for improvement

### Step 3: Generate Optimizations
- Click "Generate Optimizations"
- Review 3 optimization levels:
  - **Conservative**: Minimal changes, safest
  - **Balanced**: Good balance of safety and performance
  - **Aggressive**: Maximum performance, more changes

### Step 4: Understand Changes
- Click "Explain this optimization" on any variant
- Read detailed explanation of what changed and why

## Example Query 🔍

Try this query to see the optimizer in action:

```sql
SELECT * FROM users 
WHERE email LIKE '%@gmail.com' 
ORDER BY created_at
```

## Troubleshooting 🔧

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY not found" error
- Make sure you created the `.env` file
- Make sure your API key is correct
- Make sure there are no extra spaces or blank lines in the `.env` file
- The `.env` file should have ONLY one line with no blank lines after it

### "Invalid API Key" error (401)
- Your API key is wrong or expired
- Go to https://console.groq.com/keys and create a NEW API key
- Replace the old key in your `.env` file
- **Important:** Never share your API key publicly (including in GitHub repos)

### "Model decommissioned" error (400)
If you see `llama-3.1-70b-versatile has been decommissioned`, update your `app.py`:
- Find line with: `model="llama-3.1-70b-versatile"`
- Replace with: `model="llama-3.3-70b-versatile"`
- Save and restart the app

### Port 5000 already in use
Edit `app.py` and change the port:
```python
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### API rate limits
Groq free tier has limits. If you hit them:
- Wait a few minutes
- Or create multiple API keys and rotate them

### Testing Your API Key
Create `test_key.py` to verify your setup:
```python
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
print(f"API Key loaded: '{api_key}'")
print(f"Length: {len(api_key) if api_key else 0}")
print(f"Starts with gsk_: {api_key.startswith('gsk_') if api_key else False}")

try:
    client = Groq(api_key=api_key.strip())
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say 'API key works!'"}],
        max_tokens=10
    )
    print("✅ SUCCESS! API key is valid!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ ERROR: {e}")
```

Run with: `python test_key.py`

## Project Structure 📁

```
sql-query-optimizer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API key)
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # Frontend logic
└── templates/
    └── index.html        # Main HTML page
```

## Technologies Used 💻

- **Backend**: Flask (Python)
- **AI Model**: Groq API (Llama 3.3 70B Versatile)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **API**: REST API architecture

## Features in Detail 🎯

### 1. Query Analysis
- Syntax validation
- Logical error detection
- Performance issue identification
- Best practice recommendations

### 2. Multi-Level Optimization
- **Conservative**: Safe optimizations only
- **Balanced**: Good performance improvements with minimal risk
- **Aggressive**: Maximum performance optimizations

### 3. AI-Powered Explanations
- Understands what the query does
- Explains optimization techniques
- Highlights trade-offs
- Educational insights

## Tips for Best Results 💡

1. **Provide Schema Info**: Better analysis with table structures
2. **Use Real Queries**: Test with your actual production queries
3. **Try Different Dialects**: See dialect-specific optimizations
4. **Read Explanations**: Learn SQL optimization techniques
5. **Compare Variants**: Understand different optimization approaches

## Common Issues Detected 🎯

- Missing indexes
- SELECT * usage
- Inefficient JOINs
- Missing WHERE clauses
- Subquery optimization opportunities
- Index usage issues
- Query structure problems

## API Endpoints 🌐

- `GET /` - Main application page
- `POST /analyze` - Analyze SQL query
- `POST /optimize` - Generate optimized queries
- `POST /explain` - Explain optimizations

## Development 🚧

To run in development mode:

```bash
# Make sure debug=True in app.py
python app.py
```

Changes to Python files require restart, but template/static files reload automatically.

## Deployment 🚀

For production deployment:

1. Set `debug=False` in `app.py`
2. Use production WSGI server (Gunicorn, uWSGI)
3. Set strong SECRET_KEY
4. Use environment variables for all secrets
5. Enable HTTPS

## Support 📧

If you have issues:
1. Check this README
2. Verify all files are in correct locations
3. Ensure API key is valid
4. Check Python version (3.8+)

## License 📄

This project is for educational purposes.

## Contributing 🤝

Feel free to fork and improve!

---

**Happy SQL Optimizing! 🎉**