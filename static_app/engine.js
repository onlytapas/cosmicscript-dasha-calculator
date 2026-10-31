/*
 * JavaScript port of numerology/engine.py for the single-file (no server) build.
 *
 * Every function mirrors its Python counterpart line for line, including the
 * spreadsheet cell names. Dates are UTC midnight Date objects so that adding
 * days is never affected by daylight-saving changes. tests/test_static.py runs
 * this file under Node and compares its output with the Python engine.
 */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.CosmicEngine = factory();
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    const DAY_MS = 86400000;

    function createEngine(DATA) {
        const { PLANETS, WEEKDAY_PLANET, DAY_NAMES, CONFIG } = DATA;

        // ---- Digit helpers ------------------------------------------------
        function digitSumOnce(n) {
            return String(Math.abs(Math.trunc(n))).split('').reduce((s, d) => s + Number(d), 0);
        }
        function digitSumToSingle(n) {
            n = Math.abs(Math.trunc(n));
            while (n > 9) n = digitSumOnce(n);
            return n;
        }

        // ---- Dates ---------------------------------------------------------
        function isLeap(y) { return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0; }
        function makeDate(y, m, d) {
            const date = new Date(Date.UTC(y, m - 1, d));
            if (date.getUTCFullYear() !== y || date.getUTCMonth() !== m - 1 || date.getUTCDate() !== d) {
                throw new Error(`invalid date ${y}-${m}-${d}`);
            }
            return date;
        }
        function addDays(date, n) { return new Date(date.getTime() + n * DAY_MS); }
        function safeDate(year, month, day) {
            if (month === 2 && day === 29 && !isLeap(year)) day = 28;
            if ((month === 4 || month === 6 || month === 9 || month === 11) && day === 31) day = 30;
            return makeDate(year, month, day);
        }

        // ---- Root and Destiny ---------------------------------------------
        function calcRootAndDestiny(day, month, year) {
            const A2 = day;
            const B2 = A2 >= 10 ? Number(String(A2)[0]) : 0;
            const C2 = Number(String(A2).slice(-1));
            const D2 = C2 + B2;
            const E2 = D2 >= 10 ? Number(String(D2)[0]) : 0;
            const G2 = Number(String(D2).slice(-1));
            const H2 = E2 + G2;
            let I2 = H2;
            if (H2 === day) I2 = 0;
            else if (day !== 0 && H2 === day / 10) I2 = 0;

            const A3 = month;
            const B3 = A3 >= 10 ? Number(String(A3)[0]) : 0;
            const C3 = Number(String(A3).slice(-1));
            const D3 = C3 + B3;

            const yearStr = String(year);
            const first2 = yearStr.slice(0, 2);
            const B4 = first2 === '19' ? 1 : (first2 === '20' ? 2 : 9);
            const C4str = String(Number(yearStr.slice(-2))).padStart(2, '0');
            const D4 = Number(C4str[0]);
            const E4 = Number(C4str[1]);
            const G4 = E4 + D4 + B4;
            const H4 = G4 >= 10 ? Number(String(G4)[0]) : 0;
            const I4 = Number(String(G4).slice(-1));
            const J4 = I4 + H4;

            const A5 = H2 + D3 + J4;

            const dashaA3 = digitSumOnce(day);
            const dashaA4 = digitSumOnce(dashaA3);
            const rootNum = dashaA4;

            const dashaB3 = digitSumOnce(month);
            const dashaB4 = digitSumOnce(dashaB3);
            const dashaC3 = digitSumOnce(year);
            const dashaC4 = digitSumOnce(dashaC3);
            const dashaA5 = dashaA4 + dashaB4 + dashaC4;
            const dashaA6 = digitSumOnce(dashaA5);
            const dashaA7 = digitSumOnce(dashaA6);
            const destiny = dashaA7;

            const gridDigits = {
                B1: B2 !== 0 ? B2 : null,
                B2: C2 !== 0 ? C2 : null,
                Root: I2 > 0 ? I2 : null,
                Destiny: destiny,
                M1: B3 > 0 ? B3 : null,
                M2: C3 > 0 ? C3 : null,
                Y1: D4 > 0 ? D4 : null,
                Y2: E4 > 0 ? E4 : null,
            };

            return {
                root: rootNum,
                destiny: destiny,
                grid_digits: gridDigits,
                reduced_month: dashaB4,
                day_digits: { B2, C2, D2, E2, G2, H2, I2 },
                month_digits: { B3, C3, D3 },
                year_digits: { B4, C4: C4str, D4, E4, G4, H4, I4, J4 },
                destiny_chain: { A5, H2, D3, J4 },
                dasha_steps: {
                    day_sum: dashaA3, day_root: dashaA4,
                    month_sum: dashaB3, month_root: dashaB4,
                    year_sum: dashaC3, year_root: dashaC4,
                    total: dashaA5, total_sum: dashaA6, destiny: dashaA7,
                },
            };
        }

        // ---- Grids ---------------------------------------------------------
        function buildNatalGrid(gridDigits) {
            const grid = {};
            for (let i = 1; i <= 9; i++) grid[i] = '';
            for (const d of Object.values(gridDigits)) {
                if (d !== null && d >= 1 && d <= 9) grid[d] += String(d);
            }
            return grid;
        }
        function buildYearlyGrid(natal, maha, antar) {
            const grid = Object.assign({}, natal);
            if (maha && maha >= 1 && maha <= 9) grid[maha] += String(maha);
            if (antar && antar >= 1 && antar <= 9) grid[antar] += String(antar);
            return grid;
        }

        // ---- Maha Dasha ----------------------------------------------------
        function calcDashaPeriods(rootNum, birthDate) {
            const periods = [];
            let num = rootNum;
            let start = birthDate;
            let age = 0;
            for (let cycle = 0; cycle < 12; cycle++) {
                for (let k = 0; k < 9; k++) {
                    let end;
                    try {
                        end = addDays(safeDate(start.getUTCFullYear() + num, start.getUTCMonth() + 1, start.getUTCDate()), -1);
                    } catch (e) {
                        break;
                    }
                    periods.push({ number: num, start, end, start_age: age, duration: num });
                    age += num;
                    start = addDays(end, 1);
                    num = num + 1 > 9 ? 1 : num + 1;
                }
            }
            return periods;
        }
        function findMahaDasha(periods, date) {
            const t = date.getTime();
            for (const p of periods) if (p.start.getTime() <= t && t <= p.end.getTime()) return p.number;
            return null;
        }

        // ---- Antardasha ----------------------------------------------------
        function calcAntardasha(year, birthDay, birthMonth, rootNum, reducedMonth) {
            const date = safeDate(year, birthMonth, birthDay);
            const jsWeekday = date.getUTCDay();          // 0 = Sunday, as in the sheet
            const dayName = DAY_NAMES[jsWeekday];
            const planetNumber = WEEKDAY_PLANET[jsWeekday];
            const yy = Number(String(year).slice(-2));
            const total = yy + rootNum + reducedMonth + planetNumber;
            const P = digitSumOnce(total);
            const Q = digitSumOnce(P);
            return { year, date, day_name: dayName, planet_number: planetNumber, yy, sum: total, P, antardasha_number: Q };
        }

        // ---- Pratyantar Dasha ---------------------------------------------
        function calcPratyantarDasha(antarNum, yearStart, birthDay, birthMonth, reviewYear) {
            const periods = [];
            let num = antarNum;
            let start = yearStart;
            const yearEnd = addDays(safeDate(reviewYear + 1, birthMonth, birthDay), -1);
            for (let i = 0; i < 9; i++) {
                const duration = CONFIG.PRATYANTAR_DAYS_PER_UNIT * num;
                let end = addDays(start, duration);
                if (i === 8 && end.getTime() > yearEnd.getTime()) end = yearEnd;
                periods.push({ number: num, start, end, planet: PLANETS[num] });
                start = addDays(end, 1);
                num = num + 1 > 9 ? 1 : num + 1;
            }
            return periods;
        }

        // ---- Full report ---------------------------------------------------
        function todayUTC() {
            const now = new Date();
            return new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
        }
        function generateFullReport(day, month, year, today) {
            today = today || todayUTC();
            const calc = calcRootAndDestiny(day, month, year);
            const natal = buildNatalGrid(calc.grid_digits);
            const birth = safeDate(year, month, day);
            const periods = calcDashaPeriods(calc.root, birth);
            const currentYear = today.getUTCFullYear();

            const antardasha = [];
            for (let y = currentYear - CONFIG.ANTARDASHA_YEARS_BEFORE; y < currentYear + CONFIG.ANTARDASHA_YEARS_AFTER; y++) {
                try { antardasha.push(calcAntardasha(y, day, month, calc.root, calc.reduced_month)); } catch (e) { /* skip */ }
            }

            const reviewYears = [];
            for (let i = -CONFIG.REVIEW_YEARS_BEFORE; i < CONFIG.REVIEW_YEARS_AFTER; i++) {
                const ry = currentYear + i;
                try {
                    const bday = safeDate(ry, month, day);
                    const maha = findMahaDasha(periods, bday);
                    const ae = antardasha.find((a) => a.year === ry) || null;
                    const antarNum = ae ? ae.antardasha_number : null;
                    const grid = buildYearlyGrid(natal, maha, antarNum);
                    const prat = antarNum ? calcPratyantarDasha(antarNum, bday, day, month, ry) : [];
                    reviewYears.push({ year: ry, maha_dasha: maha, antar_dasha: antarNum, grid, pratyantar: prat });
                } catch (e) { /* skip */ }
            }

            return {
                day, month, year,
                birth_date: birth,
                calc,
                natal_grid: natal,
                dasha_periods: periods.slice(0, CONFIG.MAHA_DASHA_PERIODS_SHOWN),
                antardasha_data: antardasha,
                review_years: reviewYears,
                current_year: currentYear,
            };
        }

        return {
            digitSumOnce, digitSumToSingle, safeDate, makeDate, addDays, todayUTC,
            calcRootAndDestiny, buildNatalGrid, buildYearlyGrid, calcDashaPeriods, findMahaDasha,
            calcAntardasha, calcPratyantarDasha, generateFullReport,
        };
    }

    return { createEngine };
}));
