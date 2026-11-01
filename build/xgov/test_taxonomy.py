"""Regression tests for tagging rules v2. Each case names the defect it guards (D7 = independent review 2026-10-08)."""
import sys, os, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomy
from taxonomy import tag, sector, readme_lede, standards_from_files
C = [  # name, desc, topics, lede, sector, must, mustnot, dam, guards
 ("ukgov-metadata-exchange-model","A metadata model for describing data assets","dataset,dcat","", "", {"DF3","DF5"}, set(), True, "core DAM repo tagged"),
 ("product-catalogue-service","shop products","","", "", set(), {"DF3"}, False, "D-X1 bare catalogue"),
 ("terraform-aws-focus","Terraform module for shipping AWS FOCUS cost exports","","", "", {"FF"}, set(), False, "FinOps module is firmer foundations"),
 ("focus-group-notes","notes from user research focus group","","", "", set(), {"FF"}, False, "D-X2 bare focus"),
 ("user-agent-parser","parse browser user agents","","", "", set(), {"BP2"}, False, "D-X3 bare agents"),
 ("chair","","","", "", set(), {"BP2"}, False, "'ai' inside a word"),
 ("ai","","","", "", {"BP2"}, set(), False, "repo named ai"),
 ("whitehall","Publishing app for GOV.UK","","", "", set(), {"DF3","DF5","BP2","BP3"}, False, "generic repo untagged"),
 ("cloud-platform-terraform-sqs","Terraform module for the Cloud Platform","","", "", set(), {"BP3"}, False, "D7 bare platform/terraform module (MoJ Cloud Platform)"),
 ("acp-tf-nlb","reusable terraform module for NLB","","", "", set(), {"BP3"}, False, "D7 reusable/terraform module"),
 ("eori-common-component-hods-proxy","common component","","", "", set(), {"BP3"}, False, "D7 common component"),
 ("trader-services-performance-tests","performance tests for the service","","", "", set(), {"BP6"}, False, "D7 service performance in test names"),
 ("ey-recovery-prototype","Prototype built with govuk-frontend","","", "", set(), {"BP1"}, False, "D7 govuk frontend is not joining up services"),
 ("modernisation-platform-slackbot","Slack bot for the Modernisation Platform","","", "", set(), {"FF"}, False, "D7 'modernisation' is MoJ's hosting platform name"),
 ("weather_datahub_utilities","Utilities for the Met Office Weather DataHub","","", "", set(), set(), False, "D7 DataHub product name is not DAM"),
 ("hmpps-datahub-query-metrics","Metrics for datahub queries","","", "", set(), set(), False, "D7 datahub metrics not DAM"),
 ("nhp_ats_backup","Backup of model-run metadata","","", "", set(), {"DF3","DF5"}, False, "D7 model-run metadata not DAM"),
 ("synthesis","AI tool to synthesise documents with privacy controls","","", "", {"BP2"}, {"DF6"}, False, "D7 bare privacy"),
 ("api-catalogue","The list of APIs in Government","api,register,catalogue","This API catalogue is for central government and local government APIs.", "UK central government and ALBs", {"DF3"}, {"LOCAL"}, False, "D7 'local government' mention in a central repo"),
 ("dis-dataset-catalogue-tests","Tests for the dataset catalogue","","", "", {"DF3"}, set(), True, "D7 miss: dataset catalogue"),
 ("ds-data-api","InformationAsset records API","","", "", {"DF5"}, set(), True, "D7 miss: CamelCase InformationAsset"),
 ("data-vocab","Data vocabulary for GOV.UK One Login","","", "", {"DF3","BP1"}, set(), True, "D7 miss: data vocab"),
 ("records-management","Records management tooling","","", "", {"DF5"}, set(), True, "D7 miss: records management"),
 ("bin-day","Find your bin collection day","","", "Local government", {"LOCAL"}, set(), False, "local sector tagging still works"),
 ("ec2_metadata","Read EC2 instance metadata","","", "", set(), {"DF3"}, False, "V4-2 technical metadata is not DAM"),
 ("fb-metadata-api","Metadata API for form builder forms","","", "", set(), {"DF3"}, False, "V4-2 form metadata is not DAM"),
 ("dataset-metadata-service","Publish dataset metadata using DCAT","","", "", {"DF3"}, set(), True, "V4-2 dataset metadata still tagged"),
 ("laa-data-claims-api","Claims API built by the LAA Data Stewardship team","","", "", set(), {"DF5"}, False, "V4-2 team name is not data stewardship"),
 ("terraform-azurerm-aspnet-data-protection","ASP.NET Data Protection keys in Azure","","", "", set(), {"DF6"}, False, "V4-2 ASP.NET data protection keys"),
 ("dpia-tool","Data protection impact assessment tool","","", "", {"DF6"}, set(), False, "V4-2 DPIA still tagged"),
 ("core-shared-services","Shared services ECR registry","","", "", set(), {"BP3"}, False, "V4-2 shared services is an infrastructure name"),
 ("observability-dns-iac","Observability DNS infrastructure","","", "", set(), {"FF"}, False, "V4-2 observability is not firmer foundations"),
 ("council-tax-ufs-frontend","Council tax frontend for HMRC","","", "UK central government and ALBs", set(), {"LOCAL"}, False, "V4-2 central council tax service"),
 ("data-quality-service","Data quality checks for bus timetables","","", "", {"DF5"}, set(), False, "V4-2 data quality is DF5, not DAM cataloguing"),
 ("hmpps-datahub-query-metrics2","Data product query metrics for the prison reporting data hub","","", "", set(), {"DF3"}, False, "V4-2 internal data products are not public data infrastructure"),
 ("govuk-knowledge-graph-gcp","GovSearch knowledge graph of GOV.UK content","","", "", set(), {"DF3"}, False, "V4-2 content search knowledge graph"),
 ("gmp","Integration with the Data Exchange Service (DES)","","", "", set(), {"DF3"}, False, "V4-2 HMRC integration layer name"),
 ("vulnerable-claimants","Support for vulnerable people","","", "", set(), {"FF"}, False, "'vulnerable' is not 'vulnerability'"),
 ("cookie-consent","Cookie consent banner","","", "", set(), {"DF6"}, False, "bare consent removed"),
 ("dns-records","DNS records for example.gov.uk","dns","", "", set(), {"FF"}, False, "D7 bare dns"),
 ("notify-slack","Notify slack channel on deploy","","", "", set(), {"BP1"}, False, "bare notify is not GOV.UK Notify"),
 ("notifications-api","GOV.UK Notify API","","", "", {"BP1"}, set(), False, "GOV.UK Notify still tagged"),
]
fails = 0
for n, d, tp, le, sc, must, mustnot, dam, why in C:
    tags, stds, dm = tag(n, d, tp, le, sc)
    ok = must <= set(tags) and not (mustnot & set(tags)) and (bool(dm) == dam)
    print(("PASS " if ok else "FAIL ") + f"T-{n}: {sorted(tags)} dam={dm}  [{why}]"); fails += not ok
ok = readme_lede("# Title\n\n[![badge](x)](y)\n\nThis tool does a thing.\nIt helps.\n\n## Next") == "This tool does a thing. It helps."
print(("PASS " if ok else "FAIL ") + "T-lede: README lede skips headings and badges"); fails += not ok
ok = standards_from_files(["api/openapi.yaml", "x.ttl", "datapackage.json"]) == {"OpenAPI": 1, "RDF / OWL / SHACL": 1, "Frictionless Data Package": 1}
print(("PASS " if ok else "FAIL ") + "T-files: standards detected from file names"); fails += not ok
ok = sector("ScottishParliament", "U.K. Central") == "Parliament" and sector("osgeouk", "U.K. Central") == "Communities and partnerships" and sector("NHSX", "U.K. Central") == "Health and care" and sector("wmfs", "U.K. Councils") == "Local government"
print(("PASS " if ok else "FAIL ") + "T-sector: sector precedence (Parliament before Scotland; communities separate)"); fails += not ok
saved = taxonomy.CS["BP3"]; taxonomy.CS["BP3"] = re.compile(r"\bplatform\b", re.I)
neg = "BP3" in taxonomy.tag("cloud-platform-terraform-sqs", "Terraform module for the Cloud Platform", "")[0]; taxonomy.CS["BP3"] = saved
print(("PASS " if neg else "FAIL ") + "T-neg: reintroducing bare 'platform' is detected by the suite"); fails += not neg
print(f"{len(C) + 4} taxonomy tests, {fails} failures"); sys.exit(1 if fails else 0)
