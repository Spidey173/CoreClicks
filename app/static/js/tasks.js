/**
 * CoreClicks 2.0 Task Manager & Kanban Studio
 * HTML5 Drag-and-Drop Kanban, Status updates, List view, Filters & Progress Stats
 */

let allTasks = [];
let currentView = 'kanban';

async function loadTasks() {
    try {
        const tasks = await apiFetch('/api/v1/tasks');
        allTasks = tasks;
        renderTasks();
        updateTaskStats();
    } catch (err) {
        console.error(err);
    }
}

function renderTasks() {
    if (currentView === 'kanban') {
        renderKanbanBoard();
    } else {
        renderListView();
    }
}

function renderKanbanBoard() {
    const cols = {
        todo: document.getElementById('kanban-todo-list'),
        in_progress: document.getElementById('kanban-in_progress-list'),
        review: document.getElementById('kanban-review-list'),
        done: document.getElementById('kanban-done-list'),
    };

    Object.values(cols).forEach(el => {
        if (el) el.innerHTML = '';
    });

    const categoryFilter = document.getElementById('task-category-filter')?.value || 'all';
    const priorityFilter = document.getElementById('task-priority-filter')?.value || 'all';
    const searchFilter = document.getElementById('task-search-input')?.value.toLowerCase().trim() || '';

    const filtered = allTasks.filter(t => {
        const matchCat = categoryFilter === 'all' || t.category === categoryFilter;
        const matchPri = priorityFilter === 'all' || t.priority === priorityFilter;
        const matchSearch = !searchFilter || t.title.toLowerCase().includes(searchFilter) || (t.description && t.description.toLowerCase().includes(searchFilter));
        return matchCat && matchPri && matchSearch;
    });

    filtered.forEach(task => {
        const colEl = cols[task.status] || cols.todo;
        if (!colEl) return;

        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.draggable = true;
        card.dataset.taskId = task.id;

        const priBadge = task.priority === 'high' ? 'badge-soft-danger' :
                         task.priority === 'medium' ? 'badge-soft-warning' : 'badge-soft-info';

        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <span class="badge ${priBadge} text-capitalize">${task.priority}</span>
                <div class="dropdown">
                    <button class="btn btn-sm btn-link text-muted p-0" data-bs-toggle="dropdown"><i class="fas fa-ellipsis-vertical"></i></button>
                    <ul class="dropdown-menu dropdown-menu-end shadow-sm">
                        <li><button class="dropdown-item text-danger" onclick="deleteTask(${task.id})"><i class="fas fa-trash me-2"></i>Delete</button></li>
                    </ul>
                </div>
            </div>
            <h6 class="fw-bold mb-1">${escapeHtml(task.title)}</h6>
            ${task.description ? `<p class="small text-muted mb-2">${escapeHtml(task.description)}</p>` : ''}
            <div class="d-flex justify-content-between align-items-center pt-2 border-top small text-muted">
                <span class="badge bg-subtle text-muted">${escapeHtml(task.category)}</span>
                ${task.due_date ? `<span><i class="far fa-calendar me-1"></i>${task.due_date}</span>` : ''}
            </div>
        `;

        // Drag events
        card.addEventListener('dragstart', (e) => {
            card.classList.add('dragging');
            e.dataTransfer.setData('text/plain', task.id);
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });

        colEl.appendChild(card);
    });
}

function initKanbanDragDrop() {
    document.querySelectorAll('.kanban-col-droppable').forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('bg-subtle-box');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('bg-subtle-box');
        });

        zone.addEventListener('drop', async (e) => {
            e.preventDefault();
            zone.classList.remove('bg-subtle-box');
            const taskId = e.dataTransfer.getData('text/plain');
            const targetStatus = zone.dataset.status;

            if (taskId && targetStatus) {
                // Find task to check if status actually changed
                const t = allTasks.find(x => x.id === parseInt(taskId));
                if (t && t.status !== targetStatus) {
                    try {
                        await apiFetch(`/api/v1/tasks/${taskId}/position`, {
                            method: 'PUT',
                            body: { status: targetStatus, position: 0 }
                        });
                        t.status = targetStatus;
                        renderTasks();
                        updateTaskStats();
                        showToast(`Moved to ${targetStatus.replace('_', ' ')}`, 'info');
                    } catch (err) {
                        console.error(err);
                    }
                }
            }
        });
    });
}

function renderListView() {
    const container = document.getElementById('tasks-list-view-container');
    if (!container) return;

    if (allTasks.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-5">No tasks found</div>';
        return;
    }

    container.innerHTML = allTasks.map(t => `
        <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-surface mb-2 rounded border">
            <div class="d-flex align-items-center gap-3">
                <input type="checkbox" class="form-check-input mt-0" ${t.status === 'done' ? 'checked' : ''} onchange="toggleTaskDone(${t.id}, this.checked)">
                <div>
                    <h6 class="mb-0 fw-bold ${t.status === 'done' ? 'text-decoration-line-through text-muted' : ''}">${escapeHtml(t.title)}</h6>
                    <span class="small text-muted">${escapeHtml(t.category)} • Priority: ${t.priority}</span>
                </div>
            </div>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${t.id})"><i class="fas fa-trash"></i></button>
        </div>
    `).join('');
}

async function toggleTaskDone(taskId, isDone) {
    const newStatus = isDone ? 'done' : 'todo';
    try {
        await apiFetch(`/api/v1/tasks/${taskId}`, {
            method: 'PUT',
            body: { status: newStatus }
        });
        const t = allTasks.find(x => x.id === taskId);
        if (t) t.status = newStatus;
        renderTasks();
        updateTaskStats();
    } catch (err) {
        console.error(err);
    }
}

async function handleCreateTask() {
    const titleInput = document.getElementById('new-task-title');
    const descInput = document.getElementById('new-task-desc');
    const priSelect = document.getElementById('new-task-priority');
    const catInput = document.getElementById('new-task-category');
    const dueInput = document.getElementById('new-task-due');

    const title = titleInput ? titleInput.value.trim() : '';
    if (!title) {
        showToast('Please enter a task title', 'warning');
        return;
    }

    const payload = {
        title,
        description: descInput ? descInput.value.trim() : '',
        priority: priSelect ? priSelect.value : 'medium',
        category: catInput ? catInput.value.trim() : 'General',
        due_date: dueInput ? dueInput.value : null,
    };

    try {
        const res = await apiFetch('/api/v1/tasks', {
            method: 'POST',
            body: payload
        });

        allTasks.unshift(res.task);
        renderTasks();
        updateTaskStats();

        // Close modal
        const modalEl = document.getElementById('createTaskModal');
        if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }

        if (titleInput) titleInput.value = '';
        if (descInput) descInput.value = '';

        showToast('Task added successfully!', 'success');
    } catch (err) {
        console.error(err);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        await apiFetch(`/api/v1/tasks/${taskId}`, { method: 'DELETE' });
        allTasks = allTasks.filter(t => t.id !== taskId);
        renderTasks();
        updateTaskStats();
        showToast('Task deleted', 'info');
    } catch (err) {
        console.error(err);
    }
}

function updateTaskStats() {
    const total = allTasks.length;
    const done = allTasks.filter(t => t.status === 'done').length;
    const rate = total > 0 ? Math.round((done / total) * 100) : 0;

    const rateEl = document.getElementById('task-completion-rate');
    const progEl = document.getElementById('task-completion-progress');

    if (rateEl) rateEl.textContent = `${rate}%`;
    if (progEl) progEl.style.width = `${rate}%`;
}

document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    initKanbanDragDrop();

    const createBtn = document.getElementById('save-new-task-btn');
    if (createBtn) createBtn.addEventListener('click', handleCreateTask);

    const searchInput = document.getElementById('task-search-input');
    const catFilter = document.getElementById('task-category-filter');
    const priFilter = document.getElementById('task-priority-filter');

    if (searchInput) searchInput.addEventListener('input', renderTasks);
    if (catFilter) catFilter.addEventListener('change', renderTasks);
    if (priFilter) priFilter.addEventListener('change', renderTasks);
});
