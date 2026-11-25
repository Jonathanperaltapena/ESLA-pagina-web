// Convierte video/cuadros/*.html en PNG de 2880×1620 (1920×1080 a escala 1.5).
// Uso: PW=$(npm root -g)/playwright node video/capturas.js
const fs = require('fs'), path = require('path');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const dir = path.resolve(__dirname, 'cuadros');
  const names = fs.readFileSync(path.join(dir, 'lista.txt'), 'utf8').trim().split('\n');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1.5 });
  for (const n of names) {
    await p.goto('file://' + path.join(dir, n + '.html'), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(dir, n + '.png') });
  }
  await b.close();
  console.log('ok', names.length);
})();
