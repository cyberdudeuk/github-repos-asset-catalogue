"""The tooling register (R77): tools and products that deliver DAMA activities, with how each is recognised in evidence.

One row per tool:  id | name | maker | model | activities | text pattern | supplier pattern
  model       Open source, Open core, Commercial, Cloud service or Public sector (built and shared by a public body)
  activities  DMBOK activity codes from dmbok.py the tool is used for
  text        how the product is named in a README, a repository description or a tender notice (strict: product names, not
              generic words); empty means the tool is only recognised through rules.py repository evidence
  supplier    how its maker appears as a supplier in an award notice; empty when the maker is not a supplier (open source)
Tools that rules.py already detects in code (VENDORS) keep their repository evidence: file and dependency patterns there.
"""
import re

ROWS = r"""
gx|Great Expectations|Great Expectations (GX)|Open core|DQ-04 DQ-03 DQ-06 DQ-08|great[ _-]?expectations|great expectations
soda|Soda|Soda Data|Open core|DQ-04 DQ-06 DQ-08|soda[ -]core|soda[ -]cloud|soda data|soda data (?:nv|ltd)
deequ|Deequ|Amazon Web Services (open source)|Open source|DQ-04 DQ-03|pydeequ|amazon deequ|aws deequ|
pandera|Pandera|Union.ai (open source)|Open source|DQ-04|pandera|
pointblank|pointblank|Posit (open source)|Open source|DQ-04|pointblank|
ydata|ydata-profiling|YData (open source)|Open source|DQ-03|ydata[ -]profiling|pandas[ -]profiling|
frictionless|Frictionless Data|Open Knowledge Foundation|Open source|DQ-04 MET-03|frictionless data|frictionless[ -]py|data ?package|
csvlint|CSVLint|Open Data Institute|Open source|DQ-04|csvlint|
elementary|Elementary|Elementary Data|Open core|DQ-06|elementary[ -]data|elementary data
evidently|Evidently|Evidently AI|Open core|DQ-06 DS-04 ETH-04|evidently ?ai|evidently ai
montecarlo|Monte Carlo|Monte Carlo Data|Commercial|DQ-06|monte carlo data|monte carlo data
informatica|Informatica|Informatica|Commercial|DQ-03 DQ-05 INT-02 MET-03 REF-03 GOV-04 DQ-02 DQ-08|informatica|informatica
ataccama|Ataccama|Ataccama|Commercial|DQ-03 DQ-05 REF-03 MET-03 DQ-02 DQ-08|ataccama|ataccama
experian|Experian Aperture Data Studio|Experian|Commercial|DQ-03 DQ-05 REF-05|aperture data studio|experian (?:data quality|pandora|aperture)|
talend|Talend|Qlik (Talend)|Commercial|INT-02 DQ-05|talend|talend
splink|Splink|Ministry of Justice (open source)|Public sector|REF-04 DQ-05|splink|
dbt|dbt|dbt Labs|Open core|INT-02 DQ-04 MET-05 ARCH-06 MOD-05|dbt[ -](?:core|cloud|labs)|data build tool|dbt labs
airflow|Apache Airflow|Apache Software Foundation|Open source|INT-03 INT-08|apache airflow|airflow dags?|mwaa|cloud composer|astronomer
dagster|Dagster|Dagster Labs|Open core|INT-03 MET-05|dagster|dagster labs|elementl
prefect|Prefect|Prefect Technologies|Open core|INT-03|prefect (?:flows?|cloud|orion)|prefect technologies
spark|Apache Spark|Apache Software Foundation|Open source|INT-02 DS-02 DW-02|apache spark|pyspark|spark ?sql|
kafka|Apache Kafka|Apache Software Foundation (Confluent offers a paid edition)|Open source|INT-04|apache kafka|confluent (?:cloud|platform|kafka)|kafka streams|confluent
glue|AWS Glue|Amazon Web Services|Cloud service|INT-02 MET-03|aws glue|glue data catalog|
adf|Azure Data Factory|Microsoft|Cloud service|INT-02 INT-03|azure data factory|
databricks|Databricks|Databricks|Commercial|DW-02 DS-02 DS-03 INT-02 MET-03 ARCH-06 DW-06|databricks|unity catalog|databricks
snowflake|Snowflake|Snowflake|Commercial|DW-02 STO-01 DW-06|snowflake (?:data cloud|computing|warehouse|account)|snowpark|snowflake (?:computing|inc)
bigquery|Google BigQuery|Google Cloud|Cloud service|DW-02|bigquery|
redshift|Amazon Redshift|Amazon Web Services|Cloud service|DW-02|amazon redshift|aws redshift|redshift (?:cluster|serverless)|
athena|Amazon Athena|Amazon Web Services|Cloud service|DW-02 INT-07|amazon athena|aws athena|
synapse|Azure Synapse and Microsoft Fabric|Microsoft|Cloud service|DW-02 INT-02|azure synapse|microsoft fabric|synapse analytics|
powerbi|Power BI|Microsoft|Commercial|DW-03 DW-05|power ?bi|
tableau|Tableau|Salesforce (Tableau)|Commercial|DW-03 DW-05|tableau|tableau software
qlik|Qlik|Qlik|Commercial|DW-03 DW-05|qlik ?(?:view|sense|cloud)|qliktech|qlik
looker|Looker|Google Cloud|Commercial|DW-03 DW-05|looker(?: studio)?|lookml|
superset|Apache Superset|Apache Software Foundation|Open source|DW-03|apache superset|preset\.io|
metabase|Metabase|Metabase|Open core|DW-03 DW-05|metabase|
shiny|Shiny|Posit|Open source|DW-03 DS-05|r ?shiny|shiny (?:app|server|dashboard)|shinyapps|posit (?:connect|pbc)|rstudio connect|
streamlit|Streamlit|Snowflake (open source)|Open source|DW-03 DS-05|streamlit|
dash|Plotly Dash|Plotly|Open core|DW-03 DS-05|plotly dash|dash plotly|dash app|plotly
sas|SAS|SAS Institute|Commercial|DW-04 DS-03 DQ-05|sas (?:viya|institute|enterprise guide|software|analytics|9\.4|grid|eminer|visual analytics|data management)|sas institute|sas software
ckan|CKAN|Open Knowledge Foundation|Open source|MET-03 MET-06 MET-02|ckan|
datahub|DataHub|Acryl Data (open source DataHub)|Open core|MET-03 MET-05 ARCH-06 MET-02 MET-07|datahub (?:project|metadata|gms)|linkedin datahub|acryl data|acryl
openmetadata|OpenMetadata|Collate (open source OpenMetadata)|Open core|MET-03 MET-05 ARCH-06 MET-02 MET-07|openmetadata|getcollate|
amundsen|Amundsen|LF AI and Data Foundation|Open source|MET-03|amundsen|
purview|Microsoft Purview|Microsoft|Cloud service|MET-03 MET-05 SEC-03 DOC-05 GOV-09 GOV-10 SEC-02 DOC-01|microsoft purview|azure purview|
collibra|Collibra|Collibra|Commercial|MET-03 MET-04 GOV-04 GOV-05 DQ-06 REF-02 ARCH-06 DQ-02 DQ-08 GOV-10 MET-07|collibra|collibra
alation|Alation|Alation|Commercial|MET-03 MET-04|alation|alation
dataplex|Google Dataplex|Google Cloud|Cloud service|MET-03 DQ-06|dataplex|
atlas|Apache Atlas|Apache Software Foundation|Open source|MET-03 MET-05|apache atlas|
openlineage|OpenLineage and Marquez|LF AI and Data Foundation|Open source|MET-05|openlineage|marquez|
atlan|Atlan|Atlan|Commercial|MET-03 MET-05 GOV-05 ARCH-06 MET-07|atlan (?:data|catalog|workspace)|atlan\.com|atlan
dataworld|data.world|data.world|Commercial|MET-03|data\.world|data\.world
solidatus|Solidatus|Solidatus|Commercial|MET-05 ARCH-04|solidatus|solidatus
manta|MANTA|IBM (MANTA)|Commercial|MET-05|manta (?:flow|lineage)|getmanta|manta software
octopai|Octopai|Octopai|Commercial|MET-05|octopai|octopai
infomgmt|Informatica Axon and CDGC|Informatica|Commercial|GOV-04 MET-04 MET-03|informatica axon|cloud data governance and catalog|enterprise data catalog|
onetrust|OneTrust|OneTrust|Commercial|GOV-07 SEC-03 SEC-01 SEC-02|onetrust|onetrust
bigid|BigID|BigID|Commercial|SEC-03 GOV-07|bigid|bigid
varonis|Varonis|Varonis|Commercial|SEC-03 SEC-08 SEC-04|varonis|varonis
immuta|Immuta|Immuta|Commercial|SEC-04 SEC-05|immuta|immuta
privitar|Privitar|Informatica (Privitar)|Commercial|SEC-05|privitar|privitar
protegrity|Protegrity|Protegrity|Commercial|SEC-05|protegrity|protegrity
vault|HashiCorp Vault|HashiCorp (IBM)|Open core|SEC-05 SEC-04|hashicorp vault|vault (?:secrets|kv)|
presidio|Microsoft Presidio|Microsoft (open source)|Open source|SEC-03 SEC-05|presidio|
sdcmicro|sdcMicro and statistical disclosure control|International Household Survey Network (open source)|Open source|SEC-05|sdcmicro|statistical disclosure control|
arx|ARX anonymisation tool|ARX (open source)|Open source|SEC-05|arx (?:anonymi[sz]ation|data anonymi[sz]ation)|
sdv|Synthetic Data Vault|DataCebo (open source)|Open core|SEC-06|synthetic data vault|sdv\.dev|datacebo
synthpop|synthpop|Open source (R)|Open source|SEC-06|synthpop|
mostly|MOSTLY AI|MOSTLY AI|Commercial|SEC-06|mostly ?ai|mostly ai
okta|Okta|Okta|Commercial|SEC-04|okta|okta
entra|Microsoft Entra ID|Microsoft|Cloud service|SEC-04|entra id|azure active directory|azure ad|
postgres|PostgreSQL|PostgreSQL Global Development Group|Open source|STO-01 STO-02 STO-04|postgres(?:ql)?|postgis|
mysql|MySQL and MariaDB|Oracle (MySQL); MariaDB Foundation|Open source|STO-01 STO-04|mysql|mariadb|
sqlserver|Microsoft SQL Server|Microsoft|Commercial|STO-01 STO-04 DW-02 MOD-05|sql server|mssql|azure sql|ssis|ssrs|ssas|
oracle|Oracle Database|Oracle|Commercial|STO-01 STO-04|oracle (?:database|db|exadata|autonomous|12c|19c|21c|23ai|rac)|
mongodb|MongoDB|MongoDB|Open core|STO-01|mongodb|mongo atlas|mongodb
neo4j|Neo4j|Neo4j|Open core|STO-01 MOD-06|neo4j|cypher query|neo4j
elastic|Elasticsearch and OpenSearch|Elastic; OpenSearch Project|Open core|STO-01 DOC-04 DW-03|elasticsearch|opensearch|kibana|elastic stack|elastic(?:search)? (?:bv|nv|ltd)
redis|Redis|Redis|Open core|STO-01|redis|
cassandra|Apache Cassandra|Apache Software Foundation|Open source|STO-01|cassandra|datastax|datastax
dynamodb|Amazon DynamoDB|Amazon Web Services|Cloud service|STO-01|dynamodb|
cosmos|Azure Cosmos DB|Microsoft|Cloud service|STO-01|cosmos ?db|
s3|Amazon S3|Amazon Web Services|Cloud service|STO-01 STO-06 ARCH-05|amazon s3|aws s3|s3 bucket|
flyway|Flyway|Redgate|Open core|STO-03|flyway|
liquibase|Liquibase|Liquibase|Open core|STO-03|liquibase|liquibase
alembic|Alembic|SQLAlchemy project|Open source|STO-03|alembic (?:migration|revision|upgrade)|
veeam|Veeam|Veeam|Commercial|STO-05|veeam|veeam
commvault|Commvault|Commvault|Commercial|STO-05|commvault|commvault
rubrik|Rubrik|Rubrik|Commercial|STO-05|rubrik|rubrik
cohesity|Cohesity|Cohesity|Commercial|STO-05|cohesity|cohesity
druva|Druva|Druva|Commercial|STO-05|druva|druva
mulesoft|MuleSoft|Salesforce (MuleSoft)|Commercial|INT-05 INT-02|mulesoft|anypoint|mulesoft
boomi|Boomi|Boomi|Commercial|INT-02 INT-05|dell boomi|boomi (?:atomsphere|integration|platform)|boomi
snaplogic|SnapLogic|SnapLogic|Commercial|INT-02|snaplogic|snaplogic
fivetran|Fivetran|Fivetran|Commercial|INT-02|fivetran|fivetran
airbyte|Airbyte|Airbyte|Open core|INT-02|airbyte|airbyte
matillion|Matillion|Matillion|Commercial|INT-02|matillion|matillion
nifi|Apache NiFi|Apache Software Foundation|Open source|INT-02 INT-04|apache nifi|nifi (?:flow|processor)|
debezium|Debezium|Red Hat (open source)|Open source|INT-04|debezium|
kinesis|Amazon Kinesis|Amazon Web Services|Cloud service|INT-04|kinesis|
eventhubs|Azure Event Hubs and Service Bus|Microsoft|Cloud service|INT-04|event ?hubs?|azure service bus|
rabbitmq|RabbitMQ|Broadcom (open source)|Open source|INT-04|rabbitmq|
apigee|Apigee|Google Cloud|Cloud service|INT-05|apigee|
apim|Azure API Management|Microsoft|Cloud service|INT-05|azure api management|
kong|Kong|Kong|Open core|INT-05|kong (?:gateway|api|konnect)|kong inc
wso2|WSO2|WSO2|Open core|INT-05 INT-02|wso2|wso2
apigw|Amazon API Gateway|Amazon Web Services|Cloud service|INT-05|api gateway \(aws\)|aws api gateway|amazon api gateway|
xroad|X-Road|Nordic Institute for Interoperability Solutions|Open source|INT-06|x-road|
sharepoint|SharePoint and Microsoft 365|Microsoft|Cloud service|DOC-02 DOC-03 DOC-05|sharepoint|
opentext|OpenText|OpenText|Commercial|DOC-02 DOC-05 DOC-06 DOC-01|opentext|documentum|content server|livelink|open text|opentext
objective|Objective ECM and Objective's other information products|Objective Corporation|Commercial|DOC-02 DOC-05 DOC-01|objective (?:ecm|ecms|nexus|gov365|3sixty|keystone)|objective corporation|objective corporation
preservica|Preservica|Preservica|Commercial|DOC-05|preservica|preservica
arkivum|Arkivum|Arkivum|Commercial|DOC-05|arkivum|arkivum
alfresco|Alfresco|Hyland (Alfresco)|Open core|DOC-02|alfresco|hyland
box|Box|Box|Commercial|DOC-02|box\.com|box enterprise|
archivematica|Archivematica|Artefactual Systems (open source)|Open source|DOC-05|archivematica|artefactual
droid|DROID and PRONOM|The National Archives|Public sector|DOC-05|droid (?:file|format)|pronom|
drupal|Drupal|Drupal community|Open source|DOC-03|drupal|
wordpress|WordPress|WordPress Foundation; Automattic|Open source|DOC-03|wordpress|automattic
contentful|Contentful|Contentful|Commercial|DOC-03|contentful|contentful
umbraco|Umbraco|Umbraco|Open core|DOC-03|umbraco|umbraco
squiz|Squiz Matrix and DXP|Squiz|Commercial|DOC-03|squiz|squiz
tesseract|Tesseract OCR|Open source (Google)|Open source|DOC-02|tesseract|
abbyy|ABBYY|ABBYY|Commercial|DOC-02|abbyy|abbyy
semarchy|Semarchy|Semarchy|Commercial|REF-03 REF-06|semarchy|semarchy
reltio|Reltio|Reltio|Commercial|REF-03|reltio|reltio
profisee|Profisee|Profisee|Commercial|REF-03|profisee|profisee
tamr|Tamr|Tamr|Commercial|REF-03 REF-04|tamr|tamr
stibo|Stibo Systems STEP|Stibo Systems|Commercial|REF-03|stibo|stibo
mds|Microsoft Master Data Services|Microsoft|Commercial|REF-03 REF-02|master data services|
geoplace|AddressBase and the UPRN|Ordnance Survey and GeoPlace|Public sector|REF-05|addressbase|uprn|usrn|os places api|geoplace|(?:geoplace|ordnance survey)
idealpostcodes|Ideal Postcodes|Ideal Postcodes|Commercial|REF-05|ideal ?postcodes|ideal postcodes
loqate|Loqate|GBG (Loqate)|Commercial|REF-05|loqate|loqate
dedupe|dedupe|dedupe.io (open source)|Open source|REF-04 DQ-05|dedupe(?:\.io)?|
recordlinkage|Python Record Linkage Toolkit|Open source|Open source|REF-04|recordlinkage|record linkage toolkit|
fastlink|fastLink|Open source (R)|Open source|REF-04|fastlink|
registers|Registers and code lists published by government|Government Digital Service and others|Public sector|REF-02 REF-06|gov\.uk registers?|registers\.service\.gov\.uk|
teradata|Teradata|Teradata|Commercial|DW-02|teradata|teradata
microstrategy|MicroStrategy|MicroStrategy (Strategy)|Commercial|DW-03|microstrategy|microstrategy
businessobjects|SAP BusinessObjects|SAP|Commercial|DW-03|business ?objects|sap bo|sap businessobjects|
cognos|IBM Cognos|IBM|Commercial|DW-03|cognos|
thoughtspot|ThoughtSpot|ThoughtSpot|Commercial|DW-05|thoughtspot|thoughtspot
grafana|Grafana|Grafana Labs|Open core|DW-03 STO-04 INT-08 DW-06|grafana|grafana labs
r|R|R Foundation|Open source|DW-04 DS-03|r (?:package|markdown|studio|script)|rstudio|cran|tidyverse|quarto|
python|Python data stack (pandas, NumPy, scikit-learn)|Python Software Foundation and open source projects|Open source|DW-04 DS-03 DS-02|(?-i:pandas)|numpy|scikit-learn|jupyter|
stata|Stata|StataCorp|Commercial|DW-04 DS-03|stata|statacorp
spss|IBM SPSS|IBM|Commercial|DW-04 DS-03|spss|
alteryx|Alteryx|Alteryx|Commercial|INT-02 DQ-05 DS-02|alteryx|alteryx
knime|KNIME|KNIME|Open core|INT-02 DS-03|knime|knime
dataiku|Dataiku|Dataiku|Commercial|DS-03 DS-04 DS-02|dataiku|dataiku
datarobot|DataRobot|DataRobot|Commercial|DS-03 DS-04|datarobot|datarobot
sagemaker|Amazon SageMaker|Amazon Web Services|Cloud service|DS-03 DS-04|sagemaker|
azureml|Azure Machine Learning|Microsoft|Cloud service|DS-03 DS-04|azure machine learning|azureml|azure ml|
vertex|Google Vertex AI|Google Cloud|Cloud service|DS-03 DS-04|vertex ai|
mlflow|MLflow|Databricks (open source)|Open source|DS-04|mlflow|
palantir|Palantir Foundry|Palantir Technologies|Commercial|DW-02 INT-02 DS-03 SEC-07|palantir foundry|palantir (?:aip|gotham|platform)|foundry \(palantir\)|palantir
esri|Esri ArcGIS|Esri|Commercial|REF-05 DW-03|arcgis|esri (?:arcgis|mapserver|featureserver|uk)|esri
qgis|QGIS|QGIS project|Open source|REF-05|qgis|
sparx|Sparx Enterprise Architect|Sparx Systems|Commercial|ARCH-01 ARCH-03 MOD-02 MOD-03 MOD-07 INT-01|sparx|enterprise architect \(sparx\)|sparx systems
leanix|LeanIX|SAP (LeanIX)|Commercial|ARCH-01 ARCH-07 INT-01|leanix|leanix
ardoq|Ardoq|Ardoq|Commercial|ARCH-01 ARCH-04 INT-01|ardoq|ardoq
orbus|Orbus iServer|Orbus Software|Commercial|ARCH-01|orbus|iserver365|orbus software
archi|Archi (ArchiMate modelling)|Open Group ArchiMate Forum and open source|Open source|ARCH-01 ARCH-03 MOD-07 INT-01|archimate|archi tool|
erwin|erwin Data Modeler|Quest Software (erwin)|Commercial|MOD-02 MOD-03 MOD-04 MOD-05 MOD-07|erwin data (?:modeler|intelligence)|erwin dm|
erstudio|ER/Studio|IDERA|Commercial|MOD-02 MOD-03 MOD-04 MOD-05 MOD-07|er/studio|
powerdesigner|SAP PowerDesigner|SAP|Commercial|MOD-03 MOD-04 MOD-05 MOD-07|powerdesigner|
dbdiagram|dbdiagram and DBML|Holistics|Commercial|MOD-04|dbml|dbdiagram|
jsonschema|JSON Schema|JSON Schema organisation|Open source|MOD-04 DQ-04|json ?schema|
linkml|LinkML|LinkML community|Open source|MOD-06 MOD-04 MOD-07|linkml|
protege|Protégé|Stanford University (open source)|Open source|MOD-06|prot[eé]g[eé]|
poolparty|PoolParty|Semantic Web Company|Commercial|MOD-06 MET-04 DOC-04 MET-02|poolparty|semantic web company
graphdb|GraphDB and RDF triple stores|Ontotext and others|Open core|MOD-06 STO-01 MET-02|graphdb|ontotext|triple ?store|apache jena|fuseki|stardog|virtuoso|ontotext
trino|Trino and Presto|Trino Software Foundation; Starburst|Open source|INT-07|trino|presto(?:db)?|starburst|starburst
denodo|Denodo|Denodo|Commercial|INT-07|denodo|denodo
servicenow|ServiceNow|ServiceNow|Commercial|GOV-06 DQ-07|servicenow|servicenow
excel|Microsoft Excel|Microsoft|Commercial|DW-03 DQ-03|microsoft excel|excel (?:spreadsheet|workbook|macros?|vba|add-in)|power query|
fairlearn|Fairlearn|Fairlearn community (open source)|Open source|ETH-04|fairlearn|
aif360|AI Fairness 360|LF AI and Data Foundation (open source)|Open source|ETH-04|ai fairness 360|aif360|
dsh|Trusted research environments (secure data environments)|Public sector and research bodies|Public sector|SEC-07|trusted research environment|secure data environment|secure research service|integrated data service|
"""


# Precision of text matches, judged by reading random samples of matched snippets with each repository's description.
# Judged by Claude on 10 November 2026; not owner-confirmed. A tool whose matches were mostly wrong was narrowed or removed.
PRECISION = dict(judged_by="Claude, 10 November 2026 (not owner-confirmed)", method="Random samples of 6 name, description or README matches per tool, judged by reading the snippet and the repository description",
    rounds={"postgres": [6, 6, ""], "redis": [6, 6, ""], "r": [6, 6, ""], "s3": [6, 6, ""], "python": [6, 6, ""], "entra": [6, 6, ""], "sqlserver": [6, 6, ""], "eventhubs": [6, 6, ""],
            "tableau": [6, 6, ""], "grafana": [6, 6, ""], "jsonschema": [6, 6, ""], "powerbi": [6, 5, "one snippet did not show the product"],
            "sharepoint": [6, 4, "mentions of Office 365 email routing and a meeting recording"], "esri": [6, 4, "the Esri shapefile format, not the product: narrowed after this round"],
            "excel": [6, 1, ".xlsx files are a format, not the tool: narrowed to named Excel use after this round"],
            "jira": [6, 1, "ticket and project links, not data issue management: removed from the register after this round"]},
    notices={"powerbi": [4, 4, ""], "sqlserver": [4, 4, ""], "oracle": [4, 4, ""], "qlik": [4, 4, ""], "tableau": [4, 4, ""], "sas": [4, 4, ""], "esri": [4, 4, ""],
             "palantir": [4, 4, "supplier matches: Palantir awarded, including framework places"], "informatica": [4, 4, ""], "snowflake": [4, 4, ""], "servicenow": [4, 4, "IT service management, mapped to issue management"],
             "opentext": [4, 4, ""], "r": [4, 4, ""], "elastic": [4, 4, ""],
             "sharepoint": [4, 1, "Microsoft 365 contracts for networks and skills: narrowed to SharePoint itself after this round"],
             "objective": [4, 2, "awards for Objective's other products (case management, file collaboration): the tool is named for all of them"],
             "python": [3, 2, "'PANDAS V', a pantograph monitoring system: pandas now matches in lower case only"],
             "box": [1, 0, "a different company called Box: the supplier pattern was removed"]})


def top_split(s):
    """Split on "|" outside brackets, so alternatives inside (?:...) stay together."""
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([": depth += 1
        elif ch in ")]": depth -= 1
        if ch == "|" and depth == 0: parts.append(cur); cur = ""
        else: cur += ch
    return parts + [cur]


def parse():
    out = []
    for line in ROWS.strip().splitlines():
        tid, name, maker, model, acts, rest = line.split("|", 5)
        # the text pattern has "|" alternatives of its own: the last top-level alternative is the supplier pattern
        alts = top_split(rest)
        text, supplier = "|".join(alts[:-1]), alts[-1]
        out.append(dict(id=tid, name=name, maker=maker, model=model, acts=acts.split(), text=text, supplier=supplier))
    return out


TOOLS = parse()


def text_rx(t):
    return re.compile(r"(?<![a-z0-9])(?:" + t["text"] + r")(?![a-z0-9])", re.I) if t["text"] else None


def supplier_rx(t):
    return re.compile(r"(?<![a-z0-9])(?:" + t["supplier"] + r")(?![a-z0-9])", re.I) if t["supplier"] else None
