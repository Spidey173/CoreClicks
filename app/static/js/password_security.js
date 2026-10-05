/**
 * CoreClicks 2.0 Password Security Auditor
 * Entropy scoring, crack time, breach database scan, passphrase & random generators
 */

async function handleAnalyzePassword() {
    const input = document.getElementById('password-input');
    const pwd = input ? input.value : '';

    try {
        const res = await apiFetch('/api/v1/password-security/analyze', {
            method: 'POST',
            body: { password: pwd }
        });

        renderPasswordAnalysis(res.analysis);
        loadAuditHistory();
    } catch (err) {
        console.error(err);
    }
}

function renderPasswordAnalysis(analysis) {
    const scoreBar = document.getElementById('password-strength-progress');
    const scoreText = document.getElementById('password-score-text');
    const strengthBadge = document.getElementById('password-strength-badge');
    const entropyEl = document.getElementById('password-entropy-val');
    const crackTimeEl = document.getElementById('password-crack-time-val');
    const breachAlert = document.getElementById('password-breach-alert');
    const recsList = document.getElementById('password-recommendations-list');

    const score = analysis.score || 0;
    if (scoreBar) {
        scoreBar.style.width = `${score}%`;
        scoreBar.className = `progress-bar ${
            score < 30 ? 'bg-danger' :
            score < 50 ? 'bg-warning' :
            score < 75 ? 'bg-info' : 'bg-success'
        }`;
    }

    if (scoreText) scoreText.textContent = `${score}/100`;
    if (strengthBadge) {
        strengthBadge.textContent = analysis.strength;
        strengthBadge.className = `badge badge-soft-${
            analysis.strength.includes('Weak') ? 'danger' :
            analysis.strength === 'Fair' ? 'warning' : 'success'
        } fs-6`;
    }

    if (entropyEl) entropyEl.textContent = `${analysis.entropy_bits} bits`;
    if (crackTimeEl) crackTimeEl.textContent = analysis.crack_time;

    if (breachAlert) {
        breachAlert.style.display = analysis.is_breached ? 'block' : 'none';
    }

    if (recsList) {
        if (analysis.recommendations.length === 0) {
            recsList.innerHTML = '<li class="text-success small"><i class="fas fa-check-circle me-1"></i> Excellent password! Meets all enterprise security standards.</li>';
        } else {
            recsList.innerHTML = analysis.recommendations.map(r => `
                <li class="text-muted small mb-1"><i class="fas fa-circle-info text-primary me-1"></i> ${escapeHtml(r)}</li>
            `).join('');
        }
    }
}

async function handleGeneratePassword() {
    const type = document.querySelector('input[name="gen-type"]:checked')?.value || 'random';
    const length = document.getElementById('gen-length-slider')?.value || 16;
    const words = document.getElementById('gen-words-slider')?.value || 4;

    try {
        const res = await apiFetch('/api/v1/password-security/generate', {
            method: 'POST',
            body: { type, length, words }
        });

        const input = document.getElementById('password-input');
        if (input) input.value = res.password;

        renderPasswordAnalysis(res.analysis);
        loadAuditHistory();
        showToast('Generated high-entropy password!', 'success');
    } catch (err) {
        console.error(err);
    }
}

async function loadAuditHistory() {
    const listEl = document.getElementById('password-audit-history-list');
    if (!listEl) return;

    try {
        const history = await apiFetch('/api/v1/password-security/history');
        if (history.length === 0) {
            listEl.innerHTML = '<div class="text-center text-muted py-3 small">No audit history</div>';
            return;
        }

        listEl.innerHTML = history.map(h => `
            <div class="p-2 border-bottom small d-flex justify-content-between align-items-center">
                <span class="font-monospace text-muted">${escapeHtml(h.masked_password)}</span>
                <div class="d-flex align-items-center gap-2">
                    <span class="badge badge-soft-info">${h.entropy_bits} bits</span>
                    <span class="badge ${h.score >= 70 ? 'badge-soft-success' : 'badge-soft-danger'}">${h.strength}</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadAuditHistory();

    const input = document.getElementById('password-input');
    if (input) {
        input.addEventListener('input', handleAnalyzePassword);
    }

    const genBtn = document.getElementById('generate-password-btn');
    if (genBtn) genBtn.addEventListener('click', handleGeneratePassword);

    const copyBtn = document.getElementById('copy-password-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const pwd = document.getElementById('password-input')?.value || '';
            if (pwd) copyToClipboard(pwd, 'Password copied securely!');
        });
    }
});
