/*
 * Front page: client details once, then tap any reading to open it.
 * The details stay filled in for this browser tab (sessionStorage), so the consultant can
 * go back and open the next reading without typing them again. "Save" keeps a client in
 * this browser (localStorage) for later visits. Nothing leaves the device.
 * Exposed as window.initHomePage so the static build can call it after rendering.
 * Report links start with window.cosmicRouteBase ('#/' in the static build) or '/' (Flask).
 */
window.initHomePage = function () {
    const form = document.getElementById('readingForm');
    if (!form) return;
    const base = window.cosmicRouteBase || '/';
    const $ = (id) => document.getElementById(id);

    // Astrology and the complete reading also need the time and place of birth.
    const READINGS = {
        complete:   { title: 'Complete Reading',   route: 'complete-report', chart: true },
        numerology: { title: 'Numerology',         route: 'report' },
        name:       { title: 'Name Numerology',    route: 'name-report' },
        astro:      { title: 'Astrology · Kundli', route: 'astro-report',    chart: true },
    };

    // ---- Headline appears word by word
    const headline = form.querySelector('.headline');
    if (headline && !headline.dataset.split) {
        headline.dataset.split = '1';
        let i = 0;
        const wrap = (node) => [...node.childNodes].forEach((n) => {
            if (n.nodeType !== 3) { wrap(n); return; }
            const frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach((part) => {
                if (!part.trim()) { frag.appendChild(document.createTextNode(part)); return; }
                const s = document.createElement('span');
                s.className = 'w'; s.style.setProperty('--i', i++); s.textContent = part;
                frag.appendChild(s);
            });
            n.replaceWith(frag);
        });
        wrap(headline);
    }

    // ---- Cards: gentle 3D tilt and a light that follows the pointer
    form.querySelectorAll('.reading').forEach((card) => {
        card.addEventListener('pointermove', (e) => {
            const r = card.getBoundingClientRect();
            const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
            card.style.setProperty('--mx', x * 100 + '%');
            card.style.setProperty('--my', y * 100 + '%');
            if (e.pointerType === 'mouse') {
                card.style.setProperty('--ry', (x - .5) * 8 + 'deg');
                card.style.setProperty('--rx', (.5 - y) * 8 + 'deg');
            }
        });
        card.addEventListener('pointerleave', () => { card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg'); });
    });

    // ---- Typing: digits only in number boxes, jump to the next box when full
    function autoAdvance(ids) {
        ids.forEach((id, i) => {
            const el = $(id), next = $(ids[i + 1]);
            el.addEventListener('input', () => {
                el.value = el.value.replace(/\D/g, '');
                if (next && el.value.length >= el.maxLength) next.focus();
            });
        });
    }
    autoAdvance(['day', 'month', 'year']);
    autoAdvance(['hour', 'minute']);
    autoAdvance(['askHour', 'askMinute']);
    document.querySelectorAll('.f input').forEach((el) => el.addEventListener('input', () => el.classList.remove('invalid')));

    // ---- Place suggestions. The built-in list (window.cosmicPlaceSearch in the static build, /places in Flask)
    // answers at once; a free online search of OpenStreetMap (Photon) then adds the smaller towns and
    // villages. Only the typed place name is sent. A place from the online search carries its
    // coordinates and time zone in the hidden ...Geo field, as "lat,lon,timezone".
    const fold = (text) => text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
    const SETTLEMENTS = ['city', 'town', 'village', 'hamlet', 'suburb', 'municipality', 'borough', 'locality'];
    async function localPlaces(q) {
        if (window.cosmicPlaceSearch) return window.cosmicPlaceSearch(q);
        const res = await fetch('/places?q=' + encodeURIComponent(q));
        return res.json();
    }
    async function onlinePlaces(q) {
        try {
            const res = await fetch('https://photon.komoot.io/api/?osm_tag=place&limit=15&lang=en&lat=22&lon=79&q='
                + encodeURIComponent(fold(q).split(',')[0].trim()), { signal: AbortSignal.timeout(6000) });
            const found = (await res.json()).features || [];
            const places = found.map((f) => ({ p: f.properties, at: f.geometry.coordinates }))
                .filter(({ p }) => SETTLEMENTS.includes(p.osm_value) && p.name && p.countrycode)
                .map(({ p, at }) => ({
                    key: [p.name, p.state, p.countrycode].map((x) => fold(x || '').toLowerCase()).join('|'),
                    label: [p.name, p.county || p.district, p.state, p.countrycode].filter(Boolean).map(fold).join(', '),
                    lat: at[1], lon: at[0], country: p.countrycode,
                }));
            return places.filter((x) => x.country === 'IN').concat(places.filter((x) => x.country !== 'IN'));   // India first
        } catch (e) { return []; }                          // offline or blocked: the built-in list still works
    }
    // The chart needs the place's time zone: all of India is on IST; elsewhere ask Open-Meteo for the coordinates.
    async function timeZone(place) {
        if (place.country === 'IN') return 'Asia/Kolkata';
        try {
            const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${place.lat}&longitude=${place.lon}&timezone=auto&forecast_days=1`,
                { signal: AbortSignal.timeout(6000) });
            return (await res.json()).timezone || '';
        } catch (e) { return ''; }
    }
    let geoPending = Promise.resolve();                     // the time-zone lookup for the place just picked
    function placeSuggestions(input, list, geo) {
        let timer = null;
        function suggest(items) {
            list.innerHTML = '';
            items.forEach((item) => {
                const li = document.createElement('li');
                li.textContent = item.label;
                li.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                    input.value = item.label; geo.value = ''; list.hidden = true; input.classList.remove('invalid');
                    if (item.lat !== undefined) {
                        geoPending = timeZone(item).then((tz) => {
                            if (input.value === item.label && tz) geo.value = [item.lat, item.lon, tz].join(',');
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        });
                    }
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                });
                list.appendChild(li);
            });
            if (items.some((item) => item.lat !== undefined)) {
                const src = document.createElement('li');
                src.className = 'src'; src.textContent = 'More places: © OpenStreetMap contributors';
                list.appendChild(src);
            }
            list.hidden = items.length === 0;
        }
        input.addEventListener('input', () => {
            geo.value = '';
            clearTimeout(timer);
            const q = input.value.trim();
            if (q.length < 2) { list.hidden = true; return; }
            timer = setTimeout(async () => {
                const local = (await localPlaces(q)).slice(0, 8).map((label) => ({ label }));
                if (input.value.trim() !== q) return;
                suggest(local);
                if (q.length < 3) return;
                // Skip what the built-in list already has (it gives no state outside India), and exact repeats
                const seen = new Set();
                local.forEach((p) => {
                    const [name, ...rest] = p.label.toLowerCase().split(', ');
                    seen.add([name, rest.slice(0, -1).join(', '), rest[rest.length - 1]].join('|'));
                    if (rest.length === 1) seen.add(name + '|' + rest[0]);
                });
                const extra = (await onlinePlaces(q)).filter((p) => {
                    if (seen.has(p.key) || seen.has(p.label.toLowerCase()) || seen.has(p.key.split('|')[0] + '|' + p.key.split('|')[2])) return false;
                    seen.add(p.label.toLowerCase());
                    return true;
                });
                if (input.value.trim() === q && document.activeElement === input) suggest(local.concat(extra).slice(0, 12));
            }, 150);
        });
        input.addEventListener('blur', () => setTimeout(() => { list.hidden = true; }, 150));
    }
    placeSuggestions($('place'), $('place-suggestions'), $('placeGeo'));
    placeSuggestions($('askPlace'), $('askPlace-suggestions'), $('askPlaceGeo'));

    // ---- The details stay for this tab: restored every time the front page opens
    const SESSION = 'cosmicscript-form';
    const fieldIds = ['first', 'middle', 'last', 'day', 'month', 'year', 'hour', 'minute', 'place', 'placeGeo'];
    const v = (id) => $(id).value.trim();
    const gender = () => form.querySelector('input[name="gender"]:checked').value;
    function read() {
        const data = { gender: gender() };
        fieldIds.forEach((id) => { data[id] = v(id); });
        return data;
    }
    function fill(data) {
        fieldIds.forEach((id) => { $(id).value = data[id] || ''; $(id).classList.remove('invalid'); });
        form.querySelector(`input[name="gender"][value="${data.gender === 'male' ? 'male' : 'female'}"]`).checked = true;
        remember();
    }
    function remember() {
        try { sessionStorage.setItem(SESSION, JSON.stringify(read())); } catch (e) { /* storage blocked */ }
        $('resetBtn').disabled = fieldIds.every((id) => !v(id));
    }
    try {
        const data = JSON.parse(sessionStorage.getItem(SESSION) || 'null');
        if (data) fill(data);
    } catch (e) { /* nothing stored */ }
    form.addEventListener('input', remember);
    form.addEventListener('change', remember);
    remember();

    // ---- Reset: clear the details and start a new client
    $('resetBtn').addEventListener('click', () => {
        if (!confirm('Clear the client details and start again?')) return;
        const btn = $('resetBtn');
        btn.classList.add('spin');
        setTimeout(() => btn.classList.remove('spin'), 600);
        fill({});
        form.querySelectorAll('.form-error').forEach((x) => { x.hidden = true; });
        form.querySelectorAll('.reading.was').forEach((x) => x.classList.remove('was'));
        $('first').focus({ preventScroll: true });
    });

    // ---- Saved clients: kept in this browser (localStorage) until deleted here or the browser data is cleared
    const SAVED = 'cosmicscript-clients';
    const fullName = (d) => [d.first, d.middle, d.last].filter(Boolean).join(' ');
    const dob = (d) => [d.day, d.month, d.year].every(Boolean) ? `${d.day.padStart(2, '0')}/${d.month.padStart(2, '0')}/${d.year}` : '';
    function loadSaved() {
        try { return JSON.parse(localStorage.getItem(SAVED) || '[]'); } catch (e) { return []; }
    }
    function storeSaved(list) {
        try { localStorage.setItem(SAVED, JSON.stringify(list)); return true; } catch (e) { return false; }
    }
    function drawSaved() {
        const list = loadSaved(), ul = $('savedList');
        $('savedCount').textContent = list.length;
        $('savedToggle').disabled = list.length === 0;
        ul.innerHTML = '';
        list.forEach((d, i) => {
            const li = document.createElement('li');
            const load = document.createElement('button');
            load.type = 'button'; load.className = 'saved-load';
            load.innerHTML = '<b></b><span></span>';
            load.firstChild.textContent = fullName(d);
            load.lastChild.textContent = dob(d);
            load.addEventListener('click', () => { fill(d); toggleSaved(false); flash('Loaded ' + fullName(d)); });
            const del = document.createElement('button');
            del.type = 'button'; del.className = 'saved-del'; del.textContent = '×';
            del.setAttribute('aria-label', 'Delete ' + fullName(d));
            del.addEventListener('click', (e) => {
                if (!confirm('Delete ' + fullName(d) + ' from this browser?')) return;
                e.stopPropagation();
                list.splice(i, 1); storeSaved(list); drawSaved();
                if (!list.length) toggleSaved(false);
            });
            li.append(load, del);
            ul.appendChild(li);
        });
    }
    function toggleSaved(open) {
        $('savedList').hidden = !open;
        $('savedToggle').setAttribute('aria-expanded', String(open));
    }
    function flash(text) {
        const btn = $('saveClient'), label = btn.querySelector('span');
        btn.classList.add('done'); label.textContent = text.length > 22 ? 'Saved' : text;
        setTimeout(() => { btn.classList.remove('done'); label.textContent = 'Save'; }, 1600);
    }
    $('savedToggle').addEventListener('click', (e) => { e.stopPropagation(); toggleSaved($('savedList').hidden); });
    document.addEventListener('click', (e) => { if (!e.target.closest('.dropdown')) toggleSaved(false); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('savedList').hidden) { toggleSaved(false); $('savedToggle').focus(); } });
    $('saveClient').addEventListener('click', () => {
        const d = read();
        if (!d.first || !d.last) return fail('Enter at least the first and last name to save a client.', $(d.first ? 'last' : 'first'));
        const list = loadSaved().filter((x) => !(fullName(x).toLowerCase() === fullName(d).toLowerCase() && dob(x) === dob(d)));
        list.unshift(d);
        if (!storeSaved(list)) return fail('This browser is not allowing anything to be saved (private window?).');
        drawSaved();
        flash('Saved');
    });
    drawSaved();

    // ---- Open a reading: check the details it needs, ask for time and place if missing
    function fail(message, el) {
        const box = $('formError');
        box.textContent = message;
        box.hidden = false;
        form.querySelectorAll('.form-error').forEach((x) => { if (x !== box) x.remove(); });
        if (el) { el.classList.add('invalid'); el.focus(); }
    }
    async function open(reading) {
        await geoPending;
        const r = READINGS[reading];
        const params = new URLSearchParams({
            name: [v('first'), v('middle'), v('last')].filter(Boolean).join(' '),
            day: v('day'), month: v('month'), year: v('year'),
        });
        if (r.chart) {
            params.set('gender', gender());
            params.set('hour', v('hour')); params.set('minute', v('minute'));
            params.set('place', v('place')); params.set('style', 'north');
            const [lat, lon, tz] = v('placeGeo').split(',');
            if (tz) { params.set('lat', lat); params.set('lon', lon); params.set('tz', tz); }
        }
        remember();
        if (base === '/') location.href = '/' + r.route + '?' + params.toString();
        else location.hash = base + r.route + '?' + params.toString();
    }
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const reading = (event.submitter && event.submitter.value) || 'complete';
        if (!READINGS[reading]) return;
        $('formError').hidden = true;
        if (!v('first')) return fail('Please enter the first name.', $('first'));
        if (!v('last')) return fail('Please enter the last name.', $('last'));
        for (const id of ['day', 'month', 'year']) if (!v(id)) return fail('Please enter the full date of birth.', $(id));
        const missing = READINGS[reading].chart && (!v('hour') || !v('minute') || !v('place'));
        if (missing) ask(reading); else open(reading);
    });

    // ---- The pop-up for the time and place of birth
    const dialog = $('askDialog');
    function ask(reading) {
        const needTime = !v('hour') || !v('minute'), needPlace = !v('place');
        $('askKicker').textContent = READINGS[reading].title;
        $('askText').textContent = 'The birth chart is drawn for the exact moment and place of birth. Please add the '
            + (needTime && needPlace ? 'time and place' : needTime ? 'time' : 'place') + ' of birth.';
        dialog.querySelector('[data-ask="time"]').hidden = !needTime;
        dialog.querySelector('[data-ask="place"]').hidden = !needPlace;
        $('askHour').value = v('hour'); $('askMinute').value = v('minute'); $('askPlace').value = ''; $('askPlaceGeo').value = '';
        $('askError').hidden = true;
        dialog.dataset.reading = reading;
        dialog.showModal();
        (needTime ? (v('hour') ? $('askMinute') : $('askHour')) : $('askPlace')).focus();
    }
    function askFail(message, el) {
        $('askError').textContent = message; $('askError').hidden = false;
        el.classList.add('invalid'); el.focus();
    }
    $('askCancel').addEventListener('click', () => dialog.close());
    $('askForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        await geoPending;
        const timeShown = !dialog.querySelector('[data-ask="time"]').hidden;
        const placeShown = !dialog.querySelector('[data-ask="place"]').hidden;
        if (timeShown) {
            for (const id of ['askHour', 'askMinute']) if (!$(id).value.trim()) return askFail('Please enter the time of birth (24-hour clock).', $(id));
            $('hour').value = $('askHour').value.trim(); $('minute').value = $('askMinute').value.trim();
        }
        if (placeShown) {
            if (!$('askPlace').value.trim()) return askFail('Please enter the place of birth and choose it from the list.', $('askPlace'));
            $('place').value = $('askPlace').value.trim();
            $('placeGeo').value = $('askPlaceGeo').value;
        }
        dialog.close();
        open(dialog.dataset.reading);
    });

    startDust();
};

// Background: the numbers 1 to 9, the 12 zodiac signs and the 9 planets of Vedic
// astrology drift slowly upwards, very faint, behind the page.
const SKY = {
    signs: ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'],
    planets: ['☉', '☽', '♂', '☿', '♃', '♀', '♄', '☊', '☋'],          // Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
    numbers: ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
};
function startDust() {
    const c = document.getElementById('dust');
    if (!c || c.dataset.running) return;
    c.dataset.running = '1';
    const ctx = c.getContext('2d');
    const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    // ︎ asks for the plain text form, so iPads do not draw the signs as colour emoji.
    const SYMBOL_FONT = '"Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif';
    const glyphs = [
        ...SKY.signs.map((t) => ({ t: t + '\uFE0E', style: '', family: SYMBOL_FONT, scale: 1 })),
        ...SKY.planets.map((t) => ({ t: t + '\uFE0E', style: '', family: SYMBOL_FONT, scale: 1 })),
        ...SKY.numbers.map((t) => ({ t, style: 'italic 400 ', family: '"Fraunces", Georgia, serif', scale: 1.2 })),
    ];
    let next = Math.floor(Math.random() * glyphs.length);   // take symbols in turn so all 30 keep appearing
    let w, h, parts = [];
    function make(y) {
        const g = glyphs[next++ % glyphs.length];
        return {
            g, x: Math.random() * w, y: y === undefined ? Math.random() * h : y,
            size: 22 + Math.random() * 14,                 // 22 to 36 px
            v: .12 + Math.random() * .22,                   // pixels per frame, upwards
            sway: Math.random() * 6.28, rot: (Math.random() - .5) * .5, spin: (Math.random() - .5) * .0015,
            alpha: .5 + Math.random() * .5, clay: Math.random() < .3,
        };
    }
    function size() {
        const dpr = Math.min(devicePixelRatio || 1, 2);
        w = innerWidth; h = innerHeight;
        c.width = w * dpr; c.height = h * dpr; c.style.width = w + 'px'; c.style.height = h + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        parts = Array.from({ length: Math.round(w * h / 30000) }, () => make());
    }
    function frame(t) {
        if (!document.body.contains(c)) return;            // the static build replaced the page
        const root = getComputedStyle(document.documentElement);
        const dark = document.documentElement.dataset.mode === 'dark';
        const sage = root.getPropertyValue('--dust').trim();
        const clay = dark ? '226, 160, 130' : '176, 100, 74';
        const base = dark ? .30 : .26;                      // faint: never in the way of the reading
        ctx.clearRect(0, 0, w, h);
        for (let i = 0; i < parts.length; i++) {
            const p = parts[i];
            if (!still) {
                p.y -= p.v;
                p.x += Math.sin(t / 4000 + p.sway) * .15;
                p.rot += p.spin;
                if (p.y < -40) parts[i] = make(h + 30);
            }
            // fade in from the bottom and out towards the top
            const edge = Math.min(1, (h - p.y + 30) / 160, (p.y + 40) / 200);
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rot);
            ctx.font = `${p.g.style}${Math.round(p.size * p.g.scale)}px ${p.g.family}`;
            ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
            ctx.fillStyle = `rgba(${p.clay ? clay : sage}, ${base * p.alpha * Math.max(0, edge)})`;
            ctx.fillText(p.g.t, 0, 0);
            ctx.restore();
        }
        if (!still) requestAnimationFrame(frame);
    }
    size();
    addEventListener('resize', size);
    const ready = document.fonts && document.fonts.load ? Promise.all([
        document.fonts.load('20px "Noto Sans Symbols"', '♈☊'), document.fonts.load('italic 400 20px "Fraunces"', '9'),
    ]).catch(() => null) : Promise.resolve();
    ready.then(() => requestAnimationFrame(frame));
}

if (document.getElementById('readingForm')) window.initHomePage();
