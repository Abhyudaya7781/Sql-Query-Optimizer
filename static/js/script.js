let currentAnalysis = null;
let allQuestions = [];

// DOM Elements - Compiler
const compilerSchema = document.getElementById('compilerSchema');
const compilerQuery = document.getElementById('compilerQuery');
const executeCompilerBtn = document.getElementById('executeCompilerBtn');
const clearCompilerBtn = document.getElementById('clearCompilerBtn');
const compilerResults = document.getElementById('compilerResults');
const compilerResultsContent = document.getElementById('compilerResultsContent');
const compilerTables = document.getElementById('compilerTables');
const compilerTablesContent = document.getElementById('compilerTablesContent');
const compilerPlaceholder = document.getElementById('compilerPlaceholder');

// DOM Elements - Optimizer
const optimizerQuery = document.getElementById('optimizerQuery');
const dialectSelect = document.getElementById('dialect');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearOptimizerBtn = document.getElementById('clearOptimizerBtn');
const optimizeBtn = document.getElementById('optimizeBtn');

const analysisSection = document.getElementById('analysisSection');
const analysisContent = document.getElementById('analysisContent');
const optimizationSection = document.getElementById('optimizationSection');
const optimizationContent = document.getElementById('optimizationContent');
const explanationSection = document.getElementById('explanationSection');
const explanationContent = document.getElementById('explanationContent');

// DOM Elements - Practice
const questionsContainer = document.getElementById('questionsContainer');

// DOM Elements - Global
const loading = document.getElementById('loading');

// ============= TAB NAVIGATION =============

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const tabName = this.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    if (tabName === 'practice' && allQuestions.length === 0) {
        loadPracticeQuestions();
    }
}

// ============= SQL COMPILER FUNCTIONS =============

if (executeCompilerBtn) executeCompilerBtn.addEventListener('click', executeCompiler);
if (clearCompilerBtn) clearCompilerBtn.addEventListener('click', clearCompiler);

async function executeCompiler() {
    const schema = compilerSchema.value.trim();
    const query = compilerQuery.value.trim();

    if (!schema) {
        alert('Please provide database schema (CREATE TABLE + INSERT statements)');
        return;
    }

    if (!query) {
        alert('Please provide a SQL query to execute');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/compile-sql', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                setup_sql: schema,
                query: query,
                dialect: 'SQLite'
            })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayCompilerResults(data);

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayCompilerResults(data) {
    // Hide placeholder
    if (compilerPlaceholder) compilerPlaceholder.style.display = 'none';

    // Display Query Results
    let resultsHtml = '';
    
    if (data.result && data.result.columns) {
        resultsHtml += `<div class="result-stats">
            <span class="stat-badge">📊 ${data.result.rows.length} rows returned</span>
        </div>`;
        
        resultsHtml += '<div class="table-wrapper">';
        resultsHtml += '<table class="data-table">';
        resultsHtml += '<thead><tr>';
        data.result.columns.forEach(col => {
            resultsHtml += `<th>${col}</th>`;
        });
        resultsHtml += '</tr></thead><tbody>';
        
        data.result.rows.forEach(row => {
            resultsHtml += '<tr>';
            row.forEach(cell => {
                resultsHtml += `<td>${cell !== null ? cell : '<span class="null-value">NULL</span>'}</td>`;
            });
            resultsHtml += '</tr>';
        });
        resultsHtml += '</tbody></table></div>';
    } else if (data.affected_rows !== null) {
        resultsHtml += `<div class="result-message">
            <div class="message-icon">✅</div>
            <div class="message-text">
                <strong>Query executed successfully</strong>
                <p>${data.affected_rows} row(s) affected</p>
            </div>
        </div>`;
    }

    compilerResultsContent.innerHTML = resultsHtml;
    showSection(compilerResults);

    // Display All Tables
    let tablesHtml = '';
    
    if (data.tables && Object.keys(data.tables).length > 0) {
        for (const [tableName, tableData] of Object.entries(data.tables)) {
            tablesHtml += `<div class="table-group">
                <div class="table-group-header">
                    <h4>${tableName}</h4>
                    <span class="row-count">${tableData.rows.length} rows</span>
                </div>
                <div class="table-wrapper">
                    <table class="data-table">
                        <thead><tr>`;
            
            tableData.columns.forEach(col => {
                tablesHtml += `<th>${col}</th>`;
            });
            
            tablesHtml += '</tr></thead><tbody>';
            
            tableData.rows.forEach(row => {
                tablesHtml += '<tr>';
                row.forEach(cell => {
                    tablesHtml += `<td>${cell !== null ? cell : '<span class="null-value">NULL</span>'}</td>`;
                });
                tablesHtml += '</tr>';
            });
            
            tablesHtml += '</tbody></table></div></div>';
        }
    }

    compilerTablesContent.innerHTML = tablesHtml;
    showSection(compilerTables);

    // Scroll to results
    compilerResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function clearCompiler() {
    compilerSchema.value = '';
    compilerQuery.value = '';
    compilerResultsContent.innerHTML = '';
    compilerTablesContent.innerHTML = '';
    hideSection(compilerResults);
    hideSection(compilerTables);
    if (compilerPlaceholder) compilerPlaceholder.style.display = 'flex';
}

function loadSampleSchema() {
    compilerSchema.value = `-- Sample Database: E-commerce Store
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    stock INTEGER
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    city TEXT
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    order_date DATE
);

-- Sample Data
INSERT INTO products VALUES (1, 'Laptop', 'Electronics', 1200.00, 15);
INSERT INTO products VALUES (2, 'Mouse', 'Electronics', 25.00, 50);
INSERT INTO products VALUES (3, 'Desk Chair', 'Furniture', 300.00, 20);
INSERT INTO products VALUES (4, 'Monitor', 'Electronics', 400.00, 12);

INSERT INTO customers VALUES (1, 'Alice Johnson', 'alice@example.com', 'New York');
INSERT INTO customers VALUES (2, 'Bob Smith', 'bob@example.com', 'Los Angeles');
INSERT INTO customers VALUES (3, 'Charlie Brown', 'charlie@example.com', 'Chicago');

INSERT INTO orders VALUES (1, 1, 1, 1, '2024-01-15');
INSERT INTO orders VALUES (2, 1, 2, 2, '2024-01-15');
INSERT INTO orders VALUES (3, 2, 4, 1, '2024-01-20');
INSERT INTO orders VALUES (4, 3, 3, 1, '2024-02-01');`;

    compilerQuery.value = `-- Sample Query: Get all orders with customer and product details
SELECT 
    o.id AS order_id,
    c.name AS customer_name,
    p.name AS product_name,
    o.quantity,
    (o.quantity * p.price) AS total_price,
    o.order_date
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id
ORDER BY o.order_date DESC;`;
}

// Make loadSampleSchema globally accessible
window.loadSampleSchema = loadSampleSchema;

// ============= QUERY OPTIMIZER FUNCTIONS =============

if (analyzeBtn) analyzeBtn.addEventListener('click', analyzeQuery);
if (clearOptimizerBtn) clearOptimizerBtn.addEventListener('click', clearOptimizer);
if (optimizeBtn) optimizeBtn.addEventListener('click', optimizeQuery);

async function analyzeQuery() {
    const query = optimizerQuery.value.trim();
    const dialect = dialectSelect.value;

    if (!query) {
        alert('Please enter a SQL query to analyze');
        return;
    }

    showLoading(true);
    hideSection(optimizationSection);
    hideSection(explanationSection);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, dialect })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        currentAnalysis = data.analysis;
        displayAnalysis(data.analysis);
        showSection(analysisSection);

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayAnalysis(analysis) {
    let html = '';

    if (analysis.syntax_issues && analysis.syntax_issues.length > 0) {
        html += '<h3>❌ Syntax Issues</h3>';
        html += '<ul class="issue-list error">';
        analysis.syntax_issues.forEach(issue => html += `<li>${issue}</li>`);
        html += '</ul>';
    }

    if (analysis.logical_issues && analysis.logical_issues.length > 0) {
        html += '<h3>⚠️ Logical Issues</h3>';
        html += '<ul class="issue-list warning">';
        analysis.logical_issues.forEach(issue => html += `<li>${issue}</li>`);
        html += '</ul>';
    }

    if (analysis.performance_issues && analysis.performance_issues.length > 0) {
        html += '<h3>🐌 Performance Issues</h3>';
        html += '<ul class="issue-list warning">';
        analysis.performance_issues.forEach(issue => html += `<li>${issue}</li>`);
        html += '</ul>';
    }

    if (analysis.overall_assessment) {
        html += '<h3>📋 Overall Assessment</h3>';
        html += `<div class="assessment">${analysis.overall_assessment}</div>`;
    }

    if (analysis.hints_for_improvement && analysis.hints_for_improvement.length > 0) {
        html += '<h3>💡 Hints for Improvement</h3>';
        html += '<ul class="issue-list success">';
        analysis.hints_for_improvement.forEach(hint => html += `<li>${hint}</li>`);
        html += '</ul>';
    }

    if (!analysis.syntax_issues?.length && !analysis.logical_issues?.length && !analysis.performance_issues?.length) {
        html += '<div class="assessment success-assessment">✅ No major issues found! Your query looks good.</div>';
    }

    analysisContent.innerHTML = html;
}

async function optimizeQuery() {
    const query = optimizerQuery.value.trim();

    if (!query || !currentAnalysis) {
        alert('Please analyze the query first');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, analysis: currentAnalysis })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayOptimizations(data.optimized);
        showSection(optimizationSection);

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayOptimizations(optimized) {
    let html = '';

    if (optimized.optimized_query) {
        html += `<div class="optimization-variant">
            <h3>✨ Optimized Query</h3>`;
        
        if (optimized.changes_made) {
            html += `<div class="changes-section">
                <strong>🔧 Changes Made:</strong>
                <ul class="changes-list">
                    ${optimized.changes_made.map(change => `<li>${change}</li>`).join('')}
                </ul>
            </div>`;
        }
        
        if (optimized.performance_gain) {
            html += `<div class="performance-section">
                <strong>⚡ Performance Gain:</strong>
                <p>${optimized.performance_gain}</p>
            </div>`;
        }
        
        html += `<div class="query-box">${escapeHtml(optimized.optimized_query)}</div>
            <button class="btn btn-primary explain-btn" onclick="explainOptimization(\`${escapeHtml(optimized.optimized_query)}\`)">
                📖 Explain Optimization
            </button>
        </div>`;
    } else {
        html += '<p class="no-results">No optimizations needed.</p>';
    }

    optimizationContent.innerHTML = html;
}

async function explainOptimization(optimizedQuery) {
    const originalQuery = optimizerQuery.value.trim();
    const dialect = dialectSelect.value;

    showLoading(true);

    try {
        const response = await fetch('/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ original: originalQuery, optimized: optimizedQuery, dialect })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayExplanation(data.explanation);
        showSection(explanationSection);
        explanationSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayExplanation(explanation) {
    let html = explanation
        .replace(/```sql\n([\s\S]*?)\n```/g, '<pre class="code-block"><code>$1</code></pre>')
        .replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
        .replace(/^####\s*(.+)$/gim, '<h4 class="section-title">$1</h4>')
        .replace(/^###\s*(.+)$/gim, '<h3 class="section-title">$1</h3>')
        .replace(/^##\s*(.+)$/gim, '<h2 class="main-title">$1</h2>')
        .replace(/^#\s*(.+)$/gim, '<h1 class="main-title">$1</h1>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        .replace(/^\d+\.\s*(.+)$/gm, '<li class="numbered-item">$1</li>')
        .replace(/(<li class="numbered-item">.*<\/li>\n?)+/g, '<ol class="explanation-list">$&</ol>')
        .replace(/^[-•]\s*(.+)$/gm, '<li class="bullet-item">$1</li>')
        .replace(/(<li class="bullet-item">.*<\/li>\n?)+/g, '<ul class="bullet-list">$&</ul>');
    
    html = html.split('\n\n').map(para => {
        para = para.trim();
        if (para && !para.startsWith('<h') && !para.startsWith('<pre') && !para.startsWith('<ol') && !para.startsWith('<ul')) {
            return '<p class="explanation-paragraph">' + para + '</p>';
        }
        return para;
    }).join('\n');
    
    explanationContent.innerHTML = html;
}

function clearOptimizer() {
    optimizerQuery.value = '';
    currentAnalysis = null;
    hideSection(analysisSection);
    hideSection(optimizationSection);
    hideSection(explanationSection);
}

// ============= PRACTICE QUESTIONS FUNCTIONS =============

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        filterQuestions(this.dataset.difficulty);
    });
});

async function loadPracticeQuestions() {
    showLoading(true);

    try {
        const response = await fetch('/get-practice-questions');
        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        allQuestions = data.questions || [];
        displayQuestions(allQuestions);

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayQuestions(questions) {
    let html = '';

    questions.forEach(q => {
        const difficultyClass = q.difficulty.toLowerCase();
        html += `
            <div class="question-card" data-difficulty="${q.difficulty}">
                <div class="question-header">
                    <h3>${q.id}. ${q.title}</h3>
                    <span class="difficulty-badge ${difficultyClass}">${q.difficulty}</span>
                </div>
                <p class="question-description">${q.description}</p>
                
                <div class="question-meta">
                    <strong>📋 Tables:</strong> ${q.tables.join(', ')}
                </div>
                
                <div class="question-meta">
                    <strong>📊 Expected Output:</strong>
                    <pre class="expected-output">${q.example_output}</pre>
                </div>
                
                <div class="question-actions">
                    <button class="btn btn-primary" onclick="viewTables(${q.id})">📋 View Tables</button>
                    <button class="btn btn-secondary" onclick="showHint(${q.id})">💡 Hint</button>
                    <button class="btn btn-secondary" onclick="showSolution(${q.id})">✓ Solution</button>
                </div>
                
                <div id="hint-${q.id}" class="hint-box hidden">
                    <strong>💡 Hint:</strong> ${q.hint}
                </div>
                
                <div id="solution-${q.id}" class="solution-box hidden">
                    <strong>✓ Solution:</strong>
                    <pre class="code-block"><code>${q.solution}</code></pre>
                    <button class="btn btn-success" onclick="runSolution(${q.id}, \`${escapeHtml(q.solution)}\`)">▶️ Run This Query</button>
                </div>
                
                <div id="tables-${q.id}" class="tables-view hidden"></div>
                
                <div id="query-${q.id}" class="query-workspace hidden">
                    <h4>✍️ Write Your Solution:</h4>
                    <textarea id="user-query-${q.id}" rows="5" placeholder="Write your SQL query here..."></textarea>
                    <button class="btn btn-success" onclick="runUserQuery(${q.id})">▶️ Run Query</button>
                </div>
                
                <div id="results-${q.id}" class="query-results hidden"></div>
            </div>
        `;
    });

    questionsContainer.innerHTML = html;
}

async function viewTables(questionId) {
    const tablesDiv = document.getElementById(`tables-${questionId}`);
    const queryDiv = document.getElementById(`query-${questionId}`);
    
    if (!tablesDiv.classList.contains('hidden')) {
        tablesDiv.classList.add('hidden');
        queryDiv.classList.add('hidden');
        return;
    }
    
    showLoading(true);

    try {
        const response = await fetch('/get-question-schema', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question_id: questionId })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayTables(questionId, data.schema, data.data);
        tablesDiv.classList.remove('hidden');
        queryDiv.classList.remove('hidden');

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayTables(questionId, schema, data) {
    const tablesDiv = document.getElementById(`tables-${questionId}`);
    let html = '<h4>📋 Database Tables:</h4>';

    for (const [tableName, tableData] of Object.entries(data)) {
        html += `<div class="table-section">
            <h5>${tableName}</h5>
            <div class="schema-info">
                <strong>Schema:</strong> ${schema[tableName].map(col => {
                    let colStr = `${col.name} (${col.type})`;
                    if (col.pk) colStr += ' PK';
                    return colStr;
                }).join(', ')}
            </div>
            <div class="table-wrapper">
                <table class="data-table">
                    <thead><tr>
                        ${tableData.columns.map(col => `<th>${col}</th>`).join('')}
                    </tr></thead>
                    <tbody>
                        ${tableData.rows.map(row => `<tr>
                            ${row.map(cell => `<td>${cell !== null ? cell : '<span class="null-value">NULL</span>'}</td>`).join('')}
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
        </div>`;
    }

    tablesDiv.innerHTML = html;
}

async function runUserQuery(questionId) {
    const queryTextarea = document.getElementById(`user-query-${questionId}`);
    const query = queryTextarea.value.trim();
    
    if (!query) {
        alert('Please write a query first');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/execute-question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, question_id: questionId })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayQueryResults(questionId, data, query);

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function runSolution(questionId, solution) {
    showLoading(true);

    try {
        const response = await fetch('/execute-question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: solution, question_id: questionId })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayQueryResults(questionId, data, solution);

    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayQueryResults(questionId, data, query) {
    const resultsDiv = document.getElementById(`results-${questionId}`);
    
    let html = '<h4>✅ Query Results:</h4>';
    html += '<div class="executed-query">';
    html += '<strong>Executed Query:</strong>';
    html += `<pre class="code-block"><code>${escapeHtml(query)}</code></pre>`;
    html += '</div>';
    
    html += `<div class="result-info"><p><strong>Rows returned:</strong> ${data.row_count}</p></div>`;

    if (data.row_count > 0) {
        html += '<div class="table-wrapper">';
        html += '<table class="data-table">';
        html += '<thead><tr>';
        data.columns.forEach(col => html += `<th>${col}</th>`);
        html += '</tr></thead><tbody>';
        
        data.rows.forEach(row => {
            html += '<tr>';
            row.forEach(cell => html += `<td>${cell !== null ? cell : '<span class="null-value">NULL</span>'}</td>`);
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
    } else {
        html += '<p class="no-results">No results found.</p>';
    }

    resultsDiv.innerHTML = html;
    resultsDiv.classList.remove('hidden');
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function filterQuestions(difficulty) {
    const filtered = difficulty === 'all' ? allQuestions : allQuestions.filter(q => q.difficulty === difficulty);
    displayQuestions(filtered);
}

function showHint(questionId) {
    document.getElementById(`hint-${questionId}`).classList.toggle('hidden');
}

function showSolution(questionId) {
    document.getElementById(`solution-${questionId}`).classList.toggle('hidden');
}

// ============= HELPER FUNCTIONS =============

function showSection(section) {
    if (section) section.classList.remove('hidden');
}

function hideSection(section) {
    if (section) section.classList.add('hidden');
}

function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
        '`': '&#96;'
    };
    return text.replace(/[&<>"'`]/g, m => map[m]);
}

// Make functions globally accessible
window.explainOptimization = explainOptimization;
window.viewTables = viewTables;
window.runUserQuery = runUserQuery;
window.runSolution = runSolution;
window.showHint = showHint;
window.showSolution = showSolution;