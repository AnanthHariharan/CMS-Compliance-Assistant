// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Example question click handler
function askExampleQuestion(element) {
    const question = element.textContent;
    document.getElementById('question').value = question;
    askQuestion();
}

// Q&A Functions
function handleQuestionKeyPress(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

async function askQuestion() {
    const questionInput = document.getElementById('question');
    const question = questionInput.value.trim();

    if (!question) {
        alert('Please enter a question');
        return;
    }

    const askBtn = document.getElementById('ask-btn');
    askBtn.disabled = true;
    askBtn.textContent = 'Processing...';

    // Add user message to chat
    addMessage('user', question);
    questionInput.value = '';

    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: question,
                n_results: 5
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Add assistant message with sources
        addMessage('assistant', data.answer, data.sources);

    } catch (error) {
        console.error('Error:', error);
        addMessage('assistant', `Error: ${error.message}. Please make sure the API server is running.`);
    } finally {
        askBtn.disabled = false;
        askBtn.textContent = 'Ask Question';
    }
}

function addMessage(type, content, sources = []) {
    const chatMessages = document.getElementById('chat-messages');

    // Remove empty state if it exists
    const emptyState = chatMessages.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = type === 'user' ? 'You' : 'Assistant';
    messageDiv.appendChild(label);

    const contentDiv = document.createElement('div');
    contentDiv.textContent = content;
    messageDiv.appendChild(contentDiv);

    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'sources';
        sourcesDiv.innerHTML = '<strong>Sources:</strong>';

        sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.innerHTML = `
                <strong>Source ${index + 1}</strong>
                (Page ${source.page_number || 'N/A'},
                Relevance: ${(source.similarity_score * 100).toFixed(1)}%)
                ${source.section_header ? `<br><em>${source.section_header}</em>` : ''}
                <br>${source.text}
            `;
            sourcesDiv.appendChild(sourceItem);
        });

        messageDiv.appendChild(sourcesDiv);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Validation Functions
async function validateNote() {
    const noteTextarea = document.getElementById('visit-note');
    const noteText = noteTextarea.value.trim();

    if (!noteText) {
        alert('Please enter a visit note to validate');
        return;
    }

    const validateBtn = document.getElementById('validate-btn');
    validateBtn.disabled = true;
    validateBtn.textContent = 'Validating...';

    const resultDiv = document.getElementById('validation-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing visit note...</p></div>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                note_text: noteText
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayValidationResult(data);

    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}. Please make sure the API server is running.</p>`;
    } finally {
        validateBtn.disabled = false;
        validateBtn.textContent = 'Validate Note';
    }
}

function displayValidationResult(result) {
    const resultDiv = document.getElementById('validation-result');

    let html = `
        <h3>Validation Result</h3>
        <span class="status-badge status-${result.status}">${formatStatus(result.status)}</span>
        <div class="score">Score: ${result.overall_score.toFixed(1)}/100</div>
        <p><strong>Summary:</strong> ${result.summary}</p>
    `;

    // Display violations
    if (result.violations && result.violations.length > 0) {
        html += '<div class="violations"><h4>Issues Found:</h4>';
        result.violations.forEach(violation => {
            html += `
                <div class="violation ${violation.severity}">
                    <div class="violation-header">
                        ${violation.category.replace(/_/g, ' ').toUpperCase()}
                        <span class="violation-severity severity-${violation.severity}">${violation.severity.toUpperCase()}</span>
                    </div>
                    <p><strong>Issue:</strong> ${violation.description}</p>
                    <p><strong>Recommendation:</strong> ${violation.recommendation}</p>
                    ${violation.guideline_reference ? `<p><em>Reference: ${violation.guideline_reference}</em></p>` : ''}
                </div>
            `;
        });
        html += '</div>';
    }

    // Display strengths
    if (result.strengths && result.strengths.length > 0) {
        html += '<div class="strengths"><h4>Strengths:</h4><ul>';
        result.strengths.forEach(strength => {
            html += `<li>${strength}</li>`;
        });
        html += '</ul></div>';
    }

    resultDiv.innerHTML = html;
}

function formatStatus(status) {
    const statusMap = {
        'compliant': 'COMPLIANT',
        'needs_review': 'NEEDS REVIEW',
        'non_compliant': 'NON-COMPLIANT'
    };
    return statusMap[status] || status;
}

// Check API health on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('API Health:', data);
            if (data.status === 'no_data') {
                alert('Warning: Vector store is empty. Please run the ingestion script first.');
            }
        }
    } catch (error) {
        console.warn('Could not connect to API:', error);
        alert('Warning: Cannot connect to API server. Please make sure it is running on http://localhost:8000');
    }
});
