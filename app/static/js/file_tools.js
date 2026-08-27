/**
 * CoreClicks 2.0 — File Converter & PDF/Image Studio
 * Image Transformation, Live Previews, PDF Merge & Split Orchestration
 */

document.addEventListener('DOMContentLoaded', () => {
    initImageStudio();
    initPdfMerge();
    initPdfSplit();
});

/* -------------------------------------------------------------------------
   1. Image Studio: Previews, Slider & Transformations
   ------------------------------------------------------------------------- */
function initImageStudio() {
    const fileInput = document.getElementById('image-file-input');
    const previewWrapper = document.getElementById('image-preview-wrapper');
    const previewThumb = document.getElementById('image-preview-thumb');
    const previewName = document.getElementById('image-preview-name');
    const previewInfo = document.getElementById('image-preview-info');
    const qualitySlider = document.getElementById('image-quality-slider');
    const qualityValDisplay = document.getElementById('quality-val-display');
    const processBtn = document.getElementById('process-image-btn');
    const resetBtn = document.getElementById('image-reset-btn');
    const resultCard = document.getElementById('image-download-result-card');
    const placeholderCard = document.getElementById('image-placeholder-card');

    if (qualitySlider && qualityValDisplay) {
        qualitySlider.addEventListener('input', () => {
            qualityValDisplay.textContent = `${qualitySlider.value}%`;
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (!file) {
                if (previewWrapper) previewWrapper.style.display = 'none';
                return;
            }

            if (previewName) previewName.textContent = file.name;
            const sizeKB = (file.size / 1024).toFixed(1);

            const reader = new FileReader();
            reader.onload = (e) => {
                if (previewThumb) previewThumb.src = e.target.result;
                const img = new Image();
                img.onload = () => {
                    if (previewInfo) previewInfo.textContent = `${sizeKB} KB • ${img.naturalWidth} × ${img.naturalHeight} px`;
                };
                img.src = e.target.result;
                if (previewWrapper) previewWrapper.style.display = 'block';
            };
            reader.readAsDataURL(file);
        });
    }

    if (processBtn) {
        processBtn.addEventListener('click', async () => {
            if (!fileInput || !fileInput.files.length) {
                showToast('Please select an image file to process', 'warning');
                return;
            }

            const formatSelect = document.getElementById('image-target-format');
            const widthInput = document.getElementById('image-resize-width');
            const heightInput = document.getElementById('image-resize-height');
            const rotateSelect = document.getElementById('image-rotate-select');
            const watermarkInput = document.getElementById('image-watermark-text');

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('target_format', formatSelect ? formatSelect.value : 'png');
            if (widthInput && widthInput.value) formData.append('width', widthInput.value);
            if (heightInput && heightInput.value) formData.append('height', heightInput.value);
            if (qualitySlider) formData.append('quality', qualitySlider.value);
            if (rotateSelect) formData.append('rotation', rotateSelect.value);
            if (watermarkInput && watermarkInput.value.trim()) formData.append('watermark', watermarkInput.value.trim());

            processBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Processing Image...';
            processBtn.disabled = true;

            try {
                const res = await apiFetch('/api/v1/file-tools/image/process', {
                    method: 'POST',
                    body: formData
                });

                if (placeholderCard) placeholderCard.style.display = 'none';
                if (resultCard) resultCard.style.display = 'flex';

                const downloadLink = document.getElementById('image-download-link');
                const statsEl = document.getElementById('image-process-stats');

                if (downloadLink) {
                    downloadLink.href = `/api/v1/file-tools/download/${res.download_token}`;
                    downloadLink.download = res.filename;
                }

                if (statsEl) {
                    const procKB = (res.processed_size / 1024).toFixed(1);
                    statsEl.textContent = `Output: ${res.filename} (${procKB} KB • ${res.savings_pct}% size change)`;
                }

                showToast('Image transformed successfully!', 'success');
            } catch (err) {
                console.error(err);
            } finally {
                processBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles me-1"></i> Process & Convert Image';
                processBtn.disabled = false;
            }
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (fileInput) fileInput.value = '';
            if (previewWrapper) previewWrapper.style.display = 'none';
            if (resultCard) resultCard.style.display = 'none';
            if (placeholderCard) placeholderCard.style.display = 'flex';
        });
    }
}

/* -------------------------------------------------------------------------
   2. PDF Merge Orchestration
   ------------------------------------------------------------------------- */
function initPdfMerge() {
    const filesInput = document.getElementById('pdf-merge-files-input');
    const mergeBtn = document.getElementById('merge-pdf-btn');
    const listWrapper = document.getElementById('pdf-merge-list-wrapper');
    const filesList = document.getElementById('pdf-merge-files-list');
    const countEl = document.getElementById('pdf-merge-count');
    const downloadCard = document.getElementById('pdf-merge-download-card');
    const downloadLink = document.getElementById('pdf-merge-download-link');
    const statsEl = document.getElementById('pdf-merge-stats');

    if (filesInput) {
        filesInput.addEventListener('change', () => {
            if (!filesList || !listWrapper || !countEl) return;
            filesList.innerHTML = '';

            const files = Array.from(filesInput.files);
            if (!files.length) {
                listWrapper.style.display = 'none';
                return;
            }

            countEl.textContent = files.length;
            files.forEach((f, idx) => {
                const li = document.createElement('li');
                li.className = 'list-group-item bg-transparent d-flex justify-content-between align-items-center py-2 px-3';
                li.innerHTML = `
                    <div class="d-flex align-items-center gap-2 text-truncate">
                        <span class="badge bg-secondary text-white rounded-pill">${idx + 1}</span>
                        <span class="text-truncate fw-semibold">${escapeHtml(f.name)}</span>
                    </div>
                    <span class="text-muted font-mono" style="font-size: 0.75rem;">${(f.size / 1024).toFixed(1)} KB</span>
                `;
                filesList.appendChild(li);
            });

            listWrapper.style.display = 'block';
            if (downloadCard) downloadCard.style.display = 'none';
        });
    }

    if (mergeBtn) {
        mergeBtn.addEventListener('click', async () => {
            if (!filesInput || filesInput.files.length < 2) {
                showToast('Please select at least 2 PDF files to merge', 'warning');
                return;
            }

            const formData = new FormData();
            for (let i = 0; i < filesInput.files.length; i++) {
                formData.append('files', filesInput.files[i]);
            }

            mergeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Merging PDF Documents...';
            mergeBtn.disabled = true;

            try {
                const res = await apiFetch('/api/v1/file-tools/pdf/merge', {
                    method: 'POST',
                    body: formData
                });

                if (downloadCard && downloadLink) {
                    downloadCard.style.display = 'block';
                    downloadLink.href = `/api/v1/file-tools/download/${res.download_token}`;
                    downloadLink.download = res.filename;
                }

                if (statsEl) {
                    statsEl.textContent = `Generated ${res.filename} (${(res.processed_size / 1024).toFixed(1)} KB)`;
                }

                showToast('PDFs merged successfully!', 'success');
            } catch (err) {
                console.error(err);
            } finally {
                mergeBtn.innerHTML = '<i class="fas fa-object-group me-1"></i> Merge Selected PDFs';
                mergeBtn.disabled = false;
            }
        });
    }
}

/* -------------------------------------------------------------------------
   3. PDF Split & Extraction
   ------------------------------------------------------------------------- */
function initPdfSplit() {
    const fileInput = document.getElementById('pdf-split-file-input');
    const pagesInput = document.getElementById('pdf-split-pages-input');
    const splitBtn = document.getElementById('split-pdf-btn');
    const downloadCard = document.getElementById('pdf-split-download-card');
    const downloadLink = document.getElementById('pdf-split-download-link');
    const statsEl = document.getElementById('pdf-split-stats');

    if (splitBtn) {
        splitBtn.addEventListener('click', async () => {
            if (!fileInput || !fileInput.files.length) {
                showToast('Please select a source PDF document', 'warning');
                return;
            }

            const pages = pagesInput ? pagesInput.value.trim() : '1';
            if (!pages) {
                showToast('Please specify the page range (e.g. 1-3, 5)', 'warning');
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('pages', pages);

            splitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Extracting PDF Pages...';
            splitBtn.disabled = true;

            try {
                const res = await apiFetch('/api/v1/file-tools/pdf/split', {
                    method: 'POST',
                    body: formData
                });

                if (downloadCard && downloadLink) {
                    downloadCard.style.display = 'block';
                    downloadLink.href = `/api/v1/file-tools/download/${res.download_token}`;
                    downloadLink.download = res.filename;
                }

                if (statsEl) {
                    statsEl.textContent = `Generated ${res.filename} (${(res.processed_size / 1024).toFixed(1)} KB)`;
                }

                showToast('Pages extracted successfully!', 'success');
            } catch (err) {
                console.error(err);
            } finally {
                splitBtn.innerHTML = '<i class="fas fa-scissors me-1"></i> Extract & Generate PDF';
                splitBtn.disabled = false;
            }
        });
    }
}
