"""Regression tests for the tooling register's text patterns (V717-4): every false match found in the precision samples of
10 November 2026 has a negative test, and each tool keeps a positive one.  python3 -I build/dama/test_tools.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import TOOLS, text_rx, supplier_rx

T = {t["id"]: t for t in TOOLS}
NOT_TEXT = [  # (tool, text that must not match) — each from a sampled false match
    ("python", "PANDAS V (Pantograph Damage Assessment System) output"),
    ("excel", "download the databakerExample.xlsx included in this repo"),
    ("esri", "writing to a file based format such as ESRI Shape, MapInfo TAB"),
    ("sharepoint", "Office 365 (including Skype voice and video) access over the LAN"),
    ("sharepoint", "Change Support for New Ways of Working (Microsoft 365)"),
    ("erwin", "Speak to Erwin about this"),
    ("palantir", "the federated data platform procurement"),
]
NOT_SUPPLIER = [("geoplace", "ORDNANCE SURVEY"), ("box", "Box UK Ltd"), ("oracle", "Oracle Corporation UK Ltd"), ("experian", "Experian Ltd"), ("loqate", "GB Group plc")]
YES_TEXT = [("python", "notebooks use pandas and numpy"), ("excel", "an Excel workbook with VBA macros"), ("esri", "published on ArcGIS Online"),
            ("sharepoint", "documents are stored in SharePoint"), ("erwin", "the model is kept in erwin Data Modeler"), ("palantir", "built on Palantir Foundry"),
            ("collibra", "Collibra data catalogue"), ("snowflake", "Provision of a Snowflake Data Cloud")]


def main():
    bad = []
    if "jira" in T: bad.append("jira was removed from the register after its matches proved to be ticket links")
    for tid, text in NOT_TEXT:
        rx = text_rx(T[tid])
        if rx and rx.search(text): bad.append(f"{tid} matches {text!r}")
    for tid, text in NOT_SUPPLIER:
        rx = supplier_rx(T[tid])
        if rx and rx.search(text): bad.append(f"{tid} supplier matches {text!r}")
    for tid, text in YES_TEXT:
        rx = text_rx(T[tid])
        if not (rx and rx.search(text)): bad.append(f"{tid} no longer matches {text!r}")
    print("\n".join(bad) or f"ok: {len(NOT_TEXT) + len(NOT_SUPPLIER) + 1} negative and {len(YES_TEXT)} positive tests")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
