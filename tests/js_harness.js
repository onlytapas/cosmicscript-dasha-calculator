// Runs the JavaScript engine + report builders under Node for the regression test.
// Usage: node js_harness.js <data.json> <cases.json> <today YYYY-MM-DD>
// cases.json: [{key, date: [d, m, y]} | {key, owner, name, birth: [d, m, y] | null, options: [...]}]
const fs = require('fs');
const path = require('path');
const [dataPath, casesPath, todayStr] = process.argv.slice(2);
const DATA = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const cases = JSON.parse(fs.readFileSync(casesPath, 'utf8'));
const root = path.resolve(__dirname, '..', 'static_app');
const engine = require(path.join(root, 'engine.js')).createEngine(DATA);
const builder = require(path.join(root, 'report.js')).createReportBuilder(DATA, engine);
const nameBuilder = require(path.join(root, 'name_engine.js')).createNameBuilder(DATA, engine, builder.formatDateLong);
const [ty, tm, td] = todayStr.split('-').map(Number);
const today = new Date(Date.UTC(ty, tm - 1, td));
const out = {};
for (const c of cases) {
    if (c.name !== undefined) {
        out[c.key] = nameBuilder.buildNameReport(c.name, c.owner, 'Client', today, c.birth, c.options);
    } else {
        const [d, m, y] = c.date;
        out[c.key] = builder.buildReport(d, m, y, 'Test Person', today);
    }
}
process.stdout.write(JSON.stringify(out));
