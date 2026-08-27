/**
 * CoreClicks 2.0 — Landing Page Interactive Engine
 * Scroll Reveals, Ecosystem Category Filters & Theme Synchronization
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveals();
    initEcosystemFilters();
    initThemeSync();
});

/* -------------------------------------------------------------------------
   1. Scroll Reveal Animations (IntersectionObserver)
   ------------------------------------------------------------------------- */
function initScrollReveals() {
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    if (!revealElements.length) return;

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                obs.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    });

    revealElements.forEach(el => observer.observe(el));
}

/* -------------------------------------------------------------------------
   2. Ecosystem Category Filter Pills
   ------------------------------------------------------------------------- */
function initEcosystemFilters() {
    const filterPills = document.querySelectorAll('.suite-filter-pill');
    const toolCards = document.querySelectorAll('.suite-tool-card-col');

    if (!filterPills.length) return;

    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            filterPills.forEach(p => p.classList.remove('active', 'btn-magma-primary'));
            filterPills.forEach(p => p.classList.add('btn-magma-outline'));

            pill.classList.remove('btn-magma-outline');
            pill.classList.add('active', 'btn-magma-primary');

            const category = pill.getAttribute('data-category');
            toolCards.forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

/* -------------------------------------------------------------------------
   3. Theme Sync with Global Toggle
   ------------------------------------------------------------------------- */
function initThemeSync() {
    const landingThemeToggle = document.getElementById('landing-theme-toggle');
    if (!landingThemeToggle) return;

    const currentTheme = localStorage.getItem('coreclicks_theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', currentTheme);

    landingThemeToggle.addEventListener('click', () => {
        const activeTheme = document.documentElement.getAttribute('data-bs-theme');
        const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', nextTheme);
        localStorage.setItem('coreclicks_theme', nextTheme);
    });
}
