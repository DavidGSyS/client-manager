/* ═══════════════════════════════════════════════
   CLIENT MANAGER PRO — JavaScript
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    // ── Theme Toggle ──
    const themeToggle = document.getElementById('themeToggle');
    const themeToggleMobile = document.getElementById('themeToggleMobile');
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(next);
    }

    function updateThemeIcon(theme) {
        const moonPath = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
        const sunPaths = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
        const svgContent = theme === 'dark' ? moonPath : sunPaths;
        ['themeIconDesktop', 'themeIconMobile'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = svgContent;
        });
    }

    if (themeToggle) themeToggle.addEventListener('click', toggleTheme);
    if (themeToggleMobile) themeToggleMobile.addEventListener('click', toggleTheme);

    // ── Mobile Sidebar ──
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const menuBtn = document.getElementById('menuToggle');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (overlay) overlay.classList.add('active');
    }
    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
    }

    if (menuBtn) menuBtn.addEventListener('click', openSidebar);
    if (overlay) overlay.addEventListener('click', closeSidebar);

    // ── Modal ──
    const addModal = document.getElementById('addModal');
    const openBtn = document.getElementById('openAddModal');
    const closeBtn = document.getElementById('closeAddModal');
    const cancelBtn = document.getElementById('cancelAddModal');

    function openModal() { if (addModal) addModal.classList.add('active'); }
    function closeModal() { if (addModal) addModal.classList.remove('active'); }

    if (openBtn) openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    if (addModal) addModal.addEventListener('click', (e) => {
        if (e.target === addModal) closeModal();
    });

    // ── Toast Auto-Dismiss ──
    setTimeout(() => {
        document.querySelectorAll('.toast').forEach(toast => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        });
    }, 3500);

    // ── Animated Stat Counters ──
    document.querySelectorAll('.stat-value[data-target]').forEach(el => {
        const target = parseInt(el.getAttribute('data-target'), 10);
        const suffix = el.getAttribute('data-suffix') || '';
        if (isNaN(target)) return;
        let start = 0;
        const duration = 900;
        const startTime = performance.now();

        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.round(eased * target);
            el.textContent = value + suffix;
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    });

    // ── Search, Filter, Sort, Pagination ──
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const tableBody = document.getElementById('clientsBody');
    const paginationInfo = document.getElementById('paginationInfo');
    const paginationButtons = document.getElementById('paginationButtons');

    if (!tableBody) return;

    const allRows = Array.from(tableBody.querySelectorAll('.client-row'));
    const PER_PAGE = 10;
    let currentPage = 1;
    let filteredRows = [...allRows];
    let sortCol = null;
    let sortDir = 'asc';

    function applyFilters() {
        const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
        const status = statusFilter ? statusFilter.value : '';

        filteredRows = allRows.filter(row => {
            const name = row.getAttribute('data-name') || '';
            const email = row.getAttribute('data-email') || '';
            const company = row.getAttribute('data-company') || '';
            const phone = row.getAttribute('data-phone') || '';
            const rowStatus = row.getAttribute('data-status') || '';

            const matchSearch = !query ||
                name.includes(query) ||
                email.includes(query) ||
                company.includes(query) ||
                phone.includes(query);
            const matchStatus = !status || rowStatus === status;

            return matchSearch && matchStatus;
        });

        currentPage = 1;
        render();
    }

    function render() {
        allRows.forEach(r => r.style.display = 'none');

        const total = filteredRows.length;
        const pages = Math.max(1, Math.ceil(total / PER_PAGE));
        if (currentPage > pages) currentPage = pages;
        const start = (currentPage - 1) * PER_PAGE;
        const end = Math.min(start + PER_PAGE, total);
        const pageRows = filteredRows.slice(start, end);

        pageRows.forEach(r => r.style.display = '');

        if (paginationInfo) {
            paginationInfo.textContent = total > 0
                ? `Mostrando ${start + 1}–${end} de ${total}`
                : 'Sin resultados';
        }

        if (paginationButtons) {
            paginationButtons.innerHTML = '';
            if (pages > 1) {
                const prevBtn = createPageBtn('←', currentPage > 1, () => { currentPage--; render(); });
                paginationButtons.appendChild(prevBtn);

                for (let i = 1; i <= pages; i++) {
                    const btn = createPageBtn(i, true, () => { currentPage = i; render(); });
                    if (i === currentPage) btn.classList.add('active');
                    paginationButtons.appendChild(btn);
                }

                const nextBtn = createPageBtn('→', currentPage < pages, () => { currentPage++; render(); });
                paginationButtons.appendChild(nextBtn);
            }
        }
    }

    function createPageBtn(label, enabled, onClick) {
        const btn = document.createElement('button');
        btn.className = 'page-btn';
        btn.textContent = label;
        btn.disabled = !enabled;
        if (enabled) btn.addEventListener('click', onClick);
        return btn;
    }

    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (statusFilter) statusFilter.addEventListener('change', applyFilters);

    // Sort
    document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-sort');

            if (sortCol === col) {
                sortDir = sortDir === 'asc' ? 'desc' : 'asc';
            } else {
                sortCol = col;
                sortDir = 'asc';
            }

            document.querySelectorAll('.data-table th').forEach(h => h.classList.remove('sorted'));
            th.classList.add('sorted');
            th.querySelector('.sort-icon').textContent = sortDir === 'asc' ? '↑' : '↓';

            filteredRows.sort((a, b) => {
                const aVal = (a.getAttribute('data-' + col) || '').toLowerCase();
                const bVal = (b.getAttribute('data-' + col) || '').toLowerCase();
                if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
                return 0;
            });

            filteredRows.forEach(row => tableBody.appendChild(row));
            currentPage = 1;
            render();
        });
    });

    applyFilters();

    // ── Chart.js ──
    const chartCanvas = document.getElementById('clientsChart');
    if (chartCanvas && typeof Chart !== 'undefined' && typeof chartLabels !== 'undefined') {
        const ctx = chartCanvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 220);
        gradient.addColorStop(0, 'rgba(14, 165, 233, 0.35)');
        gradient.addColorStop(1, 'rgba(14, 165, 233, 0.0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [{
                    label: 'Clientes registrados',
                    data: chartData,
                    borderColor: '#0ea5e9',
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    pointRadius: 5,
                    pointBackgroundColor: '#0ea5e9',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 7,
                    tension: 0.4,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#18181b',
                        titleColor: '#fafafa',
                        bodyColor: '#a1a1aa',
                        borderColor: '#27272a',
                        borderWidth: 1,
                        cornerRadius: 10,
                        padding: 14,
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#71717a', font: { size: 12, family: 'Plus Jakarta Sans' } },
                        border: { display: false },
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(113,113,122,0.12)' },
                        ticks: {
                            color: '#71717a',
                            font: { size: 12, family: 'Plus Jakarta Sans' },
                            stepSize: 1,
                        },
                        border: { display: false },
                    }
                }
            }
        });
    }

    // ── Global Search (Ctrl+K / Cmd+K) ──
    const searchOverlay = document.getElementById('globalSearchOverlay');
    const globalInput = document.getElementById('globalSearchInput');
    const searchResults = document.getElementById('globalSearchResults');
    const sidebarSearchBtn = document.getElementById('sidebarSearchBtn');
    const emptySearchHTML = '<div class="search-empty"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><p>Escribe para buscar clientes</p></div>';

    function openGlobalSearch() {
        if (!searchOverlay) return;
        searchOverlay.classList.add('active');
        setTimeout(() => { if (globalInput) globalInput.focus(); }, 50);
    }

    function closeGlobalSearch() {
        if (!searchOverlay) return;
        searchOverlay.classList.remove('active');
        if (globalInput) globalInput.value = '';
        if (searchResults) searchResults.innerHTML = emptySearchHTML;
    }

    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            (searchOverlay && searchOverlay.classList.contains('active')) ? closeGlobalSearch() : openGlobalSearch();
        }
        if (e.key === 'Escape' && searchOverlay && searchOverlay.classList.contains('active')) {
            closeGlobalSearch();
        }
    });

    if (sidebarSearchBtn) sidebarSearchBtn.addEventListener('click', openGlobalSearch);
    if (searchOverlay) searchOverlay.addEventListener('click', (e) => { if (e.target === searchOverlay) closeGlobalSearch(); });

    let searchTimeout = null;
    if (globalInput) {
        globalInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            const q = globalInput.value.trim();
            if (q.length < 2) {
                searchResults.innerHTML = emptySearchHTML;
                return;
            }
            searchTimeout = setTimeout(() => {
                fetch('/api/search?q=' + encodeURIComponent(q))
                    .then(r => r.json())
                    .then(data => {
                        if (!data.length) {
                            searchResults.innerHTML = '<div class="search-empty"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><p>Sin resultados</p></div>';
                            return;
                        }
                        searchResults.innerHTML = data.map((c, i) =>
                            '<a href="' + c.url + '" class="search-result-item" data-idx="' + i + '">' +
                            '<div class="search-result-avatar">' + c.initials + '</div>' +
                            '<div class="search-result-info">' +
                            '<div class="search-result-name">' + c.name + '</div>' +
                            '<div class="search-result-meta">' + c.email + (c.company ? ' · ' + c.company : '') + '</div>' +
                            '</div>' +
                            '<span class="search-result-badge ' + (c.status === 'active' ? '' : 'inactive') + '">' + (c.status === 'active' ? 'Activo' : 'Inactivo') + '</span>' +
                            '</a>'
                        ).join('');
                    }).catch(() => {});
            }, 200);
        });

        globalInput.addEventListener('keydown', (e) => {
            const items = searchResults.querySelectorAll('.search-result-item');
            const sel = searchResults.querySelector('.selected');
            let idx = sel ? parseInt(sel.getAttribute('data-idx')) : -1;
            if (e.key === 'ArrowDown') { e.preventDefault(); idx = Math.min(idx + 1, items.length - 1); items.forEach(i => i.classList.remove('selected')); if (items[idx]) items[idx].classList.add('selected'); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); idx = Math.max(idx - 1, 0); items.forEach(i => i.classList.remove('selected')); if (items[idx]) items[idx].classList.add('selected'); }
            else if (e.key === 'Enter') { const s = searchResults.querySelector('.selected'); if (s) { window.location.href = s.getAttribute('href'); closeGlobalSearch(); } }
        });
    }

    // Archived page filter
    const archivedSearch = document.getElementById('searchInput');
    if (archivedSearch && !document.getElementById('statusFilter')) {
        const rows = Array.from(document.querySelectorAll('#clientsBody .client-row'));
        archivedSearch.addEventListener('input', () => {
            const q = archivedSearch.value.toLowerCase().trim();
            rows.forEach(row => {
                const ok = !q || (row.getAttribute('data-name') || '').includes(q) ||
                    (row.getAttribute('data-email') || '').includes(q) ||
                    (row.getAttribute('data-company') || '').includes(q);
                row.style.display = ok ? '' : 'none';
            });
        });
    }

});