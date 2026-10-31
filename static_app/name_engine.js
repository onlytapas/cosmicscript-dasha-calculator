/*
 * JavaScript port of numerology/name_engine.py and name_report.py for the
 * single-file build. tests/test_static.py compares it with Python.
 */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.CosmicName = factory();
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    function createNameBuilder(DATA, engine, formatDateLong) {
        const { PLANETS } = DATA;
        const N = DATA.NAME;
        const OWNER_TYPES = { person: 'a person', business: 'a business' };

        function reductionSteps(total) {
            const steps = [];
            let current = total;
            while (current > 9) {
                const result = engine.digitSumOnce(current);
                steps.push({ expression: String(current).split('').join(' + '), result });
                current = result;
            }
            return steps;
        }

        function analyseName(name) {
            const words = [];
            for (const rawWord of name.toUpperCase().split(/\s+/).filter(Boolean)) {
                const letters = [];
                for (const ch of rawWord) {
                    if (Object.prototype.hasOwnProperty.call(N.LETTER_VALUES, ch)) letters.push({ char: ch, value: N.LETTER_VALUES[ch] });
                }
                if (letters.length) {
                    words.push({
                        text: rawWord,
                        letters,
                        expression: letters.map((l) => l.value).join(' + '),
                        total: letters.reduce((s, l) => s + l.value, 0),
                    });
                }
            }
            const total = words.reduce((s, w) => s + w.total, 0);
            if (total === 0) throw new Error('The name must contain at least one letter from A to Z.');
            const steps = reductionSteps(total);
            const nameNumber = steps.length ? steps[steps.length - 1].result : total;
            const gradedTotal = total > N.MAX_GRADED_TOTAL ? engine.digitSumOnce(total) : total;
            return {
                name: words.map((w) => w.text).join(' '),
                words,
                letter_count: words.reduce((s, w) => s + w.letters.length, 0),
                total,
                total_expression: words.map((w) => w.total).join(' + '),
                steps, name_number: nameNumber, graded_total: gradedTotal,
            };
        }

        function buildNameReport(name, owner, clientName, today) {
            today = today || engine.todayUTC();
            owner = OWNER_TYPES[owner] ? owner : 'person';
            const a = analyseName(name);
            const grade = N.GRADES[a.graded_total];
            const level = N.GRADE_LEVELS[grade.level];
            const used = new Set();
            a.words.forEach((w) => w.letters.forEach((l) => used.add(l.char)));

            const compound = a.total <= 52
                ? N.COMPOUND_MEANINGS[a.total]
                : `Totals above 52 take their character from the single digit they reduce to, here ${a.name_number}. The grade comes from the numerologist's table of totals.`;

            return {
                name: a.name,
                owner,
                owner_label: OWNER_TYPES[owner],
                client_name: (clientName || '').trim(),
                report_date: formatDateLong(today),
                report_year: today.getUTCFullYear(),
                words: a.words,
                letter_count: a.letter_count,
                total: a.total,
                total_expression: a.total_expression,
                steps: a.steps,
                name_number: a.name_number,
                planet: PLANETS[a.name_number],
                graded_total: a.graded_total,
                graded_by_digits: a.graded_total !== a.total,
                grade: {
                    level: grade.level,
                    label: level.label,
                    verdict: level.verdict,
                    advice: level.advice,
                    company: Boolean(grade.company),
                },
                compound_meaning: compound,
                digit_meaning: N.NAME_NUMBER_MEANINGS[a.name_number],
                table: Object.keys(N.CHALDEAN_TABLE).map(Number).sort((x, y) => x - y).map((v) => ({
                    value: v,
                    letters: N.CHALDEAN_TABLE[v].map((c) => ({ char: c, used: used.has(c) })),
                })),
            };
        }

        return { analyseName, buildNameReport };
    }

    return { createNameBuilder };
}));
