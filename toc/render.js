// Render toc.svg to high-resolution PNG and vector PDF with Chromium.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const dir = __dirname;
  const svg = fs.readFileSync(path.join(dir, 'toc.svg'), 'utf8');
  const html = `<html><body style="margin:0">${svg}</body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1100, height: 600 }, deviceScaleFactor: 3 });
  await page.setContent(html);
  await page.screenshot({ path: path.join(dir, 'toc.png'), clip: { x: 0, y: 0, width: 1100, height: 600 } });
  await page.pdf({ path: path.join(dir, 'toc.pdf'), width: '1100px', height: '600px', printBackground: true, pageRanges: '1' });
  await browser.close();
})();
