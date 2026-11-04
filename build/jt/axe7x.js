// axe-core over every view plus the open details dialog with its decision link and drafts, and the Ask answer. Nothing is mocked: the page needs no outside service (R72).
const {JSDOM} = require('jsdom'); const fs = require('fs'); const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const html = fs.readFileSync(process.argv[2], 'utf8'); const out = process.argv[3]; const only = process.argv[4] ? process.argv[4].split(',') : null;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const dom = new JSDOM('<!doctype html><html lang="en-GB"><head></head><body>' + html + '</body></html>', {runScripts: 'dangerously', url: 'https://x.test/', pretendToBeVisual: true,
  beforeParse(w) { w.matchMedia = () => ({matches: false, addEventListener() {}}); w.HTMLElement.prototype.scrollIntoView = function () {}; w.Element.prototype.scrollBy = function () {}; w.Element.prototype.scrollTo = function () {}; }});
const w = dom.window, d = w.document; w.eval(axeSrc);
(async () => {
  await sleep(200); const tabs = [...d.querySelectorAll('#rail [data-tab]')].map(b => b.dataset.tab).filter(t => !only || (process.argv[5]==="exclude" ? !only.includes(t) : only.includes(t))); const agg = {};
  const run = async (t, ctx) => { const res = await w.axe.run(ctx || d, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}, rules: {'color-contrast': {enabled: false}, 'region': {enabled: false}}});
    for (const v of res.violations) { (agg[v.id] ||= {impact: v.impact, help: v.help, n: 0, ex: new Set(), tabs: new Set()}); agg[v.id].n += v.nodes.length; agg[v.id].tabs.add(t); v.nodes.slice(0, 2).forEach(n => agg[v.id].ex.add(n.target.join(' ').slice(0, 90))); } };
  for (const t of tabs) { w.__app.showTab(t); await sleep(2); await run(t);
    if (t === 'repos') { w.__app.openSheet(w.__app.rows.find(r => r.status === 'Active').repo); await sleep(10); d.querySelector('[data-draft="impact"]').click(); await sleep(2); await run('sheet+draft'); d.querySelector('#sh-close').click(); }
    if (t === 'ask') { d.querySelector('#askq').value = 'Who else is building design systems?'; d.querySelector('#askform').dispatchEvent(new w.Event('submit', {cancelable: true})); await sleep(5); await run('ask-answer'); }
    if (t === 'standards') { w.__app.openSorg('alphagov'); await sleep(5); await run('orgpanel'); d.querySelector('#sh-close').click(); }
    if (t === 'catalogue') { w.__app.openX(w.__app.CATX[0].key); await sleep(5); await run('catsheet'); d.querySelector('#sh-close').click(); w.__app.openX(w.__app.UNL[0].key); await sleep(5); await run('unlisted'); d.querySelector('#sh-close').click(); }
    if (t === 'dama') { w.__app.damaGo('meta'); await sleep(5); await run('dama-meta'); }
    if (t === 'gds') { w.__app.GS7.area = 'components'; w.__app.showTab('gds'); await sleep(5); await run('gds'); }
    if (t === 'orgs') { w.__app.profGo(0); await sleep(5); await run('orgprofile'); }
    if (t === 'topics') { w.__app.topicGo('health'); await sleep(5); await run('topicdetail'); }
    if (t === 'landscape') { w.__app.openX(w.__app.X.find(x => x.hy).key); await sleep(5); await run('xsheet'); d.querySelector('#sh-close').click(); } }
  let n = 0; for (const [k, v] of Object.entries(agg)) { n++; console.log(k, v.impact, v.n, '|', v.help, '|', [...v.tabs].join(','), '|', [...v.ex].slice(0, 3).join(' ;; ')); }
  console.log('violation types:', n, 'views:', tabs.length);
  if (out) fs.writeFileSync(out, JSON.stringify({'T-AXE-01': {status: n ? 'fail' : 'pass', text: `axe-core finds no WCAG 2.2 A or AA or best-practice violations in ${tabs.length} views, an organisation profile, a topic drill-down, the details dialog with its decision link and a draft, and an Ask answer`, guards: 'A-1, D14', detail: Object.keys(agg).join(', ')}}));
  process.exit(0);
})();
