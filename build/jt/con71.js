// T-CON-02: text drawn on coloured blocks (treemap labels, family-tree blocks, chosen topic tiles, hero tiles) meets 4.5:1 in light and dark, measured in Chromium.
const {chromium} = require('playwright');
(async () => { const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'}); const bad = [], seen = {};
  for (const scheme of ['light', 'dark']) { const p = await (await b.newContext({viewport: {width: 1366, height: 900}, colorScheme: scheme})).newPage();
    await p.goto('file://' + process.argv[2]); await p.waitForTimeout(2000);
    const r = await p.evaluate(async () => {
      const rgb = s => { const m = s.match(/[\d.]+/g).map(Number); return m.slice(0, 3); };
      const L = c => { const v = c.map(x => { x /= 255; return x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; }); return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; };
      const cr = (a, b) => { const x = L(rgb(a)), y = L(rgb(b)); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
      const out = [], A = window.__app, sleep = ms => new Promise(r => setTimeout(r, ms));
      const svgPairs = (sel, tag) => document.querySelectorAll(sel).forEach(g => { const rc = g.querySelector('rect'), t = g.querySelector('text'); if (!rc || !t) return; const f = getComputedStyle(rc).fill; if (!f.startsWith('rgb')) return; out.push([tag, cr(getComputedStyle(t).fill, f)]); });
      A.showTab('insights'); await sleep(50); svgPairs('.tree g', 'treemap');
      A.showTab('gdsx'); await sleep(50); svgPairs('.tree g', 'treemap-gdsx');
      A.showTab('family'); await sleep(50); svgPairs('.famice .fami', 'family block');
      A.showTab('discover'); await sleep(50); document.querySelector('[data-rxtopic="health"]').click(); await sleep(50);
      const t = document.querySelector('[data-rxtopic="health"]'); const cs = getComputedStyle(t); out.push(['chosen topic', cr(cs.color, cs.backgroundColor)]);
      document.querySelector('[data-rxtopic="health"]').click();
      A.showTab('profile'); await sleep(50); const ic = document.querySelector('.rxtile.xl'); if (ic) { const c2 = getComputedStyle(ic); out.push(['hero tile icon (graphic, 3:1)', cr(c2.color, c2.backgroundColor), 3]); }
      return out; });
    for (const [tag, ratio, min = 4.5] of r) { seen[scheme + ' ' + tag] = (seen[scheme + ' ' + tag] || 0) + 1; if (ratio < min) bad.push(`${scheme} ${tag} ${ratio.toFixed(2)}`); } }
  const n = Object.values(seen).reduce((a, x) => a + x, 0); console.log('pairs', n, 'bad', bad.length, bad.slice(0, 8));
  if (process.argv[3]) require('fs').writeFileSync(process.argv[3], JSON.stringify({'T-CON-02': {status: bad.length || n < 20 ? 'fail' : 'pass', text: `text on coloured blocks meets WCAG contrast in light and dark, measured in Chromium (${n} label and tile pairs: treemaps, family-tree blocks, chosen topic tiles, hero tiles)`, guards: 'V7-16', detail: bad.slice(0, 6).join('; ')}}));
  await b.close(); })();
