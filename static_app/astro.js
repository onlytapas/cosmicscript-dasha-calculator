/*
 * JavaScript port of numerology/astro for the single-file build.
 * Uses the Swiss Ephemeris WebAssembly build (vendor/swisseph) for positions;
 * everything else mirrors vedic.py, timeutil.py and report.py.
 */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.CosmicAstro = factory();
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    const DAY_MS = 86400000;

    function createAstro(DATA, swe, helpers) {
        const A = DATA.ASTRO;
        const { formatDate, formatDateLong } = helpers;
        const SE = { SUN: 0, MOON: 1, MERCURY: 2, VENUS: 3, MARS: 4, JUPITER: 5, SATURN: 6, MEAN_NODE: 10 };
        const FLG = { SWIEPH: 2, SPEED: 256, SIDEREAL: 65536 };
        const SIDM = { lahiri: 1, raman: 3, krishnamurti: 5, true_chitra: 27 };
        const BODIES = { Sun: SE.SUN, Moon: SE.MOON, Mars: SE.MARS, Mercury: SE.MERCURY, Jupiter: SE.JUPITER, Venus: SE.VENUS, Saturn: SE.SATURN, Rahu: SE.MEAN_NODE };
        const SOUTH_LAYOUT = { 11: [0, 0], 0: [0, 1], 1: [0, 2], 2: [0, 3], 10: [1, 0], 3: [1, 3], 9: [2, 0], 4: [2, 3], 8: [3, 0], 7: [3, 1], 6: [3, 2], 5: [3, 3] };

        // ---- Time zones via Intl --------------------------------------------
        function tzOffsetMinutes(utcMs, tz) {
            const dtf = new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' });
            const p = {};
            dtf.formatToParts(new Date(utcMs)).forEach((x) => { p[x.type] = x.value; });
            const asUtc = Date.UTC(Number(p.year), Number(p.month) - 1, Number(p.day), Number(p.hour), Number(p.minute), Number(p.second));
            return (asUtc - utcMs) / 60000;
        }
        function localToUtc(y, m, d, hh, mm, tz) {
            const naive = Date.UTC(y, m - 1, d, hh, mm);
            let offset = tzOffsetMinutes(naive, tz);
            let utc = naive - offset * 60000;
            offset = tzOffsetMinutes(utc, tz);          // second pass handles DST edges
            utc = naive - offset * 60000;
            return { utcMs: utc, offsetHours: offset / 60 };
        }
        function utcToLocal(utcMs, tz) {
            return new Date(utcMs + tzOffsetMinutes(utcMs, tz) * 60000);   // "local wall clock" expressed as UTC date
        }
        function julday(utcMs) {
            const d = new Date(utcMs);
            const hour = d.getUTCHours() + d.getUTCMinutes() / 60 + d.getUTCSeconds() / 3600;
            return swe.julday(d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate(), hour);
        }

        // ---- Position helpers (vedic.py) ------------------------------------
        function dms(degrees) {
            const total = Math.round(degrees * 3600);
            const d = Math.floor(total / 3600), rem = total - d * 3600;
            const m = Math.floor(rem / 60), s = rem - m * 60;
            return { d, m, s, text: `${d}°${String(m).padStart(2, '0')}'${String(s).padStart(2, '0')}"` };
        }
        function describeLongitude(lon) {
            lon = ((lon % 360) + 360) % 360;
            const signIndex = Math.floor(lon / 30);
            const inSign = lon - signIndex * 30;
            const nakIndex = Math.floor(lon / A.NAKSHATRA_SPAN);
            const inNak = lon - nakIndex * A.NAKSHATRA_SPAN;
            const pada = Math.floor(inNak / (A.NAKSHATRA_SPAN / 4)) + 1;
            const navamsaIndex = Math.floor(lon / A.NAVAMSA_SPAN) % 12;
            return {
                longitude: lon,
                sign: A.SIGNS[signIndex].name, sign_index: signIndex, sign_lord: A.SIGNS[signIndex].lord,
                degrees: dms(inSign),
                nakshatra: A.NAKSHATRAS[nakIndex], nakshatra_index: nakIndex, nakshatra_lord: A.DASHA_LORDS[nakIndex % 9],
                pada,
                navamsa_sign: A.SIGNS[navamsaIndex].name, navamsa_index: navamsaIndex,
            };
        }
        const houseFrom = (signIndex, lagnaIndex) => ((signIndex - lagnaIndex) % 12 + 12) % 12 + 1;

        function panchang(sunLon, moonLon, localWeekday) {
            const elong = ((moonLon - sunLon) % 360 + 360) % 360;
            const tithiIndex = Math.floor(elong / 12);
            const paksha = tithiIndex < 15 ? 'Shukla' : 'Krishna';
            const within = tithiIndex % 15;
            const tithiName = tithiIndex === 14 ? 'Purnima' : tithiIndex === 29 ? 'Amavasya' : A.TITHI_NAMES[within];
            const yogaIndex = Math.floor((((sunLon + moonLon) % 360) + 360) % 360 / A.NAKSHATRA_SPAN);
            const karanaIndex = Math.floor(elong / 6);
            const karana = A.KARANA_FIXED[karanaIndex] || A.KARANA_CYCLE[((karanaIndex - 1) % 7 + 7) % 7];
            return {
                tithi: `${paksha} ${tithiName}`, tithi_number: tithiIndex + 1, paksha,
                yoga: A.YOGA_NAMES[yogaIndex], karana,
                vara: A.WEEKDAY_NAMES[localWeekday], vara_lord: A.WEEKDAY_LORDS[localWeekday],
            };
        }

        // ---- Vimshottari ------------------------------------------------------
        function dashaSequence(startLord) {
            const i = A.DASHA_LORDS.indexOf(startLord);
            return A.DASHA_LORDS.slice(i).concat(A.DASHA_LORDS.slice(0, i));
        }
        function vimshottari(moonLon, birthUtcMs, levels) {
            levels = levels || 3;
            const nakIndex = Math.floor(moonLon / A.NAKSHATRA_SPAN);
            const fraction = (moonLon - nakIndex * A.NAKSHATRA_SPAN) / A.NAKSHATRA_SPAN;
            const firstLord = A.DASHA_LORDS[nakIndex % 9];
            const firstYears = A.DASHA_YEARS[firstLord];
            const elapsedDays = fraction * firstYears * A.DASHA_YEAR_DAYS;
            const balanceDays = firstYears * A.DASHA_YEAR_DAYS - elapsedDays;
            const start = birthUtcMs - elapsedDays * DAY_MS;

            function periods(parentLord, startAt, parentDays, depth) {
                const out = [];
                let t = startAt;
                for (const lord of dashaSequence(parentLord)) {
                    const days = parentDays * A.DASHA_YEARS[lord] / A.DASHA_TOTAL_YEARS;
                    const end = t + days * DAY_MS;
                    const item = { lord, start: t, end, days };
                    if (depth < levels) item.sub = periods(lord, t, days, depth + 1);
                    out.push(item);
                    t = end;
                }
                return out;
            }
            const mahas = [];
            let t = start;
            for (const lord of dashaSequence(firstLord)) {
                const days = A.DASHA_YEARS[lord] * A.DASHA_YEAR_DAYS;
                const end = t + days * DAY_MS;
                const item = { lord, start: t, end, days, years: A.DASHA_YEARS[lord] };
                if (levels >= 2) item.sub = periods(lord, t, days, 2);
                mahas.push(item);
                t = end;
            }
            return { nakshatra: A.NAKSHATRAS[nakIndex], nakshatra_lord: firstLord, fraction_elapsed: fraction, balance_days: balanceDays, balance_years: balanceDays / A.DASHA_YEAR_DAYS, mahadashas: mahas };
        }
        function runningPeriods(mahas, atMs) {
            const chain = [];
            let level = mahas;
            while (level && level.length) {
                const cur = level.find((p) => p.start <= atMs && atMs < p.end);
                if (!cur) break;
                chain.push(cur);
                level = cur.sub || [];
            }
            return chain;
        }

        // ---- Report (report.py) -----------------------------------------------
        function chart(positions, lagnaIndex, key) {
            const bySign = {};
            for (let i = 0; i < 12; i++) bySign[i] = [];
            for (const p of A.PLANETS) {
                const pos = positions[p.key];
                bySign[pos[key]].push({ abbr: p.abbr, key: p.key, retrograde: pos.retrograde });
            }
            const houses = [];
            for (let h = 0; h < 12; h++) {
                const si = (lagnaIndex + h) % 12;
                houses.push({ house: h + 1, sign_index: si, sign: A.SIGNS[si].name, sign_number: si + 1, planets: bySign[si] });
            }
            const south = [[null, null, null, null], [null, null, null, null], [null, null, null, null], [null, null, null, null]];
            for (const [si, rc] of Object.entries(SOUTH_LAYOUT)) {
                const s = Number(si);
                south[rc[0]][rc[1]] = { sign_index: s, sign: A.SIGNS[s].name, sign_abbr: A.SIGNS[s].name.slice(0, 3), planets: bySign[s], is_lagna: s === lagnaIndex };
            }
            south[1][1] = { center: true };
            return { lagna_sign_index: lagnaIndex, lagna_sign: A.SIGNS[lagnaIndex].name, houses, south };
        }
        function periodView(p, tz, nowMs) {
            const v = {
                lord: p.lord,
                start: formatDate(utcToLocal(p.start, tz)),
                end: formatDate(utcToLocal(p.end, tz)),
                days: Math.round(p.days),
                is_current: p.start <= nowMs && nowMs < p.end,
                is_past: p.end <= nowMs,
            };
            if (p.years !== undefined) v.years = p.years;
            if (p.sub) v.sub = p.sub.map((s) => periodView(s, tz, nowMs));
            return v;
        }
        function yearsText(days) {
            const years = Math.floor(days / 365.25);
            const rem = days - years * 365.25;
            const months = Math.floor(rem / 30.4375);
            const d = Math.floor(rem - months * 30.4375);
            return `${years} years, ${months} months, ${d} days`;
        }

        function buildAstroReport(name, gender, year, month, day, hour, minute, place, chartStyle, ayanamsaMode, nowMs) {
            nowMs = nowMs === undefined ? Date.now() : nowMs;
            chartStyle = chartStyle === 'south' ? 'south' : 'north';
            ayanamsaMode = SIDM[ayanamsaMode] !== undefined ? ayanamsaMode : 'lahiri';
            swe.set_sid_mode(SIDM[ayanamsaMode], 0, 0);

            const { utcMs, offsetHours } = localToUtc(year, month, day, hour, minute, place.timezone);
            const jd = julday(utcMs);
            const flags = FLG.SWIEPH | FLG.SIDEREAL | FLG.SPEED;

            const raw = {};
            for (const [key, body] of Object.entries(BODIES)) {
                const r = swe.calc_ut(jd, body, flags);
                raw[key] = { longitude: ((r[0] % 360) + 360) % 360, speed: r[3], retrograde: r[3] < 0 };
            }
            raw.Ketu = { longitude: (raw.Rahu.longitude + 180) % 360, speed: raw.Rahu.speed, retrograde: raw.Rahu.retrograde };
            const h = swe.houses_ex(jd, FLG.SIDEREAL, place.latitude, place.longitude, 'W');
            const asc = Array.isArray(h.ascmc) ? h.ascmc[0] : (h.ascendant !== undefined ? h.ascendant : h.ascmc[0]);
            const lagna = describeLongitude(asc);

            const positions = {};
            for (const p of A.PLANETS) {
                const d = describeLongitude(raw[p.key].longitude);
                Object.assign(d, { key: p.key, abbr: p.abbr, symbol: p.symbol, retrograde: raw[p.key].retrograde, house: houseFrom(d.sign_index, lagna.sign_index) });
                positions[p.key] = d;
            }
            const moon = positions.Moon, sun = positions.Sun;
            const local = new Date(Date.UTC(year, month - 1, day, hour, minute));
            const localWeekday = local.getUTCDay();
            const dasha = vimshottari(moon.longitude, utcMs, 3);
            const chain = runningPeriods(dasha.mahadashas, nowMs);
            const utcDate = new Date(utcMs);
            const hh = (n) => String(n).padStart(2, '0');
            const now = chain.map((p) => ({ lord: p.lord, start: formatDate(utcToLocal(p.start, place.timezone)), end: formatDate(utcToLocal(p.end, place.timezone)) }));

            return {
                name: (name || '').trim(),
                gender,
                birth: {
                    date: formatDateLong(local),
                    time: `${hh(hour)}:${hh(minute)}`,
                    weekday: A.WEEKDAY_NAMES[localWeekday],
                    place: place.label,
                    latitude: place.latitude, longitude: place.longitude, timezone: place.timezone,
                    utc_offset: offsetHours,
                    utc: `${formatDate(utcDate)} ${hh(utcDate.getUTCHours())}:${hh(utcDate.getUTCMinutes())}`,
                    jd: Math.round(jd * 1e5) / 1e5,
                    ayanamsa: dms(swe.get_ayanamsa_ut(jd)),
                    ayanamsa_name: ayanamsaMode,
                },
                report_date: formatDateLong(new Date(nowMs)),
                report_year: new Date(nowMs).getUTCFullYear(),
                chart_style: chartStyle,
                lagna, moon, sun,
                positions: A.PLANETS.map((p) => positions[p.key]),
                rasi: chart(positions, lagna.sign_index, 'sign_index'),
                navamsa: chart(positions, lagna.navamsa_index, 'navamsa_index'),
                panchang: panchang(sun.longitude, moon.longitude, localWeekday),
                dasha: {
                    nakshatra: dasha.nakshatra, nakshatra_lord: dasha.nakshatra_lord,
                    fraction_elapsed: Math.round(dasha.fraction_elapsed * 1e4) / 1e4,
                    balance_years: Math.round(dasha.balance_years * 100) / 100,
                    balance_text: yearsText(dasha.balance_days),
                    mahadashas: dasha.mahadashas.map((m) => periodView(m, place.timezone, nowMs)),
                },
                now,
                now_text: now.map((p) => p.lord).join(' › '),
                now_last: now.length ? now[now.length - 1] : null,
            };
        }

        function searchPlaces(query, limit) {
            const q = A.fold(query || '').split(',')[0].trim().toLowerCase();
            if (!q) return [];
            const starts = [], contains = [];
            for (const p of A.PLACES) {
                const n = p.name.toLowerCase();
                if (n.startsWith(q)) starts.push(p); else if (n.includes(q)) contains.push(p);
            }
            return starts.concat(contains).slice(0, limit || 12);
        }
        function findPlace(label) { label = A.fold(label); return A.PLACES.find((p) => p.label === label) || null; }

        return { buildAstroReport, searchPlaces, findPlace, describeLongitude, vimshottari, panchang };
    }

    return { createAstro };
}));
