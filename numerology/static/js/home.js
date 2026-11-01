/*
 * Front page: choose a reading, fill only the details it needs, open the report.
 * Exposed as window.initHomePage so the static build can call it after rendering.
 * Report links start with window.cosmicRouteBase ('#/' in the static build) or '/' (Flask).
 */
window.initHomePage = function () {
    const form = document.getElementById('readingForm');
    if (!form) return;
    const base = window.cosmicRouteBase || '/';
    const $ = (id) => document.getElementById(id);

    // Which fields each reading shows. Every field shown is required except the middle name.
    const READINGS = {
        complete:   { title: 'Complete Reading',   button: 'Generate complete reading',  route: 'complete-report', fields: ['first', 'middle', 'last', 'dob', 'gender', 'time', 'place'] },
        numerology: { title: 'Numerology',         button: 'Generate numerology report', route: 'report',          fields: ['first', 'middle', 'last', 'dob'] },
        name:       { title: 'Name Numerology',    button: 'Generate name report',       route: 'name-report',     fields: ['first', 'middle', 'last', 'dob'] },
        astro:      { title: 'Astrology · Kundli', button: 'Generate birth chart',       route: 'astro-report',    fields: ['first', 'middle', 'last', 'dob', 'gender', 'time', 'place'] },
    };
    const current = () => (form.querySelector('input[name="reading"]:checked') || {}).value || 'complete';

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

    // ---- Show the fields the chosen reading needs
    function show(reading, first) {
        const r = READINGS[reading];
        form.querySelectorAll('.f').forEach((f) => f.classList.toggle('skip', !r.fields.includes(f.dataset.f)));
        form.querySelectorAll('.row').forEach((row) => row.classList.toggle('collapsed', [...row.querySelectorAll('.f')].every((f) => f.classList.contains('skip'))));
        $('cardTitle').innerHTML = '<span></span>';
        $('cardTitle').firstChild.textContent = r.title;
        const label = $('goText');
        label.textContent = r.button;
        label.classList.remove('swap'); void label.offsetWidth; label.classList.add('swap');
        $('formError').hidden = true;
        if (!first && window.innerWidth < 700) form.querySelector('.card').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    form.querySelectorAll('input[name="reading"]').forEach((input) => input.addEventListener('change', () => show(input.value)));
    if (!form.querySelector('input[name="reading"]:checked')) form.querySelector('input[value="complete"]').checked = true;
    show(current(), true);

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

    // ---- Button ripple where it is pressed
    const go = $('go');
    go.addEventListener('pointerdown', (e) => {
        const r = go.getBoundingClientRect(), size = Math.max(r.width, r.height) / 2;
        const s = document.createElement('span');
        s.className = 'ripple';
        s.style.width = s.style.height = size + 'px';
        s.style.left = (e.clientX - r.left - size / 2) + 'px';
        s.style.top = (e.clientY - r.top - size / 2) + 'px';
        go.appendChild(s);
        setTimeout(() => s.remove(), 700);
    });

    // ---- Typing: digits only in number boxes, jump to the next box when full
    function autoAdvance(ids) {
        ids.forEach((id, i) => {
            const el = $(id), next = $(ids[i + 1]);
            el.addEventListener('input', () => {
                el.value = el.value.replace(/\D/g, '');
                el.classList.remove('invalid');
                if (next && el.value.length >= el.maxLength) next.focus();
            });
        });
    }
    autoAdvance(['day', 'month', 'year']);
    autoAdvance(['hour', 'minute']);
    form.querySelectorAll('input[type="text"], input:not([type])').forEach((el) => el.addEventListener('input', () => el.classList.remove('invalid')));

    // ---- Place suggestions: window.cosmicPlaceSearch (static build) or the /places endpoint (Flask)
    const place = $('place'), list = $('place-suggestions');
    let timer = null;
    async function lookup(q) {
        if (window.cosmicPlaceSearch) return window.cosmicPlaceSearch(q);
        const res = await fetch('/places?q=' + encodeURIComponent(q));
        return res.json();
    }
    function suggest(items) {
        list.innerHTML = '';
        items.forEach((label) => {
            const li = document.createElement('li');
            li.textContent = label;
            li.addEventListener('mousedown', (e) => { e.preventDefault(); place.value = label; list.hidden = true; place.classList.remove('invalid'); });
            list.appendChild(li);
        });
        list.hidden = items.length === 0;
    }
    place.addEventListener('input', () => {
        clearTimeout(timer);
        const q = place.value.trim();
        if (q.length < 2) { list.hidden = true; return; }
        timer = setTimeout(async () => suggest(await lookup(q)), 120);
    });
    place.addEventListener('blur', () => setTimeout(() => { list.hidden = true; }, 150));

    // ---- Remember what was typed, so a message from the report page does not lose it
    const SAVE = 'cosmicscript-form';
    const fieldIds = ['first', 'middle', 'last', 'day', 'month', 'year', 'hour', 'minute', 'place'];
    function save() {
        const data = { reading: current(), gender: form.querySelector('input[name="gender"]:checked').value };
        fieldIds.forEach((id) => { data[id] = $(id).value; });
        try { sessionStorage.setItem(SAVE, JSON.stringify(data)); } catch (e) { /* not available */ }
    }
    if (form.querySelector('.form-error:not([hidden])')) {
        try {
            const data = JSON.parse(sessionStorage.getItem(SAVE) || 'null');
            if (data) {
                fieldIds.forEach((id) => { $(id).value = data[id] || ''; });
                const g = form.querySelector(`input[name="gender"][value="${data.gender}"]`);
                if (g) g.checked = true;
            }
        } catch (e) { /* ignore */ }
    }

    // ---- Submit: check the visible fields, then open the report
    function fail(message, el) {
        const box = $('formError');
        box.textContent = message;
        box.hidden = false;
        form.querySelectorAll('.form-error').forEach((x) => { if (x !== box) x.remove(); });
        if (el) { el.classList.add('invalid'); el.focus(); }
    }
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const r = READINGS[current()];
        const need = (f) => r.fields.includes(f);
        const v = (id) => $(id).value.trim();

        if (!v('first')) return fail('Please enter the first name.', $('first'));
        if (!v('last')) return fail('Please enter the last name.', $('last'));
        for (const id of ['day', 'month', 'year']) if (!v(id)) return fail('Please enter the full date of birth.', $(id));
        if (need('time')) for (const id of ['hour', 'minute']) if (!v(id)) return fail('Please enter the time of birth (24-hour clock).', $(id));
        if (need('place') && !v('place')) return fail('Please enter the place of birth and choose it from the list.', place);

        const params = new URLSearchParams({
            name: [v('first'), v('middle'), v('last')].filter(Boolean).join(' '),
            day: v('day'), month: v('month'), year: v('year'),
        });
        if (need('gender')) params.set('gender', form.querySelector('input[name="gender"]:checked').value);
        if (need('time')) { params.set('hour', v('hour')); params.set('minute', v('minute')); }
        if (need('place')) { params.set('place', v('place')); params.set('style', 'north'); }
        save();
        if (base === '/') location.href = '/' + r.route + '?' + params.toString();
        else location.hash = base + r.route + '?' + params.toString();
    });

    startDust();
};

// Background: gold-green dust drifting up by day, twinkling stars by night.
function startDust() {
    const c = document.getElementById('dust');
    if (!c || c.dataset.running) return;
    c.dataset.running = '1';
    const ctx = c.getContext('2d');
    const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let w, h, parts = [];
    function size() {
        const dpr = Math.min(devicePixelRatio || 1, 2);
        w = innerWidth; h = innerHeight;
        c.width = w * dpr; c.height = h * dpr; c.style.width = w + 'px'; c.style.height = h + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        parts = Array.from({ length: Math.round(w * h / 14000) }, () => ({
            x: Math.random() * w, y: Math.random() * h, r: Math.random() * 1.5 + .4,
            v: Math.random() * .18 + .04, p: Math.random() * 6.28, s: Math.random() * .02 + .005,
        }));
    }
    function frame(t) {
        if (!document.body.contains(c)) return;            // the static build replaced the page
        const dark = document.documentElement.dataset.mode === 'dark';
        const rgb = getComputedStyle(document.documentElement).getPropertyValue('--dust').trim();
        ctx.clearRect(0, 0, w, h);
        for (const p of parts) {
            if (!still) {
                p.y -= p.v; p.x += Math.sin(t / 3000 + p.p) * .12;
                if (p.y < -5) { p.y = h + 5; p.x = Math.random() * w; }
            }
            const tw = dark ? .35 + .65 * Math.abs(Math.sin(t * p.s / 10 + p.p)) : .55;
            ctx.beginPath(); ctx.arc(p.x, p.y, dark ? p.r * .9 : p.r, 0, 6.283);
            ctx.fillStyle = `rgba(${rgb}, ${(dark ? .85 : .38) * tw})`; ctx.fill();
            if (dark && p.r > 1.6) { ctx.fillStyle = `rgba(${rgb}, ${.12 * tw})`; ctx.beginPath(); ctx.arc(p.x, p.y, p.r * 4, 0, 6.283); ctx.fill(); }
        }
        if (!still) requestAnimationFrame(frame);
    }
    size();
    addEventListener('resize', size);
    requestAnimationFrame(frame);
}

if (document.getElementById('readingForm')) window.initHomePage();
