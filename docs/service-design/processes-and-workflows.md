# Processes and workflows

## W1: Refresh the data

```mermaid
flowchart TD
  S0["Read the X-Gov repo listing"]
  S1["Clone changed repositories (blobless) and read READMEs, file trees and manifests"]
  S2["Run classifiers: DAMA, APIs, open data, GDS, practices, legacy, themes"]
  S3["Read GOV.UK organisations; rebuild hierarchy and crosswalk"]
  S4["Sample and judge precision; fix rules with negative tests"]
  S0 --> S1
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> D{"Any check failing?"}
  D -- Yes --> Y["Fix the rule, add a negative test, rerun"]
  D -- No --> N["Build"]
```

## W2: Build and verify

```mermaid
flowchart TD
  S0["Assemble the page from parts"]
  S1["Embed data, fonts and test results"]
  S2["Run page self-checks on load"]
  S3["Run the harness (48+ tests)"]
  S4["Run accessibility, width and contrast tests"]
  S0 --> S1
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> D{"All pass?"}
  D -- Yes --> Y["Publish"]
  D -- No --> N["Find the root cause, fix, record the defect and its check"]
```

## W3: Handle a reported defect

```mermaid
flowchart TD
  S0["Reproduce in Chromium"]
  S1["Find the root cause"]
  S2["Write a check that fails on the old build"]
  S3["Fix"]
  S4["Prove the check passes on the new build"]
  S5["Record it in the defect register and release notes"]
  S0 --> S1
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> S5
  S5 --> D{"Full suite still green?"}
  D -- Yes --> Y["Publish a patch release"]
  D -- No --> N["Keep fixing"]
```

## W4: Answer a user question with the catalogue

```mermaid
flowchart TD
  S0["Search or browse"]
  S1["Open the profile"]
  S2["Check status, licence and care"]
  S3["Follow lineage to the evidence"]
  S4["Contact the owner"]
  S0 --> S1
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> D{"Reusable?"}
  D -- Yes --> Y["Reuse and record it"]
  D -- No --> N["Talk to the owner or build"]
```

## W5: Add a new classification

```mermaid
flowchart TD
  S0["Write the rule with word boundaries"]
  S1["Write positive and negative tests"]
  S2["Run it over the catalogue"]
  S3["Sample 15 and judge"]
  S4["Publish precision with the view"]
  S0 --> S1
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> D{"Precision acceptable?"}
  D -- Yes --> Y["Ship, labelled 'judged by Claude, not owner-confirmed'"]
  D -- No --> N["Tighten and resample"]
```

## W6: Integrate another govukOS app

```mermaid
flowchart TD
  S0["Read its ids and link scheme"]
  S1["Add its ids to the crosswalk"]
  S2["Add links out in its format"]
  S3["Offer feeds keyed by GOV.UK slug"]
  S4["Write the change for its owner"]
  S0 --> S1
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> D{"Can this session write there?"}
  D -- Yes --> Y["Make the change with a check"]
  D -- No --> N["Hand over the pack and instructions"]
```
