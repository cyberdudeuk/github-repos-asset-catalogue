import sys
p = sys.argv[1] + "/dama/gds.py"; s = open(p).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:60]; s = s.replace(a, b)
rep('r"govuk-frontend-react", r"nhsuk-frontend", r"@ministryofjustice/frontend",', 'r"govuk-frontend-react", r"@ministryofjustice/frontend",')
rep('w(r"service standard", r"service manual", r"technology code of practice",', 'w(r"(?<!nhs )(?<!nhs digital )service standard", r"(?<!nhs )(?<!nhs digital )service manual", r"technology code of practice",')
rep('''           "deps_fetched": len(os.listdir(DEPS))}''', '''           "deps_fetched": len(os.listdir(DEPS)),
           "prec": {"judged_by": "Claude, 31 October 2026 (not owner-confirmed)", "rounds": [
              {"what": "links other than the design system and components", "n": 15, "true": 11, "note": "the NHS service manual and prototype kit counted as GDS's; now excluded"},
              {"what": "design system and component links", "n": 10, "true": 9, "note": "NHS.UK frontend counted as GOV.UK Frontend; now excluded"}]}}''')
rep('''and re.search(A["procure"][5], "listed on G-Cloud 14", I),''', '''and re.search(A["procure"][5], "listed on G-Cloud 14", I) and not re.search(A["standards"][5], "the NHS digital service manual", I) and re.search(A["standards"][5], "meets the GOV.UK Service Standard", I),''')
s = s.replace("and the gcloud tool isn't G-Cloud (negative tests)", "the gcloud tool isn't G-Cloud, and the NHS service manual isn't GDS's (negative tests)")
open(p, "w").write(s); print("ok")
