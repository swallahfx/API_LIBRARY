// ============================================================================
// frontend/static/js/main.js - Main Application Logic
// ============================================================================

class AILibraryApp {
    constructor() {
        this.apiBase = '/api/v1';
        this.uploadedDocuments = [];
        this.queryHistory = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadAnalytics();
        this.setupFileUpload();
    }

    setupEventListeners() {
        // Query form submission
        const questionInput = document.getElementById('questionInput');
        const askButton = document.getElementById('askButton');
        
        if (questionInput && askButton) {
            questionInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.askQuestion();
                }
            });
            
            askButton.addEventListener('click', () => this.askQuestion());
        }

        // Upload button
        const uploadButton = document.getElementById('uploadButton');
        if (uploadButton) {
            uploadButton.addEventListener('click', () => this.triggerFileUpload());
        }
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        if (!uploadArea || !fileInput) return;

        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));

        // File input change
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        const files = e.dataTransfer.files;
        this.handleFileSelect(files);
    }

    handleFileSelect(files) {
        if (files.length === 0) return;
        
        Array.from(files).forEach(file => this.uploadFile(file));
    }

    triggerFileUpload() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.click();
    }

    async uploadFile(file) {
        const uploadLoading = document.getElementById('uploadLoading');
        if (uploadLoading) uploadLoading.style.display = 'block';

        try {
            const formData = new FormData();
            formData.append('file', file);
            
            // Add metadata if available
            const title = document.getElementById('uploadTitle')?.value;
            const author = document.getElementById('uploadAuthor')?.value;
            const category = document.getElementById('uploadCategory')?.value;
            const tags = document.getElementById('uploadTags')?.value;

            if (title) formData.append('title', title);
            if (author) formData.append('author', author);
            if (category) formData.append('category', category);
            if (tags) formData.append('tags', tags);

            const response = await fetch(`${this.apiBase}/documents/upload`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.uploadedDocuments.push(result);
                this.showNotification(`${file.name} uploaded successfully!`, 'success');
                this.loadAnalytics(); // Refresh analytics
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }
        } catch (error) {
            this.showNotification(`Failed to upload ${file.name}: ${error.message}`, 'error');
        } finally {
            if (uploadLoading) uploadLoading.style.display = 'none';
        }
    }

    async askQuestion() {
        const questionInput = document.getElementById('questionInput');
        const question = questionInput?.value?.trim();
        
        if (!question) {
            this.showNotification('Please enter a question', 'error');
            return;
        }

        const queryLoading = document.getElementById('queryLoading');
        const askButton = document.getElementById('askButton');
        
        if (queryLoading) queryLoading.style.display = 'block';
        if (askButton) askButton.disabled = true;

        try {
            const response = await fetch(`${this.apiBase}/queries/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    max_results: 5,
                    include_sources: true
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayAnswer(result);
                this.queryHistory.unshift(result);
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Query failed');
            }
        } catch (error) {
            this.showNotification(`Failed to get answer: ${error.message}`, 'error');
        } finally {
            if (queryLoading) queryLoading.style.display = 'none';
            if (askButton) askButton.disabled = false;
        }
    }

    displayAnswer(result) {
        const answerSection = document.getElementById('answerSection');
        const answerText = document.getElementById('answerText');
        const confidenceText = document.getElementById('confidenceText');
        const confidenceFill = document.getElementById('confidenceFill');
        const sourcesList = document.getElementById('sourcesList');

        if (!answerSection) return;

        // Show answer
        if (answerText) answerText.textContent = result.answer;
        
        // Show confidence
        const confidencePercent = Math.round(result.confidence * 100);
        if (confidenceText) confidenceText.textContent = `${confidencePercent}%`;
        if (confidenceFill) confidenceFill.style.width = `${confidencePercent}%`;

        // Show sources
        if (sourcesList) {
            sourcesList.innerHTML = '';
            result.sources.forEach((source, index) => {
                const sourceDiv = document.createElement('div');
                sourceDiv.className = 'source-item';
                sourceDiv.innerHTML = `
                    <div class="source-meta">
                        Source ${index + 1}: ${source.metadata.filename || 'Document'} 
                        (Relevance: ${Math.round(source.relevance_score * 100)}%)
                    </div>
                    <div>${source.content}</div>
                `;
                sourcesList.appendChild(sourceDiv);
            });
        }

        answerSection.style.display = 'block';
        answerSection.scrollIntoView({ behavior: 'smooth' });
    }

    async loadAnalytics() {
        try {
            const response = await fetch(`${this.apiBase}/analytics/`);
            if (response.ok) {
                const analytics = await response.json();
                this.displayAnalytics(analytics);
            }
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    }

    displayAnalytics(analytics) {
        const analyticsGrid = document.getElementById('analyticsGrid');
        if (!analyticsGrid) return;
        
        analyticsGrid.innerHTML = `
            <div class="stat-card">
                <span class="stat-number">${analytics.total_documents}</span>
                <div class="stat-label">Documents</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">${analytics.total_queries}</span>
                <div class="stat-label">Questions Asked</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">${analytics.popular_topics.length}</span>
                <div class="stat-label">Topics</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">${Math.round(analytics.performance_metrics?.avg_query_response_time || 0)}ms</span>
                <div class="stat-label">Avg Response Time</div>
            </div>
        `;
    }

    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (!notification) return;

        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 4000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.aiLibraryApp = new AILibraryApp();
});
