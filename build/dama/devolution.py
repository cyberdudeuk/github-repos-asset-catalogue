"""English devolution: strategic authorities and the councils in this catalogue that sit in them (7.7, R47).

Facts come from official sources read on 1 November 2026: legislation.gov.uk establishment orders, GOV.UK's English
Devolution Area Factsheets (July 2025) and GOV.UK news on Royal Assent and the Devolution Priority Programme. Anything a
secondary source alone supports is marked 'secondary'; anything not confirmed is marked 'unconfirmed'. Establishment
years for authorities set up before 2025 were not confirmed from an official source and are left out.
Mapping of councils to authorities: a council is 'constituent' when the establishing order or the factsheet names it, and
'in the area' when it is a district council inside a constituent county. GitHub accounts are joined to councils by the
public-sector-code-by-organisation register already used by the catalogue, or by name where marked.
Writes devolution.json and devolution_checks.txt. Run with python3 -I.
"""
import json, os, sys
S = os.path.dirname(os.path.abspath(__file__))
FACTSHEET = "https://www.gov.uk/government/publications/english-devolution-area-factsheets/english-devolution-area-factsheets"
AUTH = [  # id, name, kind, status, detail, constituents, source, confidence
 ("gla", "Greater London Authority", "Mayoral strategic authority (not a combined authority)", "established", "Named an established Mayoral Strategic Authority in the July 2025 factsheets.", ["The 32 London boroughs and the City of London (area)"], FACTSHEET, "official"),
 ("gmca", "Greater Manchester Combined Authority", "Mayoral combined authority", "established", "", ["Bolton", "Bury", "Manchester", "Oldham", "Rochdale", "Salford", "Stockport", "Tameside", "Trafford", "Wigan"], FACTSHEET, "official"),
 ("wmca", "West Midlands Combined Authority", "Mayoral combined authority", "established", "", ["Birmingham", "Coventry", "Dudley", "Sandwell", "Solihull", "Walsall", "Wolverhampton"], FACTSHEET, "official"),
 ("lcr", "Liverpool City Region Combined Authority", "Mayoral combined authority", "established", "", ["Halton", "Knowsley", "Liverpool", "St Helens", "Sefton", "Wirral"], FACTSHEET, "official"),
 ("wyca", "West Yorkshire Combined Authority", "Mayoral combined authority", "established", "", ["Bradford", "Calderdale", "Kirklees", "Leeds", "Wakefield"], FACTSHEET, "official"),
 ("symca", "South Yorkshire Mayoral Combined Authority", "Mayoral combined authority", "established", "", ["Barnsley", "Doncaster", "Rotherham", "Sheffield"], FACTSHEET, "official"),
 ("tvca", "Tees Valley Combined Authority", "Mayoral combined authority", "established", "", ["Darlington", "Hartlepool", "Middlesbrough", "Redcar and Cleveland", "Stockton-on-Tees"], FACTSHEET, "official"),
 ("weca", "West of England Combined Authority", "Mayoral combined authority", "established", "", ["Bath and North East Somerset", "Bristol", "South Gloucestershire"], FACTSHEET, "official"),
 ("cpca", "Cambridgeshire and Peterborough Combined Authority", "Mayoral combined authority", "established", "", ["Cambridge", "Cambridgeshire", "East Cambridgeshire", "Fenland", "Huntingdonshire", "Peterborough", "South Cambridgeshire"], FACTSHEET, "official"),
 ("nema", "North East Mayoral Combined Authority", "Mayoral combined authority", "established", "Became a mayoral combined authority in 2024.", ["County Durham", "Gateshead", "Newcastle upon Tyne", "North Tyneside", "Northumberland", "South Tyneside", "Sunderland"], FACTSHEET, "official"),
 ("ynyca", "York and North Yorkshire Combined Authority", "Mayoral combined authority", "established", "", ["York", "North Yorkshire"], FACTSHEET, "official"),
 ("emcca", "East Midlands Combined County Authority", "Mayoral combined county authority", "established", "", ["Derby", "Derbyshire", "Nottingham", "Nottinghamshire"], FACTSHEET, "official"),
 ("heyca", "Hull and East Yorkshire Combined Authority", "Mayoral combined authority", "established", "Established 5 February 2025; first mayor elected May 2025.", ["Hull", "East Riding of Yorkshire"], "https://www.legislation.gov.uk/uksi/2025/113/contents", "official"),
 ("glcca", "Greater Lincolnshire Combined County Authority", "Mayoral combined county authority", "established", "Established 5 February 2025; first mayor elected May 2025.", ["Lincolnshire", "North East Lincolnshire", "North Lincolnshire"], "https://www.legislation.gov.uk/uksi/2025/117/contents", "official"),
 ("cwca", "Cheshire and Warrington Combined Authority", "Mayoral combined authority", "established", "Established 24 February 2026; mayoral functions from 10 May 2027.", ["Cheshire East", "Cheshire West and Chester", "Warrington"], "https://www.legislation.gov.uk/uksi/2026/159/contents/made", "official"),
 ("cumbca", "Cumbria Combined Authority", "Mayoral combined authority", "established", "Established 24 February 2026; mayoral functions from 10 May 2027.", ["Cumberland", "Westmorland and Furness"], "https://www.legislation.gov.uk/uksi/2026/158/contents/made", "official"),
 ("sbcca", "Sussex and Brighton Combined County Authority", "Mayoral combined county authority", "established", "Established 26 March 2026; mayoral functions from 8 May 2028.", ["Brighton and Hove", "East Sussex", "West Sussex"], "https://www.legislation.gov.uk/uksi/2026/362/contents/made", "official"),
 ("hscca", "Hampshire and the Solent Combined County Authority", "Mayoral combined county authority", "established", "Established 4 June 2026; mayoral functions from 8 May 2028.", ["Hampshire", "Isle of Wight", "Portsmouth", "Southampton"], "https://www.legislation.gov.uk/uksi/2026/595/contents/made", "official"),
 ("gecca", "Greater Essex Combined County Authority", "Mayoral combined county authority", "in creation", "Devolution Priority Programme. Statutory tests met July 2025; regulations expected to be laid November 2026 (secondary source: Southend-on-Sea cabinet papers, 21 October 2026).", ["Essex", "Southend-on-Sea", "Thurrock"], "https://www.essex.gov.uk/devolution", "official (status: secondary)"),
 ("nscca", "Norfolk and Suffolk Combined County Authority", "Mayoral combined county authority", "in creation", "Devolution Priority Programme. Statutory tests met July 2025; no regulations found yet; first mayoral election expected May 2028 (secondary).", ["Norfolk", "Suffolk"], "https://www.gov.uk/norfolk-and-suffolk-devolution", "official (status: secondary)"),
 ("dtcca", "Devon and Torbay Combined County Authority", "Foundation (non-mayoral) combined county authority", "established", "Established 5 February 2025. Named among areas in final stages of new arrangements (Budget, October 2026); whether it has become mayoral is unconfirmed.", ["Devon", "Torbay"], "https://www.legislation.gov.uk/uksi/2025/115/contents", "official"),
 ("lancca", "Lancashire Combined County Authority", "Foundation (non-mayoral) combined county authority", "established", "Established 5 February 2025.", ["Lancashire", "Blackpool", "Blackburn with Darwen"], "https://www.legislation.gov.uk/uksi/2025/118/contents", "official"),
]
PIPELINE = {"source": "https://www.gov.uk/government/news/budget-2026-fact-sheet-delivering-for-every-region", "note": "GOV.UK says 10 new devolution arrangements are in their final stages, aiming for full coverage by the end of 2028, without naming the areas. A secondary source names Devon, Plymouth and Torbay; Hertfordshire; Lancashire; Leicester, Leicestershire and Rutland; Stoke and Staffordshire; Surrey; Thames Valley; Wessex; Kent and Medway; and Cornwall. Councils in these areas are shown as 'proposed area (unconfirmed)'.",
            "areas": {"surrey": "Surrey", "kentmedway": "Kent and Medway", "staffs": "Stoke and Staffordshire", "wessex": "Wessex", "thames": "Thames Valley", "herts": "Hertfordshire", "llr": "Leicester, Leicestershire and Rutland", "cornwall": "Cornwall"}}
ACT = {"name": "English Devolution and Community Empowerment Act 2026", "assent": "2026-04-29", "source": "https://www.gov.uk/government/news/english-devolution-bill-receives-royal-assent", "elections": "No inaugural mayoral election for a new authority was held in May 2026; the government said in December 2025 it was minded to hold four of them in May 2028. Cumbria and Cheshire and Warrington are due in May 2027.", "lgr": "Local government reorganisation was paused in September 2026 pending a review (secondary)."}
# GitHub accounts of councils and local bodies in the catalogue -> (council, nation, authority id or pipeline key or "", relation, note)
COUNCILS = {
 "coventry-city-council": ("Coventry City Council", "England", "wmca", "constituent", ""), "LiverpoolCityCouncil": ("Liverpool City Council", "England", "lcr", "constituent", ""),
 "smbc-digital": ("Stockport Metropolitan Borough Council", "England", "gmca", "constituent", ""), "TraffordCouncil": ("Trafford Metropolitan Borough Council", "England", "gmca", "constituent", ""),
 "gmfrs": ("Greater Manchester Fire and Rescue Service", "England", "gmca", "functional body", "The Mayor of Greater Manchester is the fire and rescue authority (assessed, not from the sources above)."),
 "GMFRS": ("Greater Manchester Fire and Rescue Service", "England", "gmca", "functional body", "The Mayor of Greater Manchester is the fire and rescue authority (assessed, not from the sources above)."),
 "rothgov": ("Rotherham Metropolitan Borough Council", "England", "symca", "constituent", ""), "BathnesDevelopment": ("Bath and North East Somerset Council", "England", "weca", "constituent", ""),
 "BristolCityCouncil": ("Bristol City Council", "England", "weca", "constituent", ""), "cityofyork": ("City of York Council", "England", "ynyca", "constituent", ""), "CityOfYork": ("City of York Council", "England", "ynyca", "constituent", ""),
 "hull-city-council": ("Hull City Council", "England", "heyca", "constituent", ""), "brighton-hove-gov-uk": ("Brighton and Hove City Council", "England", "sbcca", "constituent", ""),
 "east-sussex-county-council": ("East Sussex County Council", "England", "sbcca", "constituent", ""), "wealden": ("Wealden District Council", "England", "sbcca", "in the area", "A district council in East Sussex."),
 "essexcountycouncil": ("Essex County Council", "England", "gecca", "constituent", ""), "KLBC-WebTeam": ("Borough Council of King's Lynn and West Norfolk", "England", "nscca", "in the area", "A district council in Norfolk."),
 "rushmoor": ("Rushmoor Borough Council", "England", "hscca", "in the area", "A district council in Hampshire."), "devoncc": ("Devon County Council", "England", "dtcca", "constituent", ""), "DevonCountyCouncil": ("Devon County Council", "England", "dtcca", "constituent", ""), "DevonCC": ("Devon County Council", "England", "dtcca", "constituent", ""),
 "TransportForLondon": ("Transport for London", "England", "gla", "functional body", "A functional body of the Greater London Authority."),
 **{a: (n, "England", "gla", "in the area", "A London borough.") for a, n in [("CamdenCouncil", "London Borough of Camden"), ("LBHackney-IT", "London Borough of Hackney"), ("LBHounslow", "London Borough of Hounslow"), ("LambethCouncil", "London Borough of Lambeth"), ("LondonBoroughSutton", "London Borough of Sutton"), ("wfcouncil", "London Borough of Waltham Forest"), ("RoyalBoroughKingston", "Royal Borough of Kingston upon Thames"), ("LondonBoroughOfBexley", "London Borough of Bexley")]},
 "kentcc": ("Kent County Council", "England", "kentmedway", "proposed area (unconfirmed)", ""), "surreydigitalservices": ("Surrey County Council", "England", "surrey", "proposed area (unconfirmed)", ""),
 "lichfield-district-council": ("Lichfield District Council", "England", "staffs", "proposed area (unconfirmed)", "A district council in Staffordshire."), "Lichfield-District-Council": ("Lichfield District Council", "England", "staffs", "proposed area (unconfirmed)", "A district council in Staffordshire."),
 "Dorset-Council-UK": ("Dorset Council", "England", "", "none found", "Wessex is named in a secondary source; its councils are unconfirmed."),
 "OxfordshireCountyCouncil": ("Oxfordshire County Council", "England", "", "none found", "Thames Valley is named in a secondary source; its councils are unconfirmed."),
 "Reading-Borough-Council": ("Reading Borough Council", "England", "", "none found", "Thames Valley is named in a secondary source; its councils are unconfirmed."),
 "west-berkshire-council": ("West Berkshire Council", "England", "", "none found", "Thames Valley is named in a secondary source; its councils are unconfirmed."),
 "BracknellForestCouncil": ("Bracknell Forest Council", "England", "", "none found", "Thames Valley is named in a secondary source; its councils are unconfirmed."),
 "warwickshire": ("Warwickshire County Council", "England", "", "none found", "Not a constituent council of the West Midlands Combined Authority."), "HfdsCouncil": ("Herefordshire Council", "England", "", "none found", ""),
 "LutonCouncil": ("Luton Borough Council", "England", "", "none found", ""), "northamptonshire-county-council": ("Northamptonshire County Council (abolished 2021)", "England", "", "none found", "Replaced by North and West Northamptonshire councils."),
 "lgss": ("LGSS (shared service of councils)", "England", "", "none found", "A shared service, not a council."), "wmfs": ("West Midlands Fire Service", "England", "", "none found", "Its link to the West Midlands Combined Authority is not confirmed."),
 "ukfrs-CDDFRS": ("County Durham and Darlington Fire and Rescue Service", "England", "", "none found", "Its area spans two strategic authorities."), "ukfrs-hertsfrs": ("Hertfordshire Fire and Rescue Service", "England", "herts", "proposed area (unconfirmed)", ""),
 "LocalGovDrupal": ("LocalGov Drupal (councils working together)", "England", "", "none found", "Shared by many councils."),
 **{a: (n, "Scotland", "", "not English devolution", "Scotland's councils sit within Scottish devolution.") for a, n in [("DundeeCityCouncil", "Dundee City Council"), ("edinburghcouncil", "City of Edinburgh Council"), ("Falkirk-Council", "Falkirk Council"), ("openglasgow", "Glasgow City Council"), ("thehighlandcouncil", "The Highland Council"), ("TheHighlandCouncil", "The Highland Council")]},
}
LINES, FAILS = [], []
def need(ok, cid, msg):
    LINES.append(("PASS " if ok else "FAIL ") + cid + " " + msg + " [guards: R47]"); print(LINES[-1])
    if not ok: FAILS.append(cid)
if __name__ == "__main__":
    ids = {a[0] for a in AUTH}
    need(all(a[6].startswith("https://") and a[5] for a in AUTH) and len(ids) == len(AUTH), "C-DEV-01", f"{len(AUTH)} strategic authorities, each with constituent councils and an official source ({sum(a[3] == 'established' for a in AUTH)} established, {sum(a[3] == 'in creation' for a in AUTH)} in creation)")
    bad = [k for k, v in COUNCILS.items() if v[2] and v[2] not in ids and v[2] not in PIPELINE["areas"]]
    rel_ok = all((v[3] in ("constituent", "in the area", "functional body") and v[2] in ids) or (v[3] == "proposed area (unconfirmed)" and v[2] in PIPELINE["areas"]) or (v[3] in ("none found", "not English devolution") and not v[2]) for v in COUNCILS.values())
    need(not bad and rel_ok, "C-DEV-02", f"{len({v[0] for v in COUNCILS.values()})} councils and local bodies with GitHub accounts placed against an authority, a proposed area or none, each with a stated relationship")
    # negative test: a council pointing at an authority that doesn't exist, or a 'constituent' with no authority, must fail
    t1 = {**COUNCILS, "x": ("X", "England", "nowhere", "constituent", "")}; t2 = {**COUNCILS, "y": ("Y", "England", "", "constituent", "")}
    neg = [all((v[3] in ("constituent", "in the area", "functional body") and v[2] in ids) or (v[3] == "proposed area (unconfirmed)" and v[2] in PIPELINE["areas"]) or (v[3] in ("none found", "not English devolution") and not v[2]) for v in t.values()) for t in (t1, t2)]
    need(not any(neg), "C-DEV-02n", "negative tests: a council linked to an authority that doesn't exist, and a 'constituent' council with no authority, are both rejected")
    json.dump(dict(authorities=[dict(id=a[0], name=a[1], kind=a[2], status=a[3], detail=a[4], constituents=a[5], source=a[6], confidence=a[7]) for a in AUTH], pipeline=PIPELINE, act=ACT,
                   councils={k: dict(name=v[0], nation=v[1], auth=v[2], rel=v[3], note=v[4]) for k, v in COUNCILS.items()}, read="2026-11-01"), open(os.path.join(S, "devolution.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(S, "devolution_checks.txt"), "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)
