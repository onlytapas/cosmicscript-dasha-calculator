/*
 * JavaScript port of numerology/name_engine.py, compatibility.py and
 * name_report.py for the single-file build. tests/test_static.py compares it
 * with Python.
 */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.CosmicName = factory();
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    const RELATIONS = {
        friendly: { label: 'Friendly', verb: 'is a friendly number for', phrase: 'friendly to' },
        neutral: { label: 'Neutral', verb: 'is neutral towards', phrase: 'neutral to' },
        enemy: { label: 'Challenging', verb: 'is a challenging (enemy) number for', phrase: 'challenging to' },
        same: { label: 'Same number', verb: 'is the same number as', phrase: 'the same as' },
        unlisted: { label: 'Not listed', verb: 'is not listed as friendly, neutral or challenging for', phrase: 'not classified against' },
    };
    const OWNER_TYPES = { person: 'a person', business: 'a business' };
    const SYSTEM_NAME = 'Chaldean numerology';
    const MAX_OPTIONS = 2;

    function createNameBuilder(DATA, engine, formatDateLong) {
        const { PLANETS } = DATA;
        const N = DATA.NAME;
        const T = DATA.INTERPRETATIONS;
        const TABLES = [['friendly', T.FRIENDLY_NUMBERS], ['enemy', T.ENEMY_NUMBERS], ['neutral', T.NEUTRAL_NUMBERS]];

        function listedNumbers(entry) { return entry.split(',').map((x) => x.trim()).filter(Boolean).map(Number); }

        function numberRelation(base, other) {
            if (base === other) return 'same';
            for (const [key, table] of TABLES) if (listedNumbers(table[base]).includes(other)) return key;
            return 'unlisted';
        }

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

        function wordRoles(count, owner) {
            if (owner === 'business') return Array.from({ length: count }, (_, i) => (count === 1 ? 'Name' : `Word ${i + 1}`));
            if (count === 1) return ['Name'];
            return ['First name'].concat(Array(count - 2).fill('Middle name'), ['Last name']);
        }

        function grade(gradedTotal) {
            const g = N.GRADES[gradedTotal];
            const level = N.GRADE_LEVELS[g.level];
            return { level: g.level, label: level.label, verdict: level.verdict, advice: level.advice, company: Boolean(g.company) };
        }

        function compoundMeaning(total, nameNumber) {
            if (total <= 52) return N.COMPOUND_MEANINGS[total];
            return `Totals above 52 take their character from the single digit they reduce to, here ${nameNumber}. The grade comes from the numerologist's table of totals.`;
        }

        function relation(baseLabel, base, nameNumber) {
            const key = numberRelation(base, nameNumber);
            const rel = RELATIONS[key];
            return { key, label: rel.label, phrase: rel.phrase, base_label: baseLabel, base, text: `Name number ${nameNumber} ${rel.verb} ${baseLabel} ${base}.` };
        }

        function alignment(nameNumber, root, destiny) {
            const withRoot = relation('Root number', root, nameNumber);
            const withDestiny = relation('Destiny number', destiny, nameNumber);
            const keys = new Set([withRoot.key, withDestiny.key]);
            const verdict = keys.has('enemy') ? 'enemy' : (keys.size === 1 && keys.has('friendly')) ? 'friendly' : 'neutral';
            let summary = `Name number ${nameNumber} is ${withRoot.phrase} the Root number ${root} and ${withDestiny.phrase} the Destiny number ${destiny}.`;
            if (verdict === 'enemy') summary += ' A name correction is worth considering.';
            return { root: withRoot, destiny: withDestiny, verdict, summary };
        }

        function nameSummary(name, owner, birth) {
            const a = analyseName(name);
            const roles = wordRoles(a.words.length, owner);
            return {
                name: a.name,
                words: a.words.map((w, i) => Object.assign({}, w, { role: roles[i], number: engine.digitSumToSingle(w.total) })),
                letter_count: a.letter_count,
                total: a.total,
                total_expression: a.total_expression,
                steps: a.steps,
                name_number: a.name_number,
                planet: PLANETS[a.name_number],
                graded_total: a.graded_total,
                graded_by_digits: a.graded_total !== a.total,
                grade: grade(a.graded_total),
                compound_meaning: compoundMeaning(a.total, a.name_number),
                digit_meaning: N.NAME_NUMBER_MEANINGS[a.name_number],
                alignment: birth ? alignment(a.name_number, birth.root, birth.destiny) : null,
            };
        }

        function birthNumbers(day, month, year) {
            const calc = engine.calcRootAndDestiny(day, month, year);
            return {
                date: formatDateLong(engine.safeDate(year, month, day)),
                root: calc.root, destiny: calc.destiny,
                root_planet: PLANETS[calc.root], destiny_planet: PLANETS[calc.destiny],
            };
        }

        // birth: [day, month, year] or null; options: recommended spellings.
        function buildNameReport(name, owner, clientName, today, birth, options) {
            today = today || engine.todayUTC();
            owner = OWNER_TYPES[owner] ? owner : 'person';
            const birthNums = birth ? birthNumbers(birth[0], birth[1], birth[2]) : null;
            const current = nameSummary(name, owner, birthNums);
            const used = new Set();
            current.words.forEach((w) => w.letters.forEach((l) => used.add(l.char)));

            return Object.assign({}, current, {
                owner,
                owner_label: OWNER_TYPES[owner],
                title: owner === 'business' ? 'Business Name Numerology Report' : 'Personal Name Numerology Report',
                system: SYSTEM_NAME,
                client_name: (clientName || '').trim(),
                report_date: formatDateLong(today),
                report_year: today.getUTCFullYear(),
                birth: birthNums,
                options: (options || []).slice(0, MAX_OPTIONS).filter((o) => o.trim()).map((o) => nameSummary(o, owner, birthNums)),
                table: Object.keys(N.CHALDEAN_TABLE).map(Number).sort((x, y) => x - y).map((v) => ({
                    value: v,
                    letters: N.CHALDEAN_TABLE[v].map((c) => ({ char: c, used: used.has(c) })),
                })),
            });
        }

        return { analyseName, numberRelation, buildNameReport };
    }

    return { createNameBuilder };
}));
