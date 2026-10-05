// 검수용 WAV 굽기. sound.js를 헤드리스 크롬의 OfflineAudioContext로 돌려 소리마다 파일 하나를 만든다
// 실행: NODE_PATH=$(npm root -g) node web/render_sounds.mjs [출력 폴더]   (기본 web/dist/sounds)
// 앱과 같은 코드라 들리는 그대로가 앱에서 나는 소리다(입체 음향 포함, 이어폰으로 들을 것)
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = path.dirname(new URL(import.meta.url).pathname);
const outDir = process.argv[2] || path.join(here, 'dist', 'sounds');
fs.mkdirSync(outDir, { recursive: true });
const SND = require('./sound.js');

const browser = await chromium.launch();
const page = await browser.newPage();
await page.setContent('<!doctype html><meta charset="utf-8">');
await page.addScriptTag({ content: fs.readFileSync(path.join(here, 'sound.js'), 'utf8') });
const rows = [];
SND.LIST.forEach((it, i) => { it.n = String(i + 1).padStart(2, '0'); });
for (const it of SND.LIST) {
  const r = await page.evaluate(async (id) => {
    const it = SND.BY[id], sr = 44100, ctx = new OfflineAudioContext(2, Math.ceil(sr * (it.dur + 0.2)), sr);
    const E = SND.engine(ctx, ctx.destination); E.demo(id);
    const buf = await ctx.startRendering();
    const L = buf.getChannelData(0), Rr = buf.getChannelData(1), n = L.length;
    let peak = 0, ss = 0;
    const pcm = new Int16Array(n * 2);
    for (let i = 0; i < n; i++) {
      const a = L[i], b = Rr[i]; peak = Math.max(peak, Math.abs(a), Math.abs(b)); ss += a * a + b * b;
      pcm[i * 2] = Math.max(-1, Math.min(1, a)) * 32767; pcm[i * 2 + 1] = Math.max(-1, Math.min(1, b)) * 32767;
    }
    const bytes = new Uint8Array(pcm.buffer); let s = '';
    for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return { pcm: btoa(s), sr, peak, rms: Math.sqrt(ss / (2 * n)) };
  }, it.id);
  const data = Buffer.from(r.pcm, 'base64'), h = Buffer.alloc(44);
  h.write('RIFF', 0); h.writeUInt32LE(36 + data.length, 4); h.write('WAVE', 8); h.write('fmt ', 12); h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(2, 22);
  h.writeUInt32LE(r.sr, 24); h.writeUInt32LE(r.sr * 4, 28); h.writeUInt16LE(4, 32); h.writeUInt16LE(16, 34); h.write('data', 36); h.writeUInt32LE(data.length, 40);
  const f = `${it.n}_${it.mode}_${it.id}.wav`;
  fs.writeFileSync(path.join(outDir, f), Buffer.concat([h, data]));
  const db = (v) => (20 * Math.log10(Math.max(v, 1e-6))).toFixed(1);
  rows.push(`${f.padEnd(28)} ${it.name.padEnd(10)} peak ${db(r.peak)} dB  rms ${db(r.rms)} dB`);
}
await browser.close();
console.log(rows.join('\n'));
console.log('wrote', SND.LIST.length, 'files to', outDir);
