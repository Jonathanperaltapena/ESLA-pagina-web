// Convierte video/cuadros/*.html (1920×1080) o video/reel/*.html (1080×1920) en PNG a escala 1.5.
// Uso: PW=$(npm root -g)/playwright node video/capturas.js [cuadros|reel]
const fs = require('fs'), path = require('path');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const which = process.argv[2] || 'cuadros';
  const dir = path.resolve(__dirname, which);
  const vp = which === 'reel' ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 };
  const names = fs.readFileSync(path.join(dir, 'lista.txt'), 'utf8').trim().split('\n');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: vp, deviceScaleFactor: 1.5 });
  for (const n of names) {
    await p.goto('file://' + path.join(dir, n + '.html'), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(dir, n + '.png') });
  }
  await b.close();
  console.log('ok', names.length);
})();
