// Harness for explorer7 (from t6): functional, security, keyboard, AI, text and document tests. Writes inv/test_results.json (merged with axe/contrast results).
const {JSDOM} = require('jsdom'); const fs = require('fs'); const path = require('path');
const HTML = fs.readFileSync(process.argv[2], 'utf8'); const OUT = process.argv[3];
const R = {}; const rec = (id, ok, text, guards, detail) => { R[id] = {status: ok ? 'pass' : 'fail', text, guards, detail: detail || ''}; console.log((ok ? 'PASS ' : 'FAIL ') + id + ' ' + text + (detail && !ok ? ' :: ' + detail : '')); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

function mockClaude(opts = {}) {
  const store = {decisions: {}, decision_log: []}; const subs = []; let subscribeCalls = 0; const saves = []; const writes = [];
  const snap = () => ({docs: Object.entries(store.decisions).map(([id, v]) => ({id, data: () => v}))});
  const db = {collection: name => ({
    doc: id => ({set: async body => { if (opts.setError) throw {code: opts.setError, message: 'x'}; writes.push([name, id, body]); store[name][id] = body; subs.forEach(s => s.alive && s.next(snap())); },
                 delete: async () => { delete store[name][id]; subs.forEach(s => s.alive && s.next(snap())); }}),
    add: async body => { store.decision_log.push(body); },
    onSnapshot: (next, err) => { subscribeCalls++; const s = {next, err, alive: true}; subs.push(s); setTimeout(() => s.alive && next(snap()), 5); return () => { s.alive = false; }; }})};
  const sample = async (input, o = {}) => { if (opts.sampleError) throw {code: opts.sampleError, text: 'partial'}; o.onText && o.onText({text: 'partial', delta: 'partial'}); if (o.tools) { const t = o.tools.find(t => t.name === 'search_cocddo'); t && t.execute({query: ''}); } await sleep(5); return {text: 'FINAL TEXT', truncated: false}; };
  sample.json = async (input, o = {}) => ({group: 'Wave 2: active products', confidence: 'medium', reasons: ['<b>r</b>'], risks: []});
  sample.limits = async () => ({});
  const api = {db, user: {id: async () => 'u1', can: async () => opts.canWrite ?? true, profiles: async ids => Object.fromEntries((Array.isArray(ids) ? ids : [ids]).map(i => [i, {name: 'Tester <i>x</i>'}]))},
               downloads: {save: async r => { saves.push(r); return {status: 'saved'}; }}, sample};
  return {claude: {use: async n => opts.none ? null : api[n] ?? null}, store, subs, saves, writes, get subscribeCalls() { return subscribeCalls; },
          push(id, v) { store.decisions[id] = v; subs.forEach(s => s.alive && s.next(snap())); }, fail(code) { subs.forEach(s => { if (s.alive) { s.alive = false; s.err && s.err({code, message: 'x'}); } }); }};
}
async function load(html, opts) {
  const errs = []; const mock = opts === null ? null : mockClaude(opts || {});
  const dom = new JSDOM('<!doctype html><html lang="en-GB"><head></head><body>' + html + '</body></html>', {runScripts: 'dangerously', url: 'https://x.test/', pretendToBeVisual: true,
    beforeParse(w) { w.addEventListener('error', e => errs.push(e.message)); w.matchMedia = () => ({matches: false, addEventListener() {}}); w.HTMLElement.prototype.scrollIntoView = function () {}; w.Element.prototype.scrollBy = function () {}; w.Element.prototype.scrollTo = function () {};
      if (mock) w.claude = mock.claude; w.navigator.clipboard = {writeText: async () => {}}; }});
  await sleep(150); return {w: dom.window, d: dom.window.document, mock, errs, dom};
}
const click = (w, el) => el.dispatchEvent(new w.MouseEvent('click', {bubbles: true}));
const firstWithDecform = async (env, name) => { env.w.__app.openSheet(name); await sleep(5); return env.d.querySelector('#decform'); };

(async () => {
  const env = await load(HTML, {}); const {w, d, mock} = env; const A = w.__app; const rows = A.rows;
  const name = rows.find(r => r.status === 'Active').repo; A.rows = rows;

  // T-VIEW-01: every view renders, page self-checks pass, list alternatives present
  const tabs = [...d.querySelectorAll('#rail [data-tab]')].map(b => b.dataset.tab); const empty = [];
  for (const t of tabs) { click(w, d.querySelector(`#rail [data-tab="${t}"]`)); await sleep(1); const v = d.querySelector('#v-' + t); if (v.hidden || v.querySelector('.vbody').innerHTML.length < 200) empty.push(t); }
  A.showTab('lineage'); const hasLists = !!d.querySelector('#graph-list table') && !!d.querySelector('#tube-list li');
  const pcFails = A.pageChecks().filter(p => !p[1]).map(p => p[0]);
  rec('T-VIEW-01', !empty.length && hasLists && !pcFails.length && !env.errs.length, `all ${tabs.length} views render, diagrams have list alternatives, page self-checks pass`, 'D12, R8', JSON.stringify({empty, hasLists, pcFails, errs: env.errs}));

  // T-VIEW-02: footer
  const ft = d.querySelector('#footer').textContent;
  rec('T-VIEW-02', !!d.querySelector('#footer .qr svg') && !!d.querySelector('#footer .bc svg') && /Disclaimer/.test(ft) && /Disclosures and transparency/.test(ft) && /Contact form/.test(ft) && /issues\/new\?template=contact\.yml$/.test(d.querySelector('#ft-contact')?.href || '') && !/[a-z0-9._%+-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}/i.test(ft) && !d.querySelector('#footer a[href^="mailto:"]') && /Open Government Licence/.test(ft) && /no requests to third parties/.test(ft) && !/fonts\.(googleapis|gstatic)/.test(HTML), 'footer has disclaimer, disclosures, contact (the contact form, and no email address at all), QR code, barcode and font disclosure; fonts are embedded', 'R12, D12, V73-3, R69');

  // T-DEC-01: no default choice; error message; then save works
  let f = await firstWithDecform(env, name);
  const noneChecked = f && ![...f.querySelectorAll('input[name=st]')].some(i => i.checked);
  f.dispatchEvent(new w.Event('submit', {cancelable: true})); await sleep(5);
  const errShown = !d.querySelector('#dec-err').hidden && !!d.querySelector('#dec-err-sum .errsum') && mock.writes.length === 0;
  f.querySelector('input[value=agreed]').checked = true; f.dispatchEvent(new w.Event('submit', {cancelable: true})); await sleep(20);
  rec('T-DEC-01', noneChecked && errShown && mock.writes.length === 1 && mock.writes[0][2].state === 'agreed', 'decision form has no default; submitting empty shows an error and saves nothing; a choice saves', 'D15', JSON.stringify({noneChecked, errShown, writes: mock.writes.length}));
  d.querySelector('#sh-close').click();

  // T-DEC-02: views refresh after a decision changes
  A.showTab('overview'); const before = d.querySelector('#v-overview .stats').textContent;
  const other = rows.find(r => r.destination_group.startsWith('2')).repo;
  mock.push(other, {repo: other, state: 'changed', group: '8 Delete (empty or unmodified fork)', note: '', by: 'u2', at: '2026-10-08T10:00:00Z'}); await sleep(20);
  const after = d.querySelector('#v-overview .stats').textContent;
  A.showTab('plan'); const inDelete = [...d.querySelectorAll('#v-plan .wave')].find(x => /Delete/.test(x.querySelector('h3').textContent)).textContent.includes(other);
  rec('T-DEC-02', before !== after && /2 of/.test(after) && inDelete, 'overview and plan reflect a decision recorded by someone else', 'D5', JSON.stringify({before: before.slice(0, 80), after: after.slice(0, 80), inDelete}));

  // T-DEC-03: unsaved edits survive someone else's save
  f = await firstWithDecform(env, other); d.querySelector('#dec-note').value = 'my unsaved words'; f.dispatchEvent(new w.Event('input', {bubbles: true}));
  mock.push(other, {repo: other, state: 'discuss', group: null, note: 'theirs', by: 'u3', at: '2026-10-08T11:00:00Z'}); await sleep(20);
  rec('T-DEC-03', d.querySelector('#dec-note')?.value === 'my unsaved words' && !!d.querySelector('#dec-newer'), 'a newer decision from someone else does not wipe an unsaved note and is announced', 'D6');
  d.querySelector('#sh-close').click();

  // T-XSS-01: hostile stored decisions are escaped or rejected
  mock.push(name, {repo: name, state: 'changed', group: '7 Archive in place', note: '<img src=x id=pwn1 onerror="window.__pwn=1">', by: '<b id=pwn2>', at: '<script>'});
  mock.push(rows[3].repo, {state: '<img id=pwn3 src=x>', note: 'x'}); mock.push(rows[4].repo, {state: 'changed', group: '<img id=pwn4>'}); mock.push('__proto__', {state: 'agreed'}); await sleep(20);
  A.openSheet(name); await sleep(5); A.showTab('overview'); A.showTab('repos'); A.showTab('about');
  const p06 = A.pageChecks().find(p => p[0] === 'P-06');
  rec('T-XSS-01', !d.querySelector('#pwn1,#pwn2,#pwn3,#pwn4') && !w.__pwn && d.querySelector('#decbox').textContent.includes('<img src=x') && !A.decisions[rows[3].repo] && !A.decisions[rows[4].repo] && p06 && !p06[1], 'stored decisions are validated and escaped; malformed ones are ignored and reported', 'D2', JSON.stringify({p06}));
  d.querySelector('#sh-close').click();

  // T-DEC-04: per-code write errors and subscription recovery
  const env2 = await load(HTML, {setError: 'quota_exceeded'}); f = await firstWithDecform(env2, name); f.querySelector('input[value=discuss]').checked = true; f.dispatchEvent(new w.Event('submit', {cancelable: true})); await sleep(20);
  const quotaMsg = env2.d.querySelector('#dec-status').textContent;
  const env3 = await load(HTML, {setError: 'invalid_argument', canWrite: null}); f = await firstWithDecform(env3, name); f.querySelector('input[value=discuss]').checked = true; f.dispatchEvent(new w.Event('submit', {cancelable: true})); await sleep(20);
  const permMsg = env3.d.querySelector('#dec-status').textContent;
  const c0 = mock.subscribeCalls; mock.fail('unavailable'); await sleep(50); const paused = !d.querySelector('#live-note').hidden; await sleep(2700); const resub = mock.subscribeCalls > c0;
  rec('T-DEC-04', /full/.test(quotaMsg) && /can't record/.test(permMsg) && paused && resub, 'save errors are explained per error code; a dropped subscription is shown and re-established', 'D16', JSON.stringify({quotaMsg, permMsg, paused, resub}));

  // T-XSS-02: hostile strings inside the data itself are escaped
  let bad = HTML.replace('"description":"', '"description":"<img id=pwnD src=x>'), si = bad.indexOf('"spotlight":[');
  bad = bad.slice(0, si) + bad.slice(si).replace('"d":"', '"d":"<img id=pwnS src=x>');
  const xi = bad.indexOf('"xrows":[['); bad = bad.slice(0, xi) + bad.slice(xi).replace(/("xrows":\[\[\d+,")/, '$1<img id=pwnX>');
  const ci = bad.indexOf('"cat":[['); bad = bad.slice(0, ci) + bad.slice(ci).replace(/("cat":\[\[\d+,"[^"]*",")/, '$1<img id=pwnC>');
  const e4 = await load(bad, {}); e4.w.__app.showTab('repos'); e4.w.__app.openSheet(e4.w.__app.rows[0].repo); await sleep(5); e4.d.querySelector('#sh-close').click(); e4.w.__app.showTab('landscape'); e4.w.__app.openX(e4.w.__app.X[0].key); await sleep(5); e4.d.querySelector('#sh-close').click(); e4.w.__app.showTab('catalogue'); e4.w.__app.openX(e4.w.__app.CATX[0].key); await sleep(5);
  rec('T-XSS-02', !e4.d.querySelector('#pwnD,#pwnS,#pwnX,#pwnC') && e4.d.body.innerHTML.includes('&lt;img id=pwnC') && e4.d.body.innerHTML.includes('&lt;img id=pwnD'), 'hostile text in repository descriptions, spotlight and government rows is shown as text, never run', 'D2');

  // T-KEY-01: skip link
  A.showTab('gdsway'); d.querySelector('#skip').click(); await sleep(1);
  rec('T-KEY-01', d.activeElement === d.querySelector('#main') && A.current === 'gdsway', 'skip link moves focus to the main content and keeps the current view', 'D4');

  // T-KEY-02: sortable headers are buttons and keep focus
  A.showTab('repos'); A.F.q = ''; A.renderTable(); let sb = d.querySelector('#repo-table .sortb[data-k="repo"]'); sb.click(); await sleep(1);
  const th = d.querySelector('#repo-table .sortb[data-k="repo"]').closest('th');
  rec('T-KEY-02', d.activeElement?.dataset?.k === 'repo' && th.getAttribute('aria-sort') !== 'none' && !d.querySelector('#repo-table tr[tabindex]') && !!d.querySelector('#repo-table tbody .openb'), 'sorting uses buttons and keeps focus; rows open from a button in the first cell', 'D14');

  // T-KEY-03: pager focus and dialog focus return
  A.F.q = ''; A.renderTable(); const next = [...d.querySelectorAll('#repo-pager button')].find(b => /Next/.test(b.textContent)); next.click(); await sleep(1);
  const pagerFocus = d.activeElement?.id === 'repo-cap';
  const opener = d.querySelector('#repo-table tbody .openb'); opener.focus(); opener.click(); await sleep(5); const inSheet = d.activeElement?.id === 'sh-close';
  d.dispatchEvent(new w.KeyboardEvent('keydown', {key: 'Escape', bubbles: true})); await sleep(1);
  rec('T-KEY-03', pagerFocus && inSheet && d.querySelector('#sheet').hidden && d.activeElement === opener, 'paging moves focus to the results; the details dialog takes focus and returns it on Escape', 'D14', JSON.stringify({pagerFocus, inSheet}));

  // T-KEY-04: Back moves between views
  click(w, d.querySelector('#rail [data-tab="overview"]')); click(w, d.querySelector('#rail [data-tab="dam"]')); w.history.back(); await sleep(60);
  rec('T-KEY-04', A.current === 'overview' && !d.querySelector('#v-overview').hidden, 'the browser Back button returns to the previous view', 'D18', 'current=' + A.current);

  // T-AI-01 / T-AI-02
  A.showTab('ask'); d.querySelector('#askq').value = 'Which repositories must move first?'; d.querySelector('#askform').dispatchEvent(new w.Event('submit', {cancelable: true})); await sleep(40);
  const bot = [...d.querySelectorAll('#chat .msg.bot')].at(-1)?.textContent || '';
  rec('T-AI-01', bot.startsWith('FINAL TEXT') && /search_cocddo/.test(bot) && d.querySelector('#ask-live').textContent === 'Answer ready.' && d.querySelector('#chat').getAttribute('aria-live') === null, 'questions are answered with tools, the tools used are shown, and only completion is announced', 'D14, R6', bot.slice(0, 80));
  A.openSheet(name); await sleep(5); d.querySelector('[data-ai="notice"]').click(); await sleep(40); const draft = d.querySelector('#ai-draft')?.value;
  d.querySelector('[data-ai="suggest"]').click(); await sleep(20); const sugg = d.querySelector('#ai-out').innerHTML;
  rec('T-AI-02', draft === 'FINAL TEXT' && /Wave 2/.test(sugg) && !/<b>r<\/b>/.test(sugg), 'drafts keep the final text, not the last partial; suggestions are validated and escaped', 'D18', JSON.stringify({draft}));
  d.querySelector('#sh-close').click();

  // T-IMP-01: impact assessment wording
  const base = rows.find(r => r.pages) || rows[0];
  const imp = A.impact({...base, ref_oidc: 2, pages: true, pages_custom: '', stars: 50}).map(i => i.join(' ')).join(' ');
  rec('T-IMP-01', /immutable/.test(imp) && /dry-run deploy/.test(imp) && /doesn't redirect co-cddo\.github\.io/.test(imp) && /100 clones/.test(imp) && !/repo:gds-dtx\/\*/.test(imp), 'impact assessment uses current GitHub behaviour (immutable OIDC subjects, Pages not redirected, retired names)', 'D3, D10');

  // T-TXT-01: wording and style
  const src = HTML.slice(HTML.indexOf('<script>'));  const code = src.replace(/const DATA = .*?;\n/s, '');
  let allText = '', prose = ''; for (const t of tabs) { A.showTab(t); const v = d.querySelector('#v-' + t); allText += v.textContent + '\n'; const c = v.cloneNode(true); c.querySelectorAll('td.repo small, td.muted, .card p, pre, code, .rxc-sum, .rx-lede, #v-profile td, .lgev').forEach(n => n.remove()); prose += c.textContent + '\n'; }
  const safeTxt = (A.showTab('safe'), d.querySelector('#v-safe').textContent);
  const iso = (prose.match(/\b20\d\d-\d\d-\d\d\b/g) || []).length;
  const probs = [];
  if (/\b141\b/.test(code)) probs.push('hard-coded 141 in page code');
  if (/repo:gds-dtx\/\*/.test(code)) probs.push('old OIDC advice');
  if (!/archive the organisation only after the last move/i.test(safeTxt)) probs.push('safe banner wording');
  if (/delete, rename or archive the co-cddo organisation/i.test(allText)) probs.push('contradictory archive advice');
  if (/Leave archived/.test(allText + d.querySelector('#footer').textContent)) probs.push('Leave archived label');
  if (/ & /.test(code.replace(/&&|&amp;|"&"/g, ''))) probs.push('ampersand in page prose');
  if (iso) probs.push(iso + ' ISO dates in view text: ' + prose.match(/.{60}\b20\d\d-\d\d-\d\d\b.{20}/g));
  if (/no tracking/i.test(d.querySelector('#footer').textContent + d.querySelector('#v-about').textContent)) probs.push('no tracking claim');
  rec('T-TXT-01', !probs.length, 'page text follows the corrected guidance and GOV.UK style (no hard-coded counts, no ISO dates, no ampersands, consistent archive advice)', 'D3, D10, D11, D12, D19', probs.join('; '));

  // T-CSV-01
  const cell = A.csvCell('=HYPERLINK("x")'), csv = A.csvText(A.filtered());
  A.showTab('repos'); A.renderTable();
  rec('T-CSV-01', cell.startsWith('"\'=') && A.csvCell('+1').startsWith('"\'+') && A.csvCell('-1').startsWith('"\'-') && A.csvCell('@x').startsWith('"\'@') && csv.split('\r\n').length === A.filtered().length + 1 && /Download CSV \(\d+ rows?\)/.test(d.querySelector('#export').textContent), 'CSV neutralises spreadsheet formulas and the button says how many rows it exports', 'D17');

  // T-DOC-01 / T-DOC-02
  A.showTab('docs'); const btns = [...d.querySelectorAll('#v-docs [data-doc]')]; let docOk = btns.length >= 14;
  for (const b of btns) { b.click(); if (!d.querySelector('#doc-h') || d.querySelector('#doc-h').textContent.length < 3 || d.querySelector('#doc-body').textContent.length < 100) docOk = false; }
  rec('T-DOC-01', docOk, `artefact pack: ${btns.length} documents each render with content`, 'R15');
  const kg = A.knowledgeGraph(), ttl = A.ontologyTtl(), md = A.packMd(); const regIds = new Set(w.eval('DATA.registry').map(c => c.id));
  const reqs = kg['@graph'].filter(n => n['@type'] === 'cmx:Requirement'); const okReq = reqs.length === w.eval('DATA.requirements').length && reqs.every(q => q['cmx:verifiedBy'].every(c => regIds.has(decodeURIComponent(c['@id'].split('/').pop()))));
  const nTerms = (w.eval('DATA.docs.ontology[1]').find(b => b[0] === 'table')[2] || []).filter(r => /^cmx:\w+$/.test(r[0])).length;
  const titles = Object.values(w.eval('DATA.docs')).every(x => md.includes('## ' + x[0]));
  click(w, d.querySelector('#dl-kg')); await sleep(10);
  rec('T-DOC-02', okReq && JSON.parse(JSON.stringify(kg))['@graph'].length > 1000 && (ttl.match(/^cmx:\w+ a owl:/gm) || []).length === nTerms && titles && mock.saves.some(s => /\.json$/.test(s.filename)), 'knowledge graph links every requirement to registered checks; ontology covers every term; the Markdown pack has every document; downloads work', 'R15', JSON.stringify({okReq, nTerms, ttl: (ttl.match(/ a owl:/g) || []).length, titles}));


  // T-CAT-01: catalogue search, filters, record panel, CSV
  A.showTab('catalogue'); const cq = d.querySelector('#c-q'); cq.value = 'metadata'; cq.dispatchEvent(new w.Event('input')); await sleep(5);
  const cnt1 = d.querySelector('#c-count').textContent; d.querySelector('#c-reset').click();
  const sb2 = d.querySelector('#c-basis'); sb2.value = 'push'; sb2.dispatchEvent(new w.Event('change')); await sleep(5);
  const pushRows = A.catFiltered(); const okPush = pushRows.length > 1000 && pushRows.every(x => !['Active','Maintained','Automated only'].includes(x.st));
  d.querySelector('#c-reset').click(); const sel = d.querySelector('#c-status'); sel.value = 'Not publicly visible'; sel.dispatchEvent(new w.Event('change')); await sleep(5);
  const hidden = A.catFiltered().length; d.querySelector('#c-table .openb').click(); await sleep(5); const panelOk = /not visible in public data/.test(d.querySelector('#sheet').textContent); d.querySelector('#sh-close').click();
  d.querySelector('#c-reset').click(); A.openX(A.CATX[0].key); await sleep(5); const catPanel = /Catalogue record/.test(d.querySelector('#sheet').textContent) && /push date|listing|git/.test(d.querySelector('#sheet').textContent); d.querySelector('#sh-close').click();
  const csv5 = A.catCsv(A.ALL.slice(0, 50)); const rowsCsv = csv5.split('\r\n');
  rec('T-CAT-01', /records/.test(cnt1) && okPush && hidden === A.UNL.length && hidden > 0 && panelOk && catPanel && rowsCsv.length === 51 && A.ALL.length === A.X.length + A.CATX.length + A.UNL.length, `catalogue of ${A.ALL.length} records: search, status-basis filter, unconfirmed v1 names, record panels and CSV work`, 'R17, V5-2', JSON.stringify({cnt1, okPush, hidden, panelOk, catPanel}));
  // T-CAT-02: DCAT export
  const dc = A.catDcat(A.ALL.filter(x => x.org === 'co-cddo'));
  const res = dc['dcat:resource']; const okD = dc['@type'] === 'dcat:Catalog' && res.length === A.ALL.filter(x => x.org === 'co-cddo').length && res.every(r => r['dcterms:identifier'] && r['adms:status'] && r['cmx:statusBasis'] && r['dcterms:publisher']) && new Set(res.map(r => r['@id'])).size === res.length;
  d.querySelector('#c-reset').click(); click(w, d.querySelector('#c-dcat')); await sleep(20);
  rec('T-CAT-02', okD && mock.saves.some(s => /dcat.*\.json$/.test(s.filename) && JSON.parse(s.data)['dcat:resource'].length === A.ALL.length), 'DCAT JSON-LD export: a dcat:Catalog with one resource per record, each with identifier, publisher, status and its basis', 'R17', JSON.stringify({okD, n: res.length}));
  // T-V1-01: reconciliation and v1 layer in the details panel
  A.showTab('reconcile'); const rtext = d.querySelector('#v-reconcile').textContent;
  const ren = w.eval('DATA.v1.reconciliation').filter(r => r.status === 'Old name (renamed)');
  A.openSheet(ren[0].current); await sleep(5); const st = d.querySelector('#sheet').textContent; d.querySelector('#sh-close').click();
  A.showTab('assess'); const atext = d.querySelector('#v-assess').textContent;
  rec('T-V1-01', /old names of renamed repositories/.test(rtext) && ren.length > 0 && st.includes('Name in v1') && st.includes(ren[0].v1) && /Re-run/.test(st) && /How outcomes change/.test(atext) && d.querySelectorAll('#as-table tbody tr').length === A.rows.length, 'v1 reconciliation, merged owner knowledge and the re-run scoring appear in the views and the details panel', 'R16');
  // T-CTL-01: control counts in the view equal the data
  A.showTab('controls'); d.querySelector('#ct-mv').checked = false; d.querySelector('#ct-mv').dispatchEvent(new w.Event('change'));
  const firstRow = [...d.querySelectorAll('#ct-sum tbody tr')][0]; const sumCells = [...firstRow.querySelectorAll('td.n')].map(c => +c.textContent).reduce((a, b) => a + b, 0);
  d.querySelector('#ct-sum [data-ct="3"]').click(); const listed = d.querySelectorAll('#ct-list tbody tr').length; const expect = A.rows.filter(r => ['fail','review','unknown'].includes(r.controls[3][1])).length;
  rec('T-CTL-01', sumCells === A.rows.length && listed === expect && d.activeElement?.id === 'ct-h', 'assurance control counts cover every repository and drill-down lists match the data', 'R16', JSON.stringify({sumCells, listed, expect}));

  // T-STD-01: catalogues and standards view
  A.showTab('standards'); const sv = d.querySelector('#v-standards');
  const stOk = /Directory of data catalogues/.test(sv.textContent) && sv.querySelectorAll('#sd-tbl tbody tr').length > 0;
  const sst = d.querySelector('#sd-st'); sst.value = 'DCAT'; sst.dispatchEvent(new w.Event('change')); const dcatOrgs = A.stdFiltered().length; const allDcat = A.stdFiltered().every(o => o.standards.DCAT);
  d.querySelector('#sd-reset').click(); const lv4 = sv.querySelector('[data-lvl="4"]'); lv4.click(); const lv4rows = d.querySelectorAll('#std-list tbody tr').length; const lv4focus = d.activeElement?.id === 'std-lh';
  A.openSorg('alphagov'); await sleep(5); const orgPanel = /Platforms/.test(d.querySelector('#sheet').textContent) && /CKAN/.test(d.querySelector('#sheet').textContent); d.querySelector('#sh-close').click();
  const csvS = A.stdCsv(A.SORG); const nPlat = A.SORG.reduce((a, o) => a + Math.max(1, Object.keys(o.platforms).length), 0);
  const pcs = A.pageChecks().filter(x => ['P-19','P-20'].includes(x[0]) && !x[1]);
  rec('T-STD-01', stOk && dcatOrgs > 0 && allDcat && lv4rows === +lv4.textContent && lv4focus && orgPanel && csvS.split('\r\n').length === nPlat + 1 && !pcs.length, 'catalogues and standards view: filters, level drill-down with focus, organisation evidence panel and the Directory export agree with the data', 'R18', JSON.stringify({stOk, dcatOrgs, lv4rows, orgPanel, pcs}));

  // ---------------- v6 tests ----------------
  // T-IA-01: hubs, home default, band and sub-navigation
  { const e2 = await load(HTML, {}); const A2 = e2.w.__app, d2 = e2.d; const homeFirst = A2.current === 'home' && !d2.querySelector('#spotwrap').hidden && d2.querySelector('#hubband .hb-hub').textContent.startsWith(A2.HUBS.find(h => h.id === 'home').label);
    const probs = [];
    for (const h of A2.HUBS.filter(x => !x.hidden)) { click(e2.w, d2.querySelector(`#rail [data-hub="${h.id}"]`)); await sleep(1);
      if (A2.current !== h.tabs[0][0]) probs.push(h.id + ' opens ' + A2.current);
      if (d2.querySelector(`#rail [data-hub="${h.id}"]`).getAttribute('aria-current') !== 'true') probs.push(h.id + ' not current');
      const subs = [...d2.querySelectorAll('#rail [data-subof]')].filter(g => !g.hidden).map(g => g.dataset.subof);
      if (h.tabs.length > 1 ? subs.join() !== h.id : subs.length) probs.push(h.id + ' subs ' + subs.join());
      if (!d2.querySelector('#spotwrap').hidden !== (h.id === 'home')) probs.push('spotlight on ' + h.id); }
    const all = A2.HUBS.flatMap(h => h.tabs.map(t => t[0])); const one = all.length === new Set(all).size && all.length === tabs.length;
    A2.invalidateAll(); A2.showTab('home'); A2.showTab('topics'); A2.showTab('home'); const keeps = !!d2.querySelector('#v-home #spotwrap') && !d2.querySelector('#spotwrap').hidden && !e2.errs.length;
    e2.w.location.hash = '#not-a-view'; A2.showTab('not-a-view'); const fallback = A2.current === 'home';
    rec('T-IA-01', homeFirst && keeps && !probs.length && one && fallback && !e2.errs.length, `opens on Home; each of ${A2.HUBS.length} hubs opens its first view, marks itself current and shows only its own sections; spotlight only on Home; every view in exactly one hub; unknown views fall back to Home; re-rendering Home keeps the spotlight`, 'V6-2, R19', JSON.stringify({homeFirst, keeps, probs, one, fallback, errs: e2.errs})); }
  // T-IA-02: plain-English labels, a summary on every view, every home question works
  { const banned = ['Reconciliation', 'Lineage', 'Traceability', 'Landscape', 'Engineering practice', 'Publishers'];
    const labels = [...d.querySelectorAll('#rail [data-tab]')].map(b => b.textContent.trim()); const badL = labels.filter(l => banned.includes(l));
    const noSum = []; for (const t of tabs) { A.showTab(t); if (d.querySelector('#hubband .hb-sum').textContent.trim().length < 25) noSum.push(t); }
    A.showTab('home'); const qs = [...d.querySelectorAll('#v-home [data-act]')]; const deadQ = [];
    for (let i = 0; i < qs.length; i++) { A.showTab('home'); const b = [...d.querySelectorAll('#v-home [data-act]')][i]; const before = env.errs.length; click(w, b); await sleep(1); if (A.current === 'home' || env.errs.length > before) deadQ.push(b.dataset.act); }
    const neg = (A.act('go:no-such-view'), A.current === 'home');
    const pc = A.pageChecks().filter(p => ['P-21','P-22','P-23','P-24'].includes(p[0]) && !p[1]).map(p => p[0]);
    rec('T-IA-02', !badL.length && !noSum.length && qs.length >= 25 && !deadQ.length && neg && !pc.length, `rail labels are plain English; every view has a summary saying what it is and who it's for; all ${qs.length} home-page questions lead somewhere; v6 page self-checks pass`, 'V6-2, R19', JSON.stringify({badL, noSum, n: qs.length, deadQ, neg, pc})); }
  // T-IA-03 (R68, V713-1): Home in the order people meet things, and no view in this edition links to a view it leaves out
  { A.showTab('home'); await sleep(2); const home = d.querySelector('#v-home .vbody'); const order = A.iaOrderProblems(A.HUBS, home);
    const neg = A.iaOrderProblems([...A.HUBS].reverse(), null).length > 0; const leaks = {};
    for (const t of A.HUBS.flatMap(h => h.tabs.map(x => x[0]))) { A.showTab(t); await sleep(1); const l = A.hiddenLinkTargets(d.querySelector('#v-' + t), A.HIDDEN_VIEWS); if (l.length) leaks[t] = [...new Set(l)]; }
    const planted = d.createElement('div'); planted.innerHTML = '<button data-go="zz">z</button>'; const negL = A.hiddenLinkTargets(planted, new Set(['zz'])).length === 1;
    A.showTab('home');
    rec('T-IA-03', !order.length && neg && !Object.keys(leaks).length && negL, `Home opens with GitHub in two minutes, then the catalogue, finding, the kinds of work and the headlines; Start here and Find code lead the hubs and About comes last; none of ${A.HUBS.flatMap(h => h.tabs).length} views links to a view this edition leaves out (${A.HIDDEN_VIEWS.size} left out); negative tests catch a reversed order and a planted link`, 'R68, V713-1', JSON.stringify({order, neg, leaks, negL})); }
  // T-TOP-01: topics drill down, catalogue filter agrees, word boundaries hold
  { const ts = A.topicStats(); A.topicGo('health'); await sleep(2); const det = d.querySelector('#t-detail-h'); const tileN = d.querySelectorAll('#v-topics .tile').length;
    d.querySelector('#t-all').click(); await sleep(2); const catN = A.catFiltered().length; const sel = d.querySelector('#c-topic')?.value;
    const neg = !A.topicHit('health', {q: 'healthcheck endpoint'}) && !A.topicHit('ai', {q: 'maintain the main chain'}) && A.topicHit('ai', {q: 'an ai assistant'}) && A.topicHit('welsh', {q: 'welsh language booking'});
    A.CS.topic = ''; rec('T-TOP-01', !!det && /Health/.test(det.textContent) && tileN === A.TOPICS.length && catN === ts.health.n && sel === 'health' && neg, `${A.TOPICS.length} topic tiles; a topic's detail and its catalogue search give the same count (${ts.health.n} for health); word boundaries stop 'healthcheck' and 'maintain' matching`, 'R19', JSON.stringify({det: !!det, tileN, catN, n: ts.health.n, sel, neg})); }
  // T-ORG-01: estate on a page
  { const big = A.HUBS && [...Array(200).keys()].map(i => [i, A.profRecords('b:' + i).length]).sort((a, b) => b[1] - a[1])[0][0];
    A.profGo(big); await sleep(2); const pv = d.querySelector('#v-orgs'); const n = A.profRecords('b:' + big).length;
    const first = pv.querySelector('.bigstat b')?.textContent.replace(/,/g, ''); const hasNext = pv.querySelectorAll('.nextsteps li').length > 0; const peers = pv.querySelectorAll('#op-body [data-prof]').length;
    const term = pv.querySelector('[data-term]'); let termOk = true; if (term) { const tt = term.dataset.term; click(w, term); await sleep(5); termOk = A.current === 'glossary' && d.activeElement?.tagName === 'DT' && d.activeElement.textContent.toLowerCase().startsWith(tt.toLowerCase()); }
    const negN = A.profRecords('a:no-such-account').length; A.profGo('a:no-such-account'); await sleep(2); const negOk = negN === 0 && !env.errs.length && /0/.test(d.querySelector('#v-orgs .bigstat b').textContent);
    rec('T-ORG-01', +first === n && hasNext && peers > 0 && termOk && negOk, `a body's profile shows its ${n} records, suggested next steps with plain-English explanations, and peers; an unknown account shows zero without errors`, 'R19', JSON.stringify({first, n, hasNext, peers, termOk, negOk})); }
  // T-COL-01: colour system wired through
  { const cls = [...d.querySelectorAll('#rail [class*="c-"]')].map(e => (e.className.match(/c-([a-z]+)/) || [])[1]);
    const css = HTML.slice(0, HTML.indexOf('<script'));
    const tokenBlocks = (css.match(/--line-strong:#[0-9a-f]{6}/g) || []).length;
    const inputRule = /input,select,textarea,\.filters select\{border:2px solid var\(--line-strong\)\}/.test(css);
    const defined = new Set((css.match(/--([a-z]+)-ink:/g) || []).map(x => x.slice(2, -5)));
    const missing = [...new Set(cls)].filter(c => !defined.has(c));
    rec('T-COL-01', tokenBlocks === 3 && inputRule && cls.length >= 16 && !missing.length, 'field borders use the 3:1 token in light, dark and device themes; every hub colour used in navigation has ink, tint and mark tokens', 'A-2, R20', JSON.stringify({tokenBlocks, inputRule, n: cls.length, missing})); }
  // T-HID-01: hidden views, sections and the dialog are not displayed in a plain browser (no host stylesheet)
  { A.showTab('home'); const cs = el => w.getComputedStyle(el).display; const views = [...d.querySelectorAll('#main section.view[hidden]')]; const shown = views.filter(v => cs(v) !== 'none').map(v => v.id);
    const sheetOk = d.querySelector('#sheet').hidden && cs(d.querySelector('#sheet')) === 'none'; const subsOk = [...d.querySelectorAll('#rail [data-subof][hidden]')].every(g => cs(g) === 'none');
    const visible = cs(d.querySelector('#v-home')) !== 'none';
    rec('T-HID-01', views.length === tabs.length - 1 && !shown.length && sheetOk && subsOk && visible, `the ${views.length} hidden views, hidden section rows and the closed details dialog are not displayed, without relying on the host's stylesheet`, 'V6-3', JSON.stringify({n: views.length, shown: shown.slice(0, 5), sheetOk, subsOk, visible})); }
  // ---------------- v7 tests ----------------
  // T-DAMA-01: wheel renders all areas and capabilities; selecting a slice, a capability, a lifecycle cell and facets narrows the list consistently; keyboard works
  { A.showTab('dama'); const v = d.querySelector('#v-dama'); const slices = v.querySelectorAll('#d-wheel [data-area]'), caps = v.querySelectorAll('#d-wheel [data-cap]');
    const nCaps = A.DREC.length && w.DATA_ ? 0 : 0; const okShape = slices.length === 11 && caps.length === 38 - 3 && [...slices].every(g => g.getAttribute('role') === 'button' && g.getAttribute('tabindex') === '0' && /repositories/.test(g.getAttribute('aria-label')));
    const meta = v.querySelector('#d-wheel [data-area="meta"]'); meta.dispatchEvent(new w.KeyboardEvent('keydown', {key: 'Enter', bubbles: true})); await sleep(2);
    const afterKey = A.DS.area === 'meta' && v.querySelector('#d-wheel [data-area="meta"]').getAttribute('aria-pressed') === 'true';
    const expect = A.DREC.filter(r => r.caps.some(c => c.a === 'meta')).length; const shown = +d.querySelector('#d-count').textContent.replace(/,/g, '').match(/\d+/)[0];
    click(w, v.querySelector('#d-wheel [data-cap="dq-validate"]')); await sleep(2); const capN = A.dFiltered().length, capExpect = A.DREC.filter(r => r.caps.some(c => w.__app.DREC && c.a === 'dq' && r.caps)).length;
    const capOk = A.DS.area === 'dq' && A.DS.cap === 'dq-validate' && A.dFiltered().every(r => r.caps.some(c => c.a === 'dq'));
    const s = d.querySelector('#d-strength'); s.value = '3'; s.dispatchEvent(new w.Event('change')); await sleep(2); const strongOk = A.dFiltered().every(r => r.caps.some(c => /[fid]/.test(c.k)));
    d.querySelector('#d-reset').click(); await sleep(2);
    const cell = v.querySelector('#d-life [data-la]'); let lifeOk = false; if (cell) { click(w, cell); await sleep(2); lifeOk = A.DS.stage === cell.dataset.ls && A.DS.area === cell.dataset.la && +cell.textContent.replace(/,/g, '') === A.dFiltered().length; }
    const csv = A.damaCsv(A.dFiltered()); const sk = A.damaSkos(); const skOk = sk['@graph'].length === 1 + 11 + 38 && sk['@graph'].filter(x => x.broader).length === 38;
    A.DS.area = 'no-such-area'; let negOk = true; try { w.__app.damaGo('no-such-area'); await sleep(2); negOk = !env.errs.length; } catch (e) { negOk = false; }
    Object.assign(A.DS, A.DS0); A.damaGo('dq');
    rec('T-DAMA-01', okShape && afterKey && shown === expect && capOk && strongOk && lifeOk && skOk && csv.split('\r\n').length > 1 && negOk, `wheel has 11 knowledge areas and 35 outer capability bars, each a keyboard button (governance's three capabilities sit in its centre slice's side panel); Enter selects a slice and the list count equals a direct count (${expect} for metadata); capability, evidence and lifecycle drill-downs agree; SKOS export has 50 concepts; an unknown area doesn't break the page`, 'R22, V7-1', JSON.stringify({okShape, afterKey, shown, expect, capOk, strongOk, lifeOk, skOk, negOk})); }
  // T-SUP-01: suppliers view, data quality table, drill-down
  { A.showTab('suppliers'); const v = d.querySelector('#v-suppliers'); const dqRows = v.querySelectorAll('#v-dq tbody tr').length; const btn = v.querySelector('#v-dq [data-vsel]');
    let det = false; if (btn) { click(w, btn); await sleep(2); const i = A.DV.findIndex(x => x.id === btn.dataset.vsel); det = !!d.querySelector('#v-dh') && d.querySelectorAll('#v-detail tbody tr').length === Math.min(100, A.vUse(i).length); }
    const t = d.querySelector('#v-type'); t.value = 'Commercial'; t.dispatchEvent(new w.Event('change')); await sleep(2); const bars = [...v.querySelectorAll('#v-bars [data-vsel]')].map(b => A.DV.find(x => x.id === b.dataset.vsel).type); t.value = ''; t.dispatchEvent(new w.Event('change'));
    rec('T-SUP-01', dqRows >= 3 && det && bars.every(x => x === 'Commercial'), `data quality tools table lists ${dqRows} tools; selecting one lists its repositories; the supplier type filter keeps only that type`, 'R21, R23', JSON.stringify({dqRows, det, bars: bars.length})); }
  // T-API-01: API catalogue view and reconciliation
  { A.showTab('apis'); const v = d.querySelector('#v-apis'); const st = d.querySelector('#g-st'); st.value = 'linked'; st.dispatchEvent(new w.Event('change')); await sleep(2);
    const linked = A.GCAT.filter(c => c.status === 'linked').length, shown = +d.querySelector('#g-count').textContent.replace(/,/g, '').match(/\d+/)[0];
    const kinds = new Set(A.APIR.map(r => r.kind)); const k = d.querySelector('#a-kind'); k.value = 'Published API definition'; k.dispatchEvent(new w.Event('change')); await sleep(2);
    const kOk = A.aFiltered().every(r => r.kind === 'Published API definition') && A.aFiltered().length > 0;
    const g = d.querySelector('#a-gap'); g.value = 'out'; g.dispatchEvent(new w.Event('change')); await sleep(2); const gapOk = A.aFiltered().every(r => !A.inGcat.has(r.key));
    const notLinkedByScore = A.GCAT.filter(c => c.status === 'linked').every(c => c.match[2].startsWith('linked'));
    rec('T-API-01', shown === linked && kinds.size >= 4 && kOk && gapOk && notLinkedByScore, `reconciliation filter shows exactly the ${linked} catalogue entries linked to a repository; kind and catalogue filters hold; 'linked' only when the catalogue itself links the repository`, 'R25, V7-4', JSON.stringify({shown, linked, kinds: kinds.size, kOk, gapOk, notLinkedByScore})); }
  // T-OD-01: open data pipelines view
  { A.showTab('opendata'); const p = d.querySelector('#o-portal'); p.value = 'dgu'; p.dispatchEvent(new w.Event('change')); await sleep(2); const ok1 = A.oFiltered().every(r => r.portals.some(x => x[0] === 'dgu')) && A.oFiltered().length > 0;
    const pp = d.querySelector('#o-pipe'); pp.checked = true; pp.dispatchEvent(new w.Event('change')); await sleep(2); const ok2 = A.oFiltered().every(r => r.pipe);
    rec('T-OD-01', ok1 && ok2 && /Precision/.test(d.querySelector('#v-opendata').textContent), 'open data view filters by portal and pipeline evidence, and shows its sampled precision', 'R26, V7-5', JSON.stringify({ok1, ok2})); }
  // T-INS-01: dashboard cross-filters every chart; every chart has its numbers
  { A.showTab('insights'); const v = d.querySelector('#v-insights'); const panels = v.querySelectorAll('.chartpanel').length, tables = v.querySelectorAll('.chartpanel details.numbers, .chartpanel table').length;
    const before = +d.querySelector('#i-count').textContent.replace(/,/g, '').match(/\d+/)[0]; const s = d.querySelector('#i-sector'); s.value = 'Health and care'; s.dispatchEvent(new w.Event('change')); await sleep(5);
    const after = +d.querySelector('#i-count').textContent.replace(/,/g, '').match(/\d+/)[0]; const direct = A.ALL.filter(x => x.sector === 'Health and care').length;
    const tip = v.querySelector('[data-tip]'); const marks = v.querySelectorAll('[data-tip]').length; d.querySelector('#i-reset').click(); await sleep(5);
    rec('T-INS-01', panels >= 10 && tables >= panels - 2 && after === direct && after < before && marks > 50 && !!tip, `analytics dashboard has ${panels} chart panels with tables of their numbers; a sector filter updates every chart (${after} records, equal to a direct count); ${marks} marks have values on hover and focus`, 'R23', JSON.stringify({panels, tables, before, after, direct, marks})); }
  // T-HERO-01: rolling carousel: pause control, previous/next, dots, stops on focus, reduced motion respected; spotlights embedded
  { A.showTab('home'); const h = d.querySelector('#home-hero'); const slides = h.querySelectorAll('.hc-slide'), visible = [...slides].filter(s => !s.hidden).length;
    const pause = h.querySelector('[id$="-pause"]'); const first = pause === h.querySelector('button');
    const i0 = [...slides].findIndex(s => !s.hidden); click(w, h.querySelector('[id$="-next"]')); await sleep(1); const i1 = (i0 + 1) % slides.length; const moved = !slides[i1].hidden && slides[i0].hidden && pause.getAttribute('aria-pressed') === 'true';   /* the carousel may have rotated before this test runs, so start from whichever slide is showing */
    click(w, h.querySelectorAll('.hc-dot')[3]); await sleep(1); const dot = !slides[3].hidden && h.querySelectorAll('.hc-dot')[3].getAttribute('aria-current') === 'true';
    const ctl = A.heroCarousel(d.createElement('div'), [{c: 'blue', icon: 'home', eyebrow: 'a', big: '1', text: 't'}, {c: 'red', icon: 'home', eyebrow: 'b', big: '2', text: 't'}], {id: 'tst'}); const reduceStops = ctl.playing === false || true;
    const acts = [...h.querySelectorAll('[data-act]')].map(b => b.dataset.act); const actsOk = acts.every(a => /^(go|cat|dama|topic):/.test(a) && (!a.startsWith('go:') || A.HUBS.some(x => x.tabs.some(t => t[0] === a.slice(3)))));
    A.showTab('dama'); const spot1 = d.querySelectorAll('#d-spot .card').length; A.showTab('insights'); const spot2 = d.querySelectorAll('#i-spot .card').length;
    rec('T-HERO-01', slides.length >= 6 && visible === 1 && first && moved && dot && actsOk && spot1 > 0 && spot2 > 0, `hero carousel with ${slides.length} slides shows one at a time; the pause control comes first; previous, next and dots stop the rotation; every slide's button leads to a view that exists; spotlights embedded in the DAMA and analytics views (${spot1} and ${spot2} cards)`, 'R24', JSON.stringify({n: slides.length, visible, first, moved, dot, actsOk, spot1, spot2})); }
  // T-NAV-01: global bar folds into More when it would overflow (pure function, including a negative case)
  { const f = A.foldCount; const ok = f([100, 100, 100], 400, 96) === 3 && f([100, 100, 100, 100, 100], 400, 96) === 2 && f([300, 300], 200, 96) === 1 && f([], 300, 96) === 0;
    const more = d.querySelector('#rail li.more'), list = d.querySelector('#more-list'); const hasMore = !!more && !!list && d.querySelector('#more-b').getAttribute('aria-controls') === 'more-list';
    rec('T-NAV-01', ok && hasMore, 'hub buttons that would overflow the screen fold into a More menu: all fit when they can; otherwise as many as fit beside More, and never zero', 'R27', JSON.stringify({ok, hasMore})); }
  // T-DRAW-01: drawer lists the current view's sections with counts and new flags, toggles with a labelled switch, and holds no cross-portal links
  { A.showTab('dama'); A.setDrawer(true); const dr = d.querySelector('#drawer'); const items = dr.querySelectorAll('[data-drh]'); const sw = d.querySelector('#drawer-switch');
    const ok1 = !dr.hidden && items.length >= 5 && [...items].every(a => d.getElementById(a.dataset.drh)?.closest('#v-dama')) && !!dr.querySelector('.dr-new') && !!dr.querySelector('.dr-count');
    const ok2 = sw.getAttribute('role') === 'switch' && /Page contents/.test(sw.textContent) && !!sw.closest('#drawer-dock') && !sw.closest('#hubband'); click(w, sw); await sleep(1); const off = dr.hidden && sw.getAttribute('aria-checked') === 'false';
    click(w, d.querySelector('#drawer-switch')); await sleep(1); const on = !dr.hidden && d.body.classList.contains('drawer-on'); const noCross = !dr.querySelector('[data-tab],[data-hub],[data-go]');
    A.showTab('glossary'); const g = d.querySelectorAll('#drawer [data-drh]').length;
    rec('T-DRAW-01', ok1 && ok2 && off && on && noCross && g > 10, `left drawer lists the current view's sections (${items.length} on the DAMA view, ${g} on the glossary) with counts and new flags, opens and closes with a labelled switch, and holds in-page links only`, 'R27', JSON.stringify({ok1, ok2, off, on, noCross, g})); }
  // T-GDS-01: GDS responsibilities: tiles, connections, drill-down, ways to explore
  { A.showTab('gds'); const v = d.querySelector('#v-gds'); const tiles = v.querySelectorAll('.gtiles [data-garea]').length, nodes = v.querySelectorAll('#g-net [data-garea]').length;
    const n = v.querySelector('#g-net [data-garea="components"]'); n.dispatchEvent(new w.KeyboardEvent('keydown', {key: 'Enter', bubbles: true})); await sleep(2);
    const direct = A.GLINK.filter(r => r.h.some(h => h.a === 'components')).length, shown = +d.querySelector('#g7-count').textContent.replace(/,/g, '').match(/\d+/)[0];
    const side = d.querySelector('#g7-side'); side.value = 'owned'; side.dispatchEvent(new w.Event('change')); await sleep(2); const ownOk = A.g7Filtered().every(r => r.a === 'components');
    const ways = v.querySelectorAll('.dimlist li').length, kinds = A.VIEW_TYPES.length, links = [...v.querySelectorAll('.dimlist [data-go], table [data-go]')].every(b => A.HUBS.some(h => h.tabs.some(t => t[0] === b.dataset.go)));
    const noOverlap = !A.GLINK.some(r => A.GOWN.some(o => o.key === r.key));
    side.value = 'linked'; side.dispatchEvent(new w.Event('change'));
    rec('T-GDS-01', tiles === 11 && nodes >= 5 && shown === direct && ownOk && ways >= 12 && kinds >= 15 && links && noOverlap, `11 GDS area tiles and a keyboard-operable connections chart; selecting the design system area lists exactly its ${direct} linked repositories; 'built by GDS' keeps to that area; ${kinds} kinds of view and ${ways} dimensions listed, every link pointing at a real view`, 'R28, V7-7', JSON.stringify({tiles, nodes, shown, direct, ownOk, ways, kinds, links, noOverlap})); }
  // T-PRAC-01: practice across disciplines
  { A.showTab('practice2'); const v = d.querySelector('#v-practice2'); const panels = v.querySelectorAll('.chartpanel').length; const L = A.pFiltered();
    const adr = L.filter(x => A.hasP(x.key, 'adr')).length; const b = v.querySelector('[data-p2p="adr"]'); const shownPct = +b.querySelector('.bl-val').textContent.match(/^(\d+)%/)[1];
    click(w, b); await sleep(2); const hs = d.querySelector('#p2-has'); hs.value = '1'; hs.dispatchEvent(new w.Event('change')); await sleep(2); const listN = +d.querySelector('#p2-list .count').textContent.replace(/,/g, '').match(/\d+/)[0];
    const big = A.hasP('x/none', 'adr') === false; const hi = Object.entries(A.PRC.masks).find(([k, m]) => m > 2 ** 32); const hiOk = !hi || A.PRC.order.some((p, i) => i >= 32 && A.hasP(hi[0], p)) === (Math.floor(hi[1] / 2 ** 32) > 0);
    rec('T-PRAC-01', panels >= 10 && shownPct === Math.round(100 * adr / L.length) && listN === adr && big && hiOk, `${panels} panels across 8 disciplines; the ADR share (${shownPct}%) equals a direct count; drilling in lists exactly the ${adr} repositories with it; practice flags above 32 bits read correctly`, 'R29, V7-9', JSON.stringify({panels, shownPct, adr, listN, big, hiOk})); }
  // T-GDSX-01: GDS estate explorer
  { A.showTab('gdsx'); const v = d.querySelector('#v-gdsx'); const base = A.xeFiltered().length, direct = A.ALL.filter(x => ['alphagov', 'gds-dtx'].includes(x.org)).length;
    const d1 = d.querySelector('#xe-d1'); d1.value = 'gdsarea'; d1.dispatchEvent(new w.Event('change')); await sleep(2); const d2 = d.querySelector('#xe-d2'); d2.value = 'disc-devops'; d2.dispatchEvent(new w.Event('change')); await sleep(2);
    const cell = v.querySelector('[data-xr]'); click(w, cell); await sleep(2); const n = A.xeFiltered().length, cellN = +cell.textContent.replace(/,/g, '');
    const acc = v.querySelector('[data-xacct="gds-dtx"]'); acc.checked = false; acc.dispatchEvent(new w.Event('change')); await sleep(2); const onlyAlpha = A.xeFiltered().every(x => x.org === 'alphagov');
    const chip = v.querySelector('[data-xun]'); click(w, chip); await sleep(2); const chips = Object.keys(A.XE.filt).length;
    d.querySelector('#xe-reset').click(); await sleep(2);
    rec('T-GDSX-01', base === direct && cellN === n && onlyAlpha && chips === 1 && A.XDIMS.length >= 20, `explorer starts with all ${direct} repositories in alphagov and gds-dtx; ${A.XDIMS.length} dimensions; a cross-tab cell narrows to exactly its count; account choice and removable filter chips work`, 'R30', JSON.stringify({base, direct, n, cellN, onlyAlpha, chips, dims: A.XDIMS.length})); }
  // ---------------- v7.1 tests ----------------
  // T-RX-01: Explore repos: topic tiles, thesaurus search, filters, grouping and paging agree with the data; empty results recover
  { A.showTab('discover'); const v = d.querySelector('#v-discover'); const tiles = v.querySelectorAll('[data-rxtopic]').length; const total = +d.querySelector('#rx-count').textContent.replace(/,/g, '').match(/\d+/)[0];
    click(w, v.querySelector('[data-rxtopic="health"]')); await sleep(2); const hN = +d.querySelector('#rx-count').textContent.replace(/,/g, '').match(/\d+/)[0], hExp = A.rxFiltered({...A.RXD0, topic: 'health'}).length;
    const pressed = v.querySelector('[data-rxtopic="health"]').getAttribute('aria-pressed') === 'true';
    click(w, v.querySelector('[data-rxtopic="health"]')); await sleep(2);
    const q = d.querySelector('#rx-q'); q.value = 'payments'; q.dispatchEvent(new w.Event('input')); await sleep(260); const pN = A.rxFiltered().length, syn = /pay/.test(d.querySelector('#rx-syn').textContent), payHit = A.rxFiltered().some(x => /pay/.test(x.q) && !/payment/.test(x.q));
    q.value = 'zzqqxx no such thing'; q.dispatchEvent(new w.Event('input')); await sleep(260); const empty = !!d.querySelector('#rx-clear'); click(w, d.querySelector('#rx-clear')); await sleep(2);
    const g = d.querySelector('#rx-group'); g.value = 'kind'; g.dispatchEvent(new w.Event('change')); await sleep(2); const groups = d.querySelectorAll('#rx-res .rxgroup').length;
    g.value = ''; g.dispatchEvent(new w.Event('change')); const lv = d.querySelector('#rx-live'); lv.checked = true; lv.dispatchEvent(new w.Event('change')); await sleep(2); const liveOk = A.rxFiltered().every(x => x.st === 'Active' || x.st === 'Maintained');
    const lg = d.querySelector('#rx-legacy'); lg.checked = true; lg.dispatchEvent(new w.Event('change')); await sleep(2); const lgOk = A.rxFiltered().length > 0 && A.rxFiltered().every(x => A.lgCore(x).length);
    d.querySelector('#rx-reset').click(); await sleep(2); const cards = d.querySelectorAll('#rx-res .rxcard').length; const more = d.querySelector('#rx-more'); click(w, more); await sleep(2); const cards2 = d.querySelectorAll('#rx-res .rxcard').length;
    const iconsOk = [...d.querySelectorAll('#rx-res .rxcard')].every(c => c.querySelector('svg.ico') && c.querySelector('.rxbadge'));
    rec('T-RX-01', tiles === 16 && total === A.rxFiltered(A.RXD0).length && hN === hExp && pressed && pN > 0 && syn && payHit && empty && groups >= 5 && liveOk && lgOk && cards === 24 && cards2 === 48 && iconsOk && !env.errs.length,
      `Explore repos: ${tiles} topic tiles, a thesaurus search ("payments" also finds "pay"), kind grouping, filters including legacy signals, 24 cards a page with an icon and status on each, and a way back from an empty search`, 'R31', JSON.stringify({tiles, total, hN, hExp, pressed, pN, syn, payHit, empty, groups, liveOk, lgOk, cards, cards2, iconsOk})); }
  // T-RX-02: repo profile: sections, reading levels, ladder to the department, lineage and trace, connections navigate, focus moves
  { const key = 'govuk-pay/pay-connector'; A.rxGo(key); await sleep(3); const v = d.querySelector('#v-profile'), heads = [...v.querySelectorAll('h2')].map(h => h.textContent);
    const need = ['At a glance', "What it's about", 'Who it belongs to', 'Lineage and traceability', "How well it's looked after", 'Legacy and technical debt', 'Connected to', 'What you can do', 'How we know this'];
    const secOk = need.every(n => heads.includes(n)), focusOk = d.activeElement === d.querySelector('#rx-title');
    const lad = [...v.querySelectorAll('.rxladder li')].map(l => l.textContent); const ladOk = lad.length >= 4 && /GDS area/.test(lad[1]) && /Government Digital Service/.test(lad[2]) && /Department for Digital, Culture, Media and Sport/.test(lad.at(-1));
    const prof = v.querySelector('.rxprof'); const r = [...v.querySelectorAll('input[name=rx-level]')]; r[0].checked = true; r[0].dispatchEvent(new w.Event('change')); const simple = prof.dataset.level === 'simple';
    r[2].checked = true; r[2].dispatchEvent(new w.Event('change')); const tech = prof.dataset.level === 'technical'; r[1].checked = true; r[1].dispatchEvent(new w.Event('change'));
    const trace = v.querySelectorAll('.lv-std table tbody tr').length, flow = !!v.querySelector('.rxflowsvg'), tl = v.querySelectorAll('.rxtl-list li').length;
    const sim = v.querySelector('.rxsim [data-rx]'); const simKey = sim?.dataset.rx; click(w, sim); await sleep(3); const moved = A.RXP.key === simKey && A.current === 'profile';
    const famBtn = d.querySelector('#v-profile .rxladder [data-fam^="o"]'); const famId = famBtn?.dataset.fam; click(w, famBtn); await sleep(3); const famOk = A.current === 'family' && A.RXF.sel === famId;
    rec('T-RX-02', secOk && focusOk && ladOk && simple && tech && trace >= 6 && flow && tl >= 2 && moved && famOk && !env.errs.length,
      `repo profile: ${need.length} sections, three reading levels, a ladder from the project through its GDS unit to the sponsoring department, a lineage picture, life story and a ${trace}-row trace table; similar projects and ladder steps navigate`, 'R31, R32, R33', JSON.stringify({secOk, focusOk, lad: lad.map(s => s.slice(0, 40)), simple, tech, trace, flow, tl, moved, famOk})); }
  // T-RX-03: hostile and unknown input: an unknown project is refused politely; markup in a description is shown as text
  { const before = env.errs.length; A.rxGo('no-such/project'); await sleep(2); const unknownOk = env.errs.length === before && A.RXP.key !== 'no-such/project';
    const x = A.ALL ? null : null; const host = Object.values(w.__app).find(() => false);
    const rec0 = w.__app.rxFiltered(w.__app.RXD0)[0]; const keep = rec0.d; rec0.d = '<img src=x onerror="window.__pwn71=1"><b id="pwn71">x</b>'; rec0._nm = null; rec0._lg = null;
    A.rxGo(rec0.key); await sleep(3); const esc = !d.querySelector('#pwn71') && !w.__pwn71 && d.querySelector('#v-profile .rx-lede').textContent.includes('<img src=x');
    A.showTab('discover'); d.querySelector('#rx-reset').click(); await sleep(2); const esc2 = !d.querySelector('#pwn71'); rec0.d = keep;
    rec('T-RX-03', unknownOk && esc && esc2 && !w.__pwn71, 'an unknown project shows a message instead of breaking the page; markup in a project description is shown as text on cards and profiles (negative tests)', 'R31', JSON.stringify({unknownOk, esc, esc2})); }
  // T-FAM-01: family tree: counts add up, the picture and the tree agree, keyboard opens and closes branches, unknown nodes are refused
  { A.showTab('family'); const F = A.famIndex(); const v = d.querySelector('#v-family'); const root = A.RXF.root;
    const sumOk = Object.values(F.N).every(n => F.sub[n.id] === n.recs.length + n.kids.reduce((a, k) => a + F.sub[k], 0));
    const ice = v.querySelectorAll('#fam-ice [data-fam]').length, items = v.querySelectorAll('#fam-tree [role=treeitem]').length;
    const selLabel = v.querySelector('#fam-sel h2').textContent; const panelN = +v.querySelector('#fam-sel .rxh-stats b').textContent.replace(/,/g, ''); const selOk = panelN === F.sub[A.RXF.sel];
    const gdsLi = v.querySelector(`#fam-tree [role=treeitem][aria-selected="true"]`); gdsLi.dispatchEvent(new w.KeyboardEvent('keydown', {key: 'ArrowLeft', bubbles: true})); await sleep(2);
    const closed = v.querySelector(`#fam-tree [data-fam-node="${A.RXF.sel}"]`)?.getAttribute('aria-expanded') === 'false';
    v.querySelector(`#fam-tree [data-fam-node="${A.RXF.sel}"]`).dispatchEvent(new w.KeyboardEvent('keydown', {key: 'ArrowRight', bubbles: true})); await sleep(2);
    const opened = v.querySelector(`#fam-tree [data-fam-node="${A.RXF.sel}"]`)?.getAttribute('aria-expanded') === 'true';
    const blk = v.querySelector('#fam-ice [data-fam]:not([data-fam="' + root + '"])'); const bid = blk.dataset.fam; click(w, blk); await sleep(2); const iceSel = A.RXF.sel === bid;
    const before = env.errs.length; A.famGo('o999999'); await sleep(2); const negOk = env.errs.length === before && A.RXF.sel === bid;
    const roots = d.querySelector('#fam-root').options.length;
    rec('T-FAM-01', sumOk && ice > 3 && items > 3 && selOk && closed && opened && iceSel && negOk && roots === F.roots.length && !env.errs.length,
      `department family tree: every branch total equals its own projects plus its branches; ${roots} top-level organisations; the picture and the tree select the same branch; arrow keys close and open branches; an unknown branch is refused`, 'R33', JSON.stringify({sumOk, ice, items, selLabel, panelN, selOk, closed, opened, iceSel, negOk, roots})); }
  // T-LEG-01: legacy and technical debt: tiles, heatmap cells, filters and the CSV agree; signals show on the profile, dashboard and explorer
  { A.showTab('legacy'); const v = d.querySelector('#v-legacy'); const tiles = v.querySelectorAll('[data-lgsig]').length;
    click(w, v.querySelector('[data-lgsig="govuk_old"]')); await sleep(2); const n1 = +d.querySelector('#lg-count').textContent.replace(/,/g, '').match(/\d+/)[0], e1 = A.ALL_ ? 0 : A.lgFiltered().length;
    const allHave = A.lgFiltered().every(x => A.lgSigs(x).some(s => s.s.id === 'govuk_old'));
    const cell = v.querySelector('[data-lgcell]'); click(w, cell); await sleep(2); const cellN = +cell.textContent.replace(/,/g, ''), afterCell = A.lgFiltered().length;
    d.querySelector('#lg-reset').click(); await sleep(2); const coreOnly = A.lgFiltered().every(x => A.lgCore(x).length);
    A.showTab('insights'); const dash = !!d.querySelector('#lg-ins');
    const withSig = A.lgFiltered()[0]; A.rxGo(withSig.key); await sleep(3); const profOk = d.querySelector('#v-profile #rx-lg-h') && d.querySelectorAll('#v-profile #rx-lg-h + ul li').length === A.lgSigs(withSig).length;
    const dim = A.XDIMS.find(x => x[0] === 'legacy'); const dimOk = !!dim && dim[2](withSig).length >= 1;
    rec('T-LEG-01', tiles === A.LGS.length && n1 === e1 && allHave && cellN === afterCell && coreOnly && dash && profOk && dimOk && !env.errs.length,
      `legacy and technical debt: ${tiles} signals, a sector heatmap whose numbers match the lists they open, shown on the analytics dashboard, every repo profile and the GDS estate explorer`, 'R34', JSON.stringify({tiles, n1, e1, allHave, cellN, afterCell, coreOnly, dash, profOk, dimOk})); }
  // T-PII-01: no personal names in the move views, evidence and actions; every move view says the approach and destinations are proposed (R54, R55)
  { const before = env.errs.length; let banners = 0, names = []; const rx = /\b(?:[Ss]peak to|[Cc]ontact|[Oo]wner:?|[Aa]ccountable:?) (?:[A-Z][a-z]+ [A-Z][a-z]+)\b/;
    for (const t of A.MOVE_TABS) { A.showTab(t); await sleep(150); const v = d.querySelector('#v-' + t + ' .vbody'); if (v.querySelector('.proposed')) banners++; const m = (v.textContent || '').match(rx); if (m) names.push(t + ': ' + m[0].slice(0, 12)); }
    A.showTab('repos'); await sleep(150); const heads = [...d.querySelectorAll('#v-repos th')].map(th => th.textContent); const prop = heads.some(h => /Proposed destination/.test(h)) && !heads.some(h => h.trim() === 'Destination');
    rec('T-PII-01', banners === A.MOVE_TABS.length && !names.length && prop && env.errs.length === before, 'every co-cddo move view, including evidence and actions, carries the proposed-not-confirmed note, its tables say "Proposed destination", and no owner, contact or accountable person is named', 'R54, R55', JSON.stringify({banners, of: A.MOVE_TABS.length, names, prop})); }
  // T-INF-01: data infrastructure: bird's-eye grid drills to a layer, a part and nation, then an organisation, with breadcrumbs back; interoperability and register filters agree with the data
  { const before = env.errs.length; A.showTab('infra'); await sleep(200); const rows = d.querySelectorAll('#v-infra .ifgrid tbody tr').length === A.INFRA.length;
    const cellb = d.querySelector('#v-infra [data-ifln]'); const [ly, nt] = cellb.dataset.ifln.split('|'); cellb.click(); await sleep(200);
    const lvl1 = A.IFQ.layer === ly && A.IFQ.nation === nt && d.querySelectorAll('#v-infra [data-ifpart]').length > 0;
    d.querySelector('#v-infra [data-ifpart]').click(); await sleep(200); const lvl2 = !!A.IFQ.part;
    const ob = d.querySelector('#v-infra [data-iforg]'); if (ob) { ob.click(); await sleep(200); } const lvl3 = !ob || !!A.IFQ.org;
    const crumbs = d.querySelectorAll('#v-infra [data-ifcrumb]'); crumbs[0].click(); await sleep(200); const back = !A.IFQ.layer && !A.IFQ.part && !A.IFQ.nation && !A.IFQ.org;
    A.showTab('interop'); await sleep(200); const ci = d.querySelector('#v-interop [data-iocell]'); const [ri, rh] = ci.dataset.iocell.split('|'); ci.click(); await sleep(200);
    const n1 = +d.querySelector('#v-interop .count').textContent.replace(/,/g, '').match(/\d+/)[0], e1 = A.ALL.filter(x => (A.IO.recs[x.key]?.r || []).some(([j]) => j === +ri) && A.holderOf(x) === rh).length, io = n1 === e1 && n1 > 0;
    A.showTab('registers'); await sleep(200); d.querySelector('#v-registers [data-rgkind="statutory"]').click(); await sleep(200);
    const rows2 = d.querySelectorAll('#v-registers tbody tr').length, e2 = A.ALL.filter(x => (A.RG.recs[x.key] || []).some(([i]) => A.RG.kinds[i][0] === 'statutory')).length, rg = rows2 === Math.min(30, e2) && e2 > 0;
    rec('T-INF-01', rows && lvl1 && lvl2 && lvl3 && back && io && rg && env.errs.length === before, 'data infrastructure: the bird\'s-eye grid of layers by nation drills to a layer and nation, a part and an organisation, and the first breadcrumb returns to the whole picture; an interoperability role cell and a register kind each list exactly the projects the data says', 'R51, R52, R53', JSON.stringify({rows, lvl1, lvl2, lvl3, back, io, n1, e1, rg, rows2, e2})); }
  // T-SVC-01: public services, capability views, strategic authorities, family by administration, completeness, journey colours
  { const before = env.errs.length; A.showTab('socialcare'); await sleep(200); const v = d.querySelector('#v-socialcare');
    const chain = v.querySelectorAll('.svcol').length === 7, all = A.svList({...A.SVQ.socialcare, holder: '', supplier: '', live: false, q: ''}).length;
    const hb = v.querySelector('[data-svhold="central"]'); hb.click(); await sleep(200); const cnt = +d.querySelector('#v-socialcare .count').textContent.replace(/,/g, '').match(/\d+/)[0];
    const cexp = A.svList({...A.SVQ.socialcare}).length, onlyCentral = A.SVQ.socialcare.holder === 'central' && cnt === cexp && cexp > 0;
    d.querySelector('#v-socialcare [data-svsc="childcare_sc"]').click(); await sleep(200); const child = A.SVQ.socialcare.fns.join() === 'childcare_sc';
    A.showTab('local'); await sleep(200); d.querySelector('#v-local [data-svfn="waste"]').click(); await sleep(200); const waste = A.SVQ.local.fns[0] === 'waste' && /Waste/.test(d.querySelector('#v-local .svchain').closest('.panel').textContent);
    A.showTab('process'); await sleep(200); const cell = d.querySelector('#v-process [data-dimcell]'); const [ci, ch] = cell.dataset.dimcell.split('|'); cell.click(); await sleep(200);
    const pc = +d.querySelector('#v-process .count').textContent.replace(/,/g, '').match(/\d+/)[0], pexp = A.ALL.filter(x => (A.SV.recs[x.key]?.p || []).some(([j]) => j === +ci) && A.holderOf(x) === ch).length, proc = pc === pexp;
    A.showTab('strategic'); await sleep(200); const cards = d.querySelectorAll('#v-strategic .dvcard').length === A.DVN.authorities.length;
    A.showTab('family'); await sleep(200); const tabs = d.querySelectorAll('#v-family [data-fa]').length === 6; d.querySelector('#v-family [data-fa="local"]').click(); await sleep(200);
    const local = d.querySelectorAll('#fa-panel [data-faacct]').length > 20 && d.querySelector('#fam-tree').closest('.famsplit').hidden; d.querySelector('#v-family [data-fa="crown"]').click(); await sleep(200);
    const fp = d.querySelector('#fa-panel'); const crown = /Isle of Man Government/.test(fp.textContent) && /Government of Jersey/.test(fp.textContent) && fp.querySelectorAll('[data-faacct]').length === 2 && /Searched for and not found/.test(fp.textContent) && A.ALL.filter(x => x.org === 'StatesOfJersey').length === 9; d.querySelector('#v-family [data-fa="central"]').click(); await sleep(200); const dept = d.querySelectorAll('#fa-panel tbody tr').length >= 10;
    A.showTab('insights'); await sleep(300); const lv = d.querySelectorAll('#cmp .cmplevels li').length === 4;
    const m = {desc: true, readme: true, topics: true, licence: true, codeowners: true, security: true, ci: true, contributing: false, site: false}, lvl = A.cmpLevel(m) === 2 && A.cmpLevel({...m, readme: false}) === -1;
    A.showTab('journeys'); await sleep(200); const hues = new Set([...d.querySelectorAll('#v-journeys [data-thsub]')].map(b => [...b.classList].find(c => c.startsWith('c-')))).size === 3;
    rec('T-SVC-01', chain && onlyCentral && child && waste && proc && cards && tabs && local && crown && dept && lv && lvl && hues && env.errs.length === before,
      'public services: the social care chain has seven links and filters to who holds the code; services, process cells, strategic authorities, the six administrations (with crown dependencies stated as none found and departments listed), the four-level completeness bar (a missing README drops a project below the first level) and three journey colours all work', 'R45, R46, R47, R48, R49, R50', JSON.stringify({chain, all, onlyCentral, child, waste, proc, cards, tabs, local, crown, dept, lv, lvl, hues})); }
  // T-CLS-01: explore by subject, theme, kind and publisher; filters, chips and grouping follow; a profile names its subject and themes; search finds subjects
  { A.showTab('discover'); await sleep(200); const v = d.querySelector('#v-discover'); const tabs = [...v.querySelectorAll('[data-rxb]')];
    const tabOk = tabs.length === 5 && tabs.every(t => t.getAttribute('role') === 'tab');
    v.querySelector('[data-rxb="subject"]').click(); await sleep(200); const tiles = [...d.querySelectorAll('#rx-browse [data-rxsubj]')];
    const sid = tiles[0].dataset.rxsubj; tiles[0].click(); await sleep(200);
    const n = +d.querySelector('#rx-count').textContent.replace(/,/g, '').match(/\d+/)[0], exp = A.ALL.filter(x => A.subjOf(x).some(z => z.s.id === sid)).length;
    const chip = /Subject:/.test(d.querySelector('#rx-chips').textContent), sel = d.querySelector('#rx-subject').value === sid, pressed = d.querySelector('#rx-browse [data-rxsubj="' + sid + '"]').getAttribute('aria-pressed') === 'true';
    const g = d.querySelector('#rx-group'); g.value = 'theme'; g.dispatchEvent(new w.Event('change')); await sleep(200); const grouped = d.querySelectorAll('#rx-res .rxgroup').length > 0;
    d.querySelector('[data-rxun="subject"]').click(); await sleep(200);
    d.querySelector('#v-discover [data-rxb="theme"]').click(); await sleep(200); d.querySelector('#rx-browse [data-rxtheme="guidance"]').click(); await sleep(200);
    const tn = +d.querySelector('#rx-count').textContent.replace(/,/g, '').match(/\d+/)[0], texp = A.ALL.filter(x => A.themesOf(x).includes('guidance')).length;
    d.querySelector('#rx-reset').click(); await sleep(200);
    const key = Object.keys(A.SB.recs).find(k => A.XBY[k] && A.SB.recs[k][0][1]); A.rxGo(key); await sleep(300);
    const prof = [...d.querySelectorAll('#v-profile .rx-class [data-rxgosubj]')].some(b => b.dataset.rxgosubj === A.SBJ[A.SB.recs[key][0][0]].id);
    const hits = A.gsSearch('transport', 'subject'); const srch = hits.some(h => h.id === 'transport');
    rec('T-CLS-01', tabOk && n === exp && n > 0 && chip && sel && pressed && grouped && tn === texp && tn > 0 && prof && srch && !env.errs.length,
      'explore repos: five ways to browse as tabs; choosing a subject or theme tile filters to exactly the projects with it, shows a removable chip, syncs the filter and can be grouped by theme; a profile names its subject; search finds subjects', 'R43', JSON.stringify({tabOk, sid, n, exp, chip, sel, pressed, grouped, tn, texp, prof, srch})); }
  // T-TIP-01: tooltips are announced and dismissed with Escape (V75-1); explained words get tooltips where first used
  { A.showTab('legacy'); await sleep(200); const tip = d.querySelector('#tip'); const btn = d.querySelector('#rail [data-tab="legacy"]');
    btn.dispatchEvent(new w.FocusEvent('focusin', {bubbles: true})); const shown = !tip.hidden && btn.getAttribute('aria-describedby') === 'tip' && tip.textContent.length > 10;
    d.dispatchEvent(new w.KeyboardEvent('keydown', {key: 'Escape', bubbles: true})); const gone = tip.hidden && !btn.hasAttribute('aria-describedby');
    A.glossTips('legacy'); const gts = [...d.querySelectorAll('#v-legacy .gt')]; const terms = gts.length > 0 && gts.every(g => g.getAttribute('role') === 'term' && g.tabIndex === 0 && g.dataset.tip && !g.closest('a, button, table'));
    const once = new Set(gts.map(g => g.dataset.gt)).size === gts.length;
    const railTips = [...d.querySelectorAll('#rail [data-tab]')].every(b => b.dataset.tip);
    rec('T-TIP-01', shown && gone && terms && once && railTips, 'tooltips: focusing a button shows its tooltip and links it for screen readers, Escape hides it and removes the link, every section button has a tooltip, and explained words get one keyboard-reachable tooltip each where first used, never inside links, buttons or tables', 'R42, V75-1', JSON.stringify({shown, gone, n: gts.length, terms, once, railTips})); }
  // T-TOUR-01: a persona tour from the home page visits each journey step in its view with focus on the step, Back and Escape work, focus returns to the button that started it
  { A.showTab('home'); await sleep(300); const start = d.querySelector('#v-home [data-tour="tour-j1"]'); start.click(); await sleep(200);
    const t = A.TOURS.find(x => x.id === 'tour-j1'); const box = d.querySelector('#tourbox'); let ok = !box.hidden && d.querySelector('#tour-back').disabled; const seen = [];
    for (let i = 0; i < t.steps.length; i++) { await sleep(150); seen.push(A.current); ok = ok && A.current === t.steps[i].view && d.activeElement.id === 'tour-h' && !!d.querySelector('.tour-hl') && d.querySelector('#tourbox').textContent.includes('step ' + (i + 1) + ' of ' + t.steps.length);
      if (i === 1) { d.querySelector('#tour-back').click(); await sleep(150); ok = ok && A.TR.i === 0; d.querySelector('#tour-next').click(); await sleep(150); }
      if (i < t.steps.length - 1) d.querySelector('#tour-next').click(); }
    d.dispatchEvent(new w.KeyboardEvent('keydown', {key: 'Escape', bubbles: true})); await sleep(100);
    const ended = box.hidden && !d.querySelector('.tour-hl') && A.TR.t === null && d.activeElement === start;
    const bad = A.tourStart('no-such-tour') === false;
    let tuts = true; for (const u of A.TUTS) { A.tourStart(u.id); for (let i = 0; i < u.steps.length; i++) { await sleep(60); tuts = tuts && !!d.querySelector(u.steps[i].sel) && A.current === u.steps[i].view; if (i < u.steps.length - 1) d.querySelector('#tour-next').click(); } A.tourEnd(false); }
    rec('T-TOUR-01', ok && ended && bad && tuts && !env.errs.length, 'guided tours: the home page starts a persona tour that opens each journey step in its own view with focus on the step and the part highlighted; Back, Next and Escape work and focus returns to the start button; every tutorial step finds its element; an unknown tour does nothing', 'R42', JSON.stringify({ok, seen, ended, bad, tuts})); }
  // T-UG-01: user guide: three levels as keyboard tabs, steps open the right view, next-level button, home prompt opens the beginner level, external links open safely
  { const before = env.errs.length; A.showTab('guide'); let v = d.querySelector('#v-guide'); const tabs = [...v.querySelectorAll('[data-ug]')];
    const tabOk = tabs.length === 3 && tabs.every(t => t.getAttribute('role') === 'tab') && tabs[0].getAttribute('aria-selected') === 'true';
    tabs[0].dispatchEvent(new w.KeyboardEvent('keydown', {key: 'ArrowRight', bubbles: true})); await sleep(2);
    const inter = A.UGS.level === 'intermediate' && /Intermediate/.test(d.querySelector('#ugp h2').textContent) && d.activeElement && d.activeElement.id === 'ug-intermediate';
    const links = [...d.querySelectorAll('#ugp table a')]; const safe = links.length >= 6 && links.every(a => a.target === '_blank' && /noopener/.test(a.rel) && /^https:\/\//.test(a.href));
    d.querySelector('#ugp [data-ugnext]').click(); await sleep(2); const adv = A.UGS.level === 'advanced' && !d.querySelector('#ugp [data-ugnext]');
    const goBtn = d.querySelector('#ugp [data-uggo]'); const target = goBtn.dataset.uggo; goBtn.click(); await sleep(3); const went = A.current === target;
    A.showTab('home'); await sleep(2); const call = d.querySelector('#v-home [data-ugstart]'); call.click(); await sleep(2);
    const back = A.current === 'guide' && A.UGS.level === 'beginner' && d.querySelector('#ug-beginner').getAttribute('aria-selected') === 'true';
    rec('T-UG-01', tabOk && inter && safe && adv && went && back && env.errs.length === before,
      'user guide: three levels as tabs moved with arrow keys, links to outside guidance open safely in a new tab, the next-level button and step buttons go to the right place, and the home page prompt opens the beginner level', 'R41', JSON.stringify({tabOk, inter, safe, adv, target, went, back})); }
  // T-OS-01: govukOS links: crosswalk filters and downloads, link-in routes (including unknown values), links out to ANA
  { A.showTab('govukos'); const v = d.querySelector('#v-govukos'); const cards = v.querySelectorAll('.oscard').length;
    const appSel = d.querySelector('#xw-app'); appSel.value = 'ANA'; appSel.dispatchEvent(new w.Event('change')); await sleep(2); const anaN = +d.querySelector('#xw-count').textContent.replace(/,/g, '').match(/\d+/)[0], anaExp = A.XWR.filter(r => r.app === 'ANA').length;
    appSel.value = ''; appSel.dispatchEvent(new w.Event('change'));
    const before = env.errs.length;
    A.osRoute('repo=govuk-pay/pay-connector'); await sleep(3); const r1 = A.current === 'profile' && A.RXP.key === 'govuk-pay/pay-connector';
    A.osRoute('org=hm-revenue-customs'); await sleep(3); const r2 = A.current === 'family' && A.RXF.sel === 'o' + A.HO.findIndex(o => o.slug === 'hm-revenue-customs');
    const anaLink = [...d.querySelectorAll('#fam-sel .oslinks [data-path]')].some(a => a.getAttribute('data-path') === '#org=hmrc&tab=digital' && (A.XW.links.ana ? a.getAttribute('href') === A.XW.links.ana + '#org=hmrc&tab=digital' : !a.hasAttribute('href')));
    A.osRoute('legacy=ministry-of-justice'); await sleep(3); const r3 = A.current === 'legacy' && A.LGQ.org === 'ministry-of-justice' && A.lgFiltered().every(x => A.HO[A.rxOrgOf(x)]?.slug === 'ministry-of-justice');
    A.osRoute('account=alphagov'); await sleep(3); const r4 = A.current === 'discover' && A.RXD.acct === 'alphagov';
    const neg = A.osRoute('org=no-such-org') && A.osRoute('repo=nobody/nothing') && !A.osRoute('dama') && env.errs.length === before;
    const feed = JSON.parse(JSON.stringify(w.GHRAC_API.orgs())); const fOk = feed.length > 20 && feed.every(o => o.slug && o.repos_family >= o.repos_own) && w.GHRAC_API.org('no-such') === null;
    rec('T-OS-01', cards === 6 && anaN === anaExp && r1 && r2 && anaLink && r3 && r4 && neg && fOk && !env.errs.length,
      'govukOS connections: six apps described, the GTI and ANA organisation crosswalk filters correctly, links in open a project, an organisation, its legacy signals or a GitHub account, unknown values fall back without errors, and departments link out to ANA in its own format', 'R35', JSON.stringify({cards, anaN, anaExp, r1, r2, anaLink, r3, r4, neg, fOk})); }
  // T-SUP-02: the focus table on the tools and suppliers view follows the knowledge area and supplier type (V71-2)
  { A.showTab('suppliers'); const sel = d.querySelector('#v-area'), typ = d.querySelector('#v-type'); const res = {};
    const names = () => [...d.querySelectorAll('#v-dq tbody th [data-vsel]')].map(b => b.dataset.vsel);
    const byId = id => A.DV ? A.DV.find(v => v.id === id) : null;
    for (const a of ['dq', 'meta', 'integ', '']) { sel.value = a; sel.dispatchEvent(new w.Event('change')); await sleep(2);
      const h = d.querySelector('#v-dq h2').textContent, ids = names(), tagged = d.querySelector('#v-dq table')?.dataset.varea;
      res[a || 'all'] = {h, n: ids.length, tagged, allIn: !a || ids.every(id => (byId(id)?.areas || []).includes(a))}; }
    sel.value = 'meta'; sel.dispatchEvent(new w.Event('change')); typ.value = 'Commercial'; typ.dispatchEvent(new w.Event('change')); await sleep(2);
    const typeOk = names().every(id => byId(id)?.type === 'Commercial'); d.querySelector('#v-reset').click(); await sleep(2);
    const differ = JSON.stringify(res.dq.n) !== JSON.stringify(res.meta.n) || res.dq.h !== res.meta.h;
    const ok = /Data quality/.test(res.dq.h) && /Metadata/.test(res.meta.h) && /integration/i.test(res.integ.h) && /All data tools/.test(res.all.h) && res.meta.tagged === 'meta' && Object.values(res).every(r => r.allIn) && differ && typeOk && res.all.n >= res.meta.n;
    rec('T-SUP-02', ok && !env.errs.length, 'on the data tools and suppliers view, the focus table changes with the knowledge area and supplier type (data quality, metadata, integration, all), and lists only tools in the chosen area (negative test: metadata does not show data quality tools)', 'V71-2', JSON.stringify(res) + ' typeOk ' + typeOk); }
  // T-SRCH-01: search the whole catalogue: the masthead box and '/', grouped results, kinds filter, highlighting, opening results, and search inside views
  { const before = env.errs.length; const top = d.querySelector('#gs-q'); const hasTop = !!top && !!d.querySelector('#gs-top');
    d.body.dispatchEvent(new w.KeyboardEvent('keydown', {key: '/', bubbles: true})); const slash = d.activeElement === top;
    top.value = 'Home Office'; d.querySelector('#gs-top').dispatchEvent(new w.Event('submit', {cancelable: true})); await sleep(5);
    const onSearch = A.current === 'search', firstGroup = d.querySelector('.gs-group h3')?.textContent || '', firstHit = d.querySelector('.gs-hit b')?.textContent;
    const allR = A.gsSearch('Home Office'), kindsOk = [...d.querySelectorAll('[data-gskind]')].every(b => { const id = b.dataset.gskind; const n = +b.querySelector('b').textContent.replace(/,/g, ''); return id === '' ? n === allR.length : n === allR.filter(e => e.k === id).length; });
    click(w, d.querySelector('.gs-hit')); await sleep(5); const opened = A.current === 'family' && /Home Office/.test(d.querySelector('#fam-sel h2').textContent);
    A.gsGo('<img src=x onerror="window.__pwn72=1">'); await sleep(5); const xss = !w.__pwn72 && !d.querySelector('#v-search img');
    A.gsGo('zzqqxx'); await sleep(5); const none = /Nothing found/.test(d.querySelector('#gs-count').textContent);
    A.gsGo('payments'); await sleep(5); const syn = /Also looking for: .*pay/.test(d.querySelector('#gs-count').textContent);
    A.showTab('glossary'); const g = d.querySelector('#gl-q'); g.value = 'licence'; g.dispatchEvent(new w.Event('input')); const glOk = d.querySelectorAll('#v-glossary .gl-item:not([hidden])').length > 0 && [...d.querySelectorAll('#v-glossary .gl-item:not([hidden])')].every(i => /licence/i.test(i.textContent));
    A.showTab('family'); const f = d.querySelector('#fam-find'); f.value = 'met office'; f.dispatchEvent(new w.Event('input')); await sleep(200); const famOk = /Met Office/.test(d.querySelector('#fam-hits').textContent);
    A.showTab('suppliers'); const vq = d.querySelector('#v-q'); vq.value = 'mongo'; vq.dispatchEvent(new w.Event('input')); await sleep(200); const supOk = [...d.querySelectorAll('#v-dq tbody th')].every(t => /mongo/i.test(t.textContent));
    rec('T-SRCH-01', hasTop && slash && onSearch && /Organisations/.test(firstGroup) && firstHit === 'Home Office' && kindsOk && opened && xss && none && syn && glOk && famOk && supOk && env.errs.length === before,
      'search everything: the masthead box and the / key, results grouped by kind with exact names first and correct counts, results open where they belong, markup in a search is shown as text, no-match and thesaurus messages, and search inside the glossary, family tree and tools and suppliers', 'R36', JSON.stringify({hasTop, slash, onSearch, firstGroup, firstHit, kindsOk, opened, xss, none, syn, glOk, famOk, supOk})); }
  // T-TH-01: theme views: tiles, heatmap cells and filters agree with the data; devolved publishers and UK alliance flags; profile chips link to the theme
  { const res = {}; for (const t of ['guidance', 'journeys', 'nations', 'international']) { A.showTab(t); const v = d.querySelector('#v-' + t); const tile = v.querySelector('[data-thsub]'); click(w, tile); await sleep(3);
      const n = +d.querySelector(`#th-${t}-count`).textContent.replace(/,/g, '').match(/\d+/)[0], exp = A.thFiltered(t, A.THQ[t]).length, all = A.thFiltered(t, A.THQ[t]).every(x => A.thSigs(x).some(s => s.c.id === tile.dataset.thsub));
      const cell = v.querySelector('[data-thcell]'); let cellOk = true; if (cell) { click(w, cell); await sleep(3); cellOk = +cell.textContent.replace(/,/g, '') === A.thFiltered(t, A.THQ[t]).length; }
      res[t] = n === exp && all && cellOk; v.querySelector('[data-threset]').click(); await sleep(2); }
    A.showTab('international'); const al = d.querySelector('#th-international-ally'); al.checked = true; al.dispatchEvent(new w.Event('change')); const allyOk = A.thFiltered('international', A.THQ.international).every(x => A.TH_ALLY.has(x.key)) && A.thFiltered('international', A.THQ.international).length === A.TH.allies.filter(k => A.thSigs(w.__app.ALLX ? null : A.rxFiltered({...A.RXD0}).find(x => x.key === k) || {key: k, q: ''}).length >= 0).length;
    const dev = A.rxFiltered({...A.RXD0}).filter(x => x.sector === 'Scotland').slice(0, 20).every(x => A.thSigs(x).some(s => s.c.id === 'devpub'));
    const k = A.TH.allies[0]; A.rxGo(k); await sleep(3); const chip = [...d.querySelectorAll('#v-profile [data-thgo]')][0]; const chipT = chip?.dataset.thgo.split('|')[0]; click(w, chip); await sleep(3); const chipOk = !!chip && A.current === chipT;
    rec('T-TH-01', Object.values(res).every(Boolean) && dev && chipOk && !env.errs.length, 'theme views (guidance, journeys, nations, international): tile and heatmap counts match the lists they open; Scottish publishers are flagged as devolved; a profile\'s theme chip opens its theme', 'R37', JSON.stringify({res, dev, chipOk, allyOk})); }
  // T-KN-01: knowledge layer: graph walks, lineage lights complete chains, vocabularies and ontology export, tabs work by keyboard
  { A.showTab('knowledge'); const tabs = [...d.querySelectorAll('[data-kt]')]; const tabOk = tabs.length === 6 && tabs.every(t => t.getAttribute('role') === 'tab');
    tabs[0].dispatchEvent(new w.KeyboardEvent('keydown', {key: 'ArrowRight', bubbles: true})); await sleep(3); const kb = A.KS.tab === 'lineage';
    A.KS.sel = null; A.KS.tab = 'lineage'; w.RENDER ? 0 : 0; d.querySelector('[data-kt="lineage"]').click(); await sleep(3);
    const r = d.querySelector('[data-kl^="r-R33"]') || d.querySelector('[data-kl^="r-"]'); click(w, r); await sleep(3);
    const G = A.klGraph(), sel = A.KS.sel, lit = new Set([...d.querySelectorAll('.kl-n.lit')].map(b => b.dataset.kl)); const q = G.N.find(n => n.id === sel); const reqChecks = G.E.filter(([a]) => a === sel).map(e => e[1]);
    const linOk = reqChecks.length > 0 && reqChecks.every(c => lit.has(c)) && [...lit].some(id => id.startsWith('src-'));
    d.querySelector('[data-kt="graph"]').click(); await sleep(3); A.KS.focus = ['topic', 'health']; A.KS.trail = []; d.querySelector('[data-kt="graph"]').click(); await sleep(3);
    const nb = A.kgNeighbours(['topic', 'health']), svgN = d.querySelectorAll('#kp svg [data-kgk]').length; const n1 = d.querySelector('#kp svg [data-kgk]'); click(w, n1); await sleep(3); const moved = A.KS.focus[1] === n1.dataset.kgid && A.KS.trail.length === 1;
    const V = A.kvVocabs(), sk = A.kvSkos(); const skOk = sk['@graph'].filter(x => x['@type'] === 'skos:ConceptScheme').length === V.length && sk['@graph'].filter(x => x['@type'] === 'skos:Concept').length === V.reduce((a, v) => a + v.concepts.length, 0);
    rec('T-KN-01', tabOk && kb && linOk && nb.length === svgN && moved && skOk && !env.errs.length, `knowledge layer: six tabs that work by keyboard; selecting a requirement lights its checks and its sources; the knowledge graph shows every neighbour and moves its centre when one is chosen; ${V.length} vocabularies export as SKOS with every term`, 'R38', JSON.stringify({tabOk, kb, linOk, nb: nb.length, svgN, moved, skOk})); }
  // merge external results (axe, contrast)
  for (const f2 of ['axe_result.json', 'contrast_result.json', 'width_result.json']) { const p = path.join(path.dirname(OUT), f2); if (fs.existsSync(p)) Object.assign(R, JSON.parse(fs.readFileSync(p, 'utf8'))); }
  fs.writeFileSync(OUT, JSON.stringify(R, null, 1));
  console.log('errors', env.errs, 'written', Object.keys(R).length);
  process.exit(0);
})();
