const {chromium} = require('playwright');
(async () => { const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'}); const f = 'file://' + process.argv[2]; const out = [];
  for (const h of ['org=hm-revenue-customs', 'repo=govuk-pay/pay-connector', 'legacy=ministry-of-justice', 'account=alphagov', 'org=no-such-org', 'repo=nobody/nothing', 'dama']) {
    const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message)); await p.goto(f + '#' + h); await p.waitForTimeout(1800);
    out.push(await p.evaluate(h => { const A = window.__app; return h + ' -> ' + A.current + ' | ' + location.hash + ' | ' + (A.current === 'family' ? document.querySelector('#fam-sel h2')?.textContent : A.current === 'profile' ? document.querySelector('#rx-title')?.textContent : A.current === 'legacy' ? document.querySelector('#lg-count')?.textContent + ' ' + document.querySelector('#lg-chips')?.textContent : A.current === 'discover' ? document.querySelector('#rx-count')?.textContent : ''); }, h) + (errs.length ? ' ERR ' + errs[0] : ''));
    await p.close(); }
  console.log(out.join('\n')); await b.close(); })();
