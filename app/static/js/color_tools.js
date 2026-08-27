/**
 * CoreClicks 2.0 — Color Studio & WCAG Contrast Audit
 * Minimalist, High-Craft Editorial Interface
 */

let currentPalette = [];
let savedPalettesList = [];

document.addEventListener('DOMContentLoaded', () => {
    initColorStudio();
    initContrastAuditor();
    loadSavedPalettes();
});

/* -------------------------------------------------------------------------
   1. Harmony Palette Generator & Swatch Orchestration
   ------------------------------------------------------------------------- */
function initColorStudio() {
    const picker = document.getElementById('base-color-picker');
    const hexText = document.getElementById('base-hex-text');
    const harmonySelect = document.getElementById('harmony-type-select');
    const randomBtn = document.getElementById('random-palette-btn');
    const saveBtn = document.getElementById('save-palette-btn');

    const updatePalette = async () => {
        let baseHex = picker ? picker.value : '#E4572E';
        if (hexText && hexText.value.trim().startsWith('#')) {
            baseHex = hexText.value.trim();
        }

        const harmony = harmonySelect ? harmonySelect.value : 'Complementary';

        try {
            const res = await apiFetch('/api/v1/color-tools/generate', {
                method: 'POST',
                body: { base_color: baseHex, harmony }
            });

            currentPalette = res.palette;
            renderPaletteSwatches(res.palette);
            updateExportCode(res.palette, res.tailwind_config);
        } catch (err) {
            console.error(err);
        }
    };

    if (picker) {
        picker.addEventListener('input', (e) => {
            if (hexText) hexText.value = e.target.value;
            updatePalette();
        });
    }

    if (hexText) {
        hexText.addEventListener('input', (e) => {
            const val = e.target.value.trim();
            if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
                if (picker) picker.value = val;
                updatePalette();
            }
        });
    }

    if (harmonySelect) harmonySelect.addEventListener('change', updatePalette);

    if (randomBtn) {
        randomBtn.addEventListener('click', () => {
            const randomHex = '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0').toUpperCase();
            if (picker) picker.value = randomHex;
            if (hexText) hexText.value = randomHex;
            updatePalette();
        });
    }

    if (saveBtn) saveBtn.addEventListener('click', saveCurrentPalette);

    // Preset Theme Buttons
    document.querySelectorAll('.preset-theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const color = btn.dataset.color;
            const harmony = btn.dataset.harmony;
            if (picker) picker.value = color;
            if (hexText) hexText.value = color;
            if (harmonySelect && harmony) harmonySelect.value = harmony;
            updatePalette();
            showToast(`Applied ${btn.textContent.trim()} theme`, 'info');
        });
    });

    // Initial load
    updatePalette();
}

function renderPaletteSwatches(palette) {
    const container = document.getElementById('palette-swatches-container');
    if (!container) return;

    container.innerHTML = palette.map((color, index) => `
        <div class="col">
            <div class="magma-card overflow-hidden h-100 shadow-sm border border-custom" style="transition: transform 0.2s ease;">
                <!-- Large Swatch Canvas -->
                <div class="p-3 d-flex flex-column justify-content-between cursor-pointer" 
                     style="background-color: ${color.hex}; color: ${color.best_text}; min-height: 190px;"
                     onclick="copyToClipboard('${color.hex}', 'Copied ${color.hex}!')"
                     title="Click to copy HEX">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge ${color.best_text === '#ffffff' ? 'bg-dark bg-opacity-75 text-white' : 'bg-light bg-opacity-75 text-dark'} font-mono small">#${index + 1}</span>
                        <i class="far fa-copy opacity-75"></i>
                    </div>

                    <div>
                        <div class="fs-4 fw-bold font-mono">${color.hex.toUpperCase()}</div>
                    </div>
                </div>

                <!-- Swatch Details -->
                <div class="p-3 bg-surface small">
                    <div class="d-flex justify-content-between text-muted mb-1 font-mono" style="font-size: 0.75rem;">
                        <span>RGB:</span>
                        <span class="cursor-pointer" onclick="copyToClipboard('${color.rgb}', 'Copied RGB!')">${color.rgb}</span>
                    </div>
                    <div class="d-flex justify-content-between text-muted mb-2 font-mono" style="font-size: 0.75rem;">
                        <span>HSL:</span>
                        <span class="cursor-pointer" onclick="copyToClipboard('${color.hsl}', 'Copied HSL!')">${color.hsl}</span>
                    </div>

                    <div class="d-flex justify-content-between align-items-center pt-2 border-top border-custom">
                        <span class="small text-muted" style="font-size: 0.75rem;">WCAG AA</span>
                        <span class="badge ${color.wcag_aa ? 'badge-soft-success' : 'badge-soft-danger'}">
                            ${color.wcag_aa ? 'Pass' : 'Fail'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

/* -------------------------------------------------------------------------
   2. WCAG 2.1 Contrast Testing Lab
   ------------------------------------------------------------------------- */
function initContrastAuditor() {
    const fgPicker = document.getElementById('contrast-fg-input');
    const fgText = document.getElementById('contrast-fg-text');
    const bgPicker = document.getElementById('contrast-bg-input');
    const bgText = document.getElementById('contrast-bg-text');
    const swapBtn = document.getElementById('swap-contrast-colors-btn');

    const updateContrast = async () => {
        const fg = fgPicker ? fgPicker.value : '#1E1E1E';
        const bg = bgPicker ? bgPicker.value : '#FFF8F2';

        if (fgText) fgText.value = fg;
        if (bgText) bgText.value = bg;

        try {
            const res = await apiFetch('/api/v1/color-tools/contrast', {
                method: 'POST',
                body: { foreground: fg, background: bg }
            });

            const previewBox = document.getElementById('contrast-preview-box');
            const previewBtn = document.getElementById('preview-button');
            const ratioEl = document.getElementById('contrast-ratio-display');
            const badgeAA = document.getElementById('contrast-aa-badge');
            const badgeAAA = document.getElementById('contrast-aaa-badge');

            if (previewBox) {
                previewBox.style.backgroundColor = bg;
                previewBox.style.color = fg;
            }
            if (previewBtn) {
                previewBtn.style.backgroundColor = fg;
                previewBtn.style.color = bg;
            }
            if (ratioEl) ratioEl.textContent = `${res.ratio}:1`;

            if (badgeAA) {
                badgeAA.className = `badge ${res.wcag_aa_normal ? 'bg-success' : 'bg-danger'}`;
                badgeAA.textContent = res.wcag_aa_normal ? 'Pass' : 'Fail';
            }
            if (badgeAAA) {
                badgeAAA.className = `badge ${res.wcag_aaa_normal ? 'bg-success' : 'bg-danger'}`;
                badgeAAA.textContent = res.wcag_aaa_normal ? 'Pass' : 'Fail';
            }
        } catch (err) {
            console.error(err);
        }
    };

    if (fgPicker) fgPicker.addEventListener('input', updateContrast);
    if (bgPicker) bgPicker.addEventListener('input', updateContrast);

    if (fgText) {
        fgText.addEventListener('input', (e) => {
            if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value.trim())) {
                if (fgPicker) fgPicker.value = e.target.value.trim();
                updateContrast();
            }
        });
    }

    if (bgText) {
        bgText.addEventListener('input', (e) => {
            if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value.trim())) {
                if (bgPicker) bgPicker.value = e.target.value.trim();
                updateContrast();
            }
        });
    }

    if (swapBtn) {
        swapBtn.addEventListener('click', () => {
            const temp = fgPicker.value;
            fgPicker.value = bgPicker.value;
            bgPicker.value = temp;
            updateContrast();
            showToast('Swapped colors', 'info');
        });
    }

    // Initial audit
    updateContrast();
}

/* -------------------------------------------------------------------------
   3. Saved Palettes Library
   ------------------------------------------------------------------------- */
async function saveCurrentPalette() {
    if (currentPalette.length === 0) return;

    const name = prompt('Name this color palette:', 'Sunset Palette') || 'Custom Palette';
    const harmony = document.getElementById('harmony-type-select')?.value || 'Custom';
    const hexList = currentPalette.map(c => c.hex);

    try {
        await apiFetch('/api/v1/color-tools/palettes', {
            method: 'POST',
            body: { name, harmony_type: harmony, colors: hexList }
        });
        loadSavedPalettes();
        showToast('Palette saved to library!', 'success');
    } catch (err) {
        console.error(err);
    }
}

async function loadSavedPalettes() {
    try {
        const palettes = await apiFetch('/api/v1/color-tools/palettes');
        savedPalettesList = palettes;
        renderSavedPalettes();
    } catch (err) {
        console.error(err);
    }
}

function renderSavedPalettes() {
    const listEl = document.getElementById('saved-palettes-list');
    const countEl = document.getElementById('saved-palettes-count');
    if (!listEl) return;

    if (countEl) countEl.textContent = `${savedPalettesList.length} Saved`;

    if (savedPalettesList.length === 0) {
        listEl.innerHTML = `
            <div class="text-center text-muted py-5 small">
                <i class="fas fa-palette fs-3 mb-2 opacity-50 text-warning"></i>
                <div>No saved palettes yet</div>
                <div class="text-muted mt-1" style="font-size: 0.75rem;">Click "Save Palette" above to preserve your favorites.</div>
            </div>
        `;
        return;
    }

    listEl.innerHTML = savedPalettesList.map(p => `
        <div class="magma-card p-3 mb-3 border border-custom">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <h6 class="fw-bold mb-0 small text-truncate cursor-pointer" onclick="loadSavedPaletteToStudio(${JSON.stringify(p.colors).replace(/"/g, '&quot;')})">
                        ${escapeHtml(p.name)}
                    </h6>
                    <span class="text-muted" style="font-size: 0.72rem;">${escapeHtml(p.harmony_type || 'Palette')}</span>
                </div>
                <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-magma-ghost p-1 text-primary" title="Apply Palette"
                            onclick="loadSavedPaletteToStudio(${JSON.stringify(p.colors).replace(/"/g, '&quot;')})">
                        <i class="fas fa-arrow-up-right-from-square"></i>
                    </button>
                    <button class="btn btn-sm btn-magma-ghost p-1 text-danger" title="Delete Palette"
                            onclick="deleteSavedPalette(${p.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="d-flex rounded-3 overflow-hidden shadow-sm border border-custom" style="height: 34px; cursor: pointer;"
                 onclick="loadSavedPaletteToStudio(${JSON.stringify(p.colors).replace(/"/g, '&quot;')})">
                ${p.colors.map(hex => `<div class="flex-grow-1" style="background-color: ${hex};" title="${hex}"></div>`).join('')}
            </div>
        </div>
    `).join('');
}

window.loadSavedPaletteToStudio = function(colors) {
    if (!colors || !colors.length) return;
    const base = colors[0];
    const picker = document.getElementById('base-color-picker');
    const hexText = document.getElementById('base-hex-text');
    if (picker) picker.value = base;
    if (hexText) hexText.value = base;

    apiFetch('/api/v1/color-tools/generate', {
        method: 'POST',
        body: { base_color: base, harmony: 'Complementary' }
    }).then(res => {
        currentPalette = res.palette;
        renderPaletteSwatches(res.palette);
        updateExportCode(res.palette, res.tailwind_config);
        showToast('Palette applied to studio!', 'success');
    });
};

async function deleteSavedPalette(id) {
    try {
        await apiFetch(`/api/v1/color-tools/palettes/${id}`, { method: 'DELETE' });
        savedPalettesList = savedPalettesList.filter(p => p.id !== id);
        renderSavedPalettes();
        showToast('Palette removed', 'info');
    } catch (err) {
        console.error(err);
    }
}

/* -------------------------------------------------------------------------
   4. Token Export Engine
   ------------------------------------------------------------------------- */
function updateExportCode(palette, tailwindConfig) {
    const cssCodeEl = document.getElementById('export-css-code');
    const tailwindCodeEl = document.getElementById('export-tailwind-code');
    const jsonCodeEl = document.getElementById('export-json-code');

    if (cssCodeEl && palette) {
        let css = ":root {\n";
        palette.forEach((c, idx) => {
            css += `  --color-${idx + 1}: ${c.hex};\n`;
        });
        css += "}";
        cssCodeEl.textContent = css;
    }

    if (tailwindCodeEl) {
        tailwindCodeEl.textContent = tailwindConfig || "// Tailwind configuration";
    }

    if (jsonCodeEl && palette) {
        jsonCodeEl.textContent = JSON.stringify(palette, null, 2);
    }
}

window.copyFromElement = function(elementId, msg) {
    const el = document.getElementById(elementId);
    if (!el) return;
    copyToClipboard(el.textContent, msg || 'Copied to clipboard!');
};
