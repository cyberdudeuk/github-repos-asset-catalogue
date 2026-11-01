const {chromium} = require('playwright');
(async () => { const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'}); const p = await (await b.newContext({viewport: {width: 1366, height: 900}})).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(2500);
  const r = await p.evaluate(async () => { const A = window.__app, sleep = ms => new Promise(r => setTimeout(r, ms)), out = {};
    const pc = pageChecks(); out.fail = pc.filter(c => !c[1]).map(c => c[0] + ' ' + c[2]); out.p42 = pc.find(c => c[0] === 'P-42')?.[2];
    for (const t of ['guidance', 'journeys', 'nations', 'international']) { A.showTab(t); await sleep(30); out[t] = document.querySelector(`#th-${t}-count`).textContent + ' | tiles ' + [...document.querySelectorAll(`#v-${t} [data-thsub]`)].map(b => b.querySelector('.lgt-l').textContent + '=' + b.querySelector('.lgt-n').textContent).join(', '); }
    A.showTab('knowledge'); await sleep(30); out.kg = document.querySelector('#kp h2').textContent + ' nodes ' + document.querySelectorAll('#kp svg [data-kgk]').length;
    document.querySelector('#kp svg [data-kgk]').dispatchEvent(new MouseEvent('click', {bubbles: true})); await sleep(30); out.kg2 = document.querySelector('.kg-side p').textContent.slice(0, 90);
    for (const t of ['lineage', 'vocab', 'ontology', 'dict', 'thes']) { document.querySelector(`[data-kt="${t}"]`).click(); await sleep(40); out[t] = document.querySelector('#kp h2').textContent + ' · ' + document.querySelector('#kp').textContent.length; }
    document.querySelector('[data-kt="lineage"]').click(); await sleep(30); const n = document.querySelector('[data-kl="r-R33"]') || document.querySelector('[data-kl^="r-"]'); n.click(); await sleep(30); out.lin = document.querySelector('.kl-sel')?.textContent.slice(0, 120) + ' lit ' + document.querySelectorAll('.kl-n.lit').length;
    A.rxGo('govuk-pay/pay-connector'); await sleep(30); out.chips = [...document.querySelectorAll('#v-profile .rxchips .rxchip')].map(c => c.textContent.trim()).join(' | ');
    A.gsGo('playbook'); await sleep(50); out.srch = document.querySelector('#gs-count').textContent + ' :: ' + [...document.querySelectorAll('[data-gskind]')].map(b => b.textContent.trim()).join(' | ');
    return out; });
  console.log(JSON.stringify(r, null, 1)); console.log('ERRS', errs.slice(0, 5));
  for (const t of ['nations', 'knowledge']) { await p.evaluate(t => { window.__app.showTab(t); if (t === 'knowledge') { window.__app.KS.tab = 'lineage'; window.__app.KS.sel = 'r-R33'; } }, t); await p.evaluate(() => { const A = window.__app; if (A.current === 'knowledge') RENDER.knowledge(); }); await p.waitForTimeout(300); await p.screenshot({path: `/tmp/s72_${t}.png`, fullPage: false}); }
  await b.close(); })();
