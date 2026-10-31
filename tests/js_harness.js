// Runs the JavaScript engine + report builder under Node for the regression test.
// Usage: node js_harness.js <data.json> <today YYYY-MM-DD> <dd-mm-yyyy> [...]
const fs = require('fs');
const path = require('path');
const [dataPath, todayStr, ...dates] = process.argv.slice(2);
const DATA = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const root = path.resolve(__dirname, '..', 'static_app');
const engine = require(path.join(root, 'engine.js')).createEngine(DATA);
const builder = require(path.join(root, 'report.js')).createReportBuilder(DATA, engine);
const nameBuilder = require(path.join(root, 'name_engine.js')).createNameBuilder(DATA, engine, builder.formatDateLong);
const [ty, tm, td] = todayStr.split('-').map(Number);
const today = new Date(Date.UTC(ty, tm - 1, td));
const out = {};
for (const key of dates) {
    if (key.startsWith('name:')) {
        const [, owner, name] = key.split(':');
        out[key] = nameBuilder.buildNameReport(name, owner, 'Client', today);
    } else {
        const [d, m, y] = key.split('-').map(Number);
        out[key] = builder.buildReport(d, m, y, 'Test Person', today);
    }
}
process.stdout.write(JSON.stringify(out));
