import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_deps import parse
ok = True
def t(name, path, text, want, tf=None):
    global ok; eco, d, f, err = parse(path, text); good = set(want) <= d and (tf is None or set(tf) <= f) and not err
    print("PASS" if good else "FAIL", name, sorted(d)[:8], sorted(f)[:5], err); ok &= good
t("requirements", "requirements.txt", "great_expectations==0.18.1\n# comment\npandas>=2\n-r other.txt\nsoda-core-postgres[x]==3.0", ["great-expectations", "pandas", "soda-core-postgres"])
t("pyproject pep621", "pyproject.toml", '[project]\ndependencies=["pandera>=0.18", "splink"]\n[dependency-groups]\ndev=["pytest"]', ["pandera", "splink", "pytest"])
t("pyproject poetry", "pyproject.toml", '[tool.poetry.dependencies]\npython="^3.11"\npydeequ="1.1"\n', ["pydeequ"])
t("R DESCRIPTION", "DESCRIPTION", "Package: x\nImports:\n    pointblank (>= 0.11),\n    dplyr\nSuggests: testthat\n", ["pointblank", "dplyr", "testthat"])
t("package.json", "package.json", '{"dependencies":{"@elastic/elasticsearch":"8"},"devDependencies":{"jest":"29"}}', ["@elastic/elasticsearch", "jest"])
t("sbt", "build.sbt", 'libraryDependencies += "com.amazon.deequ" % "deequ" % "2.0.7-spark-3.5"\n"org.apache.spark" %% "spark-sql" % "3.5.0"', ["deequ", "spark-sql"])
t("terraform", "infra/main.tf", 'resource "aws_glue_job" "x" {}\nprovider "snowflake" {}\nsource = "databricks/databricks"', [], ["aws_glue_job", "provider:snowflake", "source:databricks/databricks"])
# negative tests: malformed input reports an error and yields nothing; a comment isn't a dependency
eco, d, f, err = parse("package.json", "{not json"); neg1 = bool(err) and not d
eco, d, f, err = parse("requirements.txt", "# great_expectations\n"); neg2 = not d
print("PASS" if neg1 and neg2 else "FAIL", "negative: malformed JSON flagged, commented line ignored"); ok &= neg1 and neg2
sys.exit(0 if ok else 1)
