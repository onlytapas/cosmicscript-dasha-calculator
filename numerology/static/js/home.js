// Landing page: switch between the two calculators and auto-advance the date fields.
(function () {
    const card = document.querySelector('.entry-card');
    const tabs = card.querySelectorAll('.tab');
    const panels = card.querySelectorAll('.tab-panel');

    function activate(name) {
        tabs.forEach((t) => t.setAttribute('aria-selected', String(t.dataset.tab === name)));
        panels.forEach((p) => p.classList.toggle('active', p.dataset.panel === name));
        card.dataset.activeTab = name;
    }
    tabs.forEach((t) => t.addEventListener('click', () => activate(t.dataset.tab)));

    const day = document.getElementById('day');
    const month = document.getElementById('month');
    const year = document.getElementById('year');
    day.addEventListener('input', () => { if (day.value.length >= 2) month.focus(); });
    month.addEventListener('input', () => { if (month.value.length >= 2) year.focus(); });
})();
