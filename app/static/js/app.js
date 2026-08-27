/**
 * CoreClicks 2.0 Global Application Shell
 * Theme Manager, Omni-Search (Cmd+K), Notification Center & Toasts
 */

// Theme Manager
function initTheme() {
    const savedTheme = localStorage.getItem('coreclicks_theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', next);
            localStorage.setItem('coreclicks_theme', next);
            updateThemeIcon(next);
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Global API Fetch Helper
async function apiFetch(url, options = {}) {
    const headers = {};
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }
    headers['Accept'] = 'application/json';

    if (options.headers) {
        Object.assign(headers, options.headers);
    }

    const config = { ...options, headers };
    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        config.body = JSON.stringify(options.body);
    }

    try {
        const response = await fetch(url, config);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const errorMsg = data.message || `Request failed with status ${response.status}`;
            showToast(errorMsg, 'danger');
            throw new Error(errorMsg);
        }

        return data;
    } catch (err) {
        console.error('API Error:', err);
        throw err;
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container-custom';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-success text-white' :
                    type === 'danger' ? 'bg-danger text-white' :
                    type === 'warning' ? 'bg-warning text-dark' : 'bg-dark text-white';

    toast.className = `p-3 rounded-3 shadow-lg ${bgClass} d-flex align-items-center justify-content-between gap-3 animate__animated animate__fadeInUp`;
    toast.style.minWidth = '280px';
    toast.style.maxWidth = '400px';

    const icon = type === 'success' ? 'fa-circle-check' :
                 type === 'danger' ? 'fa-circle-xmark' :
                 type === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-info';

    toast.innerHTML = `
        <div class="d-flex align-items-center gap-2 small fw-semibold">
            <i class="fas ${icon}"></i>
            <span>${escapeHtml(message)}</span>
        </div>
        <button type="button" class="btn-close btn-close-white small p-0 opacity-75" style="font-size: 0.65rem;" onclick="this.parentElement.remove()"></button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4500);
}

// Utility: HTML Escape
function escapeHtml(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[tag] || tag));
}

// Global Omni-Search (Cmd+K / Ctrl+K)
function initOmniSearch() {
    const modalEl = document.getElementById('omniSearchModal');
    const input = document.getElementById('omni-search-input');
    const resultsContainer = document.getElementById('omni-results-container');
    if (!modalEl || !input) return;

    const modal = new bootstrap.Modal(modalEl);

    // Keyboard shortcut listener
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            modal.show();
            setTimeout(() => input.focus(), 250);
        }
    });

    let debounceTimer;
    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const q = input.value.trim();
        if (q.length < 2) {
            if (resultsContainer) resultsContainer.innerHTML = '<div class="text-center text-muted py-4 small">Type at least 2 characters to search...</div>';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const res = await apiFetch(`/api/v1/search?q=${encodeURIComponent(q)}`);
                renderOmniSearchResults(res.results);
            } catch (err) {
                console.error(err);
            }
        }, 200);
    });
}

function renderOmniSearchResults(results) {
    const container = document.getElementById('omni-results-container');
    if (!container) return;

    let html = '';
    let totalMatches = 0;

    // Tasks
    if (results.tasks && results.tasks.length > 0) {
        totalMatches += results.tasks.length;
        html += '<div class="small fw-bold text-muted text-uppercase mb-1 px-2 pt-2"><i class="fas fa-tasks text-success me-1"></i> Tasks</div>';
        results.tasks.forEach(t => {
            html += `
                <a href="/tasks" class="omni-result-item">
                    <span>${escapeHtml(t.title)}</span>
                    <span class="badge badge-soft-success">${t.status}</span>
                </a>
            `;
        });
    }

    // Notes
    if (results.notes && results.notes.length > 0) {
        totalMatches += results.notes.length;
        html += '<div class="small fw-bold text-muted text-uppercase mb-1 px-2 pt-2"><i class="fas fa-note-sticky text-warning me-1"></i> Notes</div>';
        results.notes.forEach(n => {
            html += `
                <a href="/notes" class="omni-result-item">
                    <span>${escapeHtml(n.title)}</span>
                    <span class="badge badge-soft-warning">${n.folder}</span>
                </a>
            `;
        });
    }

    // Expenses
    if (results.expenses && results.expenses.length > 0) {
        totalMatches += results.expenses.length;
        html += '<div class="small fw-bold text-muted text-uppercase mb-1 px-2 pt-2"><i class="fas fa-wallet text-info me-1"></i> Expenses</div>';
        results.expenses.forEach(e => {
            html += `
                <a href="/expenses" class="omni-result-item">
                    <span>${escapeHtml(e.merchant || e.category)}</span>
                    <span class="badge ${e.type === 'income' ? 'badge-soft-success' : 'badge-soft-danger'}">$${e.amount.toFixed(2)}</span>
                </a>
            `;
        });
    }

    // Short URLs
    if (results.urls && results.urls.length > 0) {
        totalMatches += results.urls.length;
        html += '<div class="small fw-bold text-muted text-uppercase mb-1 px-2 pt-2"><i class="fas fa-link text-primary me-1"></i> Short Links</div>';
        results.urls.forEach(u => {
            html += `
                <a href="/url-shortener" class="omni-result-item">
                    <span>/${escapeHtml(u.short_code)} — ${escapeHtml(u.title)}</span>
                    <span class="badge badge-soft-primary">${u.clicks} clicks</span>
                </a>
            `;
        });
    }

    if (totalMatches === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4 small">No matching records found across your workspace.</div>';
    } else {
        container.innerHTML = html;
    }
}

// Notification Center
async function loadNotifications() {
    const listEl = document.getElementById('notifications-dropdown-list');
    const badge = document.getElementById('notifications-badge');
    if (!listEl) return;

    try {
        const res = await apiFetch('/api/v1/notifications');
        if (badge) {
            badge.textContent = res.unread_count;
            badge.style.display = res.unread_count > 0 ? 'inline-block' : 'none';
        }

        if (res.notifications.length === 0) {
            listEl.innerHTML = '<div class="text-center text-muted py-3 small">No notifications yet</div>';
            return;
        }

        listEl.innerHTML = res.notifications.map(n => `
            <div class="p-2 border-bottom small ${n.is_read ? 'opacity-75' : 'bg-subtle-box'} mb-1 rounded">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-bold">${escapeHtml(n.title)}</span>
                    <span class="badge badge-soft-${n.type}">${n.type}</span>
                </div>
                <div class="text-muted small">${escapeHtml(n.message)}</div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

// Copy Helper
function copyToClipboard(text, successMsg = 'Copied to clipboard!') {
    navigator.clipboard.writeText(text).then(() => {
        showToast(successMsg, 'success');
    }).catch(() => {
        showToast('Failed to copy to clipboard', 'danger');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initOmniSearch();
    loadNotifications();

    const notifBtn = document.getElementById('notificationsDropdownBtn');
    if (notifBtn) {
        notifBtn.addEventListener('click', loadNotifications);
    }

    const markAllReadBtn = document.getElementById('mark-all-read-btn');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async () => {
            await apiFetch('/api/v1/notifications/mark-all-read', { method: 'POST' });
            loadNotifications();
            showToast('All notifications marked as read', 'info');
        });
    }
});
