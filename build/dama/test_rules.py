"""Regression tests for DAMA rules: each false positive found in the precision review has a negative test (31 Oct 2026)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import classify
ok = True
def t(label, basic="", readme="", paths=(), deps=(), tf=(), has=(), hasnot=(), vend=(), novend=()):
    global ok; r = classify(basic, readme, list(paths), list(deps), list(tf))
    good = all(c in r["caps"] for c in has) and not any(c in r["caps"] for c in hasnot) and all(v in r["vend"] for v in vend) and not any(v in r["vend"] for v in novend)
    print("PASS" if good else "FAIL", label, "" if good else sorted(r["caps"]) + sorted(r["vend"])); ok &= good
# positives
t("GE dependency", deps=[("py", "great-expectations")], has=["dq-validate"], vend=["gx"])
t("GE config folder", paths=["great_expectations/great_expectations.yml"], has=["dq-validate"], vend=["gx"])
t("Soda checks", paths=["soda/checks.yml"], deps=[("py", "soda-core-postgres")], has=["dq-validate"], vend=["soda"])
t("pointblank in R only", deps=[("r", "pointblank")], has=["dq-validate"], vend=["pointblank"])
t("data quality framework in description", basic="Implements the government data quality framework", has=["dq-framework"])
t("splink linkage", deps=[("py", "splink")], has=["ref-link"], vend=["splink"])
t("dbt project", paths=["dbt_project.yml"], has=["integ-transform"], vend=["dbt"])
t("Glue from Terraform", tf=["aws_glue_job"], has=["integ-transform"], vend=["glue"])
t("CKAN extension", paths=["ckanext-foo/plugin.py"], has=["meta-cat"], vend=["ckan"])
# negatives from the review
t("NEG dq- name prefix is not data quality", basic="dq packer ops linux bastion", hasnot=["dq-framework"])
t("NEG json-schema.org is not schema.org metadata", readme="definitions [json schema](https://json-schema.org/)", hasnot=["meta-dict"])
t("NEG 'pii' inside a journal URL", readme="https://www.sciencedirect.com/science/article/pii/S0010465524001188", hasnot=["sec-pii"])
t("NEG Azure 'Data Owner role'", readme="Azure Service Bus Data Owner role on the resource group", hasnot=["gov-steward"])
t("NEG metrics dashboard link in README", readme="[Metrics dashboard](https://grafana.example)", hasnot=["dwbi-dash"])
t("NEG database mentioned in README only", readme="The application uses a Postgres database", hasnot=["store-db"])
t("NEG TRE as a job name", readme="build.tax.service.gov.uk/job/TRE/job/x", hasnot=["sec-env"])
t("NEG 'validate' npm package is not the R validate package", deps=[("js", "validate")], hasnot=["dq-validate"])
t("NEG 'evidently' as an English word", readme="Evidently, this works", novend=["evidently"])
t("NEG 'healthcheck' isn't health", basic="healthcheck endpoint", hasnot=["dq-framework"])
t("NEG 'profile data' (a user profile) is not profiling", basic="acsp profile data api handling the data", hasnot=["dq-profile"])
t("NEG 'LAA Data Stewardship' is a programme name", basic="Source code for LAA Digital's Access Data Stewardship API", hasnot=["gov-steward"])
t("data stewards in general still match", basic="meet the user needs of data stewards", has=["gov-steward"])
sys.exit(0 if ok else 1)
