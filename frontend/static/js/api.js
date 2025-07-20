
// ============================================================================
// frontend/static/js/api.js - API Communication Layer
// ============================================================================

class APIClient {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Network error' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Document endpoints
    async uploadDocument(formData) {
        return this.request('/documents/upload', {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    }

    async getDocuments(page = 1, limit = 20) {
        return this.request(`/documents/?page=${page}&limit=${limit}`);
    }

    async getDocument(documentId) {
        return this.request(`/documents/${documentId}`);
    }

    async deleteDocument(documentId) {
        return this.request(`/documents/${documentId}`, {
            method: 'DELETE'
        });
    }

    // Query endpoints
    async askQuestion(question, options = {}) {
        return this.request('/queries/ask', {
            method: 'POST',
            body: JSON.stringify({
                question,
                max_results: options.maxResults || 5,
                include_sources: options.includeSources !== false,
                context_filter: options.contextFilter,
                temperature: options.temperature || 0.3
            })
        });
    }

    async getQueryHistory(page = 1, limit = 20) {
        return this.request(`/queries/history?page=${page}&limit=${limit}`);
    }

    async getQuery(queryId) {
        return this.request(`/queries/${queryId}`);
    }

    // Analytics endpoints
    async getAnalytics() {
        return this.request('/analytics/');
    }

    async getDocumentAnalytics() {
        return this.request('/analytics/documents');
    }

    async getQueryAnalytics() {
        return this.request('/analytics/queries');
    }

    // Health endpoint
    async getHealth() {
        return this.request('/health/', {
            headers: {} // No auth required for health check
        });
    }
}

// Export for use in other modules
window.APIClient = APIClient;