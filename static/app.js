// RSS News Aggregator JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-refresh functionality
    setupAutoRefresh();
    
    // Search functionality
    setupSearch();
    
    // Feed management
    setupFeedManagement();
});

// Auto-refresh every 5 minutes
function setupAutoRefresh() {
    const autoRefreshCheckbox = document.getElementById('autoRefresh');
    let refreshInterval;

    if (autoRefreshCheckbox) {
        autoRefreshCheckbox.addEventListener('change', function() {
            if (this.checked) {
                refreshInterval = setInterval(() => {
                    location.reload();
                }, 5 * 60 * 1000); // 5 minutes
                showNotification('Auto-refresh enabled', 'info');
            } else {
                clearInterval(refreshInterval);
                showNotification('Auto-refresh disabled', 'info');
            }
        });
    }
}

// Search functionality
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.toLowerCase();
            const articles = document.querySelectorAll('.article-card');
            
            articles.forEach(article => {
                const title = article.querySelector('.card-title').textContent.toLowerCase();
                const description = article.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(query) || description.includes(query)) {
                    article.closest('.col-md-6, .col-lg-4').style.display = 'block';
                } else {
                    article.closest('.col-md-6, .col-lg-4').style.display = 'none';
                }
            });
        }, 300));
    }
}

// Feed management functionality
function setupFeedManagement() {
    // Add feed form validation
    const addFeedForm = document.getElementById('addFeedForm');
    if (addFeedForm) {
        addFeedForm.addEventListener('submit', function(e) {
            const url = document.getElementById('url').value;
            if (!isValidURL(url)) {
                e.preventDefault();
                showNotification('Please enter a valid RSS URL', 'error');
            }
        });
    }

    // Feed toggle buttons
    document.querySelectorAll('.toggle-feed').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const feedId = this.dataset.feedId;
            const feedName = this.dataset.feedName;
            
            if (confirm(`Toggle feed "${feedName}"?`)) {
                window.location.href = this.href;
            }
        });
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function showNotification(message, type = 'info') {
    const alertClass = {
        'info': 'alert-info',
        'success': 'alert-success',
        'warning': 'alert-warning',
        'error': 'alert-danger'
    }[type] || 'alert-info';

    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Fetch now functionality
async function fetchNow() {
    const btn = document.querySelector('button[onclick="fetchNow()"]');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/fetch_now');
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Successfully fetched ${data.fetched} articles and analyzed ${data.analyzed}`, 'success');
            setTimeout(() => location.reload(), 2000);
        } else {
            showNotification(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Relevance score color coding
function updateRelevanceColors() {
    document.querySelectorAll('.relevance-badge').forEach(badge => {
        const score = parseFloat(badge.textContent);
        if (score >= 80) {
            badge.className = badge.className.replace('bg-primary', 'bg-success');
        } else if (score >= 60) {
            badge.className = badge.className.replace('bg-primary', 'bg-info');
        } else if (score >= 40) {
            badge.className = badge.className.replace('bg-primary', 'bg-warning');
        } else {
            badge.className = badge.className.replace('bg-primary', 'bg-secondary');
        }
    });
}

// Initialize relevance colors on page load
document.addEventListener('DOMContentLoaded', updateRelevanceColors);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + R for manual refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        fetchNow();
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
        }
    }
});

// Service worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}