import os
import json
import sqlite3
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Optional: configure external SQL question APIs here
EXTERNAL_SQL_SOURCES = {
    # Example placeholders:
    # "leetcode": "https://your-leetcode-sql-api-endpoint",
    # "some_source": "https://another-sql-api-endpoint"
}

# System prompts
ANALYZE_SYSTEM_PROMPT = """
You are an expert SQL query reviewer and performance engineer.
Your job:
- Analyze SQL queries for syntax issues, logical issues, and performance/maintainability problems.
- Output STRICT JSON only, no markdown, no code blocks, just pure JSON.
"""

OPTIMIZE_SYSTEM_PROMPT = """
You are an expert SQL optimizer.
Generate ONE best optimized version of the given query that balances performance and maintainability.
Return STRICT JSON only, no markdown, no code blocks, just pure JSON.
"""

EXPLAIN_SYSTEM_PROMPT = """
You are a senior backend engineer and SQL instructor.
Explain SQL queries in simple language using markdown format.
"""

def call_groq(system_prompt, user_prompt, response_format="json"):
    """Helper function to call Groq API"""
    try:
        if response_format == "json":
            user_prompt = user_prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no extra text."

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        response = completion.choices[0].message.content

        if response_format == "json":
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

        return response
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        raise e

# ================== QUESTION DATABASE INITIALIZATION ==================

def init_question_db(question_id):
    """
    Creates an in-memory SQLite database for a given question_id
    with the proper schema + seed data.
    """
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    if question_id == 1:
        # Question 1: Employees Earning More Than Managers
        cursor.execute('''
            CREATE TABLE Employee (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                salary INTEGER,
                managerId INTEGER
            )
        ''')
        employees = [
            (1, 'Joe', 70000, 3),
            (2, 'Henry', 80000, 4),
            (3, 'Sam', 60000, None),
            (4, 'Max', 90000, None)
        ]
        cursor.executemany('INSERT INTO Employee VALUES (?, ?, ?, ?)', employees)

    elif question_id == 2:
        # Question 2: Duplicate Emails
        cursor.execute('''
            CREATE TABLE Person (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL
            )
        ''')
        persons = [
            (1, 'john@example.com'),
            (2, 'bob@example.com'),
            (3, 'john@example.com')
        ]
        cursor.executemany('INSERT INTO Person VALUES (?, ?)', persons)

    elif question_id == 3:
        # Question 3: Customers Who Never Order
        cursor.execute('''
            CREATE TABLE Customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Orders (
                id INTEGER PRIMARY KEY,
                customerId INTEGER
            )
        ''')
        customers = [(1, 'Joe'), (2, 'Henry'), (3, 'Sam'), (4, 'Max')]
        orders = [(1, 3), (2, 1)]
        cursor.executemany('INSERT INTO Customers VALUES (?, ?)', customers)
        cursor.executemany('INSERT INTO Orders VALUES (?, ?)', orders)

    elif question_id == 4:
        # Question 4: Second Highest Salary
        cursor.execute('''
            CREATE TABLE Employee (
                id INTEGER PRIMARY KEY,
                salary INTEGER
            )
        ''')
        employees = [(1, 100), (2, 200), (3, 300)]
        cursor.executemany('INSERT INTO Employee VALUES (?, ?)', employees)

    elif question_id == 5:
        # Question 5: Department Highest Salary
        cursor.execute('''
            CREATE TABLE Employee (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                salary INTEGER,
                departmentId INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE Department (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        employees = [
            (1, 'Joe', 85000, 1),
            (2, 'Henry', 80000, 2),
            (3, 'Sam', 60000, 2),
            (4, 'Max', 90000, 1),
            (5, 'Janet', 69000, 1),
            (6, 'Randy', 85000, 1),
            (7, 'Will', 70000, 1)
        ]
        departments = [(1, 'IT'), (2, 'Sales')]
        cursor.executemany('INSERT INTO Employee VALUES (?, ?, ?, ?)', employees)
        cursor.executemany('INSERT INTO Department VALUES (?, ?)', departments)

    elif question_id == 6:
        # Question 6: Rising Temperature
        cursor.execute('''
            CREATE TABLE Weather (
                id INTEGER PRIMARY KEY,
                recordDate DATE NOT NULL,
                temperature INTEGER
            )
        ''')
        weather = [
            (1, '2015-01-01', 10),
            (2, '2015-01-02', 25),
            (3, '2015-01-03', 20),
            (4, '2015-01-04', 30)
        ]
        cursor.executemany('INSERT INTO Weather VALUES (?, ?, ?)', weather)

    elif question_id == 7:
        # Question 7: Delete Duplicate Emails (view only)
        cursor.execute('''
            CREATE TABLE Person (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL
            )
        ''')
        persons = [
            (1, 'john@example.com'),
            (2, 'bob@example.com'),
            (3, 'john@example.com')
        ]
        cursor.executemany('INSERT INTO Person VALUES (?, ?)', persons)

    elif question_id == 8:
        # Question 8: Rank Scores
        cursor.execute('''
            CREATE TABLE Scores (
                id INTEGER PRIMARY KEY,
                score REAL
            )
        ''')
        scores = [(1, 3.50), (2, 3.65), (3, 4.00), (4, 3.85), (5, 4.00), (6, 3.65)]
        cursor.executemany('INSERT INTO Scores VALUES (?, ?)', scores)

    elif question_id == 9:
        # Question 9: Customers With Multiple Orders Per Month
        cursor.execute('''
            CREATE TABLE Customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE NOT NULL,
                amount REAL
            )
        ''')
        customers = [
            (1, 'Alice'),
            (2, 'Bob'),
            (3, 'Charlie')
        ]
        orders = [
            (1, 1, '2023-01-01', 100.0),
            (2, 1, '2023-01-05', 150.0),
            (3, 1, '2023-02-10', 200.0),
            (4, 2, '2023-01-03', 50.0),
            (5, 2, '2023-01-20', 80.0),
            (6, 3, '2023-03-01', 120.0)
        ]
        cursor.executemany('INSERT INTO Customers VALUES (?, ?, ?)', customers)
        cursor.executemany('INSERT INTO Orders VALUES (?, ?, ?, ?)', orders)

    elif question_id == 10:
        # Question 10: Monthly Revenue by Product Category
        cursor.execute('''
            CREATE TABLE Products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Orders (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                order_date DATE NOT NULL,
                quantity INTEGER,
                price_per_unit REAL
            )
        ''')
        products = [
            (1, 'iPhone', 'Electronics'),
            (2, 'MacBook', 'Electronics'),
            (3, 'T-Shirt', 'Apparel'),
            (4, 'Jeans', 'Apparel')
        ]
        orders = [
            (1, 1, '2023-01-05', 2, 900.0),
            (2, 1, '2023-01-25', 1, 950.0),
            (3, 2, '2023-02-10', 1, 1500.0),
            (4, 3, '2023-01-07', 5, 20.0),
            (5, 4, '2023-01-08', 3, 40.0),
            (6, 3, '2023-02-01', 2, 22.0)
        ]
        cursor.executemany('INSERT INTO Products VALUES (?, ?, ?)', products)
        cursor.executemany('INSERT INTO Orders VALUES (?, ?, ?, ?, ?)', orders)

    elif question_id == 11:
        # Question 11: Top 3 Products by Revenue Per Category
        cursor.execute('''
            CREATE TABLE Products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE OrderItems (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                quantity INTEGER,
                price REAL
            )
        ''')
        products = [
            (1, 'iPhone', 'Electronics'),
            (2, 'MacBook', 'Electronics'),
            (3, 'AirPods', 'Electronics'),
            (4, 'T-Shirt', 'Apparel'),
            (5, 'Jeans', 'Apparel'),
            (6, 'Jacket', 'Apparel')
        ]
        items = [
            (1, 1, 10, 900.0),
            (2, 2, 5, 1500.0),
            (3, 3, 20, 150.0),
            (4, 4, 30, 20.0),
            (5, 5, 10, 40.0),
            (6, 6, 5, 100.0)
        ]
        cursor.executemany('INSERT INTO Products VALUES (?, ?, ?)', products)
        cursor.executemany('INSERT INTO OrderItems VALUES (?, ?, ?, ?)', items)

    elif question_id == 12:
        # Question 12: Churned Users (No Activity in Last 30 Days)
        cursor.execute('''
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                signup_date DATE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Events (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                event_time DATE NOT NULL,
                event_type TEXT NOT NULL
            )
        ''')
        users = [
            (1, 'Alice', '2023-01-01'),
            (2, 'Bob', '2023-01-10'),
            (3, 'Charlie', '2023-02-01'),
            (4, 'David', '2023-02-15')
        ]
        events = [
            (1, 1, '2023-03-01', 'login'),
            (2, 1, '2023-03-15', 'purchase'),
            (3, 2, '2023-02-01', 'login'),
            (4, 3, '2023-02-10', 'login')
            # user 4 never active
        ]
        cursor.executemany('INSERT INTO Users VALUES (?, ?, ?)', users)
        cursor.executemany('INSERT INTO Events VALUES (?, ?, ?, ?)', events)

    elif question_id == 13:
        # Question 13: Second Highest Salary Per Department
        cursor.execute('''
            CREATE TABLE Department (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Employee (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                salary INTEGER,
                department_id INTEGER
            )
        ''')
        departments = [
            (1, 'Engineering'),
            (2, 'Sales')
        ]
        employees = [
            (1, 'Alice', 120000, 1),
            (2, 'Bob', 100000, 1),
            (3, 'Charlie', 90000, 1),
            (4, 'Dan', 80000, 2),
            (5, 'Eve', 75000, 2),
            (6, 'Frank', 70000, 2)
        ]
        cursor.executemany('INSERT INTO Department VALUES (?, ?)', departments)
        cursor.executemany('INSERT INTO Employee VALUES (?, ?, ?, ?)', employees)

    elif question_id == 14:
        # Question 14: Running Total of Revenue Per User
        cursor.execute('''
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                order_date DATE NOT NULL,
                amount REAL
            )
        ''')
        users = [
            (1, 'Alice'),
            (2, 'Bob')
        ]
        orders = [
            (1, 1, '2023-01-01', 50.0),
            (2, 1, '2023-01-10', 100.0),
            (3, 1, '2023-02-01', 150.0),
            (4, 2, '2023-01-05', 200.0),
            (5, 2, '2023-02-05', 100.0)
        ]
        cursor.executemany('INSERT INTO Users VALUES (?, ?)', users)
        cursor.executemany('INSERT INTO Orders VALUES (?, ?, ?, ?)', orders)

    elif question_id == 15:
        # Question 15: Most Recent Order Per Customer
        cursor.execute('''
            CREATE TABLE Customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE NOT NULL,
                amount REAL
            )
        ''')
        customers = [
            (1, 'Alice'),
            (2, 'Bob'),
            (3, 'Charlie')
        ]
        orders = [
            (1, 1, '2023-01-01', 50.0),
            (2, 1, '2023-03-01', 70.0),
            (3, 2, '2023-02-01', 100.0),
            (4, 3, '2023-01-15', 30.0),
            (5, 3, '2023-04-01', 90.0)
        ]
        cursor.executemany('INSERT INTO Customers VALUES (?, ?, ?)', customers)
        cursor.executemany('INSERT INTO Orders VALUES (?, ?, ?, ?)', orders)

    elif question_id == 16:
        # Question 16: Daily Active Users (DAU)
        cursor.execute('''
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Events (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                event_date DATE NOT NULL,
                event_type TEXT NOT NULL
            )
        ''')
        users = [
            (1, 'Alice'),
            (2, 'Bob'),
            (3, 'Charlie')
        ]
        events = [
            (1, 1, '2023-03-01', 'login'),
            (2, 1, '2023-03-01', 'view'),
            (3, 2, '2023-03-01', 'login'),
            (4, 2, '2023-03-02', 'login'),
            (5, 3, '2023-03-02', 'login'),
            (6, 1, '2023-03-03', 'login')
        ]
        cursor.executemany('INSERT INTO Users VALUES (?, ?, ?)', users)
        cursor.executemany('INSERT INTO Events VALUES (?, ?, ?, ?)', events)

    elif question_id == 17:
        # Question 17: Conversion from View to Purchase
        cursor.execute('''
            CREATE TABLE Events (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                event_time DATE NOT NULL,
                event_type TEXT NOT NULL
            )
        ''')
        events = [
            (1, 1, '2023-03-01', 'view'),
            (2, 1, '2023-03-01', 'purchase'),
            (3, 2, '2023-03-01', 'view'),
            (4, 2, '2023-03-02', 'view'),
            (5, 3, '2023-03-01', 'view'),
            (6, 4, '2023-03-01', 'purchase')
        ]
        cursor.executemany('INSERT INTO Events VALUES (?, ?, ?, ?)', events)

    elif question_id == 18:
        # Question 18: Users with 3 Consecutive Login Days
        cursor.execute('''
            CREATE TABLE Logins (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                login_date DATE NOT NULL
            )
        ''')
        logins = [
            (1, 1, '2023-03-01'),
            (2, 1, '2023-03-02'),
            (3, 1, '2023-03-03'),
            (4, 2, '2023-03-01'),
            (5, 2, '2023-03-03'),
            (6, 3, '2023-03-05'),
            (7, 3, '2023-03-06'),
            (8, 3, '2023-03-07')
        ]
        cursor.executemany('INSERT INTO Logins VALUES (?, ?, ?)', logins)

    elif question_id == 19:
        # Question 19: Average Order Value per User Segment
        cursor.execute('''
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                segment TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount REAL
            )
        ''')
        users = [
            (1, 'Alice', 'A'),
            (2, 'Bob', 'A'),
            (3, 'Charlie', 'B'),
            (4, 'David', 'B')
        ]
        orders = [
            (1, 1, 100.0),
            (2, 1, 50.0),
            (3, 2, 80.0),
            (4, 3, 200.0),
            (5, 4, 300.0),
            (6, 4, 100.0)
        ]
        cursor.executemany('INSERT INTO Users VALUES (?, ?, ?)', users)
        cursor.executemany('INSERT INTO Orders VALUES (?, ?, ?)', orders)

    elif question_id == 20:
        # Question 20: First Purchase Date Per Marketing Channel
        cursor.execute('''
            CREATE TABLE Users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                channel TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE Orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                order_date DATE NOT NULL,
                amount REAL
            )
        ''')
        users = [
            (1, 'Alice', 'Ads'),
            (2, 'Bob', 'Organic'),
            (3, 'Charlie', 'Ads'),
            (4, 'David', 'Referral')
        ]
        orders = [
            (1, 1, '2023-01-10', 100.0),
            (2, 1, '2023-02-01', 50.0),
            (3, 2, '2023-01-05', 80.0),
            (4, 3, '2023-03-01', 200.0),
            (5, 4, '2023-01-20', 150.0)
        ]
        cursor.executemany('INSERT INTO Users VALUES (?, ?, ?)', users)
        cursor.executemany('INSERT INTO Orders VALUES (?, ?, ?, ?)', orders)

    conn.commit()
    return conn

# ================== ROUTES ==================

@app.route('/')
def index():
    return render_template('index.html')

# ---------- ANALYZE / OPTIMIZE / EXPLAIN ----------

@app.route('/analyze', methods=['POST'])
def analyze_query():
    try:
        data = request.json
        query = data.get('query', '')
        dialect = data.get('dialect', 'PostgreSQL')

        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400

        analyze_prompt = f"""
You must respond ONLY with valid JSON.
Dialect: "{dialect}"

SQL query:
{query}

Return JSON in this exact format:
{{
  "syntax_issues": ["issue1", "issue2"],
  "logical_issues": ["issue1"],
  "performance_issues": ["issue1"],
  "needs_optimization": true,
  "overall_assessment": "brief assessment",
  "hints_for_improvement": ["hint1", "hint2"]
}}
"""

        analysis_response = call_groq(ANALYZE_SYSTEM_PROMPT, analyze_prompt, "json")
        analysis = json.loads(analysis_response)

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except json.JSONDecodeError as e:
        return jsonify({'error': f'Failed to parse analysis response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/optimize', methods=['POST'])
def optimize_query():
    try:
        data = request.json
        query = data.get('query', '')
        analysis = data.get('analysis', {})

        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400

        optimize_prompt = f"""
You must respond ONLY with valid JSON.
Original SQL:
{query}

Detected issues:
{json.dumps(analysis, indent=2)}

Generate ONE optimized version in this exact format:
{{
  "original": "{query[:100]}...",
  "optimized_query": "SELECT ...",
  "changes_made": ["change1", "change2", "change3"],
  "performance_gain": "Expected improvement description"
}}
"""

        optimize_response = call_groq(OPTIMIZE_SYSTEM_PROMPT, optimize_prompt, "json")
        optimized = json.loads(optimize_response)

        return jsonify({
            'success': True,
            'optimized': optimized
        })

    except json.JSONDecodeError as e:
        return jsonify({'error': f'Failed to parse optimization response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/explain', methods=['POST'])
def explain_query():
    try:
        data = request.json
        original = data.get('original', '')
        optimized = data.get('optimized', '')
        dialect = data.get('dialect', 'PostgreSQL')

        if not original.strip() or not optimized.strip():
            return jsonify({'error': 'Both queries are required'}), 400

        explain_prompt = f"""
Dialect: {dialect}

Original query:
{original}

Optimized query:
{optimized}

Explain in markdown format:
1. What the original query does
2. What optimizations were made
3. Why these optimizations improve performance
4. Any trade-offs to consider

Keep it simple and educational.
"""

        explanation = call_groq(EXPLAIN_SYSTEM_PROMPT, explain_prompt, "markdown")

        return jsonify({
            'success': True,
            'explanation': explanation
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- GENERIC SQL PLAYGROUND (user-provided schema) ----------
# (You can still keep this if you want step-by-step multi-query execution.)

@app.route('/playground/execute', methods=['POST'])
def playground_execute():
    """
    Execute user-provided setup SQL (schema + seed data) and then a sequence of queries.
    Returns:
      - last query result (if SELECT)
      - affected rows (if non-SELECT)
      - snapshot of all tables after all queries
    """
    try:
        data = request.json or {}
        setup_sql = (data.get('setup_sql') or '').strip()
        queries = data.get('queries') or []

        if not setup_sql:
            return jsonify({'error': 'Setup SQL (schema + seed data) is required'}), 400
        if not isinstance(queries, list) or len(queries) == 0:
            return jsonify({'error': 'At least one query is required'}), 400

        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        # 1) Apply schema + seed data
        try:
            cursor.executescript(setup_sql)
        except sqlite3.Error as e:
            conn.close()
            return jsonify({'error': f'Error in setup SQL: {str(e)}'}), 400

        last_result = None
        affected_rows = None
        last_query_type = None
        last_query_text = None

        # 2) Apply each step query in order
        for raw_q in queries:
            q = (raw_q or '').strip()
            if not q:
                continue
            last_query_text = q
            last_query_type = q.split()[0].upper()

            try:
                cursor.execute(q)
            except sqlite3.Error as e:
                conn.close()
                return jsonify({'error': f'Error in query \"{q}\": {str(e)}'}), 400

            if cursor.description is not None:
                cols = [d[0] for d in cursor.description]
                rows = cursor.fetchall()
                last_result = {
                    'columns': cols,
                    'rows': rows
                }
                affected_rows = None
            else:
                affected_rows = cursor.rowcount
                last_result = None

        # 3) Snapshot all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = {}
        for (table_name,) in cursor.fetchall():
            cursor.execute(f"PRAGMA table_info({table_name})")
            cols_meta = cursor.fetchall()
            col_names = [c[1] for c in cols_meta]  # name
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            tables[table_name] = {
                'columns': col_names,
                'rows': rows
            }

        conn.close()

        return jsonify({
            'success': True,
            'last_query_type': last_query_type,
            'last_query_text': last_query_text,
            'result': last_result,
            'affected_rows': affected_rows,
            'tables': tables
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- NEW: SQL COMPILER (user schema + query + optimization) ----------

@app.route('/compile-sql', methods=['POST'])
def compile_sql():
    """
    User provides:
      - setup_sql: schema + seed data (SQLite compatible)
      - query: single SQL query
      - dialect: (optional) for LLM hints, defaults to PostgreSQL

    We:
      1) Build in-memory DB, run setup_sql
      2) Execute the query and capture result
      3) Analyze the query with Groq
      4) If needs_optimization == true, call optimize and return optimized query + hints
    """
    try:
        data = request.json or {}
        setup_sql = (data.get('setup_sql') or '').strip()
        query = (data.get('query') or '').strip()
        dialect = data.get('dialect', 'PostgreSQL')

        if not setup_sql:
            return jsonify({'error': 'Setup SQL (schema + seed data) is required'}), 400
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400

        # 1. Build DB and run user's query
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        try:
            cursor.executescript(setup_sql)
        except sqlite3.Error as e:
            conn.close()
            return jsonify({'error': f'Error in setup SQL: {str(e)}'}), 400

        try:
            cursor.execute(query)
        except sqlite3.Error as e:
            conn.close()
            return jsonify({'error': f'SQL Error in query: {str(e)}'}), 400

        result = None
        affected_rows = None
        if cursor.description is not None:
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            result = {
                "columns": cols,
                "rows": rows
            }
        else:
            affected_rows = cursor.rowcount

        # Take snapshot of all tables after query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = {}
        for (table_name,) in cursor.fetchall():
            cursor.execute(f"PRAGMA table_info({table_name})")
            cols_meta = cursor.fetchall()
            col_names = [c[1] for c in cols_meta]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            tables[table_name] = {
                "columns": col_names,
                "rows": rows
            }

        conn.close()

        # 2. Analyze with Groq
        analyze_prompt = f"""
You must respond ONLY with valid JSON.
Dialect: "{dialect}"

SQL query:
{query}

Return JSON in this exact format:
{{
  "syntax_issues": ["issue1", "issue2"],
  "logical_issues": ["issue1"],
  "performance_issues": ["issue1"],
  "needs_optimization": true,
  "overall_assessment": "brief assessment",
  "hints_for_improvement": ["hint1", "hint2"]
}}
"""
        analysis_json = call_groq(ANALYZE_SYSTEM_PROMPT, analyze_prompt, "json")
        analysis = json.loads(analysis_json)

        optimized = None
        # 3. If optimization needed, call optimizer
        if analysis.get("needs_optimization", False):
            optimize_prompt = f"""
You must respond ONLY with valid JSON.
Original SQL:
{query}

Detected issues:
{json.dumps(analysis, indent=2)}

Generate ONE optimized version in this exact format:
{{
  "original": "{query[:100]}...",
  "optimized_query": "SELECT ...",
  "changes_made": ["change1", "change2", "change3"],
  "performance_gain": "Expected improvement description"
}}
"""
            optimized_json = call_groq(OPTIMIZE_SYSTEM_PROMPT, optimize_prompt, "json")
            optimized = json.loads(optimized_json)

        return jsonify({
            "success": True,
            "result": result,
            "affected_rows": affected_rows,
            "tables": tables,
            "analysis": analysis,
            "optimized": optimized
        })

    except json.JSONDecodeError as e:
        return jsonify({'error': f'Failed to parse Groq JSON: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- PRACTICE QUESTION EXECUTION ----------

@app.route('/execute-question', methods=['POST'])
def execute_question():
    try:
        data = request.json
        query = data.get('query', '').strip()
        question_id = data.get('question_id', 1)

        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400

        if not query.upper().startswith('SELECT'):
            return jsonify({'error': 'Only SELECT queries are allowed'}), 400

        conn = init_question_db(question_id)
        cursor = conn.cursor()

        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'columns': columns,
            'rows': rows,
            'row_count': len(rows)
        })

    except sqlite3.Error as e:
        return jsonify({'error': f'SQL Error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-question-schema', methods=['POST'])
def get_question_schema():
    try:
        data = request.json
        question_id = data.get('question_id', 1)

        conn = init_question_db(question_id)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        schema_info = {}
        table_data = {}

        for (table_name,) in tables:
            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema_info[table_name] = [
                {'name': col[1], 'type': col[2], 'notnull': col[3], 'pk': col[5]}
                for col in columns
            ]

            # Get all data
            cursor.execute(f"SELECT * FROM {table_name}")
            col_names = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            table_data[table_name] = {
                'columns': col_names,
                'rows': rows
            }

        conn.close()

        return jsonify({
            'success': True,
            'schema': schema_info,
            'data': table_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- PRACTICE QUESTIONS METADATA (20 QUESTIONS) ----------

@app.route('/get-practice-questions', methods=['GET'])
def get_practice_questions():
    questions = [
        {
            "id": 1,
            "difficulty": "Easy",
            "title": "Employees Earning More Than Their Managers",
            "description": "Find the employees who earn more than their managers.",
            "tables": ["Employee (id, name, salary, managerId)"],
            "example_output": "name\nJoe",
            "hint": "Use a self-join to compare employee salary with their manager's salary.",
            "solution": "SELECT e1.name FROM Employee e1 JOIN Employee e2 ON e1.managerId = e2.id WHERE e1.salary > e2.salary"
        },
        {
            "id": 2,
            "difficulty": "Easy",
            "title": "Duplicate Emails",
            "description": "Report all the duplicate emails.",
            "tables": ["Person (id, email)"],
            "example_output": "email\njohn@example.com",
            "hint": "Use GROUP BY and HAVING COUNT(*) > 1.",
            "solution": "SELECT email FROM Person GROUP BY email HAVING COUNT(*) > 1"
        },
        {
            "id": 3,
            "difficulty": "Easy",
            "title": "Customers Who Never Order",
            "description": "Find all customers who never order anything.",
            "tables": ["Customers (id, name)", "Orders (id, customerId)"],
            "example_output": "Customers\nHenry\nMax",
            "hint": "Use LEFT JOIN or NOT IN to find customers without orders.",
            "solution": "SELECT name AS Customers FROM Customers WHERE id NOT IN (SELECT customerId FROM Orders)"
        },
        {
            "id": 4,
            "difficulty": "Medium",
            "title": "Second Highest Salary",
            "description": "Find the second highest salary from the Employee table. If there is no second highest salary, return null.",
            "tables": ["Employee (id, salary)"],
            "example_output": "SecondHighestSalary\n200",
            "hint": "Use DISTINCT, ORDER BY DESC, LIMIT with OFFSET.",
            "solution": "SELECT (SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1) AS SecondHighestSalary"
        },
        {
            "id": 5,
            "difficulty": "Medium",
            "title": "Department Highest Salary",
            "description": "Find employees who have the highest salary in each department.",
            "tables": ["Employee (id, name, salary, departmentId)", "Department (id, name)"],
            "example_output": "Department | Employee | Salary\nIT | Max | 90000\nIT | Joe | 85000\nSales | Henry | 80000",
            "hint": "Use JOIN with a subquery to find max salary per department.",
            "solution": "SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary FROM Employee e JOIN Department d ON e.departmentId = d.id WHERE (e.departmentId, e.salary) IN (SELECT departmentId, MAX(salary) FROM Employee GROUP BY departmentId)"
        },
        {
            "id": 6,
            "difficulty": "Medium",
            "title": "Rising Temperature",
            "description": "Find the ids for days where the temperature is higher compared to the previous day.",
            "tables": ["Weather (id, recordDate, temperature)"],
            "example_output": "id\n2\n4",
            "hint": "Self-join the table on recordDate-1 day and compare temperatures.",
            "solution": "SELECT w1.id FROM Weather w1 JOIN Weather w2 ON DATE(w1.recordDate) = DATE(w2.recordDate, '+1 day') WHERE w1.temperature > w2.temperature"
        },
        {
            "id": 7,
            "difficulty": "Easy",
            "title": "Delete Duplicate Emails (Identify)",
            "description": "Identify duplicate emails. Keep only the row with the smallest id.",
            "tables": ["Person (id, email)"],
            "example_output": "email | id\njohn@example.com | 3",
            "hint": "Use MIN(id) GROUP BY email to find which ones to keep.",
            "solution": "SELECT p1.email, p1.id FROM Person p1 WHERE p1.id NOT IN (SELECT MIN(id) FROM Person GROUP BY email)"
        },
        {
            "id": 8,
            "difficulty": "Hard",
            "title": "Rank Scores",
            "description": "Rank scores from highest to lowest. Ties share the same rank, and the next rank is the next integer.",
            "tables": ["Scores (id, score)"],
            "example_output": "score | rank\n4.00 | 1\n4.00 | 1\n3.85 | 2",
            "hint": "Use DENSE_RANK() or count distinct scores >= current.",
            "solution": "SELECT score, (SELECT COUNT(DISTINCT score) FROM Scores s2 WHERE s2.score >= s1.score) AS rank FROM Scores s1 ORDER BY score DESC"
        },
        {
            "id": 9,
            "difficulty": "Medium",
            "title": "Customers With Multiple Orders Per Month",
            "description": "Find customers who placed at least 2 orders in the same calendar month.",
            "tables": ["Customers (id, name)", "Orders (id, customer_id, order_date, amount)"],
            "example_output": "name | order_month | order_count\nAlice | 2023-01 | 2\nBob | 2023-01 | 2",
            "hint": "Group by customer and month (use strftime).",
            "solution": "SELECT c.name, strftime('%Y-%m', o.order_date) AS order_month, COUNT(*) AS order_count FROM Customers c JOIN Orders o ON c.id = o.customer_id GROUP BY c.id, order_month HAVING COUNT(*) >= 2 ORDER BY c.name, order_month"
        },
        {
            "id": 10,
            "difficulty": "Medium",
            "title": "Monthly Revenue by Product Category",
            "description": "Compute total revenue per category per month. Revenue = quantity * price_per_unit.",
            "tables": ["Products (id, name, category)", "Orders (id, product_id, order_date, quantity, price_per_unit)"],
            "example_output": "category | month | revenue\nElectronics | 2023-01 | ...",
            "hint": "Join Orders with Products, group by category and month.",
            "solution": "SELECT p.category, strftime('%Y-%m', o.order_date) AS month, SUM(o.quantity * o.price_per_unit) AS revenue FROM Products p JOIN Orders o ON p.id = o.product_id GROUP BY p.category, month ORDER BY month, p.category"
        },
        {
            "id": 11,
            "difficulty": "Hard",
            "title": "Top 3 Products by Revenue Per Category",
            "description": "For each category, find up to 3 products with the highest total revenue.",
            "tables": ["Products (id, name, category)", "OrderItems (id, product_id, quantity, price)"],
            "example_output": "category | name | revenue | rank\nElectronics | MacBook | ... | 1",
            "hint": "Aggregate revenue per product and use ROW_NUMBER() over each category.",
            "solution": "SELECT category, name, revenue, rn AS rank FROM ( SELECT p.category, p.name, SUM(oi.quantity * oi.price) AS revenue, ROW_NUMBER() OVER(PARTITION BY p.category ORDER BY SUM(oi.quantity * oi.price) DESC) AS rn FROM Products p JOIN OrderItems oi ON p.id = oi.product_id GROUP BY p.category, p.name ) t WHERE rn <= 3 ORDER BY category, revenue DESC"
        },
        {
            "id": 12,
            "difficulty": "Medium",
            "title": "Churned Users (No Activity in Last 30 Days)",
            "description": "Assume today is 2023-03-31. Find users who have no events in the last 30 days but had at least one event before that.",
            "tables": ["Users (id, name, signup_date)", "Events (id, user_id, event_time, event_type)"],
            "example_output": "name\nBob",
            "hint": "Find last event date per user and filter by date.",
            "solution": "WITH last_event AS ( SELECT u.id, u.name, MAX(e.event_time) AS last_time FROM Users u LEFT JOIN Events e ON u.id = e.user_id GROUP BY u.id, u.name ) SELECT name FROM last_event WHERE last_time IS NOT NULL AND last_time < '2023-03-02'"
        },
        {
            "id": 13,
            "difficulty": "Medium",
            "title": "Second Highest Salary Per Department",
            "description": "For each department, find the second highest distinct salary. If it does not exist, return NULL.",
            "tables": ["Department (id, name)", "Employee (id, name, salary, department_id)"],
            "example_output": "department | second_highest_salary\nEngineering | 100000\nSales | 75000",
            "hint": "Use subquery with DISTINCT salary ordered by DESC and OFFSET 1.",
            "solution": "SELECT d.name AS department, ( SELECT DISTINCT salary FROM Employee e2 WHERE e2.department_id = d.id ORDER BY salary DESC LIMIT 1 OFFSET 1 ) AS second_highest_salary FROM Department d"
        },
        {
            "id": 14,
            "difficulty": "Medium",
            "title": "Running Total of Revenue Per User",
            "description": "For each user and order, compute the running total of revenue ordered by order_date.",
            "tables": ["Users (id, name)", "Orders (id, user_id, order_date, amount)"],
            "example_output": "name | order_date | amount | running_total\nAlice | 2023-01-01 | 50 | 50\nAlice | 2023-01-10 | 100 | 150",
            "hint": "Use SUM(amount) OVER(PARTITION BY user_id ORDER BY order_date).",
            "solution": "SELECT u.name, o.order_date, o.amount, SUM(o.amount) OVER(PARTITION BY o.user_id ORDER BY o.order_date) AS running_total FROM Users u JOIN Orders o ON u.id = o.user_id ORDER BY u.name, o.order_date"
        },
        {
            "id": 15,
            "difficulty": "Easy",
            "title": "Most Recent Order Per Customer",
            "description": "For each customer, find their most recent order date and amount.",
            "tables": ["Customers (id, name)", "Orders (id, customer_id, order_date, amount)"],
            "example_output": "name | order_date | amount\nAlice | 2023-03-01 | 70.0",
            "hint": "Use ROW_NUMBER() over each customer ordered by date DESC.",
            "solution": "SELECT name, order_date, amount FROM ( SELECT c.name, o.order_date, o.amount, ROW_NUMBER() OVER(PARTITION BY c.id ORDER BY o.order_date DESC) AS rn FROM Customers c JOIN Orders o ON c.id = o.customer_id ) t WHERE rn = 1 ORDER BY name"
        },
        {
            "id": 16,
            "difficulty": "Easy",
            "title": "Daily Active Users (DAU)",
            "description": "Count distinct active users per day based on Events.",
            "tables": ["Users (id, name)", "Events (id, user_id, event_date, event_type)"],
            "example_output": "event_date | dau\n2023-03-01 | 2\n2023-03-02 | 2",
            "hint": "Count DISTINCT user_id per event_date.",
            "solution": "SELECT event_date, COUNT(DISTINCT user_id) AS dau FROM Events GROUP BY event_date ORDER BY event_date"
        },
        {
            "id": 17,
            "difficulty": "Medium",
            "title": "Conversion from View to Purchase",
            "description": "Compute the number of users who viewed and also purchased, and the overall conversion rate.",
            "tables": ["Events (id, user_id, event_time, event_type)"],
            "example_output": "view_users | purchase_users | converted_users | conversion_rate",
            "hint": "Find users with view, users with purchase, and their intersection.",
            "solution": "WITH view_users AS (SELECT DISTINCT user_id FROM Events WHERE event_type = 'view'), purchase_users AS (SELECT DISTINCT user_id FROM Events WHERE event_type = 'purchase'), converted AS (SELECT v.user_id FROM view_users v INNER JOIN purchase_users p ON v.user_id = p.user_id) SELECT (SELECT COUNT(*) FROM view_users) AS view_users, (SELECT COUNT(*) FROM purchase_users) AS purchase_users, (SELECT COUNT(*) FROM converted) AS converted_users, 1.0 * (SELECT COUNT(*) FROM converted) / NULLIF((SELECT COUNT(*) FROM view_users), 0) AS conversion_rate"
        },
        {
            "id": 18,
            "difficulty": "Hard",
            "title": "Users with 3 Consecutive Login Days",
            "description": "Find users who logged in for at least 3 consecutive days.",
            "tables": ["Logins (id, user_id, login_date)"],
            "example_output": "user_id\n1\n3",
            "hint": "Use LAG/LEAD or date difference tricks to detect streaks.",
            "solution": "WITH ordered AS ( SELECT user_id, login_date, ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY login_date) AS rn FROM Logins ), grouped AS ( SELECT user_id, DATE(login_date, '-' || rn || ' day') AS grp_key FROM ordered ) SELECT DISTINCT user_id FROM grouped GROUP BY user_id, grp_key HAVING COUNT(*) >= 3"
        },
        {
            "id": 19,
            "difficulty": "Medium",
            "title": "Average Order Value per User Segment",
            "description": "Compute average order value per user segment.",
            "tables": ["Users (id, name, segment)", "Orders (id, user_id, amount)"],
            "example_output": "segment | avg_order_value\nA | ...\nB | ...",
            "hint": "Join Users and Orders, group by segment.",
            "solution": "SELECT u.segment, AVG(o.amount) AS avg_order_value FROM Users u JOIN Orders o ON u.id = o.user_id GROUP BY u.segment"
        },
        {
            "id": 20,
            "difficulty": "Medium",
            "title": "First Purchase Date Per Marketing Channel",
            "description": "For each acquisition channel, find the earliest purchase date among its users.",
            "tables": ["Users (id, name, channel)", "Orders (id, user_id, order_date, amount)"],
            "example_output": "channel | first_purchase_date\nAds | 2023-01-10\nOrganic | 2023-01-05",
            "hint": "Join Users and Orders, group by channel and take MIN(order_date).",
            "solution": "SELECT u.channel, MIN(o.order_date) AS first_purchase_date FROM Users u JOIN Orders o ON u.id = o.user_id GROUP BY u.channel ORDER BY u.channel"
        }
    ]

    return jsonify({
        "success": True,
        "questions": questions
    })

# ---------- EXTERNAL QUESTION SOURCE HOOK (still stub) ----------

@app.route('/get-external-questions', methods=['GET'])
def get_external_questions():
    """
    Generic hook to fetch SQL problems from external APIs (e.g., LeetCode-like).
    You MUST configure EXTERNAL_SQL_SOURCES and map the JSON into the same
    format used by /get-practice-questions.
    """
    source = request.args.get('source', 'leetcode')

    if source not in EXTERNAL_SQL_SOURCES:
        return jsonify({'error': f'External source \"{source}\" is not configured on the server.'}), 400

    try:
        url = EXTERNAL_SQL_SOURCES[source]
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        # TODO: Map "raw" to the expected format.
        questions = []

        return jsonify({
            "success": True,
            "questions": questions,
            "note": "You must implement mapping from the external API response to this format."
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5000)




