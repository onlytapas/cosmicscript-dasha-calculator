/*
 * Single-page shell for the static (no server) build.
 *
 * Renders the same Jinja templates as the Flask app through Nunjucks, runs
 * the JavaScript engine in the browser, and keeps the current report in the
 * URL hash so a refresh brings it back.
 */
(function () {
    'use strict';

    const DATA = window.COSMIC_DATA;
    const engine = window.CosmicEngine.createEngine(DATA);
    const builder = window.CosmicReport.createReportBuilder(DATA, engine);

    // ---- Templates -----------------------------------------------------------
    function TemplateLoader() {}
    TemplateLoader.prototype.getSource = function (name) {
        const src = DATA.TEMPLATES[name];
        if (src === undefined) throw new Error('Unknown template ' + name);
        return { src, path: name, noCache: false };
    };
    const env = new nunjucks.Environment(new TemplateLoader(), { autoescape: true });
    env.addGlobal('url_for', (endpoint) => (endpoint === 'main.report' ? '#/report' : '#/'));
    env.addGlobal('app_version', DATA.VERSION);

    const app = document.getElementById('app');

    // ---- Validation (mirrors numerology/web/validation.py) --------------------
    function parseBirthDate(day, month, year) {
        if (!day || !month || !year) throw new Error('Please enter the day, month and year of birth.');
        if (month < 1 || month > 12) throw new Error('Month must be between 1 and 12.');
        if (year < 1900 || year > 2099) throw new Error('Year must be between 1900 and 2099.');
        try { engine.makeDate(year, month, day); } catch (e) { throw new Error('That day does not exist in the chosen month.'); }
        return { day, month, year };
    }

    // ---- Views ---------------------------------------------------------------
    function showHome(error) {
        document.body.className = 'landing';
        document.title = 'CosmicScript · Generate a Dasha Report';
        app.innerHTML = env.render('home.html', { error: error || '' });
        window.scrollTo(0, 0);

        const day = document.getElementById('day');
        const month = document.getElementById('month');
        const year = document.getElementById('year');
        day.addEventListener('input', () => { if (day.value.length >= 2) month.focus(); });
        month.addEventListener('input', () => { if (month.value.length >= 2) year.focus(); });

        app.querySelector('form').addEventListener('submit', (event) => {
            event.preventDefault();
            const params = new URLSearchParams({
                day: day.value, month: month.value, year: year.value,
                name: document.getElementById('name').value.trim(),
            });
            location.hash = '#/report?' + params.toString();
        });
    }

    function showReport(params) {
        let birth;
        try {
            birth = parseBirthDate(Number(params.get('day')), Number(params.get('month')), Number(params.get('year')));
        } catch (e) {
            location.hash = '#/';
            showHome(e.message);
            return;
        }
        const r = builder.buildReport(birth.day, birth.month, birth.year, params.get('name') || '');
        document.body.className = 'report';
        document.title = 'Numerology Report · ' + (r.client_name || r.dob_short);
        app.innerHTML = env.render('report.html', { r });
        window.scrollTo(0, 0);
        initToolbar('Report_' + (r.client_name || 'Client').replace(/\s+/g, '_') + '_' + r.dob_short.replace(/\s+/g, '-') + '.html');
    }

    // ---- Report toolbar (same behaviour as numerology/static/js/report.js) ----
    function initToolbar(filename) {
        const editToggle = document.getElementById('editToggle');
        let editing = true;

        function setEditing(on) {
            editing = on;
            document.querySelectorAll('.editable').forEach((el) => el.setAttribute('contenteditable', on ? 'true' : 'false'));
            document.body.classList.toggle('editing-off', !on);
            editToggle.textContent = on ? 'Editing on' : 'Editing off';
            editToggle.setAttribute('aria-pressed', String(on));
        }

        function saveAsHtml() {
            const wasEditing = editing;
            setEditing(false);
            const copy = document.documentElement.cloneNode(true);
            copy.querySelectorAll('.toolbar, script, .edit-hint, .cosmos').forEach((el) => el.remove());
            copy.querySelectorAll('[contenteditable]').forEach((el) => el.removeAttribute('contenteditable'));
            const blob = new Blob(['<!DOCTYPE html>\n' + copy.outerHTML], { type: 'text/html' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            URL.revokeObjectURL(link.href);
            setEditing(wasEditing);
        }

        editToggle.addEventListener('click', () => setEditing(!editing));
        document.getElementById('saveHtml').addEventListener('click', saveAsHtml);
        document.getElementById('printBtn').addEventListener('click', () => window.print());
        setEditing(true);
    }

    // ---- Router --------------------------------------------------------------
    function route() {
        const hash = location.hash || '#/';
        if (hash.startsWith('#/report')) {
            showReport(new URLSearchParams(hash.split('?')[1] || ''));
        } else {
            showHome('');
        }
    }
    window.addEventListener('hashchange', route);
    route();
})();
