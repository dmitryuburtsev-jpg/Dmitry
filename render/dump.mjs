// Выгрузка габаритов деталей 3D-сцены в model/parts.json: node render/dump.mjs
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const srv = spawn('python3', ['-m', 'http.server', '8765', '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
try {
  const page = await browser.newPage({ viewport: { width: 400, height: 300 } });
  await page.route('https://cdn.jsdelivr.net/npm/three@0.169.0/**', route => {
    const rel = route.request().url().split('three@0.169.0/')[1];
    route.fulfill({ body: readFileSync(path.join(process.env.THREE_DIR, rel)), contentType: 'application/javascript' });
  });
  await page.goto('http://127.0.0.1:8765/render/viewer.html?shot&dump');
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });
  const parts = await page.evaluate(() => window.__dump);
  writeFileSync(path.join(ROOT, 'model', 'parts.json'), JSON.stringify(parts));
  console.log(parts.length, 'деталей');
} finally { await browser.close(); srv.kill(); }
