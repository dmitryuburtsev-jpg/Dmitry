// Рендер PNG-видов через headless Chromium: node render/render.mjs
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const THREE_DIR = process.env.THREE_DIR;            // локальная копия пакета three
const views = (process.argv[2] || 'ext_front,ext_back,ext_side,int_bench,int_tech,int_back,cut,frame').split(',');
const W = +(process.env.W || 1800), H = +(process.env.H || 1100);

const srv = spawn('python3', ['-m', 'http.server', '8765', '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.log('[err]', e.message));
  await page.route('https://cdn.jsdelivr.net/npm/three@0.169.0/**', route => {
    const rel = route.request().url().split('three@0.169.0/')[1];
    route.fulfill({ body: readFileSync(path.join(THREE_DIR, rel)), contentType: 'application/javascript' });
  });
  for (const spec of views) {
    // вид[:цвет:имя] — например ext_front:%23733c2c:color_8017
    const [v, color, name] = spec.split(':');
    await page.goto(`http://127.0.0.1:8765/render/viewer.html?shot&view=${v}${color ? '&color=' + color : ''}`);
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
    await page.screenshot({ path: path.join(ROOT, 'images', `${name || v}.png`) });
    console.log('ok', name || v);
  }
} finally {
  await browser.close();
  srv.kill();
}
