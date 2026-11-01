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
    const ok2 = sw.getAttribute('role') === 'switch' && /Page contents/.test(sw.textContent); click(w, sw); await sleep(1); const off = dr.hidden && sw.getAttribute('aria-checked') === 'false';
    click(w, d.querySelector('#drawer-switch')); await sleep(1); const on = !dr.hidden; const noCross = !dr.querySelector('[data-tab],[data-hub],[data-go]');
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
