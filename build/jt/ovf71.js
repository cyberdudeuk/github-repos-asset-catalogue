const {chromium} = require('playwright');
(async () => { const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'});
  const all = {};
  for (const W of [320, 390, 768, 1366]) { const p = await (await b.newContext({viewport: {width: W, height: 800}})).newPage(); await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  const tabs = await p.evaluate(() => [...document.querySelectorAll('#rail [data-tab]')].map(b => b.dataset.tab)); const res = [];
  for (const t of tabs) { const o = await p.evaluate(t => { window.__app.showTab(t); if (t === 'orgs') window.__app.profGo(0); if (t === 'topics') window.__app.topicGo('health'); if (t === 'profile') window.__app.rxGo('govuk-pay/pay-connector');
      const ov = document.documentElement.scrollWidth - document.documentElement.clientWidth; let culprit = '';
      if (ov > 0) { const all = [...document.querySelectorAll('#v-' + t + ' *, #rail *, #hubband *, footer *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1 && !e.closest('.tbl-wrap,.hero-track,.graph-wrap,pre')); culprit = all.slice(0, 3).map(e => e.tagName + '.' + e.className.toString().slice(0, 25) + ':' + Math.round(e.getBoundingClientRect().right)).join(' | '); }
      return [ov, culprit]; }, t); if (o[0] > 0) res.push(t + ' ' + o[0] + ' ' + o[1]); }
  all[W] = res; console.log(W, res.length ? res : 'no overflow'); }
  const bad = Object.values(all).flat(); const n = (await 0, Object.keys(all).length);
  if (process.argv[3]) require('fs').writeFileSync(process.argv[3], JSON.stringify({'T-WID-01': {status: bad.length ? 'fail' : 'pass', text: 'no view scrolls sideways at 320, 390, 768 or 1366 pixels wide in Chromium, including an organisation profile and a topic drill-down; wide tables scroll inside their own box', guards: 'V6-4', detail: bad.slice(0, 6).join('; ')}}));
  await b.close(); })();
