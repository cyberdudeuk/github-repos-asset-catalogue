const {chromium} = require('playwright');
(async () => { const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'}); const p = await (await b.newContext({viewport: {width: 390, height: 900}})).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(2500);
  const r = await p.evaluate(async () => { const A = window.__app, out = {}, sleep = ms => new Promise(r => setTimeout(r, ms)); const pc = pageChecks(); out.fail = pc.filter(c => !c[1]).map(c => c[0] + ' ' + c[2]); out.p43 = pc.find(c => c[0] === 'P-43')?.[2];
    A.showTab('service'); for (const t of ['personas', 'stories', 'journeys', 'blueprints', 'workflows']) { document.querySelector(`[data-st="${t}"]`).click(); await sleep(30); out[t] = document.querySelector('#sp h2').textContent + ' ' + document.querySelector('#sp').textContent.length + ' ow ' + (document.documentElement.scrollWidth - document.documentElement.clientWidth); }
    out.fails = [...document.querySelectorAll('#v-service .gw.fail')].map(x => x.textContent);
    return out; });
  console.log(JSON.stringify(r, null, 1)); console.log('ERRS', errs.slice(0, 5)); await b.close(); })();
