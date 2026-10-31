/*
 * JavaScript port of numerology/report.py: shapes engine output for the
 * report template. Mirrors the Python module function for function.
 */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.CosmicReport = factory();
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    const DAY_MS = 86400000;

    function createReportBuilder(DATA, engine) {
        const { PLANETS, DAY_NAMES, MONTH_NAMES, MONTH_NAMES_SHORT, GRID_LAYOUT } = DATA;
        const T = DATA.INTERPRETATIONS;

        function formatDate(d) { return `${d.getUTCDate()} ${MONTH_NAMES_SHORT[d.getUTCMonth()]} ${d.getUTCFullYear()}`; }
        function formatDateLong(d) { return `${d.getUTCDate()} ${MONTH_NAMES[d.getUTCMonth()]} ${d.getUTCFullYear()}`; }
        function digitsAdded(n) { return String(n).split('').join(' + '); }
        function round2(x) { return Math.round(x * 100) / 100; }

        function reductionSteps(value, results) {
            const steps = [];
            let current = value;
            for (const result of results) {
                if (current >= 10) steps.push({ expression: digitsAdded(current), result });
                current = result;
            }
            return steps;
        }

        function currentCycleYear(raw, today) {
            const birthdayThisYear = engine.safeDate(today.getUTCFullYear(), raw.month, raw.day);
            return today.getTime() >= birthdayThisYear.getTime() ? today.getUTCFullYear() : today.getUTCFullYear() - 1;
        }

        function ageOn(date, birth) {
            let years = date.getUTCFullYear() - birth.getUTCFullYear();
            const dm = [date.getUTCMonth(), date.getUTCDate()], bm = [birth.getUTCMonth(), birth.getUTCDate()];
            if (dm[0] < bm[0] || (dm[0] === bm[0] && dm[1] < bm[1])) years -= 1;
            return years;
        }

        function numberProfile(number, interpretation) {
            const sections = [];
            for (const [label, body] of Object.entries(interpretation)) {
                if (label !== 'Ruling Planet') sections.push({ title: label, body });
            }
            return {
                number,
                planet: PLANETS[number],
                ruling_planet: interpretation['Ruling Planet'],
                sections,
                colours: T.FAVOURABLE_COLOURS[number],
                days: T.FAVOURABLE_DAYS[number],
                friendly: T.FRIENDLY_NUMBERS[number],
                neutral: T.NEUTRAL_NUMBERS[number],
                enemy: T.ENEMY_NUMBERS[number],
            };
        }

        function calculationSteps(raw) {
            const s = raw.calc.dasha_steps;
            return {
                day: { value: raw.day, steps: reductionSteps(raw.day, [s.day_sum, s.day_root]), result: s.day_root },
                month: { value: raw.month, steps: reductionSteps(raw.month, [s.month_sum, s.month_root]), result: s.month_root },
                year: { value: raw.year, steps: reductionSteps(raw.year, [s.year_sum, s.year_root]), result: s.year_root },
                destiny: {
                    parts: [s.day_root, s.month_root, s.year_root],
                    total: s.total,
                    steps: reductionSteps(s.total, [s.total_sum, s.destiny]),
                    result: s.destiny,
                },
            };
        }

        function gridSources(raw) {
            const g = raw.calc.grid_digits;
            const yy = raw.calc.year_digits.C4;
            const digits = (keys) => keys.map((k) => g[k]).filter((v) => v !== null);
            const rootNote = g.Root === null ? 'already present in the day digits, so not added again' : '';
            return [
                { label: 'Day', value: String(raw.day).padStart(2, '0'), digits: digits(['B1', 'B2']), note: 'zeros are never placed' },
                { label: 'Month', value: String(raw.month).padStart(2, '0'), digits: digits(['M1', 'M2']), note: 'zeros are never placed' },
                { label: 'Year', value: `${raw.year} → ${yy}`, digits: digits(['Y1', 'Y2']), note: 'last two digits of the year' },
                { label: 'Root', value: String(raw.calc.root), digits: digits(['Root']), note: rootNote },
                { label: 'Destiny', value: String(raw.calc.destiny), digits: digits(['Destiny']), note: '' },
            ];
        }

        function gridCells(grid) {
            return GRID_LAYOUT.map((row) => row.map((n) => ({ position: n, planet: PLANETS[n], value: grid[n], count: grid[n].length })));
        }

        function mahaDasha(raw, today) {
            const t = today.getTime();
            const periods = raw.dasha_periods.map((p) => ({
                number: p.number,
                planet: PLANETS[p.number],
                start: formatDate(p.start),
                end: formatDate(p.end),
                start_age: p.start_age,
                end_age: p.start_age + p.duration,
                duration: p.duration,
                is_current: p.start.getTime() <= t && t <= p.end.getTime(),
                is_past: p.end.getTime() < t,
            }));
            const current = periods.find((p) => p.is_current) || null;

            const rows = [];
            for (const p of periods) {
                if (rows.length === 0 || p.number === 1) rows.push([]);
                rows[rows.length - 1].push(p);
            }
            const timeline = [];
            for (const row of rows) {
                if (row[0].start_age >= 80) break;
                const totalYears = row.reduce((s, p) => s + p.duration, 0);
                timeline.push({
                    start_age: row[0].start_age,
                    end_age: row[row.length - 1].end_age,
                    segments: row.map((p) => Object.assign({}, p, { width: round2(100 * p.duration / totalYears) })),
                });
            }
            return { periods, current, timeline };
        }

        function antardasha(raw, cycleYear) {
            const rootNum = raw.calc.root;
            const reducedMonth = raw.calc.reduced_month;
            const rows = raw.antardasha_data.map((a) => {
                const number = a.antardasha_number;
                return {
                    year: a.year,
                    birthday: formatDate(a.date),
                    weekday: a.day_name,
                    weekday_planet: PLANETS[a.planet_number],
                    parts: [a.yy, rootNum, reducedMonth, a.planet_number],
                    total: a.sum,
                    steps: reductionSteps(a.sum, [a.P, number]),
                    number,
                    planet: PLANETS[number],
                    is_current: a.year === cycleYear,
                };
            });
            return { rows, root: rootNum, reduced_month: reducedMonth, current: rows.find((r) => r.is_current) || null };
        }

        function reviewYears(raw, today, cycleYear) {
            const t = today.getTime();
            return raw.review_years.map((ry) => {
                const totalDays = ry.pratyantar.reduce((s, p) => s + (p.end.getTime() - p.start.getTime()) / DAY_MS + 1, 0) || 1;
                const prats = ry.pratyantar.map((p) => {
                    const days = (p.end.getTime() - p.start.getTime()) / DAY_MS + 1;
                    return {
                        number: p.number,
                        planet: p.planet,
                        start: formatDate(p.start),
                        end: formatDate(p.end),
                        days,
                        width: round2(100 * days / totalDays),
                        is_active: p.start.getTime() <= t && t <= p.end.getTime(),
                    };
                });
                return {
                    year: ry.year,
                    label: `${ry.year}–${ry.year + 1}`,
                    maha: ry.maha_dasha ? PLANETS[ry.maha_dasha] : null,
                    antar: ry.antar_dasha ? PLANETS[ry.antar_dasha] : null,
                    cells: gridCells(ry.grid),
                    pratyantar: prats,
                    active_pratyantar: prats.find((p) => p.is_active) || null,
                    is_current: ry.year === cycleYear,
                };
            });
        }

        function buildReport(day, month, year, clientName, today) {
            today = today || engine.todayUTC();
            const raw = engine.generateFullReport(day, month, year, today);
            const rootNum = raw.calc.root;
            const destiny = raw.calc.destiny;
            const birth = raw.birth_date;

            const cycleYear = currentCycleYear(raw, today);
            const maha = mahaDasha(raw, today);
            const antar = antardasha(raw, cycleYear);
            const years = reviewYears(raw, today, cycleYear);
            const natal = raw.natal_grid;
            const nums = [1, 2, 3, 4, 5, 6, 7, 8, 9];

            return {
                client_name: (clientName || '').trim(),
                dob: formatDateLong(birth),
                dob_short: formatDate(birth),
                birth_weekday: DAY_NAMES[birth.getUTCDay()],
                age: ageOn(today, birth),
                report_date: formatDateLong(today),
                report_year: today.getUTCFullYear(),
                root: numberProfile(rootNum, T.ROOT_INTERPRETATIONS[rootNum]),
                destiny: numberProfile(destiny, T.DESTINY_INTERPRETATIONS[destiny]),
                steps: calculationSteps(raw),
                grid: {
                    cells: gridCells(natal),
                    sources: gridSources(raw),
                    present: nums.filter((n) => natal[n]),
                    missing: nums.filter((n) => !natal[n]),
                    repeated: nums.filter((n) => natal[n].length > 1),
                },
                maha,
                antar,
                years,
                now: {
                    maha: maha.current,
                    antar: antar.current,
                    pratyantar: (years.find((y) => y.active_pratyantar) || { active_pratyantar: null }).active_pratyantar,
                },
                planets: PLANETS,
            };
        }

        return { buildReport, formatDate, formatDateLong, reductionSteps };
    }

    return { createReportBuilder };
}));
