// Convierte impresos/brochure.html en PDF tamaño Carta.
// Uso: PW=$(npm root -g)/playwright node impresos/pdf.js
const path = require('path');
const { chromium } = require(process.env.PW || 'playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, 'brochure.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.resolve(__dirname, 'ESLA-presentacion-institucional.pdf'), width: '8.5in', height: '11in', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
