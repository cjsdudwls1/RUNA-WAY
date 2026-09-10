import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const RW = require('./core.js'); const ANIMALS = require('./animals.js');
const res = (n) => readFileSync(new URL('../core/src/test/resources/' + n, import.meta.url), 'utf8');
const by = Object.fromEntries(ANIMALS.map(a => [a.id, a]));
let fails = 0;
const track = res('golden_track.csv').trim().split('\n').map(l => { const c = l.split(','); return { t: +c[0], distCm: +c[1], speedCms: +c[2], accM: +c[3] }; });
for (const line of res('golden_expected.csv').trim().split('\n')) {
  const c = line.split(','); const s = RW.runTrack(track, by[c[0]], 500000);
  const got = [s.hits, s.sprints, s.failed ? 1 : 0, s.minGap, s.finalTimeS, s.paused, s.lost, s.reengages, s.enemyMoved];
  const exp = c.slice(1).map(Number);
  const ok = got.every((v, i) => v === exp[i]);
  if (!ok) fails++;
  console.log((ok ? 'OK  ' : 'FAIL') + ' ' + c[0] + ' got=' + got.join(',') + ' exp=' + exp.join(','));
}
const gpxRows = RW.loadTrack(res('golden_steady10.gpx'));
const expRows = res('golden_steady10_track.csv').trim().split('\n').map(l => l.split(',').map(Number));
let bad = 0;
for (let i = 0; i < expRows.length; i++) { const [t, d, s, a] = expRows[i]; const g = gpxRows[i]; if (!g || g.t !== t || Math.abs(g.distCm - d) > 1 || Math.abs(g.speedCms - s) > 1 || Math.abs(g.accM - a) > 1e-3) bad++; }
console.log((bad === 0 && gpxRows.length === expRows.length ? 'OK  ' : 'FAIL') + ' gpx rows=' + gpxRows.length + ' bad=' + bad);
if (bad) fails++;
process.exit(fails ? 1 : 0);
