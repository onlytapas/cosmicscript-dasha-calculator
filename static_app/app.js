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
    const nameBuilder = window.CosmicName.createNameBuilder(DATA, engine, builder.formatDateLong);

    // Astrology needs the Swiss Ephemeris WebAssembly build; load it on first use.
    DATA.ASTRO.PLACES = DATA.ASTRO.PLACES_RAW.map((p) => ({
        name: p[0], region: p[1], country: p[2], latitude: p[3], longitude: p[4], timezone: p[5],
        label: [p[0]].concat(p[1] ? [p[1]] : []).concat([p[2]]).join(', '),
    }));
    let astroPromise = null;
    function loadAstro() {
        if (!astroPromise) {
            astroPromise = import('./vendor/swisseph/src/swisseph.js').then(async (mod) => {
                const swe = new mod.default();
                await swe.initSwissEph();
                return window.CosmicAstro.createAstro(DATA, swe, builder);
            });
        }
        return astroPromise;
    }
    const placeIndex = window.CosmicAstro.createAstro(DATA, null, builder);   // search needs no ephemeris
    window.cosmicPlaceSearch = (q) => placeIndex.searchPlaces(q).map((p) => p.label);

    // ---- Templates -----------------------------------------------------------
    function TemplateLoader() {}
    TemplateLoader.prototype.getSource = function (name) {
        const src = DATA.TEMPLATES[name];
        if (src === undefined) throw new Error('Unknown template ' + name);
        return { src, path: name, noCache: false };
    };
    const env = new nunjucks.Environment(new TemplateLoader(), { autoescape: true });
    env.addGlobal('url_for', (endpoint) => ({
        'main.report': '#/report', 'main.name_report': '#/name-report', 'main.astro_report': '#/astro-report', 'main.complete_report': '#/complete-report',
    }[endpoint] || '#/'));
    window.cosmicRouteBase = '#/';
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

    function parseName(name) {
        const cleaned = (name || '').split(/\s+/).filter(Boolean).join(' ');
        if (!cleaned) throw new Error('Please enter a name to analyse.');
        if (cleaned.length > 80) throw new Error('The name must be 80 characters or fewer.');
        if (!/[A-Za-z]/.test(cleaned)) throw new Error('The name must contain at least one letter from A to Z.');
        return cleaned;
    }

    function parseOptionalName(name) {
        return (name || '').trim() ? parseName(name) : '';
    }

    // All three empty -> null; otherwise the date must be complete and valid.
    function parseOptionalBirthDate(day, month, year) {
        if (!day && !month && !year) return null;
        return parseBirthDate(Number(day), Number(month), Number(year));
    }

    // ---- Views ---------------------------------------------------------------
    // Back to the front page with a message, without triggering another route change.
    function backHome(message, reading) {
        history.replaceState(null, '', location.pathname + location.search + '#/?tab=' + reading);
        showHome(message, reading);
    }

    function showHome(error, reading) {
        const READINGS = { complete: 'complete', numerology: 'numerology', dasha: 'numerology', name: 'name', astro: 'astro' };
        document.body.className = 'landing';
        document.title = 'CosmicScript · Numerology and Astrology';
        app.innerHTML = env.render('home.html', { error: error || '', reading: READINGS[reading] || 'complete' });
        window.scrollTo(0, 0);
        window.initHomePage();
    }

    function render(template, context, title, filename, params) {
        document.body.className = 'report';
        document.title = title;
        app.innerHTML = env.render(template, context);
        window.scrollTo(0, 0);
        window.initReportToolbar(filename, params.get('view'));
    }

    const fileName = (prefix, name) => prefix + '_' + (name || 'Client').replace(/\s+/g, '_') + '.html';

    function showReport(params) {
        let birth;
        try {
            birth = parseBirthDate(Number(params.get('day')), Number(params.get('month')), Number(params.get('year')));
        } catch (e) { backHome(e.message, 'numerology'); return; }
        const r = builder.buildReport(birth.day, birth.month, birth.year, params.get('name') || '');
        render('report.html', { r }, 'Numerology Report · ' + (r.client_name || r.dob_short),
            'Report_' + (r.client_name || 'Client').replace(/\s+/g, '_') + '_' + r.dob_short.replace(/\s+/g, '-') + '.html', params);
    }

    function nameInputs(params) {
        return {
            name: parseName(params.get('name')),
            options: [parseOptionalName(params.get('option1')), parseOptionalName(params.get('option2'))],
        };
    }

    function showNameReport(params) {
        let input, birth;
        try {
            input = nameInputs(params);
            birth = parseOptionalBirthDate(params.get('day'), params.get('month'), params.get('year'));
        } catch (e) { backHome(e.message, 'name'); return; }
        const r = nameBuilder.buildNameReport(input.name, params.get('owner') || 'person', params.get('client') || '', null,
            birth ? [birth.day, birth.month, birth.year] : null, input.options);
        render('name_report.html', { r }, 'Name Numerology · ' + r.name, fileName('Name_Report', r.name), params);
    }

    // Date, time and place of birth (mirrors _birth_details in numerology/web/routes.py).
    function birthDetails(params) {
        const birth = parseBirthDate(Number(params.get('day')), Number(params.get('month')), Number(params.get('year')));
        const hour = Number(params.get('hour')), minute = Number(params.get('minute'));
        if (!params.get('hour') || !params.get('minute') || Number.isNaN(hour) || Number.isNaN(minute)) throw new Error('Please enter the time of birth (hours and minutes).');
        if (hour < 0 || hour > 23 || minute < 0 || minute > 59) throw new Error('Time of birth must be between 00:00 and 23:59.');
        const place = placeIndex.findPlace(params.get('place') || '');
        if (!place) throw new Error('Please choose the place of birth from the list of suggestions.');
        return { birth, time: { hour, minute }, place };
    }

    async function astroEngine() {
        document.body.className = 'report';
        app.innerHTML = '<p class="loading">Calculating planetary positions…</p>';
        try {
            return await loadAstro();
        } catch (e) {
            app.innerHTML = '<p class="loading">The astronomy library could not be loaded. Check the internet connection and try again.</p>';
            return null;
        }
    }

    function showJson(model) {
        app.innerHTML = '<pre id="json"></pre>';
        document.getElementById('json').textContent = JSON.stringify(model);
    }

    async function showAstroReport(params) {
        let d;
        try { d = birthDetails(params); } catch (e) { backHome(e.message, 'astro'); return; }
        const astro = await astroEngine();
        if (!astro) return;
        const nowMs = params.get('today') ? Date.parse(params.get('today')) : Date.now();
        const r = astro.buildAstroReport(params.get('name') || '', params.get('gender') || '', d.birth.year, d.birth.month, d.birth.day,
            d.time.hour, d.time.minute, d.place, params.get('style') || 'north', 'lahiri', nowMs);
        if (params.get('format') === 'json') { showJson(r); return; }
        render('astro_report.html', { r }, 'Birth Chart · ' + (r.name || r.birth.date), fileName('Birth_Chart', r.name), params);
    }

    // The Complete Reading (mirrors numerology/complete_report.py).
    async function showCompleteReport(params) {
        let input, d;
        try {
            input = nameInputs(params);
            d = birthDetails(params);
        } catch (e) { backHome(e.message, 'complete'); return; }
        const astro = await astroEngine();
        if (!astro) return;
        const nowMs = params.get('today') ? Date.parse(params.get('today')) : Date.now();
        const today = params.get('today') ? new Date(params.get('today').slice(0, 10) + 'T00:00:00Z') : null;
        const { day, month, year } = d.birth;
        const todayUTC = today || engine.todayUTC();
        const c = {
            name: input.name,
            report_date: builder.formatDateLong(todayUTC),
            report_year: todayUTC.getUTCFullYear(),
            numerology: builder.buildReport(day, month, year, input.name, today || undefined),
            name_report: nameBuilder.buildNameReport(input.name, 'person', input.name, today, [day, month, year], input.options),
            astro: astro.buildAstroReport(input.name, params.get('gender') || '', year, month, day, d.time.hour, d.time.minute, d.place,
                params.get('style') || 'north', 'lahiri', nowMs),
        };
        if (params.get('format') === 'json') { showJson(c); return; }
        render('complete_report.html', { c }, 'Complete Reading · ' + c.name, fileName('Complete_Reading', c.name), params);
    }

    // ---- Router --------------------------------------------------------------
    const VIEWS = { 'report': showReport, 'name-report': showNameReport, 'astro-report': showAstroReport, 'complete-report': showCompleteReport };
    function route() {
        const hash = location.hash || '#/';
        const [path, query] = hash.split('?');
        const params = new URLSearchParams(query || '');
        const view = VIEWS[path.replace(/^#\//, '')];
        if (view) view(params);
        else showHome('', params.get('tab') || (hash === '#name' ? 'name' : hash === '#astro' ? 'astro' : 'complete'));
    }
    window.addEventListener('hashchange', route);
    route();
})();
