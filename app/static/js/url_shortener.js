/**
 * CoreClicks 2.0 URL Shortener & QR Studio
 * Custom Slugs, Passwords, Expiration, QR Code Generation & Click Tracking
 */

let allLinks = [];

async function loadShortLinks() {
    try {
        const links = await apiFetch('/api/v1/url-shortener');
        allLinks = links;
        renderShortLinksTable();
    } catch (err) {
        console.error(err);
    }
}

function renderShortLinksTable() {
    const tableBody = document.getElementById('short-links-table-body');
    const emptyState = document.getElementById('urls-empty-state');
    if (!tableBody) return;

    if (allLinks.length === 0) {
        tableBody.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';
    const origin = window.location.origin;

    tableBody.innerHTML = allLinks.map(l => {
        const fullShortUrl = `${origin}/${l.short_code}`;
        return `
            <tr>
                <td>
                    <div class="fw-semibold text-truncate" style="max-width: 200px;">${escapeHtml(l.title)}</div>
                    <div class="small text-muted text-truncate" style="max-width: 250px;">
                        <a href="${escapeHtml(l.original_url)}" target="_blank" class="text-muted text-decoration-none">${escapeHtml(l.original_url)}</a>
                    </div>
                </td>
                <td>
                    <div class="d-flex align-items-center gap-2">
                        <a href="${fullShortUrl}" target="_blank" class="text-primary font-monospace fw-bold text-decoration-none">
                            /${escapeHtml(l.short_code)}
                        </a>
                        <button class="btn btn-sm btn-link text-muted p-0" onclick="copyToClipboard('${fullShortUrl}', 'Link copied!')"><i class="far fa-copy"></i></button>
                    </div>
                </td>
                <td>
                    <span class="badge badge-soft-success">${l.clicks} clicks</span>
                    ${l.has_password ? '<span class="badge badge-soft-warning ms-1"><i class="fas fa-lock"></i></span>' : ''}
                    ${l.is_expired ? '<span class="badge badge-soft-danger ms-1">Expired</span>' : ''}
                </td>
                <td class="small text-muted">${l.expires_at || 'Never'}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-custom me-1" onclick="showQrModal(${l.id}, '${escapeHtml(l.short_code)}')"><i class="fas fa-qrcode"></i></button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteShortUrl(${l.id})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    }).join('');
}

async function handleShortenUrl() {
    const url = document.getElementById('original-url-input')?.value.trim() || '';
    const title = document.getElementById('url-title-input')?.value.trim() || '';
    const custom_code = document.getElementById('custom-code-input')?.value.trim() || '';
    const password = document.getElementById('url-password-input')?.value || '';
    const expires_at = document.getElementById('url-expiry-input')?.value || null;

    if (!url) {
        showToast('Please enter destination URL', 'warning');
        return;
    }

    try {
        const res = await apiFetch('/api/v1/url-shortener', {
            method: 'POST',
            body: { url, title, custom_code, password, expires_at }
        });

        allLinks.unshift(res.short_url);
        renderShortLinksTable();
        showQrModal(res.short_url.id, res.short_url.short_code);
        showToast('Short link created!', 'success');
    } catch (err) {
        console.error(err);
    }
}

function showQrModal(id, shortCode) {
    const modalEl = document.getElementById('urlQrModal');
    const qrImg = document.getElementById('modal-qr-img');
    const pngLink = document.getElementById('download-qr-png');
    const svgLink = document.getElementById('download-qr-svg');

    if (qrImg) qrImg.src = `/api/v1/url-shortener/${id}/qr?format=png`;
    if (pngLink) pngLink.href = `/api/v1/url-shortener/${id}/qr?format=png`;
    if (svgLink) svgLink.href = `/api/v1/url-shortener/${id}/qr?format=svg`;

    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}

async function deleteShortUrl(id) {
    if (!confirm('Are you sure you want to delete this link?')) return;
    try {
        await apiFetch(`/api/v1/url-shortener/${id}`, { method: 'DELETE' });
        allLinks = allLinks.filter(l => l.id !== id);
        renderShortLinksTable();
        showToast('Link deleted', 'info');
    } catch (err) {
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadShortLinks();

    const shortenBtn = document.getElementById('shorten-url-btn');
    if (shortenBtn) shortenBtn.addEventListener('click', handleShortenUrl);
});
