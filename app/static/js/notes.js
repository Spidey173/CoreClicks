/**
 * CoreClicks 2.0 Notes & Markdown Workspace
 * Split-pane Live Preview, Folders, Tags, Version Snapshots, Word Counts & Exports
 */

let allNotes = [];
let activeNoteId = null;
let autosaveTimeout = null;

async function loadNotes() {
    try {
        const notes = await apiFetch('/api/v1/notes');
        allNotes = notes;
        renderNotesSidebar();
        if (allNotes.length > 0 && !activeNoteId) {
            selectNote(allNotes[0].id);
        }
    } catch (err) {
        console.error(err);
    }
}

function renderNotesSidebar() {
    const listEl = document.getElementById('notes-list-sidebar');
    if (!listEl) return;

    if (allNotes.length === 0) {
        listEl.innerHTML = '<div class="text-center text-muted py-4 small">No notes yet</div>';
        return;
    }

    listEl.innerHTML = allNotes.map(n => `
        <div class="p-3 border-bottom cursor-pointer hover-bg rounded mb-1 ${activeNoteId === n.id ? 'bg-subtle-box border-primary border' : ''}"
             onclick="selectNote(${n.id})">
            <div class="d-flex justify-content-between align-items-start mb-1">
                <h6 class="fw-bold mb-0 text-truncate ${n.is_pinned ? 'text-warning' : ''}">${n.is_pinned ? '<i class="fas fa-thumbtack me-1"></i>' : ''}${escapeHtml(n.title)}</h6>
                <span class="badge bg-subtle text-muted small">${escapeHtml(n.folder)}</span>
            </div>
            <p class="small text-muted text-truncate mb-1">${escapeHtml(n.content.slice(0, 60)) || 'No content...'}</p>
            <div class="d-flex justify-content-between align-items-center small text-muted" style="font-size: 0.75rem;">
                <span>${n.reading_stats ? n.reading_stats.words : 0} words</span>
                <span>${n.reading_stats ? n.reading_stats.reading_time_min : 1} min read</span>
            </div>
        </div>
    `).join('');
}

async function selectNote(noteId) {
    try {
        const note = await apiFetch(`/api/v1/notes/${noteId}`);
        activeNoteId = note.id;

        const titleInput = document.getElementById('note-title-input');
        const contentInput = document.getElementById('note-content-input');
        const folderInput = document.getElementById('note-folder-input');
        const previewEl = document.getElementById('note-live-preview');
        const statsEl = document.getElementById('note-stats-display');

        if (titleInput) titleInput.value = note.title;
        if (contentInput) contentInput.value = note.content;
        if (folderInput) folderInput.value = note.folder;
        if (previewEl) previewEl.innerHTML = note.html_preview || '<p class="text-muted fst-italic">Preview...</p>';
        if (statsEl && note.reading_stats) {
            statsEl.textContent = `${note.reading_stats.words} words • ${note.reading_stats.chars} chars • ~${note.reading_stats.reading_time_min} min read`;
        }

        renderNotesSidebar();
    } catch (err) {
        console.error(err);
    }
}

function updateMarkdownPreview() {
    const contentInput = document.getElementById('note-content-input');
    const previewEl = document.getElementById('note-live-preview');
    const statsEl = document.getElementById('note-stats-display');

    if (!contentInput || !previewEl) return;

    const raw = contentInput.value;
    const words = raw.trim() ? raw.trim().split(/\s+/).length : 0;
    const chars = raw.length;
    const readTime = Math.max(1, Math.ceil(words / 200));

    if (statsEl) {
        statsEl.textContent = `${words} words • ${chars} chars • ~${readTime} min read`;
    }

    // Trigger autosave debounced
    clearTimeout(autosaveTimeout);
    autosaveTimeout = setTimeout(saveCurrentNote, 1500);
}

async function saveCurrentNote() {
    if (!activeNoteId) return;

    const title = document.getElementById('note-title-input')?.value.trim() || 'Untitled Note';
    const content = document.getElementById('note-content-input')?.value || '';
    const folder = document.getElementById('note-folder-input')?.value.trim() || 'General';

    try {
        const res = await apiFetch(`/api/v1/notes/${activeNoteId}`, {
            method: 'PUT',
            body: { title, content, folder }
        });

        const idx = allNotes.findIndex(n => n.id === activeNoteId);
        if (idx !== -1) allNotes[idx] = res.note;
        renderNotesSidebar();

        const autosaveIndicator = document.getElementById('autosave-status-badge');
        if (autosaveIndicator) {
            autosaveIndicator.textContent = 'Saved';
            autosaveIndicator.className = 'badge badge-soft-success';
        }
    } catch (err) {
        console.error(err);
    }
}

async function handleCreateNewNote() {
    try {
        const res = await apiFetch('/api/v1/notes', {
            method: 'POST',
            body: { title: 'Untitled Note', content: '# New Note\n\nStart writing here...', folder: 'General' }
        });

        allNotes.unshift(res.note);
        selectNote(res.note.id);
        showToast('Created new note!', 'success');
    } catch (err) {
        console.error(err);
    }
}

async function handleDeleteCurrentNote() {
    if (!activeNoteId) return;
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
        await apiFetch(`/api/v1/notes/${activeNoteId}`, { method: 'DELETE' });
        allNotes = allNotes.filter(n => n.id !== activeNoteId);
        activeNoteId = allNotes.length > 0 ? allNotes[0].id : null;
        if (activeNoteId) {
            selectNote(activeNoteId);
        } else {
            renderNotesSidebar();
        }
        showToast('Note deleted', 'info');
    } catch (err) {
        console.error(err);
    }
}

async function handleTogglePin() {
    if (!activeNoteId) return;
    try {
        const res = await apiFetch(`/api/v1/notes/${activeNoteId}/pin`, { method: 'POST' });
        const n = allNotes.find(x => x.id === activeNoteId);
        if (n) n.is_pinned = res.is_pinned;
        renderNotesSidebar();
        showToast(res.is_pinned ? 'Note pinned to top' : 'Note unpinned', 'info');
    } catch (err) {
        console.error(err);
    }
}

function exportCurrentNote(format) {
    const title = document.getElementById('note-title-input')?.value.trim() || 'note';
    const content = document.getElementById('note-content-input')?.value || '';

    let blob, filename;
    if (format === 'md') {
        blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
        filename = `${title.replace(/[^a-zA-Z0-9_-]/g, '_')}.md`;
    } else {
        const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"></head><body class="container py-5">${document.getElementById('note-live-preview')?.innerHTML || ''}</body></html>`;
        blob = new Blob([html], { type: 'text/html;charset=utf-8;' });
        filename = `${title.replace(/[^a-zA-Z0-9_-]/g, '_')}.html`;
    }

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`Exported ${filename}`, 'success');
}

document.addEventListener('DOMContentLoaded', () => {
    loadNotes();

    const contentInput = document.getElementById('note-content-input');
    if (contentInput) {
        contentInput.addEventListener('input', updateMarkdownPreview);
    }

    const newBtn = document.getElementById('new-note-btn');
    if (newBtn) newBtn.addEventListener('click', handleCreateNewNote);

    const deleteBtn = document.getElementById('delete-note-btn');
    if (deleteBtn) deleteBtn.addEventListener('click', handleDeleteCurrentNote);

    const pinBtn = document.getElementById('pin-note-btn');
    if (pinBtn) pinBtn.addEventListener('click', handleTogglePin);
});
