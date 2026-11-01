"""DAMA-DMBOK2 knowledge areas, capabilities, lifecycle stages and suppliers, as matching rules (31 Oct 2026).
Each capability has up to three kinds of evidence:
  t = words in name, description, topics or README (a lead unless the words name a specific tool),
  p = a file or folder path in the repository's tree (strong: the tool is configured in the code),
  d = a package named in a dependency manifest (strong: the code depends on it).
All patterns are case-insensitive and bounded so 'healthcheck' doesn't match 'health' (see test_rules.py)."""
B = r"(?<![a-z0-9])"; E = r"(?![a-z0-9])"   # word-ish boundaries that also work around _ - . /
def w(*alts): return B + "(?:" + "|".join(alts) + ")" + E

AREAS = [
 # id, label, short label, plain-English description, capabilities [(id, label, t, p, d)]
 ("gov", "Data governance", "Governance", "Who decides about data, and how: ownership, stewardship, policy, ethics and maturity. DAMA puts it at the centre of the wheel because it steers every other area.", [
   ("gov-steward", "Ownership, stewardship and policy", w(r"data governance", r"(?<!laa )(?<!access )data stewards?(?:hip)?", r"data owners?(?:hip)?(?! role)", r"data polic(?:y|ies)", r"data strategy"), None, None),
   ("gov-maturity", "Data maturity assessment", w(r"data maturity", r"maturity (?:assessment|model|framework) for data"), None, None),
   ("gov-ethics", "Data ethics and transparency", w(r"data ethics", r"ethical data", r"algorithmic transparency", r"atrs"), None, None)]),
 ("arch", "Data architecture", "Architecture", "The overall design of an organisation's data estate: platforms, lakes, meshes and the blueprints that connect them.", [
   ("arch-platform", "Data platforms, lakes and lakehouses", w(r"data platforms?", r"data lakes?", r"lakehouse", r"data fabric", r"data hub"), w(r"lakeformation"), None),
   ("arch-mesh", "Data mesh and data products", w(r"data mesh", r"data products?"), None, None),
   ("arch-blueprint", "Data architecture and blueprints", w(r"data architecture", r"enterprise data model", r"reference architecture"), None, None)]),
 ("model", "Data modelling and design", "Modelling", "Describing what data means and how it fits together: models, schemas and ontologies.", [
   ("model-schema", "Schemas and data models", w(r"data models?", r"data modell?ing", r"json[ -]?schemas?", r"schema registry", r"entity[- ]relationship", r"logical model", r"conceptual model"), r"(?:\.schema\.json|\.avsc|\.dbml)$|(?:^|/)schemas?/[^/]+\.json$", w(r"jsonschema", r"fastjsonschema", r"ajv")),
   ("model-semantic", "Ontologies and semantic models", w(r"ontology", r"ontologies", r"linkml", r"rdf", r"owl", r"skos", r"knowledge graph", r"linked data"), r"\.(?:ttl|owl|rdf|jsonld)$|\.linkml\.ya?ml$", w(r"linkml", r"rdflib", r"owlready2", r"pyshacl", r"jena"))]),
 ("store", "Data storage and operations", "Storage", "Running the databases and stores that hold data: provisioning, migration, backup and performance.", [
   ("store-db", "Databases and data stores", w(r"database administration", r"database infrastructure", r"postgres(?:ql)? (?:database|cluster|operator)", r"rds", r"aurora", r"cosmos ?db", r"cloud sql", r"dynamodb", r"mongodb", r"elasticsearch", r"opensearch", r"neo4j", r"cassandra"), r"(?:^|/)(?:rds|aurora|database|db)[^/]*\.tf$", None),
   ("store-migrate", "Database migrations and schema change", w(r"database migrations?", r"schema migrations?", r"flyway", r"liquibase", r"alembic"), r"(?:^|/)db/migrat(?:e|ions?)/|(?:^|/)alembic/|liquibase|(?:^|/)flyway|(?:^|/)migrations/V\d", w(r"flyway-core", r"liquibase-core", r"alembic", r"knex", r"sequelize-cli", r"db-migrate")),
   ("store-backup", "Backup, retention and recovery", w(r"database backups?", r"backup and restore", r"point[- ]in[- ]time recovery", r"disaster recovery"), None, None)]),
 ("sec", "Data security and privacy", "Security", "Keeping data safe and lawful: protecting personal data, pseudonymising, controlling access and creating safe synthetic data.", [
   ("sec-anon", "Anonymisation and pseudonymisation", w(r"anonymi[sz](?:e|ed|es|ing|ation)", r"pseudonymi[sz](?:e|ed|es|ing|ation)", r"de-?identif(?:y|ied|ication)", r"statistical disclosure control", r"differential privacy", r"k-anonymity"), None, w(r"presidio-analyzer", r"presidio-anonymizer", r"sdcmicro", r"arx", r"pyarxaas", r"diffprivlib", r"opendp")),
   ("sec-pii", "Personal data detection and redaction", w(r"(?<!/)pii(?!/)", r"personally identifiable", r"personal data", r"redact(?:ion|ing)?", r"data masking", r"gdpr", r"dpia", r"data protection impact"), None, w(r"presidio-analyzer", r"scrubadub")),
   ("sec-synth", "Synthetic data", w(r"synthetic data", r"synthetic datasets?", r"synthpop"), None, w(r"sdv", r"synthpop", r"faker", r"mimesis", r"ydata-synthetic", r"synthcity")),
   ("sec-env", "Trusted research and secure data environments", w(r"trusted research environments?", r"secure data environments?", r"five safes"), None, None)]),
 ("integ", "Data integration and interoperability", "Integration", "Moving and combining data between systems: pipelines, orchestration, transformation, streaming and exchange.", [
   ("integ-orch", "Pipelines and orchestration", w(r"etl", r"elt", r"data pipelines?", r"airflow", r"dagster", r"prefect", r"luigi", r"nifi", r"data ingestion", r"ingest(?:ion)? pipeline"), r"(?:^|/)dags/[^/]+\.py$|(?:^|/)dagster\.ya?ml$|(?:^|/)airflow\.cfg$", w(r"apache-airflow", r"dagster", r"prefect", r"luigi", r"kedro", r"mage-ai")),
   ("integ-transform", "Transformation (dbt, Spark, Glue)", w(r"dbt", r"pyspark", r"apache spark", r"aws glue", r"databricks", r"data transformations?"), r"(?:^|/)dbt_project\.yml$", w(r"dbt-core", r"dbt-postgres", r"dbt-bigquery", r"dbt-snowflake", r"dbt-redshift", r"dbt-databricks", r"dbt-athena-community", r"dbt-duckdb", r"pyspark", r"spark-core", r"spark-sql", r"aws-glue-libs", r"awsglue", r"polars", r"duckdb")),
   ("integ-stream", "Streaming and messaging", w(r"kafka", r"kinesis", r"event[- ]stream(?:ing)?", r"event hubs?", r"pub/sub", r"change data capture", r"debezium"), None, w(r"kafka-python", r"confluent-kafka", r"kafkajs", r"spring-kafka", r"kafka-clients", r"debezium-core", r"aws-kinesis-agg")),
   ("integ-exchange", "Data sharing and exchange", w(r"data sharing", r"data exchange", r"data[- ]sharing agreements?", r"interoperability", r"data feeds?", r"bulk data", r"file transfer"), None, None)]),
 ("doc", "Document and content management", "Documents", "Looking after documents, records and web content, including archives and digital preservation.", [
   ("doc-records", "Records, archives and digital preservation", w(r"records management", r"electronic records", r"digital preservation", r"digital archives?", r"web archiv(?:e|ing)", r"born[- ]digital", r"retention schedules?"), None, w(r"archivematica", r"bagit")),
   ("doc-docs", "Document management and OCR", w(r"document management", r"edrms", r"sharepoint", r"ocr", r"optical character recognition", r"document (?:classification|extraction)"), None, w(r"pytesseract", r"tesseract\.js", r"textract", r"azure-ai-formrecognizer", r"pdfplumber", r"pymupdf")),
   ("doc-cms", "Web content management", w(r"content management system", r"cms", r"wordpress", r"drupal", r"wagtail", r"headless cms"), r"(?:^|/)wp-content/|(?:^|/)wp-config", w(r"wagtail", r"django-cms", r"strapi", r"contentful", r"@sanity/client"))]),
 ("ref", "Reference and master data", "Reference", "Shared lists and records everyone should agree on: code lists, registers, addresses and organisations, and matching records about the same thing.", [
   ("ref-codes", "Reference data and code lists", w(r"reference data", r"code ?lists?", r"controlled vocabular(?:y|ies)", r"lookup tables?", r"classifications? (?:service|api)"), None, None),
   ("ref-master", "Master data and registers", w(r"master data", r"mdm", r"golden record", r"single view of", r"data registers?", r"canonical (?:register|list)", r"organisation data service", r"ods codes?"), None, None),
   ("ref-address", "Addresses and location identifiers", w(r"uprn", r"usrn", r"addressbase", r"address (?:matching|lookup|index|validation)", r"postcode lookup", r"os places"), None, w(r"postcodes-io", r"ideal-postcodes", r"@ideal-postcodes/core-axios", r"loqate")),
   ("ref-link", "Record linkage and entity resolution", w(r"record linkage", r"entity resolution", r"data linkage", r"deduplicat(?:e|ion)", r"fuzzy matching", r"splink", r"probabilistic matching"), None, w(r"splink", r"recordlinkage", r"dedupe", r"fastlink"))]),
 ("dwbi", "Data warehousing and business intelligence", "Warehousing and BI", "Bringing data together for analysis and decisions: warehouses, dashboards, reports and analytical publishing.", [
   ("dwbi-wh", "Warehouses and analytical stores", w(r"data warehouse", r"warehousing", r"redshift", r"bigquery", r"snowflake", r"synapse", r"athena", r"data marts?"), None, w(r"google-cloud-bigquery", r"snowflake-connector-python", r"snowflake-sqlalchemy", r"redshift_connector", r"databricks-sql-connector", r"pyathena", r"awswrangler", r"bigrquery")),
   ("dwbi-bi", "Business intelligence tools", w(r"business intelligence", r"power ?bi", r"tableau", r"qlik(?:view|sense)?", r"looker", r"superset", r"metabase", r"quicksight"), r"\.(?:pbix|pbit|twb|twbx)$", w(r"apache-superset", r"looker-sdk", r"powerbiclient", r"tableauhyperapi", r"tableauserverclient")),
   ("dwbi-dash", "Dashboards and reporting apps", w(r"data dashboards?", r"interactive dashboards?", r"statistical dashboards?", r"reporting dashboards?", r"power ?bi dashboards?", r"dashboards? (?:of|for|showing) (?:the )?data", r"shiny apps?", r"streamlit", r"management information", r"reporting tool"), r"(?:^|/)(?:app|ui|server)\.R$", w(r"streamlit", r"dash", r"shiny", r"shinydashboard", r"flexdashboard", r"panel", r"voila")),
   ("dwbi-stats", "Statistics and reproducible analytical pipelines", w(r"official statistics", r"statistical (?:release|publication|bulletin)s?", r"reproducible analytical pipelines?", r"rap", r"sdmx"), None, w(r"sdmx1", r"pandasdmx", r"rsdmx", r"targets", r"drake"))]),
 ("meta", "Metadata management", "Metadata", "Describing data so it can be found, understood and trusted: catalogues, dictionaries, lineage and metadata standards.", [
   ("meta-cat", "Data catalogues and discovery", w(r"data catalog(?:ue)?s?", r"data discovery", r"ckan", r"datahub", r"openmetadata", r"amundsen", r"purview", r"collibra", r"alation", r"unity catalog", r"dataplex"), r"(?:^|/)ckanext[^/]*/|\.dhub\.ya?ml$|purview", w(r"ckan", r"acryl-datahub", r"openmetadata-ingestion", r"amundsen-databuilder", r"pyapacheatlas", r"azure-purview-catalog", r"azure-mgmt-purview")),
   ("meta-dict", "Data dictionaries and glossaries", w(r"data dictionar(?:y|ies)", r"business glossar(?:y|ies)", r"metadata (?:standard|schema|model)s?", r"dcat", r"dublin core", r"csvw", r"(?<!json-)schema\.org"), r"csv-metadata\.json$|(?:^|/)datapackage\.json$|\.dcat\.json$", w(r"frictionless", r"datapackage", r"csvw")),
   ("meta-lineage", "Lineage", w(r"data lineage", r"lineage", r"openlineage", r"marquez"), None, w(r"openlineage-python", r"openlineage-airflow", r"openlineage-dbt", r"openlineage-integration-common"))]),
 ("dq", "Data quality", "Quality", "Whether data is fit for use: profiling it, testing it against rules, monitoring it over time, and fixing it.", [
   ("dq-profile", "Profiling", w(r"data profiling", r"profiling (?:the )?data", r"pandas[- ]profiling", r"ydata[- ]profiling", r"sweetviz", r"skimr"), None, w(r"ydata-profiling", r"pandas-profiling", r"sweetviz", r"skimr", r"dataexplorer", r"summarytools")),
   ("dq-validate", "Validation and data testing", w(r"data validation", r"validat(?:e|es|ing) (?:the )?data", r"data tests?", r"data testing", r"great[ _-]?expectations", r"soda[ -]core", r"soda checks", r"deequ", r"pandera", r"pointblank", r"assertr", r"dbt tests?", r"csvlint", r"goodtables", r"frictionless validat\w*"), r"(?:^|/)great_expectations(?:/|\.ya?ml$)|(?:^|/)gx/great_expectations\.ya?ml$|(?:^|/)expectations/[^/]+\.json$|(?:^|/)soda/|(?:^|/)checks?\.ya?ml$", w(r"great[_-]expectations", r"great-expectations", r"soda-core", r"soda-core-[a-z]+", r"soda-sql", r"pydeequ", r"deequ", r"pandera", r"pointblank", r"assertr", r"validate", r"dbt-expectations", r"goodtables", r"csvlint", r"whylogs", r"datacompy", r"cuallee")),
   ("dq-monitor", "Monitoring and observability", w(r"data observability", r"data quality monitoring", r"monitor(?:ing)? data quality", r"data drift", r"anomal(?:y|ies) in data", r"monte carlo data", r"elementary data"), None, w(r"elementary-data", r"evidently", r"whylogs", r"montecarlodata", r"great-expectations-cloud")),
   ("dq-cleanse", "Cleansing and standardisation", w(r"data cleans?ing", r"data cleaning", r"clean(?:s?e|ing) (?:the )?data", r"data standardi[sz]ation", r"data wrangling", r"janitor"), None, w(r"pyjanitor", r"janitor", r"cleanlab", r"openrefine")),
   ("dq-framework", "Quality frameworks, assessment and reporting", w(r"data quality", r"data quality dimensions?", r"data quality (?:framework|dashboard|report|assessment|scores?|rules?)", r"dataqualitydashboard"), None, w(r"dataqualitydashboard"))]),
]

LIFECYCLE = [
 ("plan", "Plan and design", w(r"data strategy", r"data models?", r"data modell?ing", r"schemas?", r"data architecture", r"data governance", r"requirements")),
 ("create", "Create and collect", w(r"collect(?:s|ed|ion|ing)?", r"surveys?", r"capture", r"data entry", r"forms? (?:builder|runner|service)", r"ingest(?:s|ed|ion|ing)?", r"scrap(?:e|er|ing)", r"sensors?")),
 ("store", "Store and maintain", w(r"databases?", r"data stores?", r"storage", r"data lakes?", r"warehouses?", r"lakehouse", r"backups?")),
 ("process", "Process and integrate", w(r"etl", r"elt", r"pipelines?", r"transform(?:s|ed|ation|ations|ing)?", r"clean(?:s?e|ing)", r"orchestrat(?:e|ion)", r"integrat(?:e|es|ion|ing)", r"linkage", r"matching", r"validat(?:e|ion|ing)")),
 ("use", "Use and analyse", w(r"analys(?:e|is|es|ing)", r"analytics", r"dashboards?", r"reports?", r"reporting", r"visuali[sz](?:e|ation|ations)", r"models? (?:for|to) predict", r"statistics", r"machine learning", r"insights?")),
 ("share", "Share and publish", w(r"publish(?:es|ed|ing)?", r"open data", r"data sharing", r"share data", r"apis?", r"exports?", r"downloads?", r"data feeds?", r"catalog(?:ue)?s?")),
 ("archive", "Archive and retain", w(r"archiv(?:e|es|ed|ing|al)", r"preservation", r"retention", r"long[- ]term storage", r"records management")),
 ("dispose", "Dispose", w(r"delet(?:e|ion) of data", r"data deletion", r"disposal", r"purg(?:e|ing)", r"right to erasure", r"retention schedules?", r"destroy(?:ed|ing)? data"))]

# Suppliers. type: Commercial | Open core | Open source | Cloud service | Public sector. Types are as generally described as at June 2026: check before relying on them.
VENDORS = [
 # id, name, supplier, type, areas, text, path, deps
 ("gx", "Great Expectations", "Great Expectations (GX)", "Open core", ["dq"], w(r"great[ _-]?expectations", r"gx cloud"), r"(?:^|/)great_expectations(?:/|\.ya?ml$)|(?:^|/)gx/great_expectations\.ya?ml$", w(r"great[_-]expectations", r"great-expectations", r"great_expectations_cloud")),
 ("soda", "Soda", "Soda Data", "Open core", ["dq"], w(r"soda[ -]core", r"soda[ -]sql", r"soda checks", r"soda cloud", r"sodacl"), r"(?:^|/)soda/", w(r"soda-core", r"soda-core-[a-z]+", r"soda-sql")),
 ("deequ", "Deequ", "Amazon Web Services (open source)", "Open source", ["dq"], w(r"deequ", r"pydeequ"), None, w(r"pydeequ", r"deequ")),
 ("pandera", "Pandera", "Union.ai (open source)", "Open source", ["dq"], w(r"pandera"), None, w(r"pandera")),
 ("pointblank", "pointblank", "Posit (open source)", "Open source", ["dq"], w(r"pointblank"), None, w(r"pointblank")),
 ("ydata", "ydata-profiling", "YData (open source)", "Open source", ["dq"], w(r"ydata[- ]profiling", r"pandas[- ]profiling"), None, w(r"ydata-profiling", r"pandas-profiling")),
 ("frictionless", "Frictionless Data", "Open Knowledge Foundation", "Open source", ["dq", "meta"], w(r"frictionless", r"goodtables"), r"(?:^|/)datapackage\.json$", w(r"frictionless", r"goodtables", r"datapackage")),
 ("csvlint", "CSVLint", "Open Data Institute", "Open source", ["dq"], w(r"csvlint"), None, w(r"csvlint")),
 ("elementary", "Elementary", "Elementary Data", "Open core", ["dq"], w(r"elementary data", r"elementary-data"), None, w(r"elementary-data")),
 ("evidently", "Evidently", "Evidently AI", "Open core", ["dq"], w(r"evidently ai", r"evidentlyai"), None, w(r"evidently")),
 ("montecarlo", "Monte Carlo", "Monte Carlo Data", "Commercial", ["dq"], w(r"monte carlo data", r"montecarlodata"), None, w(r"montecarlodata", r"pycarlo")),
 ("informatica", "Informatica", "Informatica", "Commercial", ["dq", "meta", "integ", "ref"], w(r"informatica", r"powercenter", r"iics"), None, None),
 ("ataccama", "Ataccama", "Ataccama", "Commercial", ["dq", "ref"], w(r"ataccama"), None, None),
 ("experian", "Experian data quality", "Experian", "Commercial", ["dq", "ref"], w(r"experian aperture", r"aperture data studio", r"experian pandora", r"experian data quality", r"experian address"), None, None),
 ("talend", "Talend", "Qlik (Talend)", "Commercial", ["dq", "integ"], w(r"talend"), None, None),
 ("splink", "Splink", "Ministry of Justice (open source)", "Public sector", ["ref", "dq"], w(r"splink"), None, w(r"splink")),
 ("dbt", "dbt", "dbt Labs", "Open core", ["integ", "dq"], w(r"dbt", r"dbt[- ]core", r"dbt cloud"), r"(?:^|/)dbt_project\.yml$", w(r"dbt-core", r"dbt-[a-z]+")),
 ("airflow", "Apache Airflow", "Apache Software Foundation", "Open source", ["integ"], w(r"apache airflow", r"airflow"), r"(?:^|/)dags/[^/]+\.py$|(?:^|/)airflow\.cfg$", w(r"apache-airflow")),
 ("dagster", "Dagster", "Dagster Labs", "Open core", ["integ"], w(r"dagster"), r"(?:^|/)dagster\.ya?ml$", w(r"dagster")),
 ("prefect", "Prefect", "Prefect Technologies", "Open core", ["integ"], w(r"prefect"), None, w(r"prefect")),
 ("spark", "Apache Spark", "Apache Software Foundation", "Open source", ["integ", "dwbi"], w(r"apache spark", r"pyspark", r"spark"), None, w(r"pyspark", r"spark-core", r"spark-sql")),
 ("kafka", "Apache Kafka", "Apache Software Foundation (Confluent offers a paid edition)", "Open source", ["integ"], w(r"kafka", r"confluent"), None, w(r"kafka-python", r"confluent-kafka", r"kafkajs", r"spring-kafka", r"kafka-clients")),
 ("glue", "AWS Glue", "Amazon Web Services", "Cloud service", ["integ", "meta"], w(r"aws glue", r"glue jobs?", r"glue catalog", r"glue crawler"), r"glue", w(r"aws-glue-libs", r"awsglue")),
 ("adf", "Azure Data Factory", "Microsoft", "Cloud service", ["integ"], w(r"azure data factory", r"adf pipelines?"), r"(?:^|/)(?:adf|datafactory|data-factory)/", w(r"azure-mgmt-datafactory")),
 ("databricks", "Databricks", "Databricks", "Commercial", ["dwbi", "integ", "meta"], w(r"databricks", r"unity catalog", r"delta lake"), r"databricks", w(r"databricks-sql-connector", r"databricks-sdk", r"databricks-connect", r"delta-spark")),
 ("snowflake", "Snowflake", "Snowflake", "Commercial", ["dwbi"], w(r"snowflake"), None, w(r"snowflake-connector-python", r"snowflake-sqlalchemy", r"snowflake-snowpark-python", r"dbt-snowflake")),
 ("bigquery", "Google BigQuery", "Google Cloud", "Cloud service", ["dwbi"], w(r"bigquery"), None, w(r"google-cloud-bigquery", r"bigrquery", r"dbt-bigquery", r"@google-cloud/bigquery")),
 ("redshift", "Amazon Redshift", "Amazon Web Services", "Cloud service", ["dwbi"], w(r"redshift"), None, w(r"redshift_connector", r"dbt-redshift", r"sqlalchemy-redshift")),
 ("athena", "Amazon Athena", "Amazon Web Services", "Cloud service", ["dwbi"], w(r"athena"), None, w(r"pyathena", r"awswrangler", r"dbt-athena-community")),
 ("synapse", "Azure Synapse and Fabric", "Microsoft", "Cloud service", ["dwbi"], w(r"azure synapse", r"synapse analytics", r"microsoft fabric"), None, w(r"azure-synapse-artifacts", r"azure-mgmt-synapse")),
 ("powerbi", "Power BI", "Microsoft", "Commercial", ["dwbi"], w(r"power ?bi"), r"\.(?:pbix|pbit)$", w(r"powerbiclient")),
 ("tableau", "Tableau", "Salesforce (Tableau)", "Commercial", ["dwbi"], w(r"tableau"), r"\.(?:twb|twbx)$", w(r"tableauhyperapi", r"tableauserverclient")),
 ("qlik", "Qlik", "Qlik", "Commercial", ["dwbi"], w(r"qlik(?:view|sense)?"), None, None),
 ("looker", "Looker", "Google Cloud", "Commercial", ["dwbi"], w(r"looker"), r"\.lkml$", w(r"looker-sdk")),
 ("superset", "Apache Superset", "Apache Software Foundation", "Open source", ["dwbi"], w(r"superset"), None, w(r"apache-superset")),
 ("metabase", "Metabase", "Metabase", "Open core", ["dwbi"], w(r"metabase"), None, None),
 ("shiny", "Shiny", "Posit", "Open source", ["dwbi"], w(r"shiny", r"r shiny"), r"(?:^|/)(?:app|ui|server)\.R$", w(r"shiny", r"shinydashboard")),
 ("streamlit", "Streamlit", "Snowflake (open source)", "Open source", ["dwbi"], w(r"streamlit"), None, w(r"streamlit")),
 ("dash", "Plotly Dash", "Plotly", "Open core", ["dwbi"], w(r"plotly dash", r"dash app"), None, w(r"dash")),
 ("sas", "SAS", "SAS Institute", "Commercial", ["dwbi"], w(r"sas", r"sas viya"), r"\.sas$", w(r"saspy")),
 ("ckan", "CKAN", "Open Knowledge Foundation", "Open source", ["meta"], w(r"ckan"), r"(?:^|/)ckanext[^/]*/|(?:^|/)ckan\.ini$", w(r"ckan")),
 ("datahub", "DataHub", "Acryl Data (open source DataHub)", "Open core", ["meta"], w(r"datahub", r"acryl"), r"\.dhub\.ya?ml$", w(r"acryl-datahub")),
 ("openmetadata", "OpenMetadata", "Collate (open source OpenMetadata)", "Open core", ["meta"], w(r"openmetadata"), None, w(r"openmetadata-ingestion")),
 ("amundsen", "Amundsen", "LF AI and Data Foundation", "Open source", ["meta"], w(r"amundsen"), None, w(r"amundsen-databuilder", r"amundsen-common")),
 ("purview", "Microsoft Purview", "Microsoft", "Cloud service", ["meta", "sec"], w(r"purview"), r"purview", w(r"pyapacheatlas", r"azure-purview-catalog", r"azure-mgmt-purview")),
 ("collibra", "Collibra", "Collibra", "Commercial", ["meta", "gov", "dq"], w(r"collibra"), None, None),
 ("alation", "Alation", "Alation", "Commercial", ["meta"], w(r"alation"), None, None),
 ("dataplex", "Google Dataplex", "Google Cloud", "Cloud service", ["meta", "dq"], w(r"dataplex"), None, w(r"google-cloud-dataplex")),
 ("openlineage", "OpenLineage", "LF AI and Data Foundation", "Open source", ["meta"], w(r"openlineage", r"marquez"), None, w(r"openlineage-python", r"openlineage-airflow", r"openlineage-dbt")),
 ("linkml", "LinkML", "LinkML community", "Open source", ["model", "meta"], w(r"linkml"), r"\.linkml\.ya?ml$", w(r"linkml", r"linkml-runtime")),
 ("presidio", "Presidio", "Microsoft (open source)", "Open source", ["sec"], w(r"presidio"), None, w(r"presidio-analyzer", r"presidio-anonymizer")),
 ("sdv", "Synthetic Data Vault", "DataCebo", "Open core", ["sec"], w(r"synthetic data vault", r"sdv"), None, w(r"sdv")),
 ("sdcmicro", "sdcMicro", "Statistics Austria and partners (open source)", "Open source", ["sec"], w(r"sdcmicro"), None, w(r"sdcmicro")),
 ("ordnance", "Ordnance Survey data", "Ordnance Survey", "Public sector", ["ref"], w(r"ordnance survey", r"addressbase", r"os places", r"os data hub", r"os maps api"), None, w(r"osdatahub")),
 ("loqate", "Loqate", "GBG (Loqate)", "Commercial", ["ref"], w(r"loqate"), None, w(r"loqate")),
 ("idealpostcodes", "Ideal Postcodes and postcodes.io", "Ideal Postcodes", "Open core", ["ref"], w(r"ideal postcodes", r"postcodes\.io"), None, w(r"postcodes-io", r"@ideal-postcodes/core-axios", r"ideal-postcodes")),
 ("sharepoint", "SharePoint", "Microsoft", "Commercial", ["doc"], w(r"sharepoint"), None, w(r"office365-rest-python-client", r"@pnp/sp", r"sharepy")),
 ("wordpress", "WordPress", "WordPress Foundation (Automattic offers hosting)", "Open source", ["doc"], w(r"wordpress"), r"(?:^|/)wp-content/|(?:^|/)wp-config", None),
 ("drupal", "Drupal", "Drupal Association", "Open source", ["doc"], w(r"drupal"), None, w(r"drupal/core", r"drupal/core-recommended")),
 ("wagtail", "Wagtail", "Wagtail community (Torchbox)", "Open source", ["doc"], w(r"wagtail"), None, w(r"wagtail")),
 ("archivematica", "Archivematica", "Artefactual Systems", "Open source", ["doc"], w(r"archivematica"), None, None),
 ("preservica", "Preservica", "Preservica", "Commercial", ["doc"], w(r"preservica"), None, w(r"pypreservica")),
 ("tesseract", "Tesseract OCR", "Open source (originally Google)", "Open source", ["doc"], w(r"tesseract"), None, w(r"pytesseract", r"tesseract\.js")),
 ("textract", "Amazon Textract", "Amazon Web Services", "Cloud service", ["doc"], w(r"textract"), None, w(r"amazon-textract-caller", r"amazon-textract-textractor")),
 ("flyway", "Flyway", "Redgate", "Open core", ["store"], w(r"flyway"), r"(?:^|/)flyway|(?:^|/)migrations/V\d", w(r"flyway-core", r"flyway-database-postgresql")),
 ("liquibase", "Liquibase", "Liquibase", "Open core", ["store"], w(r"liquibase"), r"liquibase", w(r"liquibase-core")),
 ("mongodb", "MongoDB", "MongoDB", "Open core", ["store"], w(r"mongodb", r"mongo"), None, w(r"pymongo", r"mongodb", r"mongoose", r"mongodb-driver-sync")),
 ("elastic", "Elasticsearch and OpenSearch", "Elastic; OpenSearch Software Foundation", "Open core", ["store", "dwbi"], w(r"elasticsearch", r"opensearch", r"kibana"), None, w(r"elasticsearch", r"@elastic/elasticsearch", r"opensearch-py", r"@opensearch-project/opensearch")),
 ("neo4j", "Neo4j", "Neo4j", "Open core", ["store", "model"], w(r"neo4j", r"cypher"), None, w(r"neo4j", r"py2neo", r"neo4j-driver")),
 ("dynamodb", "Amazon DynamoDB", "Amazon Web Services", "Cloud service", ["store"], w(r"dynamodb"), None, None),
 ("cosmos", "Azure Cosmos DB", "Microsoft", "Cloud service", ["store"], w(r"cosmos ?db"), None, w(r"azure-cosmos", r"@azure/cosmos")),
]

# Terraform resource types and providers: infrastructure the code creates (strong evidence). pattern -> (capability, vendor or None)
TERRAFORM = [
 (r"^aws_glue_", "integ-transform", "glue"), (r"^aws_glue_catalog_", "meta-cat", "glue"), (r"^azurerm_data_factory", "integ-orch", "adf"),
 (r"^google_bigquery_", "dwbi-wh", "bigquery"), (r"^aws_redshift", "dwbi-wh", "redshift"), (r"^aws_athena_", "dwbi-wh", "athena"),
 (r"^(?:provider|source):(?:snowflake|snowflake-labs/snowflake|snowflakedb/snowflake)$|^snowflake_", "dwbi-wh", "snowflake"),
 (r"^(?:provider|source):(?:databricks|databricks/databricks)$|^databricks_", "dwbi-wh", "databricks"),
 (r"^azurerm_purview_", "meta-cat", "purview"), (r"^google_dataplex_", "meta-cat", "dataplex"), (r"^azurerm_synapse_", "dwbi-wh", "synapse"),
 (r"^aws_dynamodb_table$", "store-db", "dynamodb"), (r"^azurerm_cosmosdb_", "store-db", "cosmos"),
 (r"^aws_db_instance$|^aws_rds_cluster$|^azurerm_(?:postgresql|mssql|mysql)_|^google_sql_database", "store-db", None),
 (r"^aws_db_snapshot|^aws_backup_", "store-backup", None),
 (r"^aws_lakeformation_", "arch-platform", None), (r"^aws_kinesis_|^aws_msk_|^azurerm_eventhub", "integ-stream", "kafka"),
 (r"^aws_quicksight_", "dwbi-bi", None), (r"^aws_(?:elasticsearch|opensearch)_domain", "store-db", "elastic"),
 (r"^aws_dms_", "integ-orch", None), (r"^aws_macie2?_", "sec-pii", None), (r"^aws_sfn_state_machine$|^aws_mwaa_environment$", "integ-orch", None),
]

NAME_ONLY = {"store-db", "dwbi-dash", "integ-stream", "gov-steward", "doc-docs", "arch-platform"}
