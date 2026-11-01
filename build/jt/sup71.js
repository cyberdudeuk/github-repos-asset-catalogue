const {chromium} = require('playwright');
(async () => { const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'});
  for (const f of process.argv.slice(2)) { const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + f); await p.waitForTimeout(2000);
    const r = await p.evaluate(async () => { const A = window.__app, out = {}; A.showTab('suppliers'); const sel = document.querySelector('#v-area');
      for (const a of ['dq', 'meta', 'integ', '']) { sel.value = a; sel.dispatchEvent(new Event('change')); await new Promise(r => setTimeout(r, 30));
        const ids = [...document.querySelectorAll('#v-dq tbody th [data-vsel]')].map(b => b.dataset.vsel); out[a || 'all'] = document.querySelector('#v-dq h2').textContent + ' (' + ids.length + ') allIn=' + (!a || ids.every(id => A.DV.find(v => v.id === id).areas.includes(a))); }
      return out; });
    console.log(f.split('/').pop(), JSON.stringify(r), errs.slice(0, 2)); await p.close(); }
  await b.close(); })();
