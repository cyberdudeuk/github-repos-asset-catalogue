"""Regression tests for the topic rules (RM-02, V718-2): every false match found in the precision sample of 11 November 2026
has a negative test, and the real matches beside it a positive one.  python3 -I build/v6/test_topics.py"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topics import TOPICS, topic_text

RX = {t[0]: re.compile(t[3], re.I) for t in TOPICS}
NOT = [  # (topic, text that must not match): each a sampled false match, as the page matches it (lower case)
    ("place", "dvsa/authentication-ldap [composer]: https://getcomposer.org/"),
    ("place", "dvsa/vol-active-support this library consists of helper methods"),
    ("place", "hmcts/api-cp-caseadmin-case-urn-mapper api spec for caseurn to caseid mapper mapping"),
    ("place", "hmcts/terraform-module-trafficmanager a terraform module for creating azure traffic managers"),
    ("place", "network-rail-business-systems/support-page allows you quickly add a support page to your project"),
    ("place", "department-for-transport/odsconvertr package to convert xlsx files to ods format in r"),
    ("place", "planning-inspectorate/coding-standards configuration and other shared code for implementing our coding standards"),
    ("place", "alphagov/winston a multi-transport async logging library for node.js"),
    ("place", "hmcts/crime-mcp-register runtime plumbing for hmcts crime mcp servers — sse transport, oauth proxy"),
    ("place", "department-for-transport-bods/.github resources used throughout the department for transport's repositories"),
    ("justice", "ministryofjustice/cloud-platform documentation on the moj cloud platform ministry-of-justice"),
    ("justice", "ministryofjustice/moj-job-descriptions official job descriptions for roles within ministry of justice (moj) digital"),
]
YES = [
    ("place", "dvla/address-lookup-service enables address lookup via ordnance survey osplaces api"),
    ("place", "dvsa/mot-document-module document service for the mot testing application"),
    ("place", "dvsa/mes-configuration-service dvsa mobile examiner services for driving tests"),
    ("place", "defra/fmp-app flood mapping for planning"), ("place", "dft/road-traffic-statistics road traffic counts"),
    ("place", "dwp/postcode-format-validation validate a uk postcode"), ("place", "onsdigital/geofile-clipper geospatial clipping"), ("place", "datasciencecampus/transport-performance-visual transport performance"),
    ("justice", "ministryofjustice/yjb-platform the new youth justice platform"), ("justice", "hmcts/et-pet-admin employment tribunals"),
    ("justice", "ministryofjustice/new-probation-services probation"), ("justice", "access to justice research"),
]


def main():
    bad = [f"{t} matches {s!r}" for t, s in NOT if RX[t].search(topic_text(t, s))] + [f"{t} no longer matches {s!r}" for t, s in YES if not RX[t].search(topic_text(t, s))]
    print("\n".join(bad) or f"ok: {len(NOT)} negative and {len(YES)} positive tests")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
