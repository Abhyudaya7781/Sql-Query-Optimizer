let currentAnalysis = null;
let selectedOptimization = null;

// DOM Elements
const queryInput = document.getElementById('query');
const dialectSelect = document.getElementById('dialect');
const schemaInput = document.getElementById('schema');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const optimizeBtn = document.getElementById('optimizeBtn');
const loading = document.getElementById('loading');

const analysisSection = document.getElementById('analysisSection');
const analysisContent = document.getElementById('analysisContent');
const optimizationSection = document.getElementById('optimizationSection');
const optimizationContent = document.getElementById('optimizationContent');
const explanationSection = document.getElementById('explanationSection');
const explanationContent = document.getElementById('explanationContent');

// Event Listeners
analyzeBtn.addEventListener('click', analyzeQuery);
clearBtn.addEventListener('click', clearAll);
optimizeBtn.addEventListener('click', optimizeQuery);

// Analyze Query
async function analyzeQuery() {
    const query = queryInput.value.trim();
    const dialect = dialectSelect.value;
    const schema = schemaInput.value.trim();

    if (!query) {
        alert('Please enter a SQL query');
        return;
    }

    showLoading(true);
    hideSection(optimizationSection);
    hideSection(explanationSection);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                dialect: dialect,
                schema_info: schema || 'No schema provided'
            })
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
        alert('Error analyzing query: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display Analysis Results
function displayAnalysis(analysis) {
    let html = '';

    // Syntax Issues
    if (analysis.syntax_issues && analysis.syntax_issues.length > 0) {
        html += '<h3>❌ Syntax Issues</h3>';
        html += '<ul class="issue-list error">';
        analysis.syntax_issues.forEach(issue => {
            html += `<li>${issue}</li>`;
        });
        html += '</ul>';
    }

    // Logical Issues
    if (analysis.logical_issues && analysis.logical_issues.length > 0) {
        html += '<h3>⚠️ Logical Issues</h3>';
        html += '<ul class="issue-list warning">';
        analysis.logical_issues.forEach(issue => {
            html += `<li>${issue}</li>`;
        });
        html += '</ul>';
    }

    // Performance Issues
    if (analysis.performance_issues && analysis.performance_issues.length > 0) {
        html += '<h3>🐌 Performance Issues</h3>';
        html += '<ul class="issue-list warning">';
        analysis.performance_issues.forEach(issue => {
            html += `<li>${issue}</li>`;
        });
        html += '</ul>';
    }

    // Overall Assessment
    if (analysis.overall_assessment) {
        html += '<h3>📋 Overall Assessment</h3>';
        html += `<div class="assessment">${analysis.overall_assessment}</div>`;
    }

    // Hints for Improvement
    if (analysis.hints_for_improvement && analysis.hints_for_improvement.length > 0) {
        html += '<h3>💡 Hints for Improvement</h3>';
        html += '<ul class="issue-list success">';
        analysis.hints_for_improvement.forEach(hint => {
            html += `<li>${hint}</li>`;
        });
        html += '</ul>';
    }

    // No issues found
    if ((!analysis.syntax_issues || analysis.syntax_issues.length === 0) &&
        (!analysis.logical_issues || analysis.logical_issues.length === 0) &&
        (!analysis.performance_issues || analysis.performance_issues.length === 0)) {
        html += '<div class="assessment">✅ No major issues found! Your query looks good.</div>';
    }

    analysisContent.innerHTML = html;
}

// Optimize Query
async function optimizeQuery() {
    const query = queryInput.value.trim();

    if (!query || !currentAnalysis) {
        alert('Please analyze the query first');
        return;
    }

    showLoading(true);
    hideSection(explanationSection);

    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                analysis: currentAnalysis
            })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayOptimizations(data.optimized);
        showSection(optimizationSection);

    } catch (error) {
        alert('Error optimizing query: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display Optimization Results
function displayOptimizations(optimized) {
    let html = '';

    if (optimized.optimized_variants && optimized.optimized_variants.length > 0) {
        optimized.optimized_variants.forEach((variant, index) => {
            const badgeClass = variant.optimization_level.toLowerCase();
            html += `
                <div class="optimization-variant">
                    <h3>Version ${variant.id}: <span class="badge ${badgeClass}">${variant.optimization_level}</span></h3>
                    ${variant.changes_made ? `<p><strong>Changes:</strong> ${variant.changes_made.join(', ')}</p>` : ''}
                    <div class="query-box">${escapeHtml(variant.optimized_query)}</div>
                    <button class="explain-btn" onclick="explainOptimization('${escapeHtml(variant.optimized_query)}')">
                        Explain this optimization
                    </button>
                </div>
            `;
        });
    } else {
        html += '<p>No optimizations generated.</p>';
    }

    optimizationContent.innerHTML = html;
}

// Explain Optimization
async function explainOptimization(optimizedQuery) {
    const originalQuery = queryInput.value.trim();
    const dialect = dialectSelect.value;

    showLoading(true);

    try {
        const response = await fetch('/explain', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                original: originalQuery,
                optimized: optimizedQuery,
                dialect: dialect
            })
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
        alert('Error explaining query: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display Explanation
function displayExplanation(explanation) {
    // Convert markdown-like formatting to HTML
    let html = explanation
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```sql\n([\s\S]*?)\n```/g, '<pre><code>$1</code></pre>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^\d+\.\s/gm, '<br>• ');

    html = '<p>' + html + '</p>';
    
    explanationContent.innerHTML = html;
}

// Clear All
function clearAll() {
    queryInput.value = '';
    schemaInput.value = '';
    currentAnalysis = null;
    selectedOptimization = null;
    
    hideSection(analysisSection);
    hideSection(optimizationSection);
    hideSection(explanationSection);
}

// Helper Functions
function showSection(section) {
    section.classList.remove('hidden');
}

function hideSection(section) {
    section.classList.add('hidden');
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
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Make explainOptimization globally accessible
window.explainOptimization = explainOptimization;