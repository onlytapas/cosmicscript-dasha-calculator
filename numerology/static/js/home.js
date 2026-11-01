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
