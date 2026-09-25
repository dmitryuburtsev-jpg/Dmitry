import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
import fs from 'fs';
const dir = process.argv[2], out = process.argv[3], only = process.argv.slice(4);
const files = fs.readdirSync(dir).filter(f=>f.endsWith('.dc.html') && (!only.length || only.some(o=>f.startsWith(o))));
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
for (const f of files) {
  let s = fs.readFileSync(dir+'/'+f,'utf8');
  s = s.replace('<script src="./support.js"></script>','').replace(/<\/?x-dc>/g,'').replace(/<helmet>/,'').replace(/<\/helmet>/,'');
  const m = s.match(/"\$preview":\s*\{"width":\s*(\d+),\s*"height":\s*(\d+)/);
  if (!m) continue;
  const w=+m[1], h=+m[2];
  const p = await b.newPage({viewport:{width:w,height:h}, deviceScaleFactor: +(process.env.SCALE||1)});
  await p.setContent(s, {waitUntil:'networkidle', timeout:15000}).catch(()=>{});
  const ov = await p.evaluate(() => { const d = document.body.querySelector('div'); return [d.scrollHeight, d.clientHeight]; }); if (ov[0] > ov[1]+1) console.log('OVERFLOW', f, ov);
  await p.screenshot({path: out+'/'+f.replace('.dc.html','.png')});
  await p.close();
}
await b.close();
