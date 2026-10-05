/**
 * CoreClicks 2.0 CSV Analytics & Pandas Profiling Studio
 * CSV Upload, Statistical Summary KPIs, Chart.js Visualizations & Preview Table
 */

let activeCharts = [];

async function handleCsvUpload(file) {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const uploadStatus = document.getElementById('csv-upload-status');
    if (uploadStatus) {
        uploadStatus.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Analyzing dataset with Pandas...';
        uploadStatus.style.display = 'block';
    }

    try {
        const res = await apiFetch('/api/v1/analytics/upload', {
            method: 'POST',
            body: formData,
        });

        renderDatasetAnalysis(res.analysis);
        loadDatasetsList();
        showToast('Dataset analyzed successfully!', 'success');
    } catch (err) {
        console.error(err);
    } finally {
        if (uploadStatus) uploadStatus.style.display = 'none';
    }
}

function renderDatasetAnalysis(analysis) {
    const resultsContainer = document.getElementById('analytics-results-container');
    if (resultsContainer) resultsContainer.style.display = 'block';

    // Overview KPIs
    const ov = analysis.overview;
    document.getElementById('stat-rows-count').textContent = ov.row_count.toLocaleString();
    document.getElementById('stat-cols-count').textContent = ov.col_count;
    document.getElementById('stat-missing-count').textContent = `${ov.missing_cells} (${ov.missing_pct}%)`;
    document.getElementById('stat-dupes-count').textContent = ov.duplicate_rows;

    // Destroy old charts
    activeCharts.forEach(c => c.destroy());
    activeCharts = [];

    // Render Charts
    const chartsGrid = document.getElementById('analytics-charts-grid');
    if (chartsGrid) {
        chartsGrid.innerHTML = '';
        const charts = analysis.charts || {};

        Object.entries(charts).forEach(([key, data], idx) => {
            const isHist = key.startsWith('hist_');
            const title = key.replace('hist_', 'Histogram: ').replace('cat_', 'Top Values: ');

            const colDiv = document.createElement('div');
            colDiv.className = 'col-lg-6 mb-4';
            colDiv.innerHTML = `
                <div class="saas-card h-100 p-4">
                    <h6 class="fw-bold mb-3 small text-uppercase text-muted">${escapeHtml(title)}</h6>
                    <div style="height: 260px; position: relative;">
                        <canvas id="chart-${idx}"></canvas>
                    </div>
                </div>
            `;
            chartsGrid.appendChild(colDiv);

            const ctx = document.getElementById(`chart-${idx}`).getContext('2d');
            const newChart = new Chart(ctx, {
                type: isHist ? 'bar' : 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: title,
                        data: data.values,
                        backgroundColor: isHist ? 'rgba(79, 70, 229, 0.7)' : [
                            '#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#64748b'
                        ],
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: !isHist, position: 'bottom' } },
                    scales: isHist ? { y: { beginAtZero: true } } : {}
                }
            });
            activeCharts.push(newChart);
        });
    }

    // Preview Table
    const tableHeader = document.getElementById('analytics-table-header');
    const tableBody = document.getElementById('analytics-table-body');
    if (tableHeader && tableBody && analysis.preview_data && analysis.preview_data.length > 0) {
        const cols = Object.keys(analysis.preview_data[0]);
        tableHeader.innerHTML = cols.map(c => `<th>${escapeHtml(c)}</th>`).join('');
        tableBody.innerHTML = analysis.preview_data.map(row => `
            <tr>${cols.map(c => `<td>${escapeHtml(String(row[c]))}</td>`).join('')}</tr>
        `).join('');
    }
}

async function loadDatasetsList() {
    const listEl = document.getElementById('analytics-saved-datasets-list');
    if (!listEl) return;

    try {
        const datasets = await apiFetch('/api/v1/analytics/datasets');
        if (datasets.length === 0) {
            listEl.innerHTML = '<div class="text-center text-muted py-3 small">No saved datasets</div>';
            return;
        }

        listEl.innerHTML = datasets.map(d => `
            <div class="p-2 border-bottom small cursor-pointer hover-bg d-flex justify-content-between align-items-center"
                 onclick="loadExistingDataset(${d.id})">
                <span class="fw-semibold text-truncate me-2">${escapeHtml(d.filename)}</span>
                <span class="badge badge-soft-primary">${d.row_count} rows</span>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

async function loadExistingDataset(id) {
    try {
        const res = await apiFetch(`/api/v1/analytics/datasets/${id}`);
        renderDatasetAnalysis(res.analysis);
        showToast(`Loaded ${res.dataset.filename}`, 'info');
    } catch (err) {
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadDatasetsList();

    const fileInput = document.getElementById('csv-file-input');
    const dropzone = document.getElementById('csv-dropzone');

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) handleCsvUpload(e.target.files[0]);
        });
    }

    if (dropzone) {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('bg-subtle-box');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('bg-subtle-box'));
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('bg-subtle-box');
            if (e.dataTransfer.files.length > 0) handleCsvUpload(e.dataTransfer.files[0]);
        });
    }
});
