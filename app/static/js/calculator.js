/**
 * CoreClicks 2.0 Safe Calculator Engine
 * Scientific AST evaluation, memory registers, keyboard controls, history drawer
 */

let angleMode = 'rad';
let memoryValue = 0;

function appendCalc(val) {
    const input = document.getElementById('calc-expression-input');
    if (input) {
        input.value += val;
        input.focus();
    }
}

function clearCalc() {
    const input = document.getElementById('calc-expression-input');
    const resultEl = document.getElementById('calc-result-display');
    if (input) input.value = '';
    if (resultEl) resultEl.textContent = '0';
}

function deleteCalcChar() {
    const input = document.getElementById('calc-expression-input');
    if (input) {
        input.value = input.value.slice(0, -1);
    }
}

function toggleAngleMode() {
    angleMode = angleMode === 'rad' ? 'deg' : 'rad';
    const btn = document.getElementById('angle-mode-toggle-btn');
    if (btn) {
        btn.textContent = angleMode.toUpperCase();
        btn.className = `btn btn-sm ${angleMode === 'rad' ? 'btn-magma-primary' : 'btn-magma-outline'}`;
    }
    showToast(`Angle mode set to ${angleMode.toUpperCase()}`, 'info');
}

// Memory Registers (M+, M-, MR, MC)
function handleMemory(action) {
    const resultEl = document.getElementById('calc-result-display');
    const currentVal = parseFloat(resultEl ? resultEl.textContent : '0') || 0;

    if (action === 'MC') {
        memoryValue = 0;
        showToast('Memory Cleared (MC)', 'info');
    } else if (action === 'MR') {
        appendCalc(memoryValue.toString());
        showToast(`Memory Recalled: ${memoryValue}`, 'info');
    } else if (action === 'M+') {
        memoryValue += currentVal;
        showToast(`Added to Memory: ${memoryValue}`, 'info');
    } else if (action === 'M-') {
        memoryValue -= currentVal;
        showToast(`Subtracted from Memory: ${memoryValue}`, 'info');
    }
}

async function evaluateCalculation() {
    const input = document.getElementById('calc-expression-input');
    const resultEl = document.getElementById('calc-result-display');
    const expr = input ? input.value.trim() : '';

    if (!expr) return;

    try {
        const res = await apiFetch('/api/v1/calculator/calculate', {
            method: 'POST',
            body: { expression: expr, angle_mode: angleMode }
        });

        if (resultEl) resultEl.textContent = res.result;
        loadCalcHistory();
    } catch (err) {
        if (resultEl) resultEl.textContent = 'Error';
    }
}

async function loadCalcHistory() {
    const listEl = document.getElementById('calc-history-list');
    if (!listEl) return;

    try {
        const calcs = await apiFetch('/api/v1/calculator/history');
        if (calcs.length === 0) {
            listEl.innerHTML = '<div class="text-center text-muted py-3 small">No calculations yet</div>';
            return;
        }

        listEl.innerHTML = calcs.map(c => `
            <div class="p-2 border-bottom small d-flex justify-content-between align-items-center cursor-pointer hover-bg"
                 onclick="setCalcExpression('${escapeHtml(c.expression)}')">
                <span class="font-monospace text-muted">${escapeHtml(c.expression)} =</span>
                <span class="font-monospace fw-bold text-primary">${escapeHtml(c.result)}</span>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

function setCalcExpression(expr) {
    const input = document.getElementById('calc-expression-input');
    if (input) {
        input.value = expr;
        input.focus();
    }
}

async function clearCalcHistory() {
    await apiFetch('/api/v1/calculator/history', { method: 'DELETE' });
    loadCalcHistory();
    showToast('Calculation history cleared', 'info');
}

document.addEventListener('DOMContentLoaded', () => {
    loadCalcHistory();

    const input = document.getElementById('calc-expression-input');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                evaluateCalculation();
            }
        });
    }

    const copyBtn = document.getElementById('copy-calc-result-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const res = document.getElementById('calc-result-display')?.textContent || '0';
            copyToClipboard(res, 'Result copied to clipboard!');
        });
    }
});
