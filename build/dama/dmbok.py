"""The DAMA wheel to activity level (R77): every knowledge area of DAMA-DMBOK2 broken down into the activities that deliver it,
plus the five DMBOK2 topics outside the wheel that enterprise data management also needs, and the data lifecycle.

Source and status, stated on the page: activity groupings summarise the context diagrams of DAMA-DMBOK2 (Revised Edition,
Technics Publications, 2024), in the maintainers' own words. They are not quotations and have not been checked line by line
against the book; DAMA's own list of changes in the revised edition confirms the four activity phases (Plan, Develop,
Control, Operate). UK guidance is linked only where its address was checked (guidance_check.json).

Each activity: id, phase, name, what it is, deliverables, roles, techniques, metrics, UK guidance ids, the repository
capabilities (rules.py) that evidence it, and lifecycle stages. Writes dmbok.json and dmbok_checks.txt.
"""
import json
import os
import re
import sys

H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from rules import AREAS, LIFECYCLE

PHASES = {"P": "Plan", "D": "Develop", "C": "Control", "O": "Operate"}

# ---- UK guidance and standards: id -> (title, publisher, url). Every address is checked by guidance_check.py. ----
GUIDE = {
    "dqf": ("The Government Data Quality Framework", "Government Data Quality Hub", "https://www.gov.uk/government/publications/the-government-data-quality-framework"),
    "ethics": ("Data Ethics Framework", "Central Digital and Data Office", "https://www.gov.uk/government/publications/data-ethics-framework"),
    "atrs": ("Algorithmic Transparency Recording Standard hub", "Department for Science, Innovation and Technology", "https://www.gov.uk/government/collections/algorithmic-transparency-recording-standard-hub"),
    "tcop": ("The Technology Code of Practice", "Central Digital and Data Office", "https://www.gov.uk/guidance/the-technology-code-of-practice"),
    "apistd": ("API technical and data standards", "Government Digital Service", "https://www.gov.uk/guidance/gds-api-technical-and-data-standards"),
    "openstd": ("Open standards for government", "Central Digital and Data Office", "https://www.gov.uk/government/publications/open-standards-for-government"),
    "dsgf": ("Data Sharing Governance Framework", "Central Digital and Data Office", "https://www.gov.uk/government/publications/data-sharing-governance-framework"),
    "servman": ("Service Manual", "Government Digital Service", "https://www.gov.uk/service-manual"),
    "gdsway": ("The GDS Way", "Government Digital Service", "https://gds-way.digital.cabinet-office.gov.uk/"),
    "tna_im": ("Information management", "The National Archives", "https://www.nationalarchives.gov.uk/information-management/"),
    "ico_gdpr": ("UK GDPR guidance and resources", "Information Commissioner's Office", "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"),
    "ico_share": ("Data sharing: a code of practice", "Information Commissioner's Office", "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/data-sharing-a-code-of-practice/"),
    "ico_anon": ("Anonymisation, pseudonymisation and privacy enhancing technologies guidance", "Information Commissioner's Office", "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/"),
    "ncsc_cloud": ("Cloud security guidance", "National Cyber Security Centre", "https://www.ncsc.gov.uk/collection/cloud"),
    "ncsc_caf": ("Cyber Assessment Framework", "National Cyber Security Centre", "https://www.ncsc.gov.uk/collection/cyber-assessment-framework"),
    "gsc": ("Government Security Classifications", "Cabinet Office", "https://www.gov.uk/government/publications/government-security-classifications"),
    "uprn": ("Open standards: identifying property and street information", "Central Digital and Data Office", "https://www.gov.uk/government/publications/open-standards-for-government/identifying-property-and-street-information"),
    "codeprac": ("Code of Practice for Statistics", "Office for Statistics Regulation", "https://osr.statisticsauthority.gov.uk/the-code-of-practice-for-statistics/"),
    "rap": ("Reproducible Analytical Pipelines", "Analysis Function", "https://analysisfunction.civilservice.gov.uk/support/reproducible-analytical-pipelines/"),
    "aqua": ("The Aqua Book: guidance on producing quality analysis for government", "HM Treasury", "https://www.gov.uk/guidance/the-aqua-book"),
    "dsa": ("Data Standards Authority", "Central Digital and Data Office", "https://www.gov.uk/government/groups/data-standards-authority"),
    "dmf": ("Data maturity assessment for government", "Central Digital and Data Office", "https://www.gov.uk/government/publications/data-maturity-assessment-for-government-framework"),
    "five": ("The Five Safes Framework", "Government Digital Service and Office for National Statistics", "https://www.gov.uk/data-ethics-guidance/the-five-safes-framework"),
    "aiplay": ("AI Playbook for the UK Government", "Government Digital Service", "https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government"),
    "gcloud": ("G-Cloud 14 agreement (RM1557.14)", "Crown Commercial Service", "https://www.crowncommercial.gov.uk/agreements/RM1557.14"),
    "cfind": ("Contracts Finder", "Crown Commercial Service", "https://www.contractsfinder.service.gov.uk/"),
    "fts": ("Find a Tender", "Cabinet Office", "https://www.find-tender.service.gov.uk/"),
    "nhsdd": ("NHS Data Model and Dictionary", "NHS England", "https://www.datadictionary.nhs.uk/"),
    "gemini": ("UK GEMINI metadata standard", "Association for Geographic Information", "https://www.agi.org.uk/groups/agi-gemini/"),
    "dcat": ("Data Catalog Vocabulary (DCAT) Version 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/"),
    "skos": ("SKOS Simple Knowledge Organization System Reference", "W3C", "https://www.w3.org/TR/skos-reference/"),
    "openlineage": ("OpenLineage specification", "LF AI and Data Foundation", "https://openlineage.io/"),
    "iso8000": ("ISO 8000-1:2022 Data quality, part 1: overview", "International Organization for Standardization", "https://www.iso.org/standard/81745.html"),
    "iso15489": ("ISO 15489-1:2016 Records management, part 1: concepts and principles", "International Organization for Standardization", "https://www.iso.org/standard/62542.html"),
    "togaf": ("The TOGAF Standard", "The Open Group", "https://www.opengroup.org/togaf"),
    "archimate": ("ArchiMate specification", "The Open Group", "https://www.opengroup.org/archimate-forum/archimate-overview"),
    "dama": ("DAMA-DMBOK: Data Management Body of Knowledge", "DAMA International", "https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/"),
    "dama_changes": ("Changes to DAMA-DMBOK2", "DAMA International", "https://dama.org/cpages/changes-to-dama-dmbok-2"),
    "dama_rev": ("DAMA-DMBOK 2.0: the 2024 revision", "DAMA International", "https://dama.org/dama-dmbok-revision/"),
    # the devolved nations' own guidance (R83): each address checked by guidance_check.py like every other
    "sg_digital": ("A changing nation: how Scotland will thrive in a digital world", "Scottish Government", "https://www.gov.scot/publications/a-changing-nation-how-scotland-will-thrive-in-a-digital-world/"),
    "sg_hscdata": ("Data strategy for health and social care", "Scottish Government", "https://www.gov.scot/publications/data-strategy-health-social-care-2/"),
    "sg_datastd": ("Data standards in Scotland's public sector: framework for action", "Scottish Government", "https://www.gov.scot/publications/framework-action-data-standards-scotlands-public-sector/"),
    "sg_dsss": ("Digital Scotland Service Standard", "Scottish Government", "https://www.gov.scot/publications/digital-scotland-service-standard/"),
    "sg_code": ("Making source code open", "Scottish Government service manual", "https://servicemanual.gov.scot/making-source-code-open"),
    "nrs_rmp": ("Model Records Management Plan guidance (Public Records (Scotland) Act 2011)", "National Records of Scotland", "https://nrscotland.gov.uk/records-and-archives/model-records-management-plan-guidance"),
    "wg_digital": ("Digital strategy for Wales", "Welsh Government", "https://www.gov.wales/digital-strategy-wales-html"),
    "wg_hscdata": ("Digital and data strategy for health and social care in Wales", "Welsh Government", "https://www.gov.wales/digital-and-data-strategy-health-and-social-care-wales-html"),
    "cdps_dss": ("Digital Service Standard for Wales", "Centre for Digital Public Services", "https://digitalpublicservices.gov.wales/guidance-and-standards/digital-service-standard-wales"),
    "ni_opendata": ("Open data strategy for Northern Ireland 2020 to 2023", "Department of Finance (Northern Ireland)", "https://www.finance-ni.gov.uk/publications/open-data-strategy-northern-ireland-2020-2023"),
    "proni_rm": ("Records management for public authorities", "Public Record Office of Northern Ireland", "https://www.proni.gov.uk/records-management-public-authorities"),
}

# ---- Topics outside the wheel that DMBOK2 also covers (chapters 2 and 14 to 17) ----
EXTRA_AREAS = [
    ("ethics", "Data handling ethics", "Ethics", "How data is used fairly and transparently, beyond what the law requires: DMBOK2 chapter 2.", 2),
    ("ds", "Big data and data science", "Data science", "Exploring large and varied data, building and running models, and putting their results to work: DMBOK2 chapter 14.", 14),
    ("mat", "Data management maturity assessment", "Maturity", "Measuring how well data is managed, to plan and track improvement: DMBOK2 chapter 15.", 15),
    ("org", "Data management organisation and roles", "Organisation", "The structures, roles and skills that do data management: DMBOK2 chapter 16.", 16),
    ("chg", "Data management and organisational change", "Change", "Helping people adopt new ways of managing data: DMBOK2 chapter 17.", 17),
]
CHAPTER = {"gov": 3, "arch": 4, "model": 5, "store": 6, "sec": 7, "integ": 8, "doc": 9, "ref": 10, "dwbi": 11, "meta": 12, "dq": 13}

# (code, phase, name, what, deliverables, roles, techniques, metrics, guidance, caps, lifecycle)
A = {}
A["gov"] = [
    ("GOV-01", "P", "Define data governance for the organisation", "Agree what governance must achieve here, its scope and who sponsors it, after assessing readiness and current pain points.",
     "Governance charter; readiness assessment; scope statement", "Chief data officer; senior sponsor; data governance lead", "Readiness and culture assessment; stakeholder mapping", "Sponsor engagement; scope agreed and signed off", ["dmf", "tcop"], ["gov-steward"], ["plan"]),
    ("GOV-02", "P", "Develop the data governance strategy", "Set the goals, principles, roadmap and benefits case for governance, aligned to the organisation's strategy.",
     "Governance strategy and roadmap; benefits case", "Chief data officer; strategy team", "Business alignment workshops; options appraisal", "Roadmap milestones met; benefits realised", ["dmf"], ["gov-steward"], ["plan"]),
    ("GOV-03", "P", "Define the operating model", "Decide the bodies, decision rights, escalation paths and cadence: centralised, federated or hybrid.",
     "Operating model; terms of reference; RACI", "Data governance council; data owners; data stewards", "RACI and decision-rights mapping", "Decisions taken within agreed time; escalations resolved", ["dmf"], ["gov-steward"], ["plan"]),
    ("GOV-04", "D", "Write principles, policies and standards", "Turn the strategy into policies and standards people can follow, and the procedures that apply them.",
     "Data policies; data standards; procedures", "Data governance lead; data owners; legal and information rights", "Policy drafting and consultation; standards adoption", "Policies published and current; exceptions recorded", ["openstd", "dsa", "tcop"], ["gov-steward"], ["plan"]),
    ("GOV-05", "D", "Appoint and support data owners and stewards", "Name accountable owners and working stewards for each data domain, and give them time, training and tools.",
     "Ownership register; steward role profiles; training plan", "Data owners; data stewards; HR and learning", "Domain mapping; role profiles; communities of practice", "Domains with a named owner and steward", ["dmf"], ["gov-steward"], ["plan", "store"]),
    ("GOV-06", "C", "Manage data issues", "Log, triage and resolve data issues and disputes through the operating model, and learn from them.",
     "Issue log; resolution records", "Data stewards; data owners", "Issue triage; root cause analysis", "Issues open and their age; repeat issues", ["dqf"], ["gov-steward", "dq-framework"], ["use"]),
    ("GOV-07", "C", "Assess regulatory compliance", "Identify the laws and rules data must meet (UK GDPR, Data Protection Act 2018, FOI, records law, sector rules) and check compliance.",
     "Compliance register; DPIAs; audit reports", "Data protection officer; information rights; audit", "Compliance mapping; DPIA; audit", "Compliance findings closed; DPIAs completed before change", ["ico_gdpr", "tna_im"], ["gov-steward", "sec-pii"], ["plan", "use", "archive"]),
    ("GOV-08", "O", "Implement and embed governance", "Roll governance out in stages, fund data management work, and make it part of how projects and services run.",
     "Implementation plan; project governance checkpoints", "Programme and project boards; data governance lead", "Stage gates; communications plan", "Projects passing data checkpoints; adoption measures", ["servman", "tcop"], ["gov-steward"], ["plan"]),
    ("GOV-09", "O", "Value data as an asset", "Record what data the organisation holds, what it is worth and what it costs, and use that to set priorities.",
     "Information asset register; valuation; critical data list", "Information asset owners; finance; data owners", "Asset registers; critical data elements; valuation methods", "Assets registered with an owner; critical data identified", ["tna_im", "dmf"], ["gov-steward", "meta-cat"], ["plan", "store"]),
    ("GOV-10", "O", "Measure and report governance", "Track whether governance works, with metrics for adoption, compliance, value and quality, and report them.",
     "Governance scorecard; maturity reassessment", "Data governance council", "Scorecards; maturity assessment", "Scorecard trend; maturity score", ["dmf"], ["gov-maturity", "dq-framework"], ["use"]),
]
A["arch"] = [
    ("ARCH-01", "P", "Establish the data architecture practice", "Set up the role, scope and methods of data architecture, and how it works with enterprise and solution architecture.",
     "Architecture charter; methods; tools", "Enterprise and data architects", "Architecture frameworks (TOGAF, ArchiMate, Zachman)", "Designs reviewed by architecture", ["togaf", "archimate", "tcop"], ["arch-blueprint"], ["plan"]),
    ("ARCH-02", "P", "Understand business strategy and requirements", "Translate strategy and business needs into the data the organisation needs, now and in future.",
     "Data requirements; capability map", "Data architects; business analysts", "Capability and value-chain mapping", "Requirements traced to designs", ["servman"], ["arch-blueprint"], ["plan"]),
    ("ARCH-03", "D", "Develop the enterprise data model", "Model the organisation's main data subjects and their relationships, from conceptual down to logical level.",
     "Enterprise data model; subject area model", "Data architects; data modellers", "Conceptual and logical modelling", "Coverage of subject areas", ["openstd"], ["arch-blueprint", "model-schema"], ["plan"]),
    ("ARCH-04", "D", "Design data flows and integration architecture", "Map how data moves between systems and organisations, and choose patterns for integration and sharing.",
     "Data flow diagrams; integration architecture", "Data and integration architects", "Data flow and lineage mapping", "Flows documented for critical data", ["apistd", "dsgf"], ["arch-blueprint", "integ-exchange"], ["process", "share"]),
    ("ARCH-05", "D", "Design data platforms", "Choose and design the platforms that store and serve data: warehouses, lakes, lakehouses, and the cloud services under them.",
     "Platform architecture; reference architectures", "Data and cloud architects; platform engineers", "Reference architectures; options appraisal", "Platform reuse; cost per workload", ["tcop", "ncsc_cloud"], ["arch-platform"], ["store"]),
    ("ARCH-06", "D", "Design data products and domain ownership", "Organise data as products owned by domains, with contracts for how others can use them (data mesh and similar).",
     "Data product specifications; data contracts", "Domain owners; data product managers", "Data contracts; product thinking", "Data products with owners and contracts", ["dsgf"], ["arch-mesh"], ["share", "use"]),
    ("ARCH-07", "C", "Govern architecture change", "Review designs against standards and the target architecture, and keep the roadmap current.",
     "Architecture decisions (ADRs); roadmap; review records", "Architecture review board", "Architecture decision records; design reviews", "Decisions recorded; exceptions closed", ["gdsway", "tcop"], ["arch-blueprint"], ["plan"]),
]
A["model"] = [
    ("MOD-01", "P", "Plan data modelling", "Decide which models are needed, their notation, naming standards and where they are kept.",
     "Modelling standards; naming conventions", "Data modellers; data architects", "Modelling standards; notation choice (IE, UML, IDEF1X)", "Models meeting the standards", ["openstd", "dsa"], ["model-schema"], ["plan"]),
    ("MOD-02", "D", "Build conceptual models", "Describe the main things the business works with and how they relate, in business terms.",
     "Conceptual models", "Data modellers; subject matter experts", "Entity–relationship modelling; workshops", "Business sign-off of concepts", [], ["model-schema"], ["plan"]),
    ("MOD-03", "D", "Build logical models", "Add attributes, keys and rules, normalised and independent of any technology.",
     "Logical models", "Data modellers", "Normalisation; attribute definition", "Model quality reviews passed", [], ["model-schema"], ["plan"]),
    ("MOD-04", "D", "Build physical models and schemas", "Turn logical models into database, file or message schemas for a chosen technology.",
     "DDL; JSON Schema; XML Schema; Avro or Protobuf schemas", "Data modellers; database developers", "Physical design; denormalisation; schema languages", "Schemas generated from the model", ["apistd"], ["model-schema"], ["store", "process"]),
    ("MOD-05", "D", "Model dimensional and analytical structures", "Design star and snowflake schemas, facts and dimensions for analysis and reporting.",
     "Dimensional models; bus matrix", "BI developers; data modellers", "Dimensional modelling (Kimball); data vault", "Conformed dimensions reused", [], ["model-schema", "dwbi-wh"], ["use"]),
    ("MOD-06", "D", "Model semantics: ontologies and vocabularies", "Describe meaning formally, with ontologies, vocabularies and knowledge graphs, so data can be linked and reasoned over.",
     "Ontologies (OWL); vocabularies (SKOS); knowledge graphs", "Ontologists; information architects", "RDF, OWL, SKOS, SHACL; linked data", "Vocabularies published and reused", ["skos", "dcat", "openstd"], ["model-semantic"], ["plan", "share"]),
    ("MOD-07", "C", "Review, version and manage models", "Review models for quality, keep versions, and keep them in step with the systems they describe.",
     "Model repository; change log", "Data modellers; architecture review", "Model reviews; version control; reverse engineering", "Models current with production", ["gdsway"], ["model-schema", "store-migrate"], ["store"]),
]
A["store"] = [
    ("STO-01", "P", "Plan database technology", "Choose database and storage technologies for each need: relational, document, graph, search, time series or object storage.",
     "Technology standards; database roadmap", "Database architects; platform owners", "Technology appraisal; total cost of ownership", "Workloads on supported technology", ["tcop"], ["store-db"], ["plan", "store"]),
    ("STO-02", "D", "Build and deploy databases", "Create databases and storage with infrastructure as code, sized and secured for their use.",
     "Database instances; infrastructure code", "Database administrators; platform engineers", "Infrastructure as code; environment management", "Environments built from code", ["gdsway", "ncsc_cloud"], ["store-db"], ["store"]),
    ("STO-03", "D", "Manage schema change and migration", "Change schemas safely, migrate data between versions or platforms, and keep environments in step.",
     "Migration scripts; migration plans", "Database developers; administrators", "Versioned migrations (Flyway, Liquibase, Alembic)", "Failed migrations; rollback time", ["gdsway"], ["store-migrate"], ["store"]),
    ("STO-04", "O", "Operate, monitor and tune databases", "Keep databases available and fast: monitoring, capacity, tuning and patching.",
     "Runbooks; performance reports", "Database administrators; site reliability engineers", "Monitoring; query tuning; capacity planning", "Availability; response time; patch currency", ["gdsway"], ["store-db"], ["store", "use"]),
    ("STO-05", "O", "Back up and recover data", "Back data up, test restores, and plan for continuity and disaster recovery.",
     "Backup policy; recovery tests; continuity plans", "Database administrators; continuity managers", "Backups; point-in-time recovery; restore tests", "Recovery point and time objectives met", ["ncsc_caf"], ["store-backup"], ["store", "archive"]),
    ("STO-06", "O", "Retain, archive and purge data", "Keep data as long as needed, move it to cheaper storage, and delete it when its retention period ends.",
     "Retention schedules applied; purge logs", "Database administrators; records managers", "Lifecycle policies; tiered storage", "Data past retention removed", ["tna_im", "ico_gdpr"], ["store-backup", "doc-records"], ["archive", "dispose"]),
]
A["sec"] = [
    ("SEC-01", "P", "Identify security and privacy requirements", "Work out what law, policy and risk require: classification, privacy, retention and who may see what.",
     "Security requirements; classification scheme", "Security architects; data protection officer", "Risk assessment; threat modelling", "Requirements traced to controls", ["gsc", "ico_gdpr", "ncsc_caf"], ["sec-pii"], ["plan"]),
    ("SEC-02", "P", "Define data security policy and standards", "Set policy for access, encryption, logging, retention and sharing, and the standards that apply it.",
     "Security policy; standards", "Chief information security officer", "Policy frameworks", "Policy exceptions", ["ncsc_caf", "gsc"], ["sec-env"], ["plan"]),
    ("SEC-03", "D", "Classify and discover sensitive data", "Find personal and sensitive data wherever it is, and label it.",
     "Data classification; personal data inventory", "Data stewards; security analysts", "Discovery scanning; PII detection; labels", "Share of data classified", ["gsc", "ico_gdpr"], ["sec-pii"], ["create", "store"]),
    ("SEC-04", "D", "Control access", "Grant and review access by role and need to know, with strong authentication and least privilege.",
     "Access model; access reviews", "Identity and access management team; data owners", "Role- and attribute-based access control; single sign-on", "Access reviews done; excess privileges removed", ["ncsc_cloud"], ["sec-env"], ["use", "share"]),
    ("SEC-05", "D", "Protect data: encryption, masking and de-identification", "Encrypt data, mask or tokenise it, and anonymise or pseudonymise it for wider use.",
     "Encryption standards; de-identification methods", "Security engineers; statisticians", "Encryption; tokenisation; k-anonymity; differential privacy", "Data protected at rest and in transit", ["ico_anon", "ncsc_cloud"], ["sec-anon"], ["store", "share"]),
    ("SEC-06", "D", "Create synthetic data", "Generate data that keeps useful patterns without revealing real people, for testing and research.",
     "Synthetic datasets; utility and disclosure reports", "Data scientists; statisticians", "Statistical synthesis; generative models", "Utility retained; disclosure risk", ["ico_anon"], ["sec-synth"], ["create", "share"]),
    ("SEC-07", "O", "Provide secure data environments", "Give researchers and analysts governed access to sensitive data in trusted research environments.",
     "Trusted research environment; access agreements", "Environment operators; data owners", "Five Safes; output checking", "Projects served; outputs checked", ["five", "ico_share"], ["sec-env"], ["use", "share"]),
    ("SEC-08", "C", "Monitor, audit and respond", "Log and audit data access, detect misuse, and respond to breaches.",
     "Audit logs; incident reports", "Security operations; data protection officer", "Logging; security monitoring; breach response", "Incidents detected and reported within 72 hours", ["ncsc_caf", "ico_gdpr"], ["sec-env"], ["use"]),
]
A["integ"] = [
    ("INT-01", "P", "Plan integration and interoperability", "Decide how systems and organisations will exchange data: patterns, standards and the integration architecture.",
     "Integration strategy; interface catalogue", "Integration architects", "Pattern selection (batch, API, event)", "Interfaces documented", ["apistd", "openstd"], ["integ-exchange"], ["plan"]),
    ("INT-02", "D", "Design and build pipelines (ETL and ELT)", "Extract, load and transform data between sources and targets.",
     "Pipelines; transformation code", "Data engineers", "ETL; ELT; SQL transformation (dbt)", "Pipeline success rate; freshness", ["rap"], ["integ-transform", "integ-orch"], ["process"]),
    ("INT-03", "D", "Orchestrate and schedule", "Run pipelines in the right order and at the right time, and recover from failure.",
     "Workflow definitions; schedules", "Data engineers; platform engineers", "Workflow orchestration (Airflow, Dagster, Prefect)", "Runs on time; mean time to recover", [], ["integ-orch"], ["process"]),
    ("INT-04", "D", "Stream and process events", "Move and process data continuously as events happen, with messaging and stream processing.",
     "Event streams; topics; consumers", "Data and platform engineers", "Publish–subscribe; change data capture; stream processing", "End-to-end latency; message loss", [], ["integ-stream"], ["process"]),
    ("INT-05", "D", "Publish and consume APIs", "Expose and use data through APIs, with documentation, versioning and security.",
     "APIs; OpenAPI descriptions; API catalogue entries", "API developers; product owners", "REST, OpenAPI, GraphQL; API management", "API uptime; consumers", ["apistd", "openstd"], ["integ-exchange"], ["share"]),
    ("INT-06", "D", "Share data between organisations", "Agree, set up and run data sharing with other bodies, lawfully and with clear terms.",
     "Data sharing agreements; exchange services", "Data owners; information governance; legal", "Data sharing agreements; secure exchange", "Agreements live and reviewed", ["dsgf", "ico_share"], ["integ-exchange"], ["share"]),
    ("INT-07", "C", "Replicate and virtualise", "Copy data between stores, or present data from many stores as one, without moving it.",
     "Replication jobs; virtual views", "Data engineers", "Replication; data virtualisation; federation", "Replication lag", [], ["integ-transform"], ["process", "use"]),
    ("INT-08", "O", "Monitor integration", "Watch pipelines, interfaces and exchanges for failure, delay and drift.",
     "Integration dashboards; alerts", "Data engineers; operations", "Monitoring; alerting; SLAs", "Incidents; SLA breaches", [], ["integ-orch", "dq-monitor"], ["process"]),
]
A["doc"] = [
    ("DOC-01", "P", "Plan records and content management", "Decide what records and content must be kept, how they are organised and the rules that apply.",
     "Records management policy; file plan; retention schedule", "Records managers; information management", "Classification schemes; retention schedules", "Retention schedule coverage", ["tna_im", "iso15489"], ["doc-records"], ["plan"]),
    ("DOC-02", "D", "Capture and manage documents", "Capture documents into a managed store, index them and control versions.",
     "Document management system; metadata schema", "Records and content managers", "Capture; indexing; version control; OCR", "Documents captured with metadata", ["tna_im"], ["doc-docs"], ["create", "store"]),
    ("DOC-03", "D", "Manage web and published content", "Create, approve and publish content for websites and intranets, and keep it current.",
     "Content management system; content model; style guide", "Content designers; editors", "Content modelling; workflow; publishing", "Content reviewed on time", ["servman"], ["doc-cms"], ["create", "share"]),
    ("DOC-04", "D", "Organise with taxonomies", "Organise documents and content with taxonomies, controlled vocabularies and metadata for findability.",
     "Taxonomies; metadata schemes", "Information architects", "Taxonomy design; faceted classification", "Findability; tagging consistency", ["skos"], ["doc-docs", "meta-dict"], ["store", "use"]),
    ("DOC-05", "O", "Retain, preserve and dispose of records", "Keep records for their retention period, preserve those of lasting value, and dispose of the rest.",
     "Disposal records; transfers to archives; digital preservation", "Records managers; archivists", "Retention; digital preservation; transfer", "Records disposed on schedule; transfers made", ["tna_im", "iso15489"], ["doc-records"], ["archive", "dispose"]),
    ("DOC-06", "O", "Respond to information requests and legal holds", "Find and produce information for FOI, subject access, inquiries and legal discovery.",
     "Request responses; legal holds", "Information rights; legal", "Search; e-discovery; legal hold", "Requests answered on time", ["ico_gdpr", "tna_im"], ["doc-records", "doc-docs"], ["use"]),
]
A["ref"] = [
    ("REF-01", "P", "Identify drivers and requirements", "Find which reference and master data the organisation depends on and what problems duplicates and inconsistency cause.",
     "Requirements; scope of master data domains", "Data architects; data owners", "Domain analysis; impact assessment", "Domains in scope", ["dsa"], ["ref-master"], ["plan"]),
    ("REF-02", "D", "Manage reference data and code lists", "Keep code lists and classifications authoritative, versioned and available to everyone who needs them.",
     "Code lists; reference data service", "Reference data stewards", "Code list management; versioning; registers", "Code lists published and current", ["dsa", "openstd", "nhsdd"], ["ref-codes"], ["store", "share"]),
    ("REF-03", "D", "Manage master data", "Keep one trusted version of core records (people, organisations, places, products) across systems.",
     "Master data hub or register; golden records", "Master data stewards; data owners", "MDM styles (registry, consolidation, coexistence, centralised)", "Duplicate rate; systems using the master", ["dsa"], ["ref-master"], ["store", "share"]),
    ("REF-04", "D", "Match, link and resolve entities", "Find records that are the same thing across sources, and link or merge them.",
     "Matching rules; linked datasets", "Data scientists; data engineers", "Deterministic and probabilistic linkage (Fellegi–Sunter)", "Match precision and recall", ["ico_anon"], ["ref-link"], ["process"]),
    ("REF-05", "D", "Manage addresses and location identifiers", "Use authoritative identifiers for property, streets and places, such as UPRN and USRN.",
     "Address and location data; identifier lookups", "Location data stewards; GIS teams", "Address matching; geocoding", "Records with a UPRN", ["uprn", "gemini"], ["ref-address"], ["create", "store"]),
    ("REF-06", "O", "Govern and publish master and reference data", "Operate change control for master and reference data, and publish it for reuse.",
     "Change log; published registers", "Data stewards; data governance", "Stewardship workflow; registers", "Change requests resolved", ["dsa", "openstd"], ["ref-master", "ref-codes"], ["share"]),
]
A["dwbi"] = [
    ("DW-01", "P", "Understand requirements for analysis", "Find out which decisions, questions and reports the warehouse and BI must support.",
     "BI requirements; KPIs", "BI analysts; business owners", "Requirements workshops; KPI design", "Requirements met", ["aqua"], ["dwbi-bi"], ["plan"]),
    ("DW-02", "D", "Design and build the warehouse or lakehouse", "Design and build the analytical store: layers, models and loading.",
     "Warehouse; lakehouse; marts", "Data engineers; BI developers", "Kimball, Inmon, data vault; medallion layers", "Load success; query performance", ["tcop"], ["dwbi-wh", "arch-platform"], ["store", "process"]),
    ("DW-03", "D", "Develop reports and dashboards", "Build the reports and dashboards people use to see what is happening.",
     "Reports; dashboards", "BI developers; analysts", "Visual design; accessibility (WCAG 2.2)", "Usage; accessibility conformance", ["servman"], ["dwbi-bi", "dwbi-dash"], ["use"]),
    ("DW-04", "D", "Produce statistics and reproducible analysis", "Produce official and analytical outputs with reproducible, quality-assured pipelines.",
     "Statistical outputs; reproducible analytical pipelines", "Statisticians; analysts", "RAP; version control; peer review", "Outputs produced by RAP", ["rap", "codeprac", "aqua"], ["dwbi-stats"], ["use", "share"]),
    ("DW-05", "D", "Enable self-service analytics", "Let people answer their own questions with governed, documented data and tools.",
     "Semantic layer; certified datasets", "BI team; data stewards", "Semantic layers; certified datasets; training", "Self-service users; certified data reuse", [], ["dwbi-bi"], ["use"]),
    ("DW-06", "O", "Operate and tune the warehouse and BI", "Keep loads, refreshes and reports running, fast and trusted.",
     "Operational runbooks; refresh schedules", "BI operations", "Monitoring; tuning; release management", "Refresh success; response times", [], ["dwbi-wh", "dq-monitor"], ["use"]),
]
A["meta"] = [
    ("MET-01", "P", "Define the metadata strategy", "Decide which metadata matters, who owns it, and how it is collected and used.",
     "Metadata strategy; metadata requirements", "Metadata manager; data governance", "Requirements analysis; use cases", "Requirements met", ["dcat", "dsa"], ["meta-cat"], ["plan"]),
    ("MET-02", "D", "Define the metadata architecture and standards", "Choose metadata standards and how metadata is stored, exchanged and linked.",
     "Metadata model; exchange standards (DCAT, Dublin Core)", "Metadata architects", "Metamodels; DCAT; SKOS; schema.org", "Standards adopted", ["dcat", "skos", "gemini"], ["meta-cat", "model-semantic"], ["plan"]),
    ("MET-03", "D", "Build data catalogues", "Describe data assets so people can find, understand and request them.",
     "Data catalogue; dataset descriptions", "Data stewards; catalogue owners", "Harvesting; curation; DCAT publishing", "Assets catalogued; searches that find something", ["dcat", "tna_im"], ["meta-cat"], ["store", "share"]),
    ("MET-04", "D", "Maintain business glossaries and data dictionaries", "Define business terms and data elements consistently, and link them to the data.",
     "Business glossary; data dictionary", "Data stewards", "Term management; data dictionaries", "Terms defined and approved", ["nhsdd", "skos"], ["meta-dict"], ["plan", "use"]),
    ("MET-05", "D", "Capture lineage and impact", "Record where data comes from, how it changes and where it goes, to support trust and impact analysis.",
     "Lineage graphs; impact analysis", "Data engineers; metadata managers", "Automated lineage (OpenLineage); parsing", "Critical data with lineage", ["openlineage"], ["meta-lineage"], ["process"]),
    ("MET-06", "O", "Integrate, distribute and use metadata", "Harvest metadata from systems automatically, keep it current and share it with other catalogues.",
     "Harvesters; metadata APIs; feeds", "Metadata engineers", "Harvesting; APIs; DCAT feeds", "Freshness of metadata", ["dcat", "apistd"], ["meta-cat"], ["share"]),
    ("MET-07", "C", "Govern metadata quality", "Check metadata is complete, correct and current, and fix it when it is not.",
     "Metadata quality reports", "Data stewards", "Completeness rules; review cycles", "Mandatory fields completed", ["dqf"], ["meta-cat", "dq-framework"], ["use"]),
]
A["dq"] = [
    ("DQ-01", "P", "Define high-quality data and the DQ strategy", "Agree what good enough means for each use, and the strategy and roles for getting there.",
     "Data quality strategy; quality requirements", "Data quality lead; data owners", "Fitness-for-purpose definition; dimensions", "Requirements agreed", ["dqf", "iso8000"], ["dq-framework"], ["plan"]),
    ("DQ-02", "P", "Identify critical data and business rules", "Find the data that matters most and the rules it must follow.",
     "Critical data elements; business rules", "Data stewards; business experts", "Critical data element identification; rule capture", "Critical data with rules", ["dqf"], ["dq-framework", "dq-validate"], ["plan"]),
    ("DQ-03", "D", "Profile and assess quality", "Measure data against the rules and dimensions to find what is wrong and how much.",
     "Profiling results; quality assessment", "Data quality analysts", "Profiling; dimension scoring (completeness, accuracy, timeliness, validity, uniqueness, consistency)", "Baseline scores", ["dqf"], ["dq-profile"], ["store", "use"]),
    ("DQ-04", "D", "Validate and test data", "Check data automatically as it is created and moved, and stop or flag what fails.",
     "Validation rules; data tests", "Data engineers", "Expectations; schema validation; data contracts", "Tests passing; defects caught early", ["dqf", "rap"], ["dq-validate"], ["create", "process"]),
    ("DQ-05", "D", "Cleanse and standardise", "Correct, standardise and enrich data, and remove duplicates.",
     "Cleansing routines; standardised data", "Data quality analysts; engineers", "Standardisation; deduplication; enrichment", "Errors corrected; duplicates removed", ["dqf"], ["dq-cleanse", "ref-link"], ["process"]),
    ("DQ-06", "O", "Monitor quality and observability", "Watch quality continuously and alert when it drifts or breaks.",
     "Quality dashboards; alerts; incidents", "Data engineers; stewards", "Data observability; anomaly detection; SPC", "Incidents detected; time to resolve", ["dqf"], ["dq-monitor"], ["process", "use"]),
    ("DQ-07", "C", "Manage quality issues and root causes", "Track quality issues to their root cause and fix the process, not just the data.",
     "Issue log; root cause analyses", "Data stewards; process owners", "Root cause analysis; DMAIC", "Repeat issues", ["dqf"], ["dq-framework"], ["use"]),
    ("DQ-08", "C", "Report quality and improve", "Report quality to owners and users, and plan improvements.",
     "Quality statements; improvement plans", "Data owners; data quality lead", "Quality statements; scorecards", "Quality trend", ["dqf", "codeprac"], ["dq-framework"], ["share"]),
]
A["ethics"] = [
    ("ETH-01", "P", "Set ethical principles for data use", "Agree the values and principles that guide how data and algorithms are used.",
     "Data ethics principles", "Senior leaders; ethics adviser", "Ethics frameworks", "Principles adopted", ["ethics"], ["gov-ethics"], ["plan"]),
    ("ETH-02", "C", "Assess ethical risk", "Assess projects for fairness, transparency, accountability and public benefit.",
     "Ethics assessments", "Project teams; ethics board", "Data Ethics Framework self-assessment", "Projects assessed", ["ethics", "aiplay"], ["gov-ethics"], ["plan", "use"]),
    ("ETH-03", "O", "Be transparent about algorithms", "Publish how algorithmic tools are used in decisions that affect people.",
     "Algorithmic transparency records", "Service owners", "Algorithmic Transparency Recording Standard", "Records published", ["atrs"], ["gov-ethics"], ["share"]),
    ("ETH-04", "C", "Detect and mitigate bias", "Test data and models for bias, and reduce it.",
     "Bias assessments; mitigations", "Data scientists", "Fairness metrics; model cards", "Bias tests run before release", ["aiplay", "ethics"], ["gov-ethics"], ["use"]),
]
A["ds"] = [
    ("DS-01", "P", "Define the data science strategy and use cases", "Decide where data science and AI can help, and how success is measured.",
     "Use case portfolio; success measures", "Head of data science", "Use case assessment", "Use cases delivering value", ["aiplay"], ["dwbi-stats"], ["plan"]),
    ("DS-02", "D", "Acquire and prepare big data", "Bring in large and varied data and prepare it for analysis.",
     "Prepared datasets; feature stores", "Data engineers; data scientists", "Distributed processing (Spark); feature engineering", "Time to prepare data", [], ["integ-transform", "arch-platform"], ["create", "process"]),
    ("DS-03", "D", "Explore and model", "Explore data and build statistical, machine learning or AI models.",
     "Notebooks; models; evaluation reports", "Data scientists", "Machine learning; statistical modelling", "Model performance", ["aqua", "aiplay"], ["dwbi-stats"], ["use"]),
    ("DS-04", "O", "Deploy and monitor models (MLOps)", "Put models into service, monitor drift and performance, and retrain.",
     "Model registry; monitoring", "ML engineers", "MLOps; model monitoring; drift detection", "Models monitored; drift incidents", ["aiplay"], ["dq-monitor"], ["use"]),
    ("DS-05", "D", "Visualise and communicate results", "Show results clearly and accessibly, with their uncertainty.",
     "Visualisations; data stories", "Analysts; data scientists", "Data visualisation; accessible charts", "Use of outputs", ["codeprac"], ["dwbi-dash"], ["use", "share"]),
]
A["mat"] = [
    ("MAT-01", "P", "Choose a maturity model", "Pick a model and scale that fit the organisation, and agree the scope of the assessment.",
     "Assessment plan", "Chief data officer; assessor", "Maturity models (DAMA, CMMI DMM, government data maturity)", "Scope agreed", ["dmf"], ["gov-maturity"], ["plan"]),
    ("MAT-02", "C", "Assess current maturity", "Gather evidence and score current practice in each area.",
     "Maturity scores; evidence", "Assessors; area leads", "Surveys; interviews; evidence review", "Areas assessed", ["dmf"], ["gov-maturity"], ["plan"]),
    ("MAT-03", "P", "Plan improvement", "Set target maturity and the roadmap to reach it.",
     "Improvement roadmap", "Data leadership", "Gap analysis; prioritisation", "Roadmap funded", ["dmf"], ["gov-maturity"], ["plan"]),
    ("MAT-04", "C", "Reassess and track", "Repeat the assessment to measure progress.",
     "Trend reports", "Assessors", "Repeat assessment", "Maturity change", ["dmf"], ["gov-maturity"], ["plan"]),
]
A["org"] = [
    ("ORG-01", "P", "Design the data organisation", "Choose how data management is organised: centralised, decentralised, federated or networked.",
     "Organisation design", "Chief data officer; HR", "Operating model design", "Roles filled", ["dmf"], ["gov-steward"], ["plan"]),
    ("ORG-02", "D", "Define roles and skills", "Describe data roles and the skills they need, and build a skills plan.",
     "Role profiles; skills framework", "Data leadership; profession leads", "Skills frameworks (DDaT)", "Skills gaps closed", [], ["gov-steward"], ["plan"]),
    ("ORG-03", "O", "Build data literacy", "Help everyone understand and use data well.",
     "Learning offer; communities of practice", "Data academy; profession", "Training; communities", "Staff trained", [], ["gov-steward"], ["use"]),
]
A["chg"] = [
    ("CHG-01", "P", "Plan change for data management", "Plan how people will be brought into new data practices and tools.",
     "Change plan; stakeholder map", "Change managers; data leadership", "Change models (Kotter, ADKAR)", "Stakeholders engaged", [], ["gov-steward"], ["plan"]),
    ("CHG-02", "O", "Communicate and support adoption", "Communicate the why, train people and support them while habits change.",
     "Communications; training; support", "Change managers", "Communications; champions networks", "Adoption measures", [], ["gov-steward"], ["use"]),
]

# Activities delivered by people and decisions: tools play only a supporting part (documents, spreadsheets, surveys, meetings),
# so the tooling register names none. The page says so instead of showing an empty list (V717-5).
PEOPLE_LED = {"ARCH-02", "CHG-01", "CHG-02", "DQ-01", "DS-01", "DW-01", "ETH-01", "ETH-02", "ETH-03", "GOV-01", "GOV-02", "GOV-03", "GOV-08",
              "MAT-01", "MAT-02", "MAT-03", "MAT-04", "MET-01", "MOD-01", "ORG-01", "ORG-02", "ORG-03", "REF-01"}

ALL_AREAS = [(a[0], a[1], a[2], a[3], CHAPTER[a[0]], True) for a in AREAS] + [(e[0], e[1], e[2], e[3], e[4], False) for e in EXTRA_AREAS]


GUIDE_NATION = {k: n for n, ks in (("Scotland", ["sg_digital", "sg_hscdata", "sg_datastd", "sg_dsss", "sg_code", "nrs_rmp"]), ("Wales", ["wg_digital", "wg_hscdata", "cdps_dss"]),
                                    ("Northern Ireland", ["ni_opendata", "proni_rm"])) for k in ks}
# where each devolved source applies: added to the activities' own guidance (R83)
DEVOLVED_FOR = {"sg_digital": ["GOV-02", "ARCH-02"], "sg_hscdata": ["GOV-02", "INT-06", "DQ-01"], "sg_datastd": ["GOV-04", "REF-02", "MET-02"],
                "sg_dsss": ["GOV-08", "DOC-03"], "sg_code": ["ARCH-07"], "nrs_rmp": ["DOC-01", "DOC-05", "STO-06"],
                "wg_digital": ["GOV-02", "ARCH-02"], "wg_hscdata": ["GOV-02", "INT-06"], "cdps_dss": ["GOV-08", "DOC-03"],
                "ni_opendata": ["GOV-02", "MET-03", "INT-05"], "proni_rm": ["DOC-01", "DOC-05", "STO-06"]}


def build():
    checks = []
    def check(ok, cid, msg, guards): checks.append(("PASS " if ok else "FAIL ") + f"{cid} {msg}   [guards: {guards}]"); return ok
    caps = {c[0] for a in AREAS for c in a[4]}; lc = {l[0] for l in LIFECYCLE}
    acts = []
    for aid, *_ in ALL_AREAS:
        for code, ph, nm, what, deliv, roles, tech, met, g, cp, life in A[aid]:
            g = list(g) + [k for k, codes in DEVOLVED_FOR.items() if code in codes]
            acts.append(dict(id=code, area=aid, phase=ph, name=nm, what=what, deliverables=deliv, roles=roles, techniques=tech, metrics=met, guidance=g, caps=cp, life=life, people=code in PEOPLE_LED))
    ids = [a["id"] for a in acts]
    check(len(ids) == len(set(ids)), "C-DMB-01", f"{len(ids)} activities, each with its own identifier", "R77")
    check(all(a["area"] in A for a in acts) and set(A) == {x[0] for x in ALL_AREAS}, "C-DMB-02", f"every one of the {len(ALL_AREAS)} areas (11 on the wheel, 5 beyond it) has activities", "R77")
    bad_caps = [(a["id"], c) for a in acts for c in a["caps"] if c not in caps]
    check(not bad_caps, "C-DMB-03", f"every activity's repository capabilities exist in rules.py (unknown: {bad_caps[:3]})", "R77")
    used = {c for a in acts for c in a["caps"]}
    check(caps <= used, "C-DMB-04", f"every one of the {len(caps)} repository capabilities evidences at least one activity (unused: {sorted(caps - used)})", "R77")
    bad_g = [(a["id"], g) for a in acts for g in a["guidance"] if g not in GUIDE]
    check(not bad_g, "C-DMB-05", f"every guidance reference names a known source ({len(GUIDE)} sources)", "R77")
    check(all(a["phase"] in PHASES and a["life"] and set(a["life"]) <= lc for a in acts), "C-DMB-06", "every activity has a DAMA phase and at least one lifecycle stage that exists", "R77")
    check(all(len(a["what"]) >= 40 and a["deliverables"] and a["roles"] and a["techniques"] and a["metrics"] for a in acts), "C-DMB-07", "every activity says what it is, and names deliverables, roles, techniques and metrics", "R77")
    # negative tests: each check must fail on a broken copy
    neg = []
    b = [dict(acts[0], id=acts[1]["id"])] + acts[1:]; neg.append(len({a["id"] for a in b}) == len(b))
    neg.append(all(c in caps for c in ["no-such-cap"]))
    neg.append(all(g in GUIDE for g in ["no-such-guide"]))
    check(not any(neg), "C-DMB-07n", "negative tests: a duplicate id, an unknown capability and an unknown guidance source are each caught", "R77")
    used = {g for a in acts for g in a["guidance"]}
    nations = {n: [k for k, m in GUIDE_NATION.items() if m == n and k in used] for n in ("Scotland", "Wales", "Northern Ireland")}
    ghost = [c for codes in DEVOLVED_FOR.values() for c in codes if c not in ids] + [k for k in DEVOLVED_FOR if k not in GUIDE]
    ghost_neg = [c for c in ["NOPE-01"] if c not in ids] and not all(n for n in {"Northern Ireland": []}.values())   # negative tests: an unknown activity, a nation with none
    check(all(nations.values()) and not ghost and bool(ghost_neg), "C-DMB-09", "each devolved nation has its own guidance on the activities it informs: " + ", ".join(f"{n} {len(v)}" for n, v in nations.items())
          + f" (activities or sources that don't exist: {ghost}); negative tests catch an unknown activity and a nation with no guidance", "R83")
    ok = {}
    gp = os.path.join(H, "guidance_check.json")
    if os.path.exists(gp): ok = json.load(open(gp))
    unchecked = [k for k in GUIDE if not ok.get(k, {}).get("ok")]
    check(not unchecked, "C-DMB-08", f"every guidance address answered when last checked ({__import__('datetime').date.fromisoformat(ok['_checked']).strftime('%-d %B %Y') if ok.get('_checked') else 'never'}); failing: {unchecked}", "R77")
    out = dict(source=dict(name="DAMA-DMBOK2 Revised Edition (2024)", status="Activity groupings summarise DMBOK2's context diagrams in the maintainers' own words. They are not quotations, and have not been checked line by line against the book.",
                           phases_source=GUIDE["dama_changes"][2]),
               phases=PHASES, areas=[dict(id=a[0], name=a[1], short=a[2], desc=a[3], chapter=a[4], wheel=a[5]) for a in ALL_AREAS], activities=acts,
               guidance={k: dict(title=v[0], by=v[1], url=v[2], nation=GUIDE_NATION.get(k, "UK"), checked=ok.get(k, {}).get("ok", False)) for k, v in GUIDE.items()})
    json.dump(out, open(os.path.join(H, "dmbok.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(H, "dmbok_checks.txt"), "w").write("\n".join(checks) + "\n")
    print("\n".join(checks))
    return 0 if all(c.startswith("PASS") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(build())
