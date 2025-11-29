import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# System prompts
ANALYZE_SYSTEM_PROMPT = """
You are an expert SQL query reviewer and performance engineer.
Your job:
- Analyze SQL queries for syntax issues, logical issues, and performance/maintainability problems.
- Output STRICT JSON only, no markdown, no code blocks, just pure JSON.
"""

OPTIMIZE_SYSTEM_PROMPT = """
You are an expert SQL optimizer.
Generate multiple optimized variations of the given query.
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
            temperature=0.1,
            max_tokens=4000
        )
        
        response = completion.choices[0].message.content
        
        # Clean up response if it contains markdown code blocks
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_query():
    try:
        data = request.json
        query = data.get('query', '')
        dialect = data.get('dialect', 'PostgreSQL')
        schema_info = data.get('schema_info', 'No schema provided')
        
        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Analyze query
        analyze_prompt = f"""
You must respond ONLY with valid JSON.
Dialect: "{dialect}"
Schema info:
{schema_info}

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
        
        # Optimize query
        optimize_prompt = f"""
You must respond ONLY with valid JSON.
Original SQL:
{query}

Detected issues:
{json.dumps(analysis, indent=2)}

Generate optimized versions in this exact format:
{{
  "original": "{query[:100]}...",
  "optimized_variants": [
    {{
      "id": 1,
      "optimization_level": "conservative",
      "optimized_query": "SELECT ...",
      "changes_made": ["change1", "change2"]
    }},
    {{
      "id": 2,
      "optimization_level": "balanced",
      "optimized_query": "SELECT ...",
      "changes_made": ["change1"]
    }},
    {{
      "id": 3,
      "optimization_level": "aggressive",
      "optimized_query": "SELECT ...",
      "changes_made": ["change1"]
    }}
  ]
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
        
        # Explain differences
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)