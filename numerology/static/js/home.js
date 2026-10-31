// Landing page: tabs, auto-advance for date fields, and the place-of-birth suggestions.
// Exposed as window.initHomePage so the static build can call it after rendering.
window.initHomePage = function () {
    const card = document.querySelector('.entry-card');
    if (!card) return;
    const tabs = card.querySelectorAll('.tab');
    const panels = card.querySelectorAll('.tab-panel');

    function activate(name) {
        tabs.forEach((t) => t.setAttribute('aria-selected', String(t.dataset.tab === name)));
        panels.forEach((p) => p.classList.toggle('active', p.dataset.panel === name));
        card.dataset.activeTab = name;
    }
    tabs.forEach((t) => t.addEventListener('click', () => activate(t.dataset.tab)));

    function autoAdvance(ids) {
        ids.forEach((id, i) => {
            const el = document.getElementById(id);
            const next = document.getElementById(ids[i + 1]);
            if (el && next) el.addEventListener('input', () => { if (el.value.length >= 2) next.focus(); });
        });
    }
    autoAdvance(['day', 'month', 'year']);
    autoAdvance(['astro-day', 'astro-month', 'astro-year']);
    autoAdvance(['astro-hour', 'astro-minute']);

    // Place suggestions: window.cosmicPlaceSearch (static build) or the /places endpoint (Flask).
    const input = document.getElementById('astro-place');
    const list = document.getElementById('place-suggestions');
    if (!input || !list) return;
    let timer = null;
    async function lookup(q) {
        if (window.cosmicPlaceSearch) return window.cosmicPlaceSearch(q);
        const res = await fetch('/places?q=' + encodeURIComponent(q));
        return res.json();
    }
    function show(items) {
        list.innerHTML = '';
        items.forEach((label) => {
            const li = document.createElement('li');
            li.textContent = label;
            li.addEventListener('mousedown', (e) => { e.preventDefault(); input.value = label; list.hidden = true; });
            list.appendChild(li);
        });
        list.hidden = items.length === 0;
    }
    input.addEventListener('input', () => {
        clearTimeout(timer);
        const q = input.value.trim();
        if (q.length < 2) { list.hidden = true; return; }
        timer = setTimeout(async () => show(await lookup(q)), 120);
    });
    input.addEventListener('blur', () => setTimeout(() => { list.hidden = true; }, 150));
};
if (document.querySelector('.entry-card')) window.initHomePage();
