/**
 * CoreClicks 2.0 REST API Tester & Postman Client
 * Method selection, Auth headers, JSON payload beautifier, Latency timer & History
 */

async function handleSendApiRequest() {
    const method = document.getElementById('api-method-select')?.value || 'GET';
    const url = document.getElementById('api-url-input')?.value.trim() || '';
    const authType = document.getElementById('api-auth-type')?.value || 'none';
    const bearerToken = document.getElementById('api-auth-bearer-token')?.value || '';
    const headersText = document.getElementById('api-headers-input')?.value || '{}';
    const bodyText = document.getElementById('api-body-input')?.value || '';
    const sendBtn = document.getElementById('send-api-btn');

    if (!url) {
        showToast('Please enter target URL', 'warning');
        return;
    }

    let parsedHeaders = {};
    if (headersText.trim()) {
        try {
            parsedHeaders = JSON.parse(headersText);
        } catch (e) {
            showToast('Headers must be valid JSON', 'warning');
            return;
        }
    }

    const authData = {};
    if (authType === 'bearer') {
        authData.token = bearerToken;
    }

    if (sendBtn) {
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Sending...';
        sendBtn.disabled = true;
    }

    try {
        const res = await apiFetch('/api/v1/api-tester/send', {
            method: 'POST',
            body: {
                method,
                url,
                headers: parsedHeaders,
                body: bodyText,
                auth_type: authType,
                auth_data: authData
            }
        });

        renderApiResponse(res);
        loadApiHistory();
    } catch (err) {
        console.error(err);
    } finally {
        if (sendBtn) {
            sendBtn.innerHTML = '<i class="fas fa-paper-plane me-1"></i> Send Request';
            sendBtn.disabled = false;
        }
    }
}

function renderApiResponse(res) {
    const statusBadge = document.getElementById('api-status-badge');
    const latencyEl = document.getElementById('api-latency-badge');
    const sizeEl = document.getElementById('api-size-badge');
    const bodyEl = document.getElementById('api-response-body');
    const headersEl = document.getElementById('api-response-headers');

    const code = res.status_code || 0;
    let badgeClass = 'bg-danger';
    if (code >= 200 && code < 300) badgeClass = 'bg-success';
    else if (code >= 300 && code < 400) badgeClass = 'bg-info';
    else if (code >= 400 && code < 500) badgeClass = 'bg-warning text-dark';

    if (statusBadge) {
        statusBadge.className = `badge ${badgeClass} fs-6`;
        statusBadge.textContent = `${code} ${res.status_text || ''}`;
    }

    if (latencyEl) latencyEl.textContent = `${res.latency_ms} ms`;
    if (sizeEl) sizeEl.textContent = `${(res.size_bytes / 1024).toFixed(2)} KB`;

    if (bodyEl) {
        if (res.json_data) {
            bodyEl.textContent = JSON.stringify(res.json_data, null, 2);
        } else {
            bodyEl.textContent = res.body || 'No response body returned.';
        }
    }

    if (headersEl) {
        headersEl.textContent = JSON.stringify(res.headers, null, 2);
    }
}

async function loadApiHistory() {
    const listEl = document.getElementById('api-history-sidebar');
    if (!listEl) return;

    try {
        const logs = await apiFetch('/api/v1/api-tester/history');
        if (logs.length === 0) {
            listEl.innerHTML = '<div class="text-center text-muted py-4 small">No history</div>';
            return;
        }

        listEl.innerHTML = logs.map(l => `
            <div class="p-2 border-bottom small cursor-pointer hover-bg d-flex justify-content-between align-items-center"
                 onclick="loadHistoryReq('${escapeHtml(l.method)}', '${escapeHtml(l.url)}')">
                <div class="text-truncate me-2">
                    <span class="badge ${l.method === 'GET' ? 'bg-primary' : 'bg-success'} small text-uppercase">${l.method}</span>
                    <span class="font-monospace text-muted small ms-1">${escapeHtml(l.url)}</span>
                </div>
                <span class="badge ${l.status_code >= 200 && l.status_code < 300 ? 'badge-soft-success' : 'badge-soft-danger'}">${l.status_code || 'ERR'}</span>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

function loadHistoryReq(method, url) {
    const mSelect = document.getElementById('api-method-select');
    const uInput = document.getElementById('api-url-input');
    if (mSelect) mSelect.value = method;
    if (uInput) uInput.value = url;
    showToast(`Loaded ${method} ${url}`, 'info');
}

function beautifyJsonBody() {
    const bodyInput = document.getElementById('api-body-input');
    if (!bodyInput || !bodyInput.value.trim()) return;

    try {
        const parsed = JSON.parse(bodyInput.value.trim());
        bodyInput.value = JSON.stringify(parsed, null, 2);
        showToast('JSON formatted', 'success');
    } catch (e) {
        showToast('Invalid JSON structure', 'warning');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadApiHistory();

    const sendBtn = document.getElementById('send-api-btn');
    if (sendBtn) sendBtn.addEventListener('click', handleSendApiRequest);

    const formatBtn = document.getElementById('beautify-json-btn');
    if (formatBtn) formatBtn.addEventListener('click', beautifyJsonBody);

    const authSelect = document.getElementById('api-auth-type');
    const bearerField = document.getElementById('auth-bearer-group');
    if (authSelect && bearerField) {
        authSelect.addEventListener('change', () => {
            bearerField.style.display = authSelect.value === 'bearer' ? 'block' : 'none';
        });
    }

    const copyBtn = document.getElementById('copy-api-response-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const txt = document.getElementById('api-response-body')?.textContent || '';
            copyToClipboard(txt, 'Response body copied!');
        });
    }
});
