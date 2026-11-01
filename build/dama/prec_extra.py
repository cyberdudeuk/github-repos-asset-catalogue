"""Record the sampled precision for the API and open data views into apis.json (judged by Claude, 31 Oct 2026; not owner-confirmed)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); a = json.load(open(f"{H}/apis.json"))
a["prec"] = {"api_named": [{"round": 1, "n": 12, "true": 12, "note": "repositories named or described as an API (the weakest kind)"}],
             "opendata": [{"round": 1, "n": 15, "true": 8, "note": "'datastore' matched ordinary databases; narrowed to open data datastores"}, {"round": 2, "n": 15, "true": 14, "note": "a README that links to one data.gov.uk dataset"}]}
json.dump(a, open(f"{H}/apis.json", "w")); print("ok")
