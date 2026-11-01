// Read every catalogue account's repository list from GitHub's own web pages, in a signed-in browser tab on github.com.
// Used for the 7.9.1 check against GitHub (build/dama/ghverify.py). Read only: GET requests to pages a person can open.
// Paste into the browser console on any github.com page, after setting ACCOUNTS to the catalogue's account names.
// GitHub answers these pages as JSON when asked with Accept: application/json; 30 repositories a page.
// A member's session also sees internal and private repositories. Every row keeps GitHub's own visibility label,
// and build/dama/ghverify.py keeps only Public, Public archive and Public template rows (check C-GHV-03).
const ACCOUNTS = [/* account names */];
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function page(a, n) {
  for (let t = 0; t < 6; t++) {
    const r = await fetch(`/orgs/${a}/repositories?page=${n}`, {headers: {Accept: "application/json"}});
    if (r.status === 404) return null;                       // not an organisation, or gone
    if (r.status === 429 || r.status >= 500) { await sleep(3000 * (t + 1)); continue; }
    return (await r.json()).payload.orgReposPageRoute;
  }
  throw new Error(`${a} page ${n} failed`);
}
async function crawl() {
  const done = {};
  for (const a of ACCOUNTS) {
    const first = await page(a, 1);
    if (!first) { done[a] = {kind: "user-or-missing", rows: []}; continue; }
    const rows = [], add = p => p.repositories.forEach(x => rows.push([x.name, /archive/i.test(x.type), x.isFork, x.starsCount, x.forksCount, !!x.description, (x.allTopics || []).length,
      x.license || "", (x.lastUpdated?.timestamp || "").slice(0, 10), x.primaryLanguage?.name || "", x.issueCount, x.pullRequestCount, x.type]));
    add(first);
    for (let n = 2; n <= first.pageCount; n++) { add(await page(a, n)); await sleep(350); }
    if (rows.length !== first.repositoryCount) throw new Error(`${a}: read ${rows.length}, GitHub says ${first.repositoryCount}`);
    done[a] = {kind: "org", rows};
  }
  return done;
}
// Feature tabs for one repository: the tabs GitHub shows on its page (issues, projects, wiki, discussions ...).
async function tabs(fullName) {
  const h = await (await fetch("/" + fullName)).text();
  return [...new Set([...h.matchAll(/data-tab-item="([^"]+)"/g)].map(m => m[1]))];
}
