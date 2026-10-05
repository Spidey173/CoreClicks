/**
 * CoreClicks 2.0 Expense Tracker & Financial Hub
 * Income/Expense Logging, Category Budgets, Cash Flow Trend & Category Breakdown
 */

let cashFlowChart = null;
let categoryChart = null;

async function loadExpenseSummary() {
    try {
        const data = await apiFetch('/api/v1/expenses/summary');
        renderExpenseDashboard(data);
        loadTransactionsList();
    } catch (err) {
        console.error(err);
    }
}

function renderExpenseDashboard(summary) {
    document.getElementById('expense-total-income').textContent = `$${summary.total_income.toLocaleString()}`;
    document.getElementById('expense-total-spent').textContent = `$${summary.total_expense.toLocaleString()}`;
    document.getElementById('expense-net-savings').textContent = `$${summary.net_savings.toLocaleString()}`;
    document.getElementById('expense-savings-rate').textContent = `${summary.savings_rate}%`;

    // Cash Flow Trend Chart
    const cfCanvas = document.getElementById('expense-cashflow-chart');
    if (cfCanvas && summary.cash_flow_trend) {
        if (cashFlowChart) cashFlowChart.destroy();
        cashFlowChart = new Chart(cfCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: summary.cash_flow_trend.labels,
                datasets: [
                    { label: 'Income', data: summary.cash_flow_trend.income, backgroundColor: '#10b981', borderRadius: 4 },
                    { label: 'Expenses', data: summary.cash_flow_trend.expenses, backgroundColor: '#ef4444', borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } }
            }
        });
    }

    // Category Doughnut Chart
    const catCanvas = document.getElementById('expense-category-chart');
    if (catCanvas && summary.category_breakdown) {
        if (categoryChart) categoryChart.destroy();
        const cats = Object.keys(summary.category_breakdown);
        const vals = Object.values(summary.category_breakdown);

        categoryChart = new Chart(catCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: cats,
                datasets: [{
                    data: vals,
                    backgroundColor: ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#64748b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }

    // Budgets List
    const budgetsList = document.getElementById('expense-budgets-list');
    if (budgetsList && summary.budgets) {
        if (summary.budgets.length === 0) {
            budgetsList.innerHTML = '<div class="text-center text-muted py-3 small">No category budgets set</div>';
        } else {
            budgetsList.innerHTML = summary.budgets.map(b => `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center small mb-1">
                        <span class="fw-bold">${escapeHtml(b.category)}</span>
                        <span class="${b.is_exceeded ? 'text-danger fw-bold' : 'text-muted'}">$${b.spent} / $${b.limit}</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar ${b.is_exceeded ? 'bg-danger' : 'bg-primary'}" style="width: ${b.percentage}%;"></div>
                    </div>
                </div>
            `).join('');
        }
    }
}

async function loadTransactionsList() {
    const listEl = document.getElementById('expense-transactions-table-body');
    if (!listEl) return;

    try {
        const txs = await apiFetch('/api/v1/expenses/transactions');
        if (txs.length === 0) {
            listEl.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4 small">No transactions recorded yet</td></tr>';
            return;
        }

        listEl.innerHTML = txs.map(t => `
            <tr>
                <td><span class="badge ${t.type === 'income' ? 'badge-soft-success' : 'badge-soft-danger'} text-capitalize">${t.type}</span></td>
                <td class="fw-bold">${escapeHtml(t.merchant || t.category)}</td>
                <td><span class="badge bg-subtle text-muted">${escapeHtml(t.category)}</span></td>
                <td class="small text-muted">${t.transaction_date}</td>
                <td class="fw-bold font-monospace ${t.type === 'income' ? 'text-success' : 'text-danger'}">
                    ${t.type === 'income' ? '+' : '-'}$${t.amount.toFixed(2)}
                </td>
                <td class="text-end">
                    <button class="btn btn-sm btn-link text-danger p-0" onclick="deleteTransaction(${t.id})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

async function handleAddTransaction() {
    const type = document.getElementById('tx-type')?.value || 'expense';
    const amount = parseFloat(document.getElementById('tx-amount')?.value || '0');
    const category = document.getElementById('tx-category')?.value.trim() || 'General';
    const merchant = document.getElementById('tx-merchant')?.value.trim() || '';
    const date = document.getElementById('tx-date')?.value || '';

    if (amount <= 0) {
        showToast('Please enter a valid positive amount', 'warning');
        return;
    }

    try {
        await apiFetch('/api/v1/expenses/transactions', {
            method: 'POST',
            body: { type, amount, category, merchant, date }
        });

        loadExpenseSummary();

        // Close modal
        const modalEl = document.getElementById('addTransactionModal');
        if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }

        showToast('Transaction logged!', 'success');
    } catch (err) {
        console.error(err);
    }
}

async function deleteTransaction(id) {
    try {
        await apiFetch(`/api/v1/expenses/transactions/${id}`, { method: 'DELETE' });
        loadExpenseSummary();
        showToast('Transaction deleted', 'info');
    } catch (err) {
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadExpenseSummary();

    const saveTxBtn = document.getElementById('save-transaction-btn');
    if (saveTxBtn) saveTxBtn.addEventListener('click', handleAddTransaction);
});
