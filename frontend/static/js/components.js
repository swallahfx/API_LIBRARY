// ============================================================================
// frontend/static/js/components.js - Reusable UI Components
// ============================================================================

class UIComponents {
    static createLoadingSpinner(text = 'Loading...') {
        const wrapper = document.createElement('div');
        wrapper.className = 'loading';
        wrapper.innerHTML = `
            <div class="spinner"></div>
            <p>${text}</p>
        `;
        return wrapper;
    }

    static createDocumentCard(document) {
        const card = document.createElement('div');
        card.className = 'document-card';
        card.innerHTML = `
            <div class="document-header">
                <h3>${document.filename}</h3>
                <div class="document-actions">
                    <button class="btn btn-sm" onclick="viewDocument('${document.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-error" onclick="deleteDocument('${document.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
            <div class="document-meta">
                <span class="meta-item">
                    <i class="fas fa-file"></i> ${document.content_type}
                </span>
                <span class="meta-item">
                    <i class="fas fa-calendar"></i> ${new Date(document.upload_date).toLocaleDateString()}
                </span>
                <span class="meta-item">
                    <i class="fas fa-layer-group"></i> ${document.chunk_count || 0} chunks
                </span>
            </div>
            ${document.metadata?.description ? `<p class="document-description">${document.metadata.description}</p>` : ''}
        `;
        return card;
    }

    static createQueryCard(query) {
        const card = document.createElement('div');
        card.className = 'query-card';
        card.innerHTML = `
            <div class="query-header">
                <h4>${query.question}</h4>
                <div class="query-meta">
                    <span class="confidence-badge confidence-${this.getConfidenceLevel(query.confidence)}">
                        ${Math.round(query.confidence * 100)}% confidence
                    </span>
                    <span class="time-badge">${this.formatTime(query.timestamp)}</span>
                </div>
            </div>
            <div class="query-answer">
                ${query.answer}
            </div>
            <div class="query-sources">
                <small>${query.sources.length} sources</small>
            </div>
        `;
        return card;
    }

    static createNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
        
        return notification;
    }

    static createModal(title, content, actions = []) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-content">
                    ${content}
                </div>
                <div class="modal-actions">
                    ${actions.map(action => `
                        <button class="btn ${action.class || ''}" onclick="${action.onclick || ''}">
                            ${action.text}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }

    static getConfidenceLevel(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.6) return 'medium';
        return 'low';
    }

    static getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    static formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }

    static formatFileSize(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Export for global use
window.UIComponents = UIComponents;