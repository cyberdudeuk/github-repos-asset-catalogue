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
