// Light / dark mode. Runs in <head> so the page never flashes the wrong colours.
// The choice is remembered on this device; until one is made, the device setting decides.
(function () {
    const KEY = 'cosmicscript-mode';
    function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
    function preferred() { return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; }
    function apply(mode) {
        document.documentElement.dataset.mode = mode;
        const meta = document.querySelector('meta[name="theme-color"]');
        if (meta) meta.content = mode === 'dark' ? '#121611' : '#f2eee4';
    }
    apply(stored() || preferred());
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (!stored()) apply(preferred()); });
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.mode')) return;
        const next = document.documentElement.dataset.mode === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem(KEY, next); } catch (err) { /* private browsing: not remembered */ }
        apply(next);
    });
})();
