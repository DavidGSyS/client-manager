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
        const icon = theme === 'dark' ? '🌙' : '☀️';
        if (themeToggle) themeToggle.textContent = icon;
        if (themeToggleMobile) themeToggleMobile.textContent = icon;
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
            const rowStatus = row.getAttribute('data-status') || '';

            const matchSearch = !query || name.includes(query) || email.includes(query) || company.includes(query);
            const matchStatus = !status || rowStatus === status;

            return matchSearch && matchStatus;
        });

        currentPage = 1;
        render();
    }

    function render() {
        // Hide all
        allRows.forEach(r => r.style.display = 'none');

        // Pagination calc
        const total = filteredRows.length;
        const pages = Math.max(1, Math.ceil(total / PER_PAGE));
        if (currentPage > pages) currentPage = pages;
        const start = (currentPage - 1) * PER_PAGE;
        const end = Math.min(start + PER_PAGE, total);
        const pageRows = filteredRows.slice(start, end);

        // Show current page rows
        pageRows.forEach(r => r.style.display = '');

        // Pagination info
        if (paginationInfo) {
            paginationInfo.textContent = total > 0
                ? `Mostrando ${start + 1}–${end} de ${total}`
                : 'Sin resultados';
        }

        // Pagination buttons
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

    // Search
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

            // Update header UI
            document.querySelectorAll('.data-table th').forEach(h => h.classList.remove('sorted'));
            th.classList.add('sorted');
            th.querySelector('.sort-icon').textContent = sortDir === 'asc' ? '↑' : '↓';

            // Sort filtered rows
            filteredRows.sort((a, b) => {
                const aVal = (a.getAttribute('data-' + col) || '').toLowerCase();
                const bVal = (b.getAttribute('data-' + col) || '').toLowerCase();
                if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
                return 0;
            });

            // Re-order DOM
            filteredRows.forEach(row => tableBody.appendChild(row));
            currentPage = 1;
            render();
        });
    });

    // Initial render
    applyFilters();

    // ── Chart.js ──
    const chartCanvas = document.getElementById('clientsChart');
    if (chartCanvas && typeof Chart !== 'undefined' && typeof chartLabels !== 'undefined') {
        const ctx = chartCanvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 220);
        gradient.addColorStop(0, 'rgba(14, 165, 233, 0.3)');
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
                    pointRadius: 4,
                    pointBackgroundColor: '#0ea5e9',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
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
                        cornerRadius: 8,
                        padding: 12,
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#71717a', font: { size: 12 } },
                        border: { display: false },
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(113,113,122,0.15)' },
                        ticks: {
                            color: '#71717a',
                            font: { size: 12 },
                            stepSize: 1,
                        },
                        border: { display: false },
                    }
                }
            }
        });
    }


});